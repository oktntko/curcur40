// Copyright 2026 oktntko
// SPDX-License-Identifier: GPL-2.0-or-later

#include <string.h>
#include <hal.h>
#include "curcur40_scroll.h"
#include "wait.h"
#include "spi_master.h"
#include "pointing_device.h"
#include "drivers/sensors/pmw3360.h"
#ifdef SPLIT_KEYBOARD
#    include "transactions.h"
#endif

extern uint8_t crc8(const void *data, size_t len);

/*
 * Declare PMW33XX SPI helpers directly rather than including pmw33xx_common.h,
 * because vial-qmk's pmw33xx_common.h declares `pmw33xx_pointing_device_driver`
 * without `extern` (which triggers -fno-common multiple-definition errors).
 */
extern bool                            pmw33xx_init(uint8_t sensor);
extern uint8_t                         pmw33xx_read(uint8_t sensor, uint8_t reg_addr);
extern bool                            pmw33xx_write(uint8_t sensor, uint8_t reg_addr, uint8_t data);
extern void                            __real_pmw33xx_set_cpi(uint8_t sensor, uint16_t cpi);
extern bool                            __real_spi_start(pin_t slavePin, bool lsbFirst, uint8_t mode, uint16_t divisor);
extern void                            __real_spi_stop(void);
extern spi_status_t                    __real_spi_read(void);
extern spi_status_t                    __real_spi_receive(uint8_t *data, uint16_t length);
extern const pointing_device_driver_t *pointing_device_driver;

static uint16_t curcur40_cached_cpi     = PMW33XX_CPI;
static bool     curcur40_spi_kept_alive = false;
static pin_t    curcur40_spi_cs_pin     = PMW33XX_CS_PIN;

/*
 * Fix RP2040 ChibiOS SPI Mode 3 (CPOL=1, CPHA=1) SCLK/NCS race condition:
 * Stock QMK spi_stop() calls spiStop(&SPID1) -> hal_lld_peripheral_reset(RESETS_ALLREG_SPI1),
 * which drops SCLK (GP14) from HIGH (3.3V) to LOW (0V) after every single byte.
 * On the next spi_start(), spiStart() unresets SPI1 (SCLK rising 0V -> 3.3V) and
 * immediately calls spi_select() (NCS falling 3.3V -> 0V) with 0 ns delay — causing
 * the PMW3360 to see a spurious rising SCLK edge while NCS is low and return 0xFF.
 * Keeping SPID1 in SPI_READY holds SCLK solidly HIGH (3.3V) between all transactions.
 */
bool __wrap_spi_start(pin_t slavePin, bool lsbFirst, uint8_t mode, uint16_t divisor) {
    curcur40_spi_cs_pin = slavePin;
    if (!curcur40_spi_kept_alive || SPID1.state != SPI_READY) {
        gpio_set_pin_output(slavePin);
        gpio_write_pin_high(slavePin);
        if (!__real_spi_start(slavePin, lsbFirst, mode, divisor)) {
            return false;
        }
        /* De-assert NCS immediately and let SCLK settle at CPOL=1 HIGH for 10 us */
        gpio_write_pin_high(slavePin);
        wait_us(10);
        curcur40_spi_kept_alive = true;
    }
    /* SCLK is already stably HIGH; drive NCS low and wait tNCS-SCLK (>= 120 ns) */
    gpio_write_pin_low(slavePin);
    wait_us(2);
    return true;
}

void __wrap_spi_stop(void) {
    gpio_write_pin_high(curcur40_spi_cs_pin);
    wait_us(2);
}

spi_status_t __wrap_spi_read(void) {
    /* Transmit 0x00 (MSB=0 read bit) on MOSI instead of ChibiOS dummytx = 0xFF */
    return spi_write(0x00);
}

spi_status_t __wrap_spi_receive(uint8_t *data, uint16_t length) {
    for (uint16_t i = 0; i < length; i++) {
        data[i] = (uint8_t)spi_write(0x00);
    }
    return SPI_STATUS_SUCCESS;
}

/*
 * Fix upstream QMK SPLIT_POINTING_ENABLE + pmw3360 bug:
 * transactions.c:pointing_handlers_slave() calls get_cpi() on EVERY Slave scan.
 * Stock pmw33xx_get_cpi() reads REG_Config1 WITHOUT exiting Motion_Burst mode
 * first, receives 0xFF (MISO High-Z), and writes 0xFF (25,600 CPI, out of spec!)
 * back to REG_Config1 on every scan — causing 21x hyperspeed & cursor teleports.
 * Caching CPI avoids burst-mode corruption and saves ~540 us per Slave scan.
 */
uint16_t __wrap_pmw33xx_get_cpi(uint8_t sensor) {
    (void)sensor;
    return curcur40_cached_cpi;
}

void __wrap_pmw33xx_set_cpi(uint8_t sensor, uint16_t cpi) {
    uint16_t clamped = cpi;
    if (clamped < 100U) {
        clamped = 100U;
    } else if (clamped > 12000U) {
        clamped = 12000U;
    }
    curcur40_cached_cpi = (uint16_t)((clamped / 100U) * 100U);
    pmw33xx_write(sensor, REG_Config2, 0x00);
    __real_pmw33xx_set_cpi(sensor, curcur40_cached_cpi);
}

/* -------------------------------------------------------------------------
 * Lightweight Cortex-M0+ helpers (no libm / powf dependency)
 * ------------------------------------------------------------------------- */
static inline float abs_f(float x) {
    return (x < 0.0f) ? -x : x;
}

static inline float clamp_f(float x, float lo, float hi) {
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
}

static inline int16_t abs_i16(int16_t x) {
    return (x < 0) ? (int16_t)(-x) : x;
}

static inline int16_t clamp_i16(int16_t x, int16_t lo, int16_t hi) {
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
}

/* -------------------------------------------------------------------------
 * 1. CKW12 Ballistic Wheel State (Method A: Deterministic Flick Multiplier)
 * ------------------------------------------------------------------------- */
static bool     enc_initialized = false;
static uint32_t enc_last_ms     = 0;
static uint32_t enc_burst_ms    = 0;
static int8_t   enc_last_dir_v  = 0;
static int8_t   enc_last_dir_h  = 0;
static uint8_t  enc_streak      = 0;
static int16_t  enc_pending_v   = 0;
static int16_t  enc_pending_h   = 0;

