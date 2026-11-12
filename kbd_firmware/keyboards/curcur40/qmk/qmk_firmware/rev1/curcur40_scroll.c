// Copyright 2026 oktntko
// SPDX-License-Identifier: GPL-2.0-or-later

#include "curcur40_scroll.h"

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
 * QMK Keyboard-Level Hooks (always chain to *_user)
 * ------------------------------------------------------------------------- */
bool process_record_kb(uint16_t keycode, keyrecord_t *record) {
    if (!process_record_user(keycode, record)) {
        return false;
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
