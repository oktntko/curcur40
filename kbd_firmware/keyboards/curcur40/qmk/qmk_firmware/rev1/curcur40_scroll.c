// Copyright 2026 oktntko
// SPDX-License-Identifier: GPL-2.0-or-later

#include "curcur40_scroll.h"
#include "drivers/sensors/pmw33xx_common.h"
#include "gpio.h"
#include "i2c_master.h"
#include "pointing_device.h"
#include "timer.h"

/* -------------------------------------------------------------------------
 * Lightweight Cortex-M0+ helpers (no libm / powf / atan2f dependency)
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

static inline int32_t abs_i32(int32_t x) {
    return (x < 0) ? -x : x;
}

static inline int16_t clamp_i16(int16_t x, int16_t lo, int16_t hi) {
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
}

/* -------------------------------------------------------------------------
 * 1. Composite Right-Half Pointing Driver:
 *    PMW3360 (SPI1) + TMAG5273 / TLV493D-A1B6 3D Hall Inertia Wheel (I2C0)
 * ------------------------------------------------------------------------- */
#define WHEEL_ANGLE_FULL_LSB   4096L
#define WHEEL_ANGLE_HALF_LSB   2048
#define WHEEL_I2C_TIMEOUT_MS   2
#define WHEEL_RETRY_INTERVAL_MS 200
#define WHEEL_POLL_INTERVAL_MS 1
#define WHEEL_IDLE_RESET_MS    60
#define WHEEL_BUSY_STREAK_MAX  20
#define WHEEL_CAL_DECAY_MS     2000
#define WHEEL_CAL_BIPOLAR_MIN  1200

typedef enum {
    WHEEL_SENSOR_NONE = 0,
    WHEEL_SENSOR_TMAG5273,
    WHEEL_SENSOR_TLV493D,
} wheel_sensor_kind_t;

typedef struct {
    int16_t min_s;
    int16_t max_s;
    int16_t min_c;
    int16_t max_c;
    bool    seeded;
    bool    locked;
} wheel_cal_t;

static bool                s_pmw3360_online     = false;
static wheel_sensor_kind_t s_wheel_sensor       = WHEEL_SENSOR_NONE;
static uint8_t             s_wheel_addr8        = 0;
static bool                s_wheel_online       = false;
static bool                s_wheel_angle_locked = false;
static bool                s_wheel_resting      = true;
static bool                s_wheel_polled_once  = false;
static bool                s_wheel_click_held   = false;
static bool                s_wheel_click_seen   = false;
static uint8_t             s_wheel_err_streak   = 0;
static uint8_t             s_wheel_busy_streak  = 0;
static uint16_t            s_wheel_prev_angle   = 0;
static uint16_t            s_wheel_rest_anchor  = 0;
static uint16_t            s_wheel_poll_ms      = 0;
static uint16_t            s_wheel_retry_ms     = 0;
static uint16_t            s_wheel_motion_ms    = 0;
static uint16_t            s_wheel_click_rel_ms = 0;
static uint16_t            s_wheel_cal_decay_ms = 0;
static int32_t             s_wheel_subtick_num  = 0;
static int32_t             s_wheel_pending      = 0;
static wheel_cal_t         s_wheel_cal          = {0, 0, 0, 0, false, false};

/*
 * 12-iteration integer CORDIC atan2 returning 12-bit angle [0..4095] (0..360 deg).
 * Max error across all 360 deg is <= 1 LSB (0.088 deg), zero float / libm calls.
 */
static uint16_t cordic_atan2_12bit(int32_t y, int32_t x) {
    static const uint16_t k_atan_lut[12] = {
        8192U, 4836U, 2555U, 1297U, 651U, 326U, 163U, 81U, 41U, 20U, 10U, 5U
    };

    if (x == 0 && y == 0) {
        return 0;
    }

    int32_t mag = abs_i32(x) + abs_i32(y);
    if (mag < 4096) {
        x <<= 6;
        y <<= 6;
    }

    uint16_t angle = 0;
    if (x < 0) {
        x     = -x;
        y     = -y;
        angle = 32768U;
    }

    for (uint8_t i = 0; i < 12; i++) {
        int32_t dx = y >> i;
        int32_t dy = x >> i;
        if (y >= 0) {
            x += dx;
            y -= dy;
            angle = (uint16_t)(angle + k_atan_lut[i]);
        } else {
            x -= dx;
            y += dy;
            angle = (uint16_t)(angle - k_atan_lut[i]);
        }
    }

    return (uint16_t)(((uint16_t)(angle + 8U) >> 4) & 0x0FFFU);
}

