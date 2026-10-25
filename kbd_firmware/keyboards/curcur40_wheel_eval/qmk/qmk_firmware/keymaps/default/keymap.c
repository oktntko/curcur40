// Copyright 2026 oktntko
// SPDX-License-Identifier: GPL-2.0-or-later

#include QMK_KEYBOARD_H
#include "wheel_eval.h"

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [0] = LAYOUT(
        MS_BTN3
    ),
    [1] = LAYOUT(
        WHL_HORZ_MO
    )
};