static void curcur40_enqueue_enc_wheel(int8_t dir_v, int8_t dir_h) {
    uint32_t now = timer_read32();
    int16_t  steps = 1;

    if (!enc_initialized) {
        enc_initialized = true;
        enc_streak      = 0;
    } else {
        uint32_t dt       = timer_elapsed32(enc_last_ms);
        bool     same_dir = (dir_v == enc_last_dir_v) && (dir_h == enc_last_dir_h);

        if (!same_dir || dt > CURCUR40_ENC_ACCEL_WINDOW_MS) {
            enc_streak = 0;
            steps      = 1;
        } else if (dt >= CURCUR40_ENC_SLOW_MS) {
            enc_streak = 0;
            steps      = 1;
        } else {
            if (enc_streak < 8) {
                enc_streak++;
            }
            if (dt >= CURCUR40_ENC_MID_MS) {
                /* Moderate roll (60..94 ms): 2x -> 3x */
                steps = (enc_streak >= 2) ? 3 : 2;
            } else if (dt >= CURCUR40_ENC_FAST_MS) {
                /* Brisk roll (35..59 ms): 4x -> 6x */
                steps = (enc_streak >= 2) ? 6 : 4;
            } else if (dt >= CURCUR40_ENC_FLICK_MS) {
                /* Fast flick (20..34 ms): 6x -> 9x -> 11x */
                steps = 6 + ((enc_streak >= 2) ? 3 : 0) + ((enc_streak >= 3) ? 2 : 0);
            } else {
                /* Hard flick (< 20 ms): 8x -> CURCUR40_ENC_MAX_STEP (12x) */
                steps = (enc_streak >= 2) ? CURCUR40_ENC_MAX_STEP : 8;
            }
        }
    }

    enc_last_ms    = now;
    enc_last_dir_v = dir_v;
    enc_last_dir_h = dir_h;

    /* Cancel any remaining micro-burst in the opposite direction immediately */
    if (dir_v != 0 && (enc_pending_v * (int16_t)dir_v < 0)) {
        enc_pending_v = 0;
    }
    if (dir_h != 0 && (enc_pending_h * (int16_t)dir_h < 0)) {
        enc_pending_h = 0;
    }

    enc_pending_v = clamp_i16((int16_t)(enc_pending_v + (int16_t)dir_v * steps),
                              -CURCUR40_ENC_MAX_PENDING, CURCUR40_ENC_MAX_PENDING);
    enc_pending_h = clamp_i16((int16_t)(enc_pending_h + (int16_t)dir_h * steps),
                              -CURCUR40_ENC_MAX_PENDING, CURCUR40_ENC_MAX_PENDING);
}

/* -------------------------------------------------------------------------
 * 2. PMW3360 Trackball 2D Inertia Drag-Scroll State
 * ------------------------------------------------------------------------- */
static bool     scroll_mo_held       = false;
static bool     scroll_tg_active     = false;
static bool     scroll_sl_held       = false;
static bool     prev_scroll_active   = false;
static bool     motion_seen          = false;
static bool     is_coasting          = false;
static uint8_t  prev_zoom_mods       = 0;
static uint32_t last_motion_ms       = 0;
static uint32_t last_inertia_tick_ms = 0;
static float    scroll_accum_v       = 0.0f;
static float    scroll_accum_h       = 0.0f;
static float    ema_vel_v            = 0.0f;
static float    ema_vel_h            = 0.0f;
static float    inertia_vel_v        = 0.0f;
static float    inertia_vel_h        = 0.0f;

static void curcur40_stop_coasting(void) {
    inertia_vel_v = 0.0f;
    inertia_vel_h = 0.0f;
    ema_vel_v     = 0.0f;
    ema_vel_h     = 0.0f;
    is_coasting   = false;
}

static void curcur40_reset_scroll_state(void) {
    curcur40_stop_coasting();
    scroll_accum_v = 0.0f;
    scroll_accum_h = 0.0f;
    motion_seen    = false;
}

static inline bool curcur40_is_inertia_mode(void) {
    return scroll_mo_held || scroll_tg_active || layer_state_is(CURCUR40_SCROLL_LAYER);
}

static inline bool curcur40_is_scroll_active(void) {
    return curcur40_is_inertia_mode() || scroll_sl_held;
}

/* -------------------------------------------------------------------------
 * 3. PMW3360 Lift-Off / SQUAL Threshold Tuning & Live Notepad Diagnostics
 * ------------------------------------------------------------------------- */
typedef struct {
    uint8_t lift_cfg; /* REG_Lift_Config (0x63): 0x02 = +2mm, 0x03 = +3mm */
    uint8_t min_sq;   /* REG_Min_SQ_Run  (0x2B): default 0x10 (16)        */
    uint8_t raw_th;   /* REG_Raw_Data_Threshold (0x2C): default 0x0A (10) */
} pmw3360_tune_preset_t;

static const pmw3360_tune_preset_t pmw3360_presets[4] = {
    /* m0 (Boot default): +3mm lift-off + relaxed SQUAL threshold (6 vs 16) */
    {0x03, 0x06, 0x07},
    /* m1 (Ultra sensitivity): +3mm lift-off + minimal SQUAL cutoff (1) */
    {0x03, 0x01, 0x04},
    /* m2 (+3mm lift-off only, stock SQUAL=16 & RawTh=10) */
    {0x03, 0x10, 0x0A},
    /* m3 (Stock v0.2.2 baseline: +2mm lift-off, SQUAL=16, RawTh=10) */
    {0x02, 0x10, 0x0A},
};

static uint8_t  tb_dbg_mode       = (uint8_t)(CURCUR40_PMW3360_DEFAULT_MODE & 0x03U);
static bool     tb_dbg_streaming  = false;
static uint32_t tb_dbg_last_ms    = 0;
static int32_t  tb_dbg_dx         = 0;
static int32_t  tb_dbg_dy         = 0;
static bool     l_thumb_mo1_held  = false;
static bool     swallow_l24       = false;
static bool     swallow_l25       = false;
static bool     r_thumb_mid_held  = false;
static bool     swallow_r46       = false;
static bool     swallow_r56       = false;

enum {
    PMW_DIAG_CMD_QUERY    = 0U,
    PMW_DIAG_CMD_SET_MODE = 1U,
};

typedef struct __attribute__((packed)) {
    uint8_t cmd;
    uint8_t mode;
} pmw_diag_req_t;

typedef struct __attribute__((packed)) {
    uint8_t  ok;
    uint8_t  mode;
    uint8_t  pid;
    uint8_t  srom;
    uint8_t  mot;
    uint8_t  sq;
    uint8_t  sum;
    uint8_t  mx;
    uint8_t  mn;
    uint8_t  reinit;
    uint16_t shutter;
} pmw_diag_resp_t;

#ifdef SPLIT_KEYBOARD
_Static_assert(sizeof(pmw_diag_req_t) <= RPC_M2S_BUFFER_SIZE, "pmw_diag_req_t exceeds RPC_M2S_BUFFER_SIZE");
_Static_assert(sizeof(pmw_diag_resp_t) <= RPC_S2M_BUFFER_SIZE, "pmw_diag_resp_t exceeds RPC_S2M_BUFFER_SIZE");
#endif

