// Copyright 2026 oktntko
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

#include <stdbool.h>
#include <stdint.h>
#include "quantum.h"

/* AS5600 7-bit I2C slave address 0x36 (shifted for QMK i2c_master API) */
#define AS5600_I2C_ADDR (0x36 << 1)

/* AS5600 Register Map */
#define AS5600_REG_CONF_H      0x07
#define AS5600_REG_CONF_L      0x08
#define AS5600_REG_STATUS      0x0B
#define AS5600_REG_RAW_ANGLE_H 0x0C
#define AS5600_REG_RAW_ANGLE_L 0x0D

/* AS5600 STATUS Register Bits */
#define AS5600_STATUS_MH (1U << 3) /* Magnet too strong */
#define AS5600_STATUS_ML (1U << 4) /* Magnet too weak   */
#define AS5600_STATUS_MD (1U << 5) /* Magnet detected   */

/* Custom keycodes for testing horizontal scroll or sensitivity on Eval Pod */
enum wheel_eval_keycodes {
    WHL_HORZ_MO = QK_KB_0,
};

void wheel_eval_set_horizontal_mode(bool enabled);
bool wheel_eval_get_horizontal_mode(void);
