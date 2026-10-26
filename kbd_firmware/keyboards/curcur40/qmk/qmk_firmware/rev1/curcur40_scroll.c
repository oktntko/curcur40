// Copyright 2026 oktntko
// SPDX-License-Identifier: GPL-2.0-or-later

#include "curcur40_scroll.h"
#include "drivers/sensors/pmw33xx_common.h"
#include "i2c_master.h"
#include "pointing_device.h"
#include "timer.h"

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
 * 1. Composite Right-Half Pointing Driver: PMW3360 (SPI1) + AS5600 (I2C0)
 * ------------------------------------------------------------------------- */
#define AS5600_FULL_SCALE_LSB    4096L
#define AS5600_HALF_SCALE_LSB    2048
#define AS5600_I2C_TIMEOUT_MS    5
#define AS5600_RETRY_INTERVAL_MS 200
#define AS5600_STATUS_POLL_MS    250
#define WHEEL_IDLE_RESET_MS      60

static bool     s_pmw3360_online     = false;
static bool     s_wheel_online       = false;
static bool     s_wheel_magnet_ok    = false;
static bool     s_wheel_angle_locked = false;
static bool     s_wheel_resting      = true;
static uint16_t s_wheel_prev_angle   = 0;
static uint16_t s_wheel_rest_anchor  = 0;
static uint16_t s_wheel_retry_ms     = 0;
static uint16_t s_wheel_status_ms    = 0;
static uint16_t s_wheel_motion_ms    = 0;
static int32_t  s_wheel_subtick_num  = 0;
static int32_t  s_wheel_pending      = 0;

static bool as5600_configure(void) {
    /*
     * CONF register (0x07..0x08):
     * - SF   = 0b11 (2x slow filter -> 0.286 ms step response for fast inertia spin)
     * - FTH  = 0b001 (6 LSB fast-filter threshold: quiet at rest, instant on flick)
     * - HYST = 0b01 (1 LSB internal hysteresis)
     */
    const uint8_t conf[2] = {0x07, 0x04};
    if (i2c_write_register(CURCUR40_AS5600_I2C_ADDR, CURCUR40_AS5600_REG_CONF_H, conf, sizeof(conf), AS5600_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
        return false;
    }

    uint8_t status = 0;
    if (i2c_read_register(CURCUR40_AS5600_I2C_ADDR, CURCUR40_AS5600_REG_STATUS, &status, 1, AS5600_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
        return false;
    }

    s_wheel_magnet_ok = (status & CURCUR40_AS5600_STATUS_MD) != 0;
    s_wheel_status_ms = timer_read();
    return true;
}

static bool as5600_read_raw_angle(uint16_t *out_angle) {
    uint8_t buf[2] = {0, 0};
    if (i2c_read_register(CURCUR40_AS5600_I2C_ADDR, CURCUR40_AS5600_REG_RAW_ANGLE_H, buf, sizeof(buf), AS5600_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
        return false;
    }
    *out_angle = (uint16_t)(((uint16_t)(buf[0] & 0x0FU) << 8) | buf[1]);
    return true;
}

static inline int16_t wrap_delta_12bit(uint16_t current, uint16_t previous) {
    int16_t diff = (int16_t)current - (int16_t)previous;
    if (diff > (AS5600_HALF_SCALE_LSB - 1)) {
        diff -= (int16_t)AS5600_FULL_SCALE_LSB;
    } else if (diff < -AS5600_HALF_SCALE_LSB) {
        diff += (int16_t)AS5600_FULL_SCALE_LSB;
    }
    return diff;
}

static void curcur40_wheel_init(void) {
    i2c_init();
    s_wheel_retry_ms     = timer_read();
    s_wheel_online       = as5600_configure();
    s_wheel_angle_locked = false;
    s_wheel_resting      = true;
    s_wheel_subtick_num  = 0;
    s_wheel_pending      = 0;
}

static report_mouse_t curcur40_wheel_poll(report_mouse_t mouse_report) {
    const uint16_t now = timer_read();

    if (!s_wheel_online) {
        if (timer_elapsed(s_wheel_retry_ms) < AS5600_RETRY_INTERVAL_MS) {
            return mouse_report;
        }
        s_wheel_retry_ms = now;
        if (!as5600_configure()) {
            return mouse_report;
        }
        s_wheel_online       = true;
        s_wheel_angle_locked = false;
        s_wheel_resting      = true;
        s_wheel_subtick_num  = 0;
    }

    if (timer_elapsed(s_wheel_status_ms) >= AS5600_STATUS_POLL_MS) {
        uint8_t status = 0;
        if (i2c_read_register(CURCUR40_AS5600_I2C_ADDR, CURCUR40_AS5600_REG_STATUS, &status, 1, AS5600_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
            s_wheel_online       = false;
            s_wheel_angle_locked = false;
            s_wheel_retry_ms     = now;
            return mouse_report;
        }
        s_wheel_magnet_ok = (status & CURCUR40_AS5600_STATUS_MD) != 0;
        s_wheel_status_ms = now;
    }

    if (!s_wheel_magnet_ok) {
        s_wheel_angle_locked = false;
        return mouse_report;
    }

    uint16_t raw_angle = 0;
    if (!as5600_read_raw_angle(&raw_angle)) {
        s_wheel_online       = false;
        s_wheel_angle_locked = false;
        s_wheel_retry_ms     = now;
        return mouse_report;
    }

    if (!s_wheel_angle_locked) {
        s_wheel_prev_angle   = raw_angle;
        s_wheel_rest_anchor  = raw_angle;
        s_wheel_motion_ms    = now;
        s_wheel_resting      = true;
        s_wheel_angle_locked = true;
        return mouse_report;
    }

    if (!s_wheel_resting && timer_elapsed(s_wheel_motion_ms) >= WHEEL_IDLE_RESET_MS) {
        s_wheel_resting     = true;
        s_wheel_rest_anchor = raw_angle;
        s_wheel_prev_angle  = raw_angle;
        s_wheel_subtick_num = 0;
    }

    if (s_wheel_resting) {
        const int16_t wake_delta = wrap_delta_12bit(raw_angle, s_wheel_rest_anchor);
        if (wake_delta > -CURCUR40_WHEEL_DEADBAND_LSB && wake_delta < CURCUR40_WHEEL_DEADBAND_LSB) {
            return mouse_report;
        }
        s_wheel_resting    = false;
        s_wheel_prev_angle = s_wheel_rest_anchor;
    }

    int16_t delta_lsb = wrap_delta_12bit(raw_angle, s_wheel_prev_angle);
    if (delta_lsb != 0) {
        s_wheel_prev_angle = raw_angle;
        s_wheel_motion_ms  = now;

#if CURCUR40_WHEEL_INVERT_DIR
        delta_lsb = -delta_lsb;
#endif
        s_wheel_subtick_num += (int32_t)delta_lsb * (int32_t)CURCUR40_WHEEL_NOTCHES_PER_REV;
        const int32_t whole_ticks = s_wheel_subtick_num / AS5600_FULL_SCALE_LSB;
        if (whole_ticks != 0) {
            s_wheel_subtick_num -= whole_ticks * AS5600_FULL_SCALE_LSB;
            s_wheel_pending += whole_ticks;
        }
    }

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

    /* 1. Route AS5600 Passive Magnetic Inertia Wheel ticks (vertical or WHL_HRZ horizontal) */
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