/*
 * Lock-free double-buffered diagnostic cache on the Right half:
 * - Only the Right main QMK thread (pointing_device_init_kb / housekeeping_task_kb)
 *   ever touches SPID1, completely eliminating ChibiOS SlaveThread vs main-thread
 *   SPI bus contention.
 */
static pmw_diag_resp_t   tb_resp_buf[2];
static volatile uint8_t  tb_resp_active_idx       = 0U;
static volatile bool     tb_slave_poll_active     = false;
static volatile uint32_t tb_slave_poll_lease_ms   = 0U;
static volatile bool     tb_has_pending_mode      = false;
static volatile uint8_t  tb_pending_mode          = 0U;
static bool              tb_cache_ready           = false;
static bool              tb_sensor_disconnected   = false;
static uint32_t          tb_slave_sample_ms       = 0U;
static bool              tb_need_motion_freeze    = true;
static uint32_t          tb_last_sensor_poll_ms   = 0U;
static report_mouse_t    tb_slave_cached_report   = {0};
static volatile bool     tb_slave_report_consumed = true;
static uint8_t           tb_slave_seq             = 1U;
static uint8_t           tb_slave_last_crc8       = 0U;
static uint8_t           tb_master_last_seq       = 0U;
static uint32_t          tb_master_last_rx_ms     = 0U;
static int16_t           tb_prev_valid_dx         = 0;
static int16_t           tb_prev_valid_dy         = 0;

#ifdef SPLIT_KEYBOARD
static void curcur40_pointing_data_slave_cb(uint8_t initiator2target_buffer_size, const void *initiator2target_buffer,
                                            uint8_t target2initiator_buffer_size, void *target2initiator_buffer) {
    (void)initiator2target_buffer_size;
    (void)initiator2target_buffer;
    (void)target2initiator_buffer_size;
    (void)target2initiator_buffer;
    tb_slave_report_consumed = true;
}
#endif

static void curcur40_pmw3360_init_driver(void) {
    pmw33xx_init(0);
}

static void curcur40_pmw3360_set_cpi_driver(uint16_t cpi) {
    __wrap_pmw33xx_set_cpi(0, cpi);
}

static uint16_t curcur40_pmw3360_get_cpi_driver(void) {
    return __wrap_pmw33xx_get_cpi(0);
}

/*
 * Safe non-burst 1-ms PMW3360 motion polling driver (Datasheet R1.50 Sec 11.0, p.30):
 * - Eliminates Motion_Burst (0x50) continuous 12-byte reads so a single bit-error
 *   can never shift subsequent bytes or leave the sensor stuck in burst state.
 * - Freezes/clears the motion registers via Write(REG_Motion, 0x01) before reading
 *   REG_Motion (0x02), and only reads Delta_X_L..Delta_Y_H when bit 7 (mot) == 1
 *   and bit 3 (lift) == 0 and the reserved bits (bits 6, 5, 2, 1) are 0.
 * - Synchronizes with QMK's SPLIT_POINTING_ENABLE (transactions.c) by holding each
 *   sampled report until the Master actually pulls GET_POINTING_DATA, then clearing
 *   it to {0} and tagging each valid sample with a unique `boot_x` sequence token
 *   whose CRC8 never collides with the previous report or zero report.
 */
static report_mouse_t curcur40_pmw3360_get_report(report_mouse_t mouse_report) {
    (void)mouse_report;
    report_mouse_t zero_rep = {0};
    if (is_keyboard_left()) {
        return zero_rep;
    }

    uint32_t now = timer_read32();
    if (!tb_slave_report_consumed && timer_elapsed32(tb_last_sensor_poll_ms) < 5U) {
        return tb_slave_cached_report;
    }
    if (timer_elapsed32(tb_last_sensor_poll_ms) < 1U) {
        if (tb_slave_report_consumed) {
            memset(&tb_slave_cached_report, 0, sizeof(tb_slave_cached_report));
            tb_slave_last_crc8 = crc8(&tb_slave_cached_report, sizeof(tb_slave_cached_report));
        }
        return tb_slave_cached_report;
    }
    tb_last_sensor_poll_ms = now;

    if (tb_need_motion_freeze) {
        pmw33xx_write(0, REG_Motion, 0x01);
        tb_need_motion_freeze = false;
    }

    uint8_t mot = pmw33xx_read(0, REG_Motion);
    if (mot == 0xFFU || (mot & 0x66U) != 0U) {
        /* Invalid/corrupted status byte: re-sync by writing REG_Motion */
        tb_need_motion_freeze = true;
        memset(&tb_slave_cached_report, 0, sizeof(tb_slave_cached_report));
        tb_slave_report_consumed = true;
        tb_slave_last_crc8       = crc8(&tb_slave_cached_report, sizeof(tb_slave_cached_report));
        return tb_slave_cached_report;
    }

    if ((mot & 0x80U) == 0U) {
        /* No motion since last poll: no need to write REG_Motion on next poll */
        memset(&tb_slave_cached_report, 0, sizeof(tb_slave_cached_report));
        tb_slave_report_consumed = true;
        tb_slave_last_crc8       = crc8(&tb_slave_cached_report, sizeof(tb_slave_cached_report));
        return tb_slave_cached_report;
    }

    /* Motion bit is set: read all 4 delta registers in strict datasheet order */
    uint8_t dxl = pmw33xx_read(0, REG_Delta_X_L);
    uint8_t dxh = pmw33xx_read(0, REG_Delta_X_H);
    uint8_t dyl = pmw33xx_read(0, REG_Delta_Y_L);
    uint8_t dyh = pmw33xx_read(0, REG_Delta_Y_H);
    tb_need_motion_freeze = true;

    if ((mot & 0x08U) != 0U) {
        /* Ball is lifted: discard delta after draining registers */
        memset(&tb_slave_cached_report, 0, sizeof(tb_slave_cached_report));
        tb_slave_report_consumed = true;
        tb_slave_last_crc8       = crc8(&tb_slave_cached_report, sizeof(tb_slave_cached_report));
        return tb_slave_cached_report;
    }

    int16_t dx = (int16_t)(((uint16_t)dxh << 8) | (uint16_t)dxl);
    int16_t dy = (int16_t)(((uint16_t)dyh << 8) | (uint16_t)dyl);

    /* Reject out-of-range 1-ms spikes (e.g. 0xFFxx upper-byte sign-extension glitch) */
    if (dx > CURCUR40_MAX_VALID_DELTA || dx < -CURCUR40_MAX_VALID_DELTA ||
        dy > CURCUR40_MAX_VALID_DELTA || dy < -CURCUR40_MAX_VALID_DELTA) {
        memset(&tb_slave_cached_report, 0, sizeof(tb_slave_cached_report));
        tb_slave_report_consumed = true;
        tb_slave_last_crc8       = crc8(&tb_slave_cached_report, sizeof(tb_slave_cached_report));
        return tb_slave_cached_report;
    }

    if (dx == 0 && dy == 0) {
        memset(&tb_slave_cached_report, 0, sizeof(tb_slave_cached_report));
        tb_slave_report_consumed = true;
        tb_slave_last_crc8       = crc8(&tb_slave_cached_report, sizeof(tb_slave_cached_report));
        return tb_slave_cached_report;
    }

    report_mouse_t rep = {0};
    rep.x              = (mouse_xy_report_t)dx;
    rep.y              = (mouse_xy_report_t)dy;

    /*
     * Choose a non-zero sequence number in `boot_x` (1..125) such that:
     * 1. It differs from the previous sequence number (so Master detects every new sample), and
     * 2. `crc8(&rep)` differs from both `tb_slave_last_crc8` and `crc8(&zero_rep)`
     *    (so transactions.c:read_if_checksum_mismatch() is guaranteed to fetch it).
     */
    uint8_t zero_crc = crc8(&zero_rep, sizeof(zero_rep));
    uint8_t next_seq = tb_slave_seq;
    uint8_t new_crc  = 0U;
    for (uint8_t attempt = 0U; attempt < 16U; attempt++) {
        next_seq = (uint8_t)((next_seq % 125U) + 1U);
        rep.boot_x = (int8_t)next_seq;
        new_crc    = crc8(&rep, sizeof(rep));
        if (new_crc != tb_slave_last_crc8 && new_crc != zero_crc) {
            break;
        }
    }
    tb_slave_seq             = next_seq;
    tb_slave_last_crc8       = new_crc;
    tb_slave_cached_report   = rep;
    tb_slave_report_consumed = false;
    return tb_slave_cached_report;
}