static uint16_t wheel_eval_angle_12bit(int16_t raw_s, int16_t raw_c, const wheel_cal_t *cal) {
    int32_t ns = (int32_t)raw_s;
    int32_t nc = (int32_t)raw_c;

    if (cal->locked) {
        int32_t span_s = (int32_t)cal->max_s - (int32_t)cal->min_s;
        int32_t span_c = (int32_t)cal->max_c - (int32_t)cal->min_c;
        int32_t mid2_s = (int32_t)cal->max_s + (int32_t)cal->min_s;
        int32_t mid2_c = (int32_t)cal->max_c + (int32_t)cal->min_c;
        if (span_s >= (2 * WHEEL_CAL_BIPOLAR_MIN) && span_c >= (2 * WHEEL_CAL_BIPOLAR_MIN)) {
            /* Cross-multiply by opposite span to normalize off-axis ellipse without division */
            int32_t ds = (2 * ns - mid2_s) >> 2;
            int32_t dc = (2 * nc - mid2_c) >> 2;
            ns         = (ds * (span_c >> 2)) >> 8;
            nc         = (dc * (span_s >> 2)) >> 8;
        }
    }

    return cordic_atan2_12bit(ns, nc);
}

static void wheel_cal_reset(wheel_cal_t *cal) {
    cal->min_s  = 0;
    cal->max_s  = 0;
    cal->min_c  = 0;
    cal->max_c  = 0;
    cal->seeded = false;
    cal->locked = false;
}

static void wheel_cal_update(wheel_cal_t *cal, int16_t raw_s, int16_t raw_c, uint16_t now) {
    if (!cal->seeded) {
        cal->min_s          = raw_s;
        cal->max_s          = raw_s;
        cal->min_c          = raw_c;
        cal->max_c          = raw_c;
        cal->seeded         = true;
        cal->locked         = false;
        s_wheel_cal_decay_ms = now;
        return;
    }

    /* Gentle envelope decay prevents any single-sample glitch from pinning min/max forever */
    if (timer_elapsed(s_wheel_cal_decay_ms) >= WHEEL_CAL_DECAY_MS) {
        s_wheel_cal_decay_ms = now;
        if (cal->max_s - cal->min_s > (2 * WHEEL_CAL_BIPOLAR_MIN + 32)) {
            cal->max_s -= 4;
            cal->min_s += 4;
        }
        if (cal->max_c - cal->min_c > (2 * WHEEL_CAL_BIPOLAR_MIN + 32)) {
            cal->max_c -= 4;
            cal->min_c += 4;
        }
    }

    if (raw_s < cal->min_s) cal->min_s = raw_s;
    if (raw_s > cal->max_s) cal->max_s = raw_s;
    if (raw_c < cal->min_c) cal->min_c = raw_c;
    if (raw_c > cal->max_c) cal->max_c = raw_c;

    if (!cal->locked) {
        int32_t span_s = (int32_t)cal->max_s - (int32_t)cal->min_s;
        int32_t span_c = (int32_t)cal->max_c - (int32_t)cal->min_c;
        if (cal->min_s < -WHEEL_CAL_BIPOLAR_MIN && cal->max_s > WHEEL_CAL_BIPOLAR_MIN &&
            cal->min_c < -WHEEL_CAL_BIPOLAR_MIN && cal->max_c > WHEEL_CAL_BIPOLAR_MIN &&
            span_s * 5 >= span_c * 2 && span_c * 5 >= span_s * 2) {
            cal->locked = true;
        }
    }
}

