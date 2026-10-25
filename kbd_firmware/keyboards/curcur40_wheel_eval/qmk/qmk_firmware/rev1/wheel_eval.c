// Copyright 2026 oktntko
// SPDX-License-Identifier: GPL-2.0-or-later

#include "wheel_eval.h"
#include "i2c_master.h"
#include "pointing_device.h"
#include "timer.h"

#define AS5600_FULL_SCALE_LSB      4096L
#define AS5600_HALF_SCALE_LSB      2048
#define AS5600_I2C_TIMEOUT_MS      5
#define AS5600_RETRY_INTERVAL_MS   200
#define AS5600_STATUS_POLL_MS      250
#define WHEEL_IDLE_RESET_MS        60

static bool     s_sensor_online   = false;
static bool     s_magnet_ok       = false;
static bool     s_angle_locked    = false;
static bool     s_resting         = true;
static bool     s_horiz_mode      = false;
static uint16_t s_prev_angle      = 0;
static uint16_t s_rest_anchor     = 0;
static uint16_t s_last_retry_ms   = 0;
static uint16_t s_last_status_ms  = 0;
static uint16_t s_last_motion_ms  = 0;
static int32_t  s_subtick_numer   = 0;
static int32_t  s_pending_ticks   = 0;

void wheel_eval_set_horizontal_mode(bool enabled) {
    s_horiz_mode = enabled;
}

bool wheel_eval_get_horizontal_mode(void) {
    return s_horiz_mode;
}