static const pointing_device_driver_t curcur40_pmw3360_driver = {
    .init       = curcur40_pmw3360_init_driver,
    .get_report = curcur40_pmw3360_get_report,
    .set_cpi    = curcur40_pmw3360_set_cpi_driver,
    .get_cpi    = curcur40_pmw3360_get_cpi_driver,
};

static void curcur40_apply_pmw3360_mode(uint8_t mode) {
    if (is_keyboard_left()) {
        return;
    }
    uint8_t m = (uint8_t)(mode & 0x03U);
    /* Disable Rest mode so SQUAL is valid and reset in_burst[0] cleanly */
    pmw33xx_write(0, REG_Config2, 0x00);
    pmw33xx_write(0, REG_Lift_Config, pmw3360_presets[m].lift_cfg);
    pmw33xx_write(0, REG_Min_SQ_Run, pmw3360_presets[m].min_sq);
    pmw33xx_write(0, REG_Raw_Data_Threshold, pmw3360_presets[m].raw_th);
    tb_need_motion_freeze = true;
}

static bool curcur40_sample_pmw3360_main_thread(bool apply_mode, uint8_t new_mode, pmw_diag_resp_t *out_resp) {
    if (is_keyboard_left()) {
        if (out_resp != NULL) {
            memset(out_resp, 0, sizeof(*out_resp));
        }
        return false;
    }

    pmw33xx_write(0, REG_Config2, 0x00);
    wait_us(50);

    if (apply_mode) {
        tb_dbg_mode = (uint8_t)(new_mode & 0x03U);
        curcur40_apply_pmw3360_mode(tb_dbg_mode);
    }

    uint8_t pid  = pmw33xx_read(0, REG_Product_ID);
    uint8_t inv  = pmw33xx_read(0, REG_Inverse_Product_ID);
    uint8_t srom = pmw33xx_read(0, REG_SROM_ID);
    pmw33xx_write(0, REG_Motion, 0x01);
    uint8_t mot  = pmw33xx_read(0, REG_Motion);
    /* Clear latched motion registers per PMW3360 Datasheet Sec 11.0 (p.30) */
    (void)pmw33xx_read(0, REG_Delta_X_L);
    (void)pmw33xx_read(0, REG_Delta_X_H);
    (void)pmw33xx_read(0, REG_Delta_Y_L);
    (void)pmw33xx_read(0, REG_Delta_Y_H);
    tb_need_motion_freeze = true;
    uint8_t sq   = pmw33xx_read(0, REG_SQUAL);
    uint8_t sum  = pmw33xx_read(0, REG_Raw_Data_Sum);
    uint8_t mx   = pmw33xx_read(0, REG_Maximum_Raw_data);
    uint8_t mn   = pmw33xx_read(0, REG_Minimum_Raw_data);
    /* Datasheet p.36: read Shutter_Upper (0x0C) then Shutter_Lower (0x0B) consecutively */
    uint8_t  sh_u    = pmw33xx_read(0, REG_Shutter_Upper);
    uint8_t  sh_l    = pmw33xx_read(0, REG_Shutter_Lower);
    uint16_t shutter = ((uint16_t)sh_u << 8) | (uint16_t)sh_l;

    /*
     * Only re-initialize if the sensor had actually lost connection/power
     * (PID != 0x42 or Inverse_PID != 0xBD) and then reconnected.
     * Note: QMK runs PMW3360 on internal masked ROM where SROM_ID is normally 0x00.
     */
    uint8_t did_reinit = 0U;
    if (pid != 0x42U || inv != 0xBDU) {
        tb_sensor_disconnected = true;
    } else if (tb_sensor_disconnected) {
        tb_sensor_disconnected = false;
        if (pmw33xx_init(0)) {
            curcur40_apply_pmw3360_mode(tb_dbg_mode);
            did_reinit = 1U;
        }
    }

    pmw_diag_resp_t sample = {
        .ok      = 2U,
        .mode    = (uint8_t)(tb_dbg_mode & 0x03U),
        .pid     = pid,
        .srom    = srom,
        .mot     = mot,
        .sq      = sq,
        .sum     = sum,
        .mx      = mx,
        .mn      = mn,
        .reinit  = did_reinit,
        .shutter = shutter,
    };

    uint8_t next_idx      = (uint8_t)(tb_resp_active_idx ^ 1U);
    tb_resp_buf[next_idx] = sample;
    __asm__ volatile("" ::: "memory");
    tb_resp_active_idx = next_idx;
    tb_cache_ready     = true;

    if (out_resp != NULL) {
        *out_resp = sample;
    }
    return true;
}

#ifdef SPLIT_KEYBOARD
static void curcur40_pmw_diag_slave_cb(uint8_t in_buflen, const void *in_data,
                                       uint8_t out_buflen, void *out_data) {
    if (in_buflen < sizeof(pmw_diag_req_t) || out_buflen < sizeof(pmw_diag_resp_t)) {
        if (out_data != NULL && out_buflen > 0U) {
            memset(out_data, 0, out_buflen);
        }
        return;
    }
    pmw_diag_req_t req;
    memcpy(&req, in_data, sizeof(req));

    tb_slave_poll_lease_ms = timer_read32();
    tb_slave_poll_active   = true;

    if (req.cmd == PMW_DIAG_CMD_SET_MODE) {
        tb_pending_mode     = (uint8_t)(req.mode & 0x03U);
        tb_has_pending_mode = true;
    }

    uint8_t idx = tb_resp_active_idx;
    memcpy(out_data, &tb_resp_buf[idx], sizeof(pmw_diag_resp_t));
}
#endif