static bool tmag5273_try_configure(uint8_t addr7) {
    const uint8_t addr8 = (uint8_t)(addr7 << 1);
    uint8_t       id[3] = {0, 0, 0};

    if (i2c_read_register(addr8, CURCUR40_TMAG5273_REG_DEVICE_ID, id, sizeof(id), WHEEL_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
        return false;
    }

    const uint16_t mfg_id = (uint16_t)(((uint16_t)id[2] << 8) | id[1]);
    const uint8_t  ver    = (uint8_t)(id[0] & 0x03U);
    if (mfg_id != CURCUR40_TMAG5273_MFG_ID || (ver != 0x01U && ver != 0x02U)) {
        return false;
    }

    /*
     * Configure while in Standby Mode per TI datasheet SLYS045C Section 7.2.1.2:
     * 1. INT_CONFIG_1  (0x08) = 0x01: MASK_INTB=1b (Pin 5 ~INT tied to GNDR via rR13)
     * 2. T_CONFIG      (0x07) = 0x00: Temperature channel disabled
     * 3. DEV_CONFIG_1  (0x00) = 0x08: CONV_AVG=010b (4x avg, ~3.1 kSPS), I2C_RD=00b, CRC=0
     * 4. SNS_CONFIG_1  (0x02) = 0xB0: MAG_CH_EN=1011b (XZX pseudo-simultaneous sampling)
     *    SNS_CONFIG_2  (0x03) = 0x03: X_Y_RANGE=1b, Z_RANGE=1b (+/-80mT on x1, +/-266mT on x2)
     * 5. DEV_CONFIG_2  (0x01) = 0x12: LP_LN=1b (low-noise), OPERATING_MODE=10b (Continuous)
     */
    const uint8_t int_cfg = 0x01U;
    const uint8_t t_cfg   = 0x00U;
    const uint8_t dev_cfg1 = 0x08U;
    const uint8_t sns_cfg[2] = {0xB0U, 0x03U};
    const uint8_t dev_cfg2 = 0x12U;

    if (i2c_write_register(addr8, CURCUR40_TMAG5273_REG_INT_CFG_1, &int_cfg, 1, WHEEL_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
        return false;
    }
    if (i2c_write_register(addr8, CURCUR40_TMAG5273_REG_T_CFG, &t_cfg, 1, WHEEL_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
        return false;
    }
    if (i2c_write_register(addr8, CURCUR40_TMAG5273_REG_DEV_CFG_1, &dev_cfg1, 1, WHEEL_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
        return false;
    }
    if (i2c_write_register(addr8, CURCUR40_TMAG5273_REG_SNS_CFG_1, sns_cfg, sizeof(sns_cfg), WHEEL_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
        return false;
    }
    if (i2c_write_register(addr8, CURCUR40_TMAG5273_REG_DEV_CFG_2, &dev_cfg2, 1, WHEEL_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
        return false;
    }

    s_wheel_sensor = WHEEL_SENSOR_TMAG5273;
    s_wheel_addr8  = addr8;
    return true;
}

static bool tlv493d_try_configure(uint8_t addr7) {
    const uint8_t addr8    = (uint8_t)(addr7 << 1);
    uint8_t       rbuf[10] = {0};

    if (i2c_receive(addr8, rbuf, sizeof(rbuf), WHEEL_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
        return false;
    }

    bool all_zero = true;
    bool all_ff   = true;
    for (uint8_t i = 0; i < sizeof(rbuf); i++) {
        if (rbuf[i] != 0x00U) all_zero = false;
        if (rbuf[i] != 0xFFU) all_ff = false;
    }
    if (all_zero || all_ff) {
        return false;
    }

    /*
     * Preserve factory trim bits R_RES1..3 (bytes 7..9) and enter Master Controlled Mode:
     * - wbuf[1] MOD1: INT=0 (MUST be 0 on shared SCL!), FAST=1, LOW=1 (3.3 kHz continuous)
     * - wbuf[3] MOD2: T=1 (temp off), LP=1 (12 ms), PT=1 (odd parity check enabled)
     */
    uint8_t wbuf[4];
    wbuf[0] = 0x00U;
    wbuf[1] = (uint8_t)((rbuf[7] & 0x18U) | 0x03U);
    wbuf[2] = rbuf[8];
    wbuf[3] = (uint8_t)(0xE0U | (rbuf[9] & 0x1FU));

    /* Odd parity over all 32 bits of wbuf[0..3] stored in wbuf[1] bit 7 */
    wbuf[1] |= 0x80U;
    uint8_t p = (uint8_t)(wbuf[0] ^ wbuf[1] ^ wbuf[2] ^ wbuf[3]);
    p ^= (uint8_t)(p >> 1);
    p ^= (uint8_t)(p >> 2);
    p ^= (uint8_t)(p >> 4);
    if ((p & 0x01U) == 0U) {
        wbuf[1] &= (uint8_t)(~0x80U);
    }

    if (i2c_transmit(addr8, wbuf, sizeof(wbuf), WHEEL_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
        return false;
    }

    s_wheel_sensor = WHEEL_SENSOR_TLV493D;
    s_wheel_addr8  = addr8;
    return true;
}

static bool wheel_sensor_configure(void) {
    /* 1. Probe TI TMAG5273 family (A1/A2=0x35, B1/B2=0x22, D1/D2=0x44, C1/C2=0x78) */
    static const uint8_t k_tmag_addrs[4] = {0x35U, 0x22U, 0x44U, 0x78U};
    for (uint8_t i = 0; i < sizeof(k_tmag_addrs); i++) {
        if (tmag5273_try_configure(k_tmag_addrs[i])) {
            s_wheel_busy_streak = 0;
            return true;
        }
    }

    /* 2. Probe Infineon TLV493D-A1B6 fallback (0x5E default ADDR=1, 0x1F ADDR=0) */
    static const uint8_t k_tlv_addrs[2] = {0x5EU, 0x1FU};
    for (uint8_t i = 0; i < sizeof(k_tlv_addrs); i++) {
        if (tlv493d_try_configure(k_tlv_addrs[i])) {
            s_wheel_busy_streak = 0;
            return true;
        }
    }

    s_wheel_sensor = WHEEL_SENSOR_NONE;
    s_wheel_addr8  = 0;
    return false;
}

/*
 * Reads the two orthogonal quadrature field components in the (North-South, Up-Down)
 * rotation plane of the wheel magnet, mapped so atan2(out_sin, out_cos) increases
 * (+delta_lsb > 0) when rolling the top of the wheel North (away = Scroll UP, +V):
 *   - TMAG5273 (DBV on B.Cu rot=-90):  (Bx, Bz)
 *   - TLV493D  (TSOP-6 on B.Cu rot=-90): (By, Bz) left-aligned to 16-bit signed scale
 */
static bool wheel_sensor_read_quadrature(int16_t *out_sin, int16_t *out_cos, bool *out_busy) {
    *out_busy = false;

    if (s_wheel_sensor == WHEEL_SENSOR_TMAG5273) {
        uint8_t buf[7] = {0};
        if (i2c_read_register(s_wheel_addr8, CURCUR40_TMAG5273_REG_X_MSB_RESULT, buf, sizeof(buf), WHEEL_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
            return false;
        }
        if ((buf[6] & CURCUR40_TMAG5273_CONV_RESULT_READY) == 0U) {
            *out_busy = true;
            return true;
        }
        *out_sin = (int16_t)(((uint16_t)buf[0] << 8) | buf[1]);
        *out_cos = (int16_t)(((uint16_t)buf[4] << 8) | buf[5]);
        return true;
    }

    if (s_wheel_sensor == WHEEL_SENSOR_TLV493D) {
        uint8_t buf[6] = {0};
        if (i2c_receive(s_wheel_addr8, buf, sizeof(buf), WHEEL_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
            return false;
        }
        /* R_CHANNEL (buf[3] bits 1:0) != 0 indicates ADC was mid-conversion during readout */
        if ((buf[3] & 0x03U) != 0U) {
            *out_busy = true;
            return true;
        }
        *out_sin = (int16_t)(((uint16_t)buf[1] << 8) | ((uint16_t)(buf[4] & 0x0FU) << 4));
        *out_cos = (int16_t)(((uint16_t)buf[2] << 8) | ((uint16_t)(buf[5] & 0x0FU) << 4));
        return true;
    }

    return false;
}

static inline int16_t wrap_delta_12bit(uint16_t current, uint16_t previous) {
    int16_t diff = (int16_t)current - (int16_t)previous;
    if (diff > (WHEEL_ANGLE_HALF_LSB - 1)) {
        diff -= (int16_t)WHEEL_ANGLE_FULL_LSB;
    } else if (diff < -WHEEL_ANGLE_HALF_LSB) {
        diff += (int16_t)WHEEL_ANGLE_FULL_LSB;
    }
    return diff;
}

static void curcur40_wheel_init(void) {
    i2c_init();
    wheel_cal_reset(&s_wheel_cal);
    s_wheel_poll_ms      = timer_read();
    s_wheel_retry_ms     = s_wheel_poll_ms;
    s_wheel_online       = wheel_sensor_configure();
    s_wheel_err_streak   = s_wheel_online ? 0 : 1;
    s_wheel_polled_once  = false;
    s_wheel_angle_locked = false;
    s_wheel_resting      = true;
    s_wheel_click_held   = false;
    s_wheel_click_seen   = false;
    s_wheel_subtick_num  = 0;
    s_wheel_pending      = 0;
}

static report_mouse_t curcur40_wheel_emit_pending(report_mouse_t mouse_report) {
    if (s_wheel_pending != 0) {
        int32_t emit = s_wheel_pending;
        if (emit > MOUSE_REPORT_HV_MAX) {
            emit = MOUSE_REPORT_HV_MAX;
        } else if (emit < MOUSE_REPORT_HV_MIN) {
            emit = MOUSE_REPORT_HV_MIN;
        }
        s_wheel_pending -= emit;

        int32_t combined = (int32_t)mouse_report.v + emit;
        if (combined > MOUSE_REPORT_HV_MAX) combined = MOUSE_REPORT_HV_MAX;
        if (combined < MOUSE_REPORT_HV_MIN) combined = MOUSE_REPORT_HV_MIN;
        mouse_report.v = (mouse_hv_report_t)combined;
    }
    return mouse_report;
}

static report_mouse_t curcur40_wheel_poll(report_mouse_t mouse_report) {
    const uint16_t now = timer_read();

    if (!s_wheel_online) {
        if (timer_elapsed(s_wheel_retry_ms) < WHEEL_RETRY_INTERVAL_MS) {
            return curcur40_wheel_emit_pending(mouse_report);
        }
        s_wheel_retry_ms = now;
        if (s_wheel_err_streak >= 3) {
            i2c_init();
        }
        if (!wheel_sensor_configure()) {
            if (s_wheel_err_streak < 255) {
                s_wheel_err_streak++;
            }
            return curcur40_wheel_emit_pending(mouse_report);
        }
        s_wheel_online       = true;
        s_wheel_err_streak   = 0;
        s_wheel_angle_locked = false;
        s_wheel_resting      = true;
        s_wheel_subtick_num  = 0;
        wheel_cal_reset(&s_wheel_cal);
    }

    if (s_wheel_polled_once && timer_elapsed(s_wheel_poll_ms) < WHEEL_POLL_INTERVAL_MS) {
        return curcur40_wheel_emit_pending(mouse_report);
    }
    s_wheel_polled_once = true;
    s_wheel_poll_ms     = now;

    /* Real-time local middle-click detection on Right Half (rEXSW1 on GP7, active-low) */
    const bool click_now = !gpio_read_pin(CURCUR40_WHEEL_CLICK_PIN);
    if (click_now) {
        s_wheel_click_held   = true;
        s_wheel_click_seen   = true;
        s_wheel_click_rel_ms = now;
    } else if (s_wheel_click_held) {
        s_wheel_click_held   = false;
        s_wheel_click_rel_ms = now;
    }
    const bool click_blanked = s_wheel_click_held ||
                               (s_wheel_click_seen && timer_elapsed(s_wheel_click_rel_ms) < CURCUR40_WHEEL_CLICK_BLANK_MS);

    int16_t raw_s = 0;
    int16_t raw_c = 0;
    bool    busy  = false;
    if (!wheel_sensor_read_quadrature(&raw_s, &raw_c, &busy)) {
        s_wheel_online       = false;
        s_wheel_angle_locked = false;
        s_wheel_retry_ms     = now;
        if (s_wheel_err_streak < 255) {
            s_wheel_err_streak++;
        }
        return curcur40_wheel_emit_pending(mouse_report);
    }

    if (busy) {
        if (++s_wheel_busy_streak >= WHEEL_BUSY_STREAK_MAX) {
            /* Sensor likely brown-out reset back to Standby/Power-Down; reconfigure */
            s_wheel_online       = false;
            s_wheel_angle_locked = false;
            s_wheel_retry_ms     = now;
            s_wheel_busy_streak  = 0;
        }
        return curcur40_wheel_emit_pending(mouse_report);
    }
    s_wheel_busy_streak = 0;
    s_wheel_err_streak  = 0;

    /* Reject demagnetized / missing-wheel noise floor */
    if (abs_i32((int32_t)raw_s) + abs_i32((int32_t)raw_c) < CURCUR40_WHEEL_MIN_MAG_L1) {
        s_wheel_angle_locked = false;
        return curcur40_wheel_emit_pending(mouse_report);
    }

    /*
     * Evaluate angle with previous calibration first so updating min/max or
     * locking ellipse normalization produces strictly zero synthetic step jump.
     */
    const uint16_t angle_prev_cal = wheel_eval_angle_12bit(raw_s, raw_c, &s_wheel_cal);
    if (!click_blanked) {
        wheel_cal_update(&s_wheel_cal, raw_s, raw_c, now);
    }
    const uint16_t angle_new_cal = wheel_eval_angle_12bit(raw_s, raw_c, &s_wheel_cal);

    if (!s_wheel_angle_locked || click_blanked) {
        s_wheel_prev_angle   = angle_new_cal;
        s_wheel_rest_anchor  = angle_new_cal;
        s_wheel_motion_ms    = now;
        s_wheel_resting      = true;
        s_wheel_angle_locked = true;
        s_wheel_subtick_num  = 0;
        if (click_blanked) {
            s_wheel_pending = 0;
        }
        return curcur40_wheel_emit_pending(mouse_report);
    }

    if (!s_wheel_resting && timer_elapsed(s_wheel_motion_ms) >= WHEEL_IDLE_RESET_MS) {
        s_wheel_resting     = true;
        s_wheel_rest_anchor = angle_new_cal;
        s_wheel_prev_angle  = angle_new_cal;
        s_wheel_subtick_num = 0;
    }

    if (s_wheel_resting) {
        const int16_t wake_delta = wrap_delta_12bit(angle_prev_cal, s_wheel_rest_anchor);
        const int16_t cal_shift  = wrap_delta_12bit(angle_new_cal, angle_prev_cal);
        s_wheel_rest_anchor      = (uint16_t)((s_wheel_rest_anchor + (uint16_t)cal_shift) & 0x0FFFU);
        if (wake_delta > -CURCUR40_WHEEL_DEADBAND_LSB && wake_delta < CURCUR40_WHEEL_DEADBAND_LSB) {
            s_wheel_prev_angle = angle_new_cal;
            return curcur40_wheel_emit_pending(mouse_report);
        }
        s_wheel_resting    = false;
        s_wheel_prev_angle = (uint16_t)((s_wheel_rest_anchor - (uint16_t)cal_shift) & 0x0FFFU);
    }

    int16_t delta_lsb  = wrap_delta_12bit(angle_prev_cal, s_wheel_prev_angle);
    s_wheel_prev_angle = angle_new_cal;

    if (delta_lsb != 0) {
        s_wheel_motion_ms = now;

#if CURCUR40_WHEEL_INVERT_DIR
        delta_lsb = -delta_lsb;
#endif
        s_wheel_subtick_num += (int32_t)delta_lsb * (int32_t)CURCUR40_WHEEL_NOTCHES_PER_REV;
        const int32_t whole_ticks = s_wheel_subtick_num / WHEEL_ANGLE_FULL_LSB;
        if (whole_ticks != 0) {
            s_wheel_subtick_num -= whole_ticks * WHEEL_ANGLE_FULL_LSB;
            s_wheel_pending += whole_ticks;
        }
    }

    return curcur40_wheel_emit_pending(mouse_report);
}

#ifdef VIAL_ENABLE
void pointing_device_driver_init(void) {
    if (is_keyboard_left()) {
        return;
    }
    s_pmw3360_online = pmw33xx_init(0);
    curcur40_wheel_init();
}
#else
bool pointing_device_driver_init(void) {
    if (is_keyboard_left()) {
        return true;
    }
    s_pmw3360_online = pmw33xx_init(0);
    curcur40_wheel_init();
    /* Keep driver active so either sensor works independently and supports hot-plug */
    return true;
}
#endif

report_mouse_t pointing_device_driver_get_report(report_mouse_t mouse_report) {
    if (is_keyboard_left()) {
        return mouse_report;
    }
    if (s_pmw3360_online) {
        mouse_report = pmw33xx_get_report(mouse_report);
    }
    mouse_report = curcur40_wheel_poll(mouse_report);
    return mouse_report;
}

uint16_t pointing_device_driver_get_cpi(void) {
    if (is_keyboard_left() || !s_pmw3360_online) {
        return PMW33XX_CPI;
    }
    return pmw33xx_get_cpi(0);
}

void pointing_device_driver_set_cpi(uint16_t cpi) {
    if (!is_keyboard_left() && s_pmw3360_online) {
        pmw33xx_set_cpi(0, cpi);
    }
}

/* -------------------------------------------------------------------------
 * 2. PMW3360 Trackball 2D Inertia Drag-Scroll & Wheel Axis State (Master)
 * ------------------------------------------------------------------------- */
static bool     scroll_mo_held       = false;
static bool     scroll_tg_active     = false;
static bool     scroll_sl_held       = false;
static bool     wheel_horiz_held     = false;
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
 * QMK Keyboard-Level Hooks (always chain to *_user)
 * ------------------------------------------------------------------------- */
bool process_record_kb(uint16_t keycode, keyrecord_t *record) {
    if (!process_record_user(keycode, record)) {
        return false;
    }

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

        case WHL_HRZ:
            wheel_horiz_held = record->event.pressed;
            return false;

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

    if (!scroll_mode && prev_scroll_active) {
        curcur40_reset_scroll_state();
    }
    prev_scroll_active = scroll_mode;

    /* Prevent accidental Ctrl/Alt/GUI + coasting trackball = OS zoom explosion */
    uint8_t zoom_mods = (get_mods() | get_oneshot_mods()) & (MOD_MASK_CTRL | MOD_MASK_ALT | MOD_MASK_GUI);
    if (is_coasting && (zoom_mods & (uint8_t)(~prev_zoom_mods))) {
        curcur40_stop_coasting();
    }
    prev_zoom_mods = zoom_mods;

    /* 1. Route 3D Hall Passive Magnetic Inertia Wheel ticks (vertical or WHL_HRZ horizontal) */
    int16_t wheel_ticks = (int16_t)mouse_report.v;
    int16_t out_v       = 0;
    int16_t out_h       = (int16_t)mouse_report.h;
    mouse_report.v      = 0;
    mouse_report.h      = 0;

    if (wheel_ticks != 0) {
        if (wheel_horiz_held) {
            out_h = (int16_t)(out_h + wheel_ticks);
        } else {
            out_v = (int16_t)(out_v + wheel_ticks);
        }
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
        mouse_report.v = (mouse_hv_report_t)clamp_i16(out_v, MOUSE_REPORT_HV_MIN, MOUSE_REPORT_HV_MAX);
    }
    if (out_h != 0) {
        mouse_report.h = (mouse_hv_report_t)clamp_i16(out_h, MOUSE_REPORT_HV_MIN, MOUSE_REPORT_HV_MAX);
    }

    return pointing_device_task_user(mouse_report);
}