static bool as5600_configure(void) {
    /*
     * CONF register (0x07..0x08):
     * - SF   = 0b11 (2x slow filter -> 0.286 ms step response for fast inertia spin)
     * - FTH  = 0b001 (6 LSB fast-filter threshold: quiet at rest, instant on flick)
     * - HYST = 0b01 (1 LSB internal hysteresis)
     */
    const uint8_t conf[2] = {0x07, 0x04};
    if (i2c_write_register(AS5600_I2C_ADDR, AS5600_REG_CONF_H, conf, sizeof(conf), AS5600_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
        return false;
    }

    uint8_t status = 0;
    if (i2c_read_register(AS5600_I2C_ADDR, AS5600_REG_STATUS, &status, 1, AS5600_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
        return false;
    }

    s_magnet_ok      = (status & AS5600_STATUS_MD) != 0;
    s_last_status_ms = timer_read();
    return true;
}

static bool as5600_read_raw_angle(uint16_t *out_angle) {
    uint8_t buf[2] = {0, 0};
    if (i2c_read_register(AS5600_I2C_ADDR, AS5600_REG_RAW_ANGLE_H, buf, sizeof(buf), AS5600_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
        return false;
    }
    *out_angle = (uint16_t)(((uint16_t)(buf[0] & 0x0FU) << 8) | buf[1]);
    return true;
}

static int16_t wrap_delta_12bit(uint16_t current, uint16_t previous) {
    int16_t diff = (int16_t)current - (int16_t)previous;
    if (diff > (AS5600_HALF_SCALE_LSB - 1)) {
        diff -= (int16_t)AS5600_FULL_SCALE_LSB;
    } else if (diff < -AS5600_HALF_SCALE_LSB) {
        diff += (int16_t)AS5600_FULL_SCALE_LSB;
    }
    return diff;
}

bool pointing_device_driver_init(void) {
    i2c_init();
    s_last_retry_ms = timer_read();
    s_sensor_online = as5600_configure();
    s_angle_locked  = false;
    s_resting       = true;
    s_subtick_numer = 0;
    s_pending_ticks = 0;
    /* Always return true so USB HID & middle click stay active even if JST SH cable is hot-plugged later */
    return true;
}

report_mouse_t pointing_device_driver_get_report(report_mouse_t mouse_report) {
    const uint16_t now = timer_read();

    if (!s_sensor_online) {
        if (timer_elapsed(s_last_retry_ms) < AS5600_RETRY_INTERVAL_MS) {
            return mouse_report;
        }
        s_last_retry_ms = now;
        if (!as5600_configure()) {
            return mouse_report;
        }
        s_sensor_online = true;
        s_angle_locked  = false;
        s_resting       = true;
        s_subtick_numer = 0;
    }

    if (timer_elapsed(s_last_status_ms) >= AS5600_STATUS_POLL_MS) {
        uint8_t status = 0;
        if (i2c_read_register(AS5600_I2C_ADDR, AS5600_REG_STATUS, &status, 1, AS5600_I2C_TIMEOUT_MS) != I2C_STATUS_SUCCESS) {
            s_sensor_online = false;
            s_angle_locked  = false;
            s_last_retry_ms = now;
            return mouse_report;
        }
        s_magnet_ok      = (status & AS5600_STATUS_MD) != 0;
        s_last_status_ms = now;
    }

    if (!s_magnet_ok) {
        s_angle_locked = false;
        return mouse_report;
    }

    uint16_t raw_angle = 0;
    if (!as5600_read_raw_angle(&raw_angle)) {
        s_sensor_online = false;
        s_angle_locked  = false;
        s_last_retry_ms = now;
        return mouse_report;
    }

    if (!s_angle_locked) {
        s_prev_angle     = raw_angle;
        s_rest_anchor    = raw_angle;
        s_last_motion_ms = now;
        s_resting        = true;
        s_angle_locked   = true;
        return mouse_report;
    }

    if (!s_resting && timer_elapsed(s_last_motion_ms) >= WHEEL_IDLE_RESET_MS) {
        s_resting       = true;
        s_rest_anchor   = raw_angle;
        s_prev_angle    = raw_angle;
        s_subtick_numer = 0;
    }

    if (s_resting) {
        const int16_t wake_delta = wrap_delta_12bit(raw_angle, s_rest_anchor);
        if (wake_delta > -WHEEL_DEADBAND_LSB && wake_delta < WHEEL_DEADBAND_LSB) {
            return mouse_report;
        }
        s_resting    = false;
        s_prev_angle = s_rest_anchor;
    }

    int16_t delta_lsb = wrap_delta_12bit(raw_angle, s_prev_angle);
    if (delta_lsb != 0) {
        s_prev_angle     = raw_angle;
        s_last_motion_ms = now;

#if WHEEL_INVERT_DIR
        delta_lsb = -delta_lsb;
#endif
        s_subtick_numer += (int32_t)delta_lsb * (int32_t)WHEEL_NOTCHES_PER_REV;
        const int32_t whole_ticks = s_subtick_numer / AS5600_FULL_SCALE_LSB;
        if (whole_ticks != 0) {
            s_subtick_numer -= whole_ticks * AS5600_FULL_SCALE_LSB;
            s_pending_ticks += whole_ticks;
        }
    }

    if (s_pending_ticks != 0) {
        int32_t emit = s_pending_ticks;
        if (emit > MOUSE_REPORT_HV_MAX) {
            emit = MOUSE_REPORT_HV_MAX;
        } else if (emit < MOUSE_REPORT_HV_MIN) {
            emit = MOUSE_REPORT_HV_MIN;
        }
        s_pending_ticks -= emit;

        const bool shift_held = (get_mods() & MOD_MASK_SHIFT) != 0;
        if (s_horiz_mode || shift_held) {
            int32_t combined = (int32_t)mouse_report.h + emit;
            if (combined > MOUSE_REPORT_HV_MAX) combined = MOUSE_REPORT_HV_MAX;
            if (combined < MOUSE_REPORT_HV_MIN) combined = MOUSE_REPORT_HV_MIN;
            mouse_report.h = (mouse_hv_report_t)combined;
        } else {
            int32_t combined = (int32_t)mouse_report.v + emit;
            if (combined > MOUSE_REPORT_HV_MAX) combined = MOUSE_REPORT_HV_MAX;
            if (combined < MOUSE_REPORT_HV_MIN) combined = MOUSE_REPORT_HV_MIN;
            mouse_report.v = (mouse_hv_report_t)combined;
        }
    }

    return mouse_report;
}

uint16_t pointing_device_driver_get_cpi(void) {
    return WHEEL_NOTCHES_PER_REV;
}

void pointing_device_driver_set_cpi(uint16_t cpi) {
    (void)cpi;
}

bool process_record_kb(uint16_t keycode, keyrecord_t *record) {
    if (!process_record_user(keycode, record)) {
        return false;
    }
    if (keycode == WHL_HORZ_MO) {
        wheel_eval_set_horizontal_mode(record->event.pressed);
        return false;
    }
    return true;
}