static bool curcur40_fetch_pmw3360_diag(uint8_t cmd, uint8_t mode, pmw_diag_resp_t *resp) {
    pmw_diag_req_t req = {
        .cmd  = cmd,
        .mode = (uint8_t)(mode & 0x03U),
    };
    memset(resp, 0, sizeof(*resp));

    if (!is_keyboard_left()) {
        return curcur40_sample_pmw3360_main_thread(cmd == PMW_DIAG_CMD_SET_MODE, req.mode, resp);
    }

#ifdef SPLIT_KEYBOARD
    if (transaction_rpc_exec(RPC_ID_CURCUR40_PMW_DIAG, sizeof(req), &req, sizeof(*resp), resp)) {
        return resp->ok != 0U;
    }
#endif
    return false;
}

/* US/JIS layout-neutral ASCII helpers (only lowercase a-z, 0-9, space, '-', '\n') */
static char *buf_str(char *p, const char *s) {
    while (*s) {
        *p++ = *s++;
    }
    return p;
}

static char *buf_hex8(char *p, uint8_t v) {
    static const char hex[16] = "0123456789abcdef";
    *p++                      = hex[(v >> 4) & 0x0FU];
    *p++                      = hex[v & 0x0FU];
    return p;
}

static char *buf_u3(char *p, uint8_t v) {
    *p++ = (char)('0' + (v / 100U));
    *p++ = (char)('0' + ((v / 10U) % 10U));
    *p++ = (char)('0' + (v % 10U));
    return p;
}

static char *buf_u5(char *p, uint16_t v) {
    *p++ = (char)('0' + (v / 10000U));
    *p++ = (char)('0' + ((v / 1000U) % 10U));
    *p++ = (char)('0' + ((v / 100U) % 10U));
    *p++ = (char)('0' + ((v / 10U) % 10U));
    *p++ = (char)('0' + (v % 10U));
    return p;
}

static char *buf_i32(char *p, int32_t v) {
    uint32_t u;
    if (v < 0) {
        *p++ = '-';
        u    = (uint32_t)(-(v + 1)) + 1U;
    } else {
        u = (uint32_t)v;
    }
    if (u > 99999U) {
        u = 99999U;
    }
    char    tmp[6];
    uint8_t n = 0;
    do {
        tmp[n++] = (char)('0' + (u % 10U));
        u /= 10U;
    } while (u > 0U);
    while (n > 0U) {
        *p++ = tmp[--n];
    }
    return p;
}

static void curcur40_send_ascii(const char *s) {
    uint8_t saved_mods = get_mods();
    if (saved_mods != 0) {
        clear_mods();
        send_keyboard_report();
    }
    send_string(s);
    if (saved_mods != 0) {
        set_mods(saved_mods);
        send_keyboard_report();
    }
}

static bool curcur40_emit_pmw3360_diag_ex(uint8_t cmd, uint8_t mode) {
    pmw_diag_resp_t resp;
    if (!curcur40_fetch_pmw3360_diag(cmd, mode, &resp)) {
        curcur40_send_ascii("err trrs rpc fail flash both halves\n");
        tb_dbg_streaming = false;
        return false;
    }

    tb_dbg_mode = (uint8_t)(resp.mode & 0x03U);

    int32_t dx = tb_dbg_dx;
    int32_t dy = tb_dbg_dy;
    tb_dbg_dx  = 0;
    tb_dbg_dy  = 0;

    char  line[96];
    char *p = line;
    *p++    = 'm';
    *p++    = (char)('0' + tb_dbg_mode);
    p       = buf_str(p, (resp.ok >= 2U) ? "v2r2 id" : "v2r1 id");
    p       = buf_hex8(p, resp.pid);
    p       = buf_str(p, " sr");
    p       = buf_hex8(p, resp.srom);
    p       = buf_str(p, " lf");
    *p++    = (resp.mot & 0x08U) ? '1' : '0';
    p       = buf_str(p, " sq");
    p       = buf_u3(p, resp.sq);
    p       = buf_str(p, " sm");
    p       = buf_u3(p, resp.sum);
    p       = buf_str(p, " mx");
    p       = buf_u3(p, resp.mx);
    p       = buf_str(p, " mn");
    p       = buf_u3(p, resp.mn);
    p       = buf_str(p, " sh");
    p       = buf_u5(p, resp.shutter);
    p       = buf_str(p, " dx");
    p       = buf_i32(p, dx);
    p       = buf_str(p, " dy");
    p       = buf_i32(p, dy);
    *p++    = '\n';
    *p      = '\0';

    curcur40_send_ascii(line);

    if (resp.reinit != 0U) {
        curcur40_send_ascii("pmw3360 reinit ok\n");
    }
    return true;
}

static void curcur40_toggle_tb_dbg(void) {
    tb_dbg_streaming = !tb_dbg_streaming;
    tb_dbg_dx        = 0;
    tb_dbg_dy        = 0;
    tb_dbg_last_ms   = timer_read32();
    if (tb_dbg_streaming) {
        if (is_keyboard_left()) {
            pmw_diag_resp_t dummy;
            (void)curcur40_fetch_pmw3360_diag(PMW_DIAG_CMD_QUERY, tb_dbg_mode, &dummy);
            wait_ms(8);
        }
        char  hdr[36];
        char *p = buf_str(hdr, "pmw3360 v2 live on m");
        *p++    = (char)('0' + (tb_dbg_mode & 0x03U));
        *p++    = '\n';
        *p      = '\0';
        curcur40_send_ascii(hdr);
        (void)curcur40_emit_pmw3360_diag_ex(PMW_DIAG_CMD_QUERY, tb_dbg_mode);
        tb_dbg_last_ms = timer_read32();
    } else {
        curcur40_send_ascii("pmw3360 live off\n");
    }
}

static void curcur40_cycle_tb_mode(void) {
    uint8_t next_mode = (uint8_t)((tb_dbg_mode + 1U) & 0x03U);
    char    msg[32];
    char   *p = buf_str(msg, "pmw3360 set m");
    *p++      = (char)('0' + next_mode);
    *p++      = '\n';
    *p        = '\0';
    curcur40_send_ascii(msg);
    if (is_keyboard_left()) {
        pmw_diag_resp_t dummy;
        if (curcur40_fetch_pmw3360_diag(PMW_DIAG_CMD_SET_MODE, next_mode, &dummy)) {
            wait_ms(8);
            if (curcur40_emit_pmw3360_diag_ex(PMW_DIAG_CMD_QUERY, next_mode)) {
                tb_dbg_mode = next_mode;
            }
        } else {
            curcur40_send_ascii("err trrs rpc fail flash both halves\n");
            tb_dbg_streaming = false;
        }
    } else if (curcur40_emit_pmw3360_diag_ex(PMW_DIAG_CMD_SET_MODE, next_mode)) {
        tb_dbg_mode = next_mode;
    }
    tb_dbg_last_ms = timer_read32();
}

/* -------------------------------------------------------------------------
 * QMK Keyboard-Level Hooks (always chain to *_user)
 * ------------------------------------------------------------------------- */
void keyboard_pre_init_kb(void) {
    pointing_device_driver = &curcur40_pmw3360_driver;
    keyboard_pre_init_user();
}

void keyboard_post_init_kb(void) {
    pointing_device_driver = &curcur40_pmw3360_driver;
#ifdef SPLIT_KEYBOARD
    split_transaction_table[GET_POINTING_DATA].slave_callback = curcur40_pointing_data_slave_cb;
    transaction_register_rpc(RPC_ID_CURCUR40_PMW_DIAG, curcur40_pmw_diag_slave_cb);
#endif
    keyboard_post_init_user();
}

void pointing_device_init_kb(void) {
    pointing_device_driver = &curcur40_pmw3360_driver;
    if (!is_keyboard_left()) {
        curcur40_apply_pmw3360_mode(tb_dbg_mode);
        (void)curcur40_sample_pmw3360_main_thread(false, tb_dbg_mode, NULL);
        tb_slave_sample_ms = timer_read32();
    }
    pointing_device_init_user();
}

void housekeeping_task_kb(void) {
    if (!is_keyboard_left()) {
        if (tb_has_pending_mode) {
            uint8_t m           = tb_pending_mode;
            tb_has_pending_mode = false;
            (void)curcur40_sample_pmw3360_main_thread(true, m, NULL);
            tb_slave_sample_ms = timer_read32();
        } else if (tb_slave_poll_active && timer_elapsed32(tb_slave_poll_lease_ms) > 2500U) {
            tb_slave_poll_active = false;
        } else if (!tb_cache_ready ||
                   (tb_slave_poll_active && timer_elapsed32(tb_slave_sample_ms) >= CURCUR40_TB_SLAVE_SAMPLE_MS)) {
            (void)curcur40_sample_pmw3360_main_thread(false, tb_dbg_mode, NULL);
            tb_slave_sample_ms = timer_read32();
        }
    }

    if (tb_dbg_streaming && is_keyboard_master() &&
        timer_elapsed32(tb_dbg_last_ms) >= CURCUR40_TB_DBG_INTERVAL_MS) {
        tb_dbg_last_ms = timer_read32();
        (void)curcur40_emit_pmw3360_diag_ex(PMW_DIAG_CMD_QUERY, tb_dbg_mode);
    }
    housekeeping_task_user();
}

bool process_record_kb(uint16_t keycode, keyrecord_t *record) {
    if (!process_record_user(keycode, record)) {
        return false;
    }

    /*
     * Built-in Left- & Right-half diagnostic chords (work immediately without EEPROM reset):
     * 1. Left-hand chord (works over TRRS while right hand holds/tests the trackball):
     *    Hold Left 2nd thumb [3,4] (default MO(1)) + tap:
     *      - [2,5] ('B' key, inner bottom row) : toggle 1s live PMW3360 Notepad readout ON/OFF
     *      - [2,4] ('V' key, next to 'B')      : cycle sensitivity mode (m0..m3) + 1-line snapshot
     * 2. Right-hand chord:
     *    Hold Right middle thumb [7,4] (default MO(2)) + tap:
     *      - [4,6] (CKW12 wheel push) : toggle 1s live PMW3360 Notepad readout ON/OFF
     *      - [5,6] (inner key rEXSW2) : cycle sensitivity mode (m0..m3) + 1-line snapshot
     */
    if (!IS_ENCODEREVENT(record->event)) {
        uint8_t r = record->event.key.row;
        uint8_t c = record->event.key.col;
        if (r == 3U && c == 4U) {
            bool is_plain_mod = (keycode >= KC_LCTL && keycode <= KC_RGUI);
            l_thumb_mo1_held  = record->event.pressed && !is_plain_mod;
        } else if (r == 2U && c == 5U) {
            if (record->event.pressed && l_thumb_mo1_held) {
                swallow_l25 = true;
                curcur40_toggle_tb_dbg();
                return false;
            }
            if (!record->event.pressed && swallow_l25) {
                swallow_l25 = false;
                return false;
            }
        } else if (r == 2U && c == 4U) {
            if (record->event.pressed && l_thumb_mo1_held) {
                swallow_l24 = true;
                curcur40_cycle_tb_mode();
                return false;
            }
            if (!record->event.pressed && swallow_l24) {
                swallow_l24 = false;
                return false;
            }
        } else if (r == 7U && c == 4U) {
            r_thumb_mid_held = record->event.pressed;
        } else if (r == 4U && c == 6U) {
            if (record->event.pressed && r_thumb_mid_held) {
                swallow_r46 = true;
                curcur40_toggle_tb_dbg();
                return false;
            }
            if (!record->event.pressed && swallow_r46) {
                swallow_r46 = false;
                return false;
            }
        } else if (r == 5U && c == 6U) {
            if (record->event.pressed && r_thumb_mid_held) {
                swallow_r56 = true;
                curcur40_cycle_tb_mode();
                return false;
            }
            if (!record->event.pressed && swallow_r56) {
                swallow_r56 = false;
                return false;
            }
        }
    }

#ifdef ENCODER_MAP_ENABLE
    /* Intercept mouse wheel keycodes emitted by CKW12 (or dynamic Vial encoder_map) */
    if (IS_ENCODEREVENT(record->event)) {
        switch (keycode) {
            case QK_MOUSE_WHEEL_UP:
                if (record->event.pressed) {
                    curcur40_enqueue_enc_wheel(1, 0);
                }
                return false;
            case QK_MOUSE_WHEEL_DOWN:
                if (record->event.pressed) {
                    curcur40_enqueue_enc_wheel(-1, 0);
                }
                return false;
            case QK_MOUSE_WHEEL_RIGHT:
                if (record->event.pressed) {
                    curcur40_enqueue_enc_wheel(0, 1);
                }
                return false;
            case QK_MOUSE_WHEEL_LEFT:
                if (record->event.pressed) {
                    curcur40_enqueue_enc_wheel(0, -1);
                }
                return false;
            default:
                break;
        }
    }
#endif

    switch (keycode) {
        case SCRL_MO:
            scroll_mo_held = record->event.pressed;
            if (!curcur40_is_scroll_active()) {
                curcur40_reset_scroll_state();
            }
            return false;

        case SCRL_TG:
            if (record->event.pressed) {
                scroll_tg_active = !scroll_tg_active;
                if (!curcur40_is_scroll_active()) {
                    curcur40_reset_scroll_state();
                }
            }
            return false;

        case SCRL_SL:
            scroll_sl_held = record->event.pressed;
            curcur40_stop_coasting();
            if (!curcur40_is_scroll_active()) {
                curcur40_reset_scroll_state();
            }
            return false;

        case TB_DBG:
            if (record->event.pressed) {
                curcur40_toggle_tb_dbg();
            }
            return false;

        case TB_MOD:
            if (record->event.pressed) {
                curcur40_cycle_tb_mode();
            }
            return false;

        case KC_ESC:
            /* Pressing Esc immediately stops live Notepad streaming */
            if (record->event.pressed && tb_dbg_streaming) {
                tb_dbg_streaming = false;
                curcur40_send_ascii("pmw3360 live off\n");
                return false;
            }
            break;

        case QK_MOUSE_BUTTON_1 ... QK_MOUSE_BUTTON_8:
            /* Clicking while coasting acts as an immediate brake */
            if (record->event.pressed && is_coasting) {
                curcur40_stop_coasting();
            }
            break;

        default:
            break;
    }

    return true;
}

#ifndef ENCODER_MAP_ENABLE
bool encoder_update_kb(uint8_t index, bool clockwise) {
    if (!encoder_update_user(index, clockwise)) {
        return false;
    }
    if (index == 1) {
        /* Right half CKW12 fallback when ENCODER_MAP_ENABLE is disabled */
        curcur40_enqueue_enc_wheel(clockwise ? -1 : 1, 0);
        return false;
    }
    return true;
}
#endif

layer_state_t layer_state_set_kb(layer_state_t state) {
    state = layer_state_set_user(state);
    bool layer_scroll = ((state & ((layer_state_t)1 << CURCUR40_SCROLL_LAYER)) != 0);
    if (!scroll_mo_held && !scroll_tg_active && !scroll_sl_held && !layer_scroll) {
        curcur40_reset_scroll_state();
    }
    return state;
}

report_mouse_t pointing_device_task_kb(report_mouse_t mouse_report) {
    uint32_t now          = timer_read32();
    bool     inertia_mode = curcur40_is_inertia_mode();
    bool     prec_mode    = scroll_sl_held;
    bool     scroll_mode  = inertia_mode || prec_mode;

    /*
     * 1. Deduplicate split pointing reports on Master:
     *    In vial-qmk transactions.c:read_if_checksum_mismatch(), when Master's main loop
     *    (~200 us) polls Slave before Slave produces a new SPI sample, `else` re-copies
     *    the already-consumed report into `shared_mouse_report`.
     *    - With v2 Right half: each fresh sample carries a unique non-zero `boot_x`
     *      sequence number (1..125); any duplicate `seq == tb_master_last_seq` is zeroed.
     *    - Fallback if Right half is still on v1 (`boot_x == 0`): throttle non-zero
     *      reports to at most 1 per millisecond so sub-ms replays are discarded.
     */
    if (mouse_report.boot_x != 0) {
        uint8_t seq         = (uint8_t)mouse_report.boot_x;
        mouse_report.boot_x = 0;
        if (seq == tb_master_last_seq) {
            mouse_report.x = 0;
            mouse_report.y = 0;
        } else {
            tb_master_last_seq   = seq;
            tb_master_last_rx_ms = now;
        }
    } else if (mouse_report.x != 0 || mouse_report.y != 0) {
        if (timer_elapsed32(tb_master_last_rx_ms) < 1U) {
            mouse_report.x = 0;
            mouse_report.y = 0;
        } else {
            tb_master_last_rx_ms = now;
        }
    } else if (timer_elapsed32(tb_master_last_rx_ms) > 15U) {
        tb_prev_valid_dx = 0;
        tb_prev_valid_dy = 0;
    }

    /*
     * 2. Reject out-of-range 1-ms spikes (e.g. Delta_H = 0xFF sign-extension glitch
     *    producing -256..-190 on small positive movements) and single-frame teleports.
     */
    int16_t cur_dx = (int16_t)mouse_report.x;
    int16_t cur_dy = (int16_t)mouse_report.y;
    if (cur_dx > CURCUR40_MAX_VALID_DELTA || cur_dx < -CURCUR40_MAX_VALID_DELTA ||
        cur_dy > CURCUR40_MAX_VALID_DELTA || cur_dy < -CURCUR40_MAX_VALID_DELTA ||
        (abs_i16(cur_dx) > CURCUR40_MAX_SLEW_DELTA && abs_i16((int16_t)(cur_dx - tb_prev_valid_dx)) > CURCUR40_MAX_SLEW_DELTA) ||
        (abs_i16(cur_dy) > CURCUR40_MAX_SLEW_DELTA && abs_i16((int16_t)(cur_dy - tb_prev_valid_dy)) > CURCUR40_MAX_SLEW_DELTA)) {
        mouse_report.x = 0;
        mouse_report.y = 0;
    } else if (cur_dx != 0 || cur_dy != 0) {
        tb_prev_valid_dx = cur_dx;
        tb_prev_valid_dy = cur_dy;
    }

    /* Accumulate raw pointer counts for live diagnostic readout */
    tb_dbg_dx += (int32_t)mouse_report.x;
    tb_dbg_dy += (int32_t)mouse_report.y;

    if (!scroll_mode && prev_scroll_active) {
        curcur40_reset_scroll_state();
    }
    prev_scroll_active = scroll_mode;

    /* Prevent accidental Ctrl/Alt/GUI + coasting wheel = OS zoom explosion */
    uint8_t zoom_mods = (get_mods() | get_oneshot_mods()) & (MOD_MASK_CTRL | MOD_MASK_ALT | MOD_MASK_GUI);
    if (is_coasting && (zoom_mods & (uint8_t)(~prev_zoom_mods))) {
        curcur40_stop_coasting();
    }
    prev_zoom_mods = zoom_mods;

    int16_t out_v = 0;
    int16_t out_h = 0;

    /* 1. Drain CKW12 ballistic micro-burst (completes within <= 16 ms = 1 frame) */
    if ((enc_pending_v != 0 || enc_pending_h != 0) &&
        timer_elapsed32(enc_burst_ms) >= CURCUR40_ENC_BURST_TICK_MS) {
        enc_burst_ms = now;

        int16_t step_v = clamp_i16(enc_pending_v,
                                   -CURCUR40_ENC_BURST_MAX_PER_TICK,
                                   CURCUR40_ENC_BURST_MAX_PER_TICK);
        int16_t step_h = clamp_i16(enc_pending_h,
                                   -CURCUR40_ENC_BURST_MAX_PER_TICK,
                                   CURCUR40_ENC_BURST_MAX_PER_TICK);
        enc_pending_v = (int16_t)(enc_pending_v - step_v);
        enc_pending_h = (int16_t)(enc_pending_h - step_h);
        out_v         = (int16_t)(out_v + step_v);
        out_h         = (int16_t)(out_h + step_h);
    }

    /* 2. Process PMW3360 25mm Trackball 2D Inertia / Precision Drag-Scroll */
    if (scroll_mode) {
        int16_t raw_x = (int16_t)mouse_report.x;
        int16_t raw_y = (int16_t)mouse_report.y;

        /* Suppress pointer movement while in scroll mode */
        mouse_report.x = 0;
        mouse_report.y = 0;

#ifdef CURCUR40_SCROLL_INVERT_V
        int16_t dv = raw_y;
#else
        int16_t dv = (int16_t)(-raw_y);
#endif
#ifdef CURCUR40_SCROLL_INVERT_H
        int16_t dh = (int16_t)(-raw_x);
#else
        int16_t dh = raw_x;
#endif

        if (dv != 0 || dh != 0) {
            uint32_t move_dt = motion_seen ? timer_elapsed32(last_motion_ms) : 8U;
            if (move_dt < 1U) {
                move_dt = 1U;
            } else if (move_dt > 50U) {
                move_dt = 50U;
            }
            last_motion_ms = now;
            motion_seen    = true;

            /* Dominant-axis straightening to prevent cross-axis wobble on vertical/horizontal flicks */
            int16_t abs_v = abs_i16(dv);
            int16_t abs_h = abs_i16(dh);
            if ((float)abs_v > CURCUR40_SCROLL_AXIS_LOCK_RATIO * (float)abs_h) {
                dh = 0;
            } else if ((float)abs_h > CURCUR40_SCROLL_AXIS_LOCK_RATIO * (float)abs_v) {
                dv = 0;
            }

            if (is_coasting) {
                int16_t mag      = (int16_t)(abs_i16(dv) + abs_i16(dh));
                bool    same_dir = ((float)dv * inertia_vel_v > 0.0f) || ((float)dh * inertia_vel_h > 0.0f);

                if (!same_dir || mag <= CURCUR40_INERTIA_TOUCH_STOP_COUNTS) {
                    /* Thumb touched or nudged ball to stop coasting */
                    curcur40_stop_coasting();
                    if (mag <= CURCUR40_INERTIA_TOUCH_STOP_COUNTS) {
                        dv = 0;
                        dh = 0;
                    }
                } else {
                    /* Re-flick in the same direction builds smoothly on existing momentum */
                    ema_vel_v   = inertia_vel_v;
                    ema_vel_h   = inertia_vel_h;
                    is_coasting = false;
                }
            }

            if (dv != 0 || dh != 0) {
                float div    = prec_mode ? CURCUR40_DRAGSCROLL_PRECISION_DIVISOR : CURCUR40_DRAGSCROLL_DIVISOR;
                float step_v = (float)dv / div;
                float step_h = (float)dh / div;

                scroll_accum_v += step_v;
                scroll_accum_h += step_h;

                if (inertia_mode && !prec_mode) {
                    float inst_vel_v = step_v / (float)move_dt;
                    float inst_vel_h = step_h / (float)move_dt;
                    ema_vel_v        = 0.45f * inst_vel_v + 0.55f * ema_vel_v;
                    ema_vel_h        = 0.45f * inst_vel_h + 0.55f * ema_vel_h;
                }
            }
        } else if (motion_seen) {
            /* Ball is currently stationary: check for flick lift-off or advance coasting */
            if (!is_coasting && inertia_mode && !prec_mode) {
                if (timer_elapsed32(last_motion_ms) >= CURCUR40_INERTIA_LIFT_GAP_MS) {
                    float sv = abs_f(ema_vel_v);
                    float sh = abs_f(ema_vel_h);
                    if (sv >= CURCUR40_INERTIA_LAUNCH_VEL || sh >= CURCUR40_INERTIA_LAUNCH_VEL) {
                        inertia_vel_v = (sv >= CURCUR40_INERTIA_LAUNCH_VEL)
                                            ? clamp_f(ema_vel_v * CURCUR40_INERTIA_BOOST,
                                                      -CURCUR40_INERTIA_MAX_VEL, CURCUR40_INERTIA_MAX_VEL)
                                            : 0.0f;
                        inertia_vel_h = (sh >= CURCUR40_INERTIA_LAUNCH_VEL)
                                            ? clamp_f(ema_vel_h * CURCUR40_INERTIA_BOOST,
                                                      -CURCUR40_INERTIA_MAX_VEL, CURCUR40_INERTIA_MAX_VEL)
                                            : 0.0f;
                        is_coasting          = true;
                        last_inertia_tick_ms = now;
                    } else {
                        ema_vel_v = 0.0f;
                        ema_vel_h = 0.0f;
                    }
                }
            }

            if (is_coasting) {
                while (timer_elapsed32(last_inertia_tick_ms) >= CURCUR40_INERTIA_TICK_MS) {
                    last_inertia_tick_ms += CURCUR40_INERTIA_TICK_MS;
                    scroll_accum_v += inertia_vel_v * (float)CURCUR40_INERTIA_TICK_MS;
                    scroll_accum_h += inertia_vel_h * (float)CURCUR40_INERTIA_TICK_MS;
                    inertia_vel_v *= CURCUR40_INERTIA_DECAY_8MS;
                    inertia_vel_h *= CURCUR40_INERTIA_DECAY_8MS;

                    if (abs_f(inertia_vel_v) < CURCUR40_INERTIA_MIN_VEL) {
                        inertia_vel_v = 0.0f;
                    }
                    if (abs_f(inertia_vel_h) < CURCUR40_INERTIA_MIN_VEL) {
                        inertia_vel_h = 0.0f;
                    }
                    if (inertia_vel_v == 0.0f && inertia_vel_h == 0.0f) {
                        is_coasting = false;
                        ema_vel_v   = 0.0f;
                        ema_vel_h   = 0.0f;
                        break;
                    }
                }
            }
        }

        int16_t tb_v = clamp_i16((int16_t)scroll_accum_v, -8, 8);
        int16_t tb_h = clamp_i16((int16_t)scroll_accum_h, -8, 8);
        scroll_accum_v -= (float)tb_v;
        scroll_accum_h -= (float)tb_h;

        out_v = (int16_t)(out_v + tb_v);
        out_h = (int16_t)(out_h + tb_h);
    }

    if (out_v != 0) {
        int16_t combined_v = clamp_i16((int16_t)((int16_t)mouse_report.v + out_v),
                                       MOUSE_REPORT_HV_MIN, MOUSE_REPORT_HV_MAX);
        mouse_report.v = (mouse_hv_report_t)combined_v;
    }
    if (out_h != 0) {
        int16_t combined_h = clamp_i16((int16_t)((int16_t)mouse_report.h + out_h),
                                       MOUSE_REPORT_HV_MIN, MOUSE_REPORT_HV_MAX);
        mouse_report.h = (mouse_hv_report_t)combined_h;
    }

    return pointing_device_task_user(mouse_report);
}
