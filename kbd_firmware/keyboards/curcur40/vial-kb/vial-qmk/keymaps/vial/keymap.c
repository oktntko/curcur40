// Copyright 2024 foostan
// Copyright 2026 oktntko
// SPDX-License-Identifier: GPL-2.0-or-later

#include QMK_KEYBOARD_H
#include "curcur40_scroll.h"

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [0] = LAYOUT(
        KC_Q,    KC_W,    KC_E,    KC_R,    KC_T,    KC_TAB,     KC_BTN3, KC_Y,    KC_U,    KC_I,    KC_O,    KC_P,
        KC_A,    KC_S,    KC_D,    KC_F,    KC_G,    KC_LCTL,    KC_MUTE, KC_H,    KC_J,    KC_K,    KC_L,    KC_SCLN,
        KC_Z,    KC_X,    KC_C,    KC_V,    KC_B,                         KC_N,    KC_M,    KC_COMM, KC_DOT,  KC_SLSH,
                          KC_LGUI, MO(1),   KC_SPC,  KC_LSFT,    KC_ENT,  MO(2),   KC_BSPC
    ),

    [1] = LAYOUT(
        KC_1,    KC_2,    KC_3,    KC_4,    KC_5,    KC_ESC,     _______, KC_6,    KC_7,    KC_8,    KC_9,    KC_0,
        SCRL_TG, SCRL_MO, KC_BTN2, KC_BTN1, SCRL_SL, _______,    WHL_HRZ, KC_LEFT, KC_DOWN, KC_UP,   KC_RGHT, KC_QUOT,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                      KC_BTN1, KC_BTN2, SCRL_MO, SCRL_TG, KC_ESC,
                          _______, _______, _______, _______,    _______, MO(3),   KC_DEL
    ),

    [2] = LAYOUT(
        KC_EXLM, KC_AT,   KC_HASH, KC_DLR,  KC_PERC, KC_TAB,     _______, KC_CIRC, KC_AMPR, KC_ASTR, KC_LPRN, KC_RPRN,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, _______,    _______, KC_MINS, KC_EQL,  KC_LBRC, KC_RBRC, KC_BSLS,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                      KC_UNDS, KC_PLUS, KC_LCBR, KC_RCBR, KC_PIPE,
                          _______, MO(3),   _______, _______,    _______, _______, KC_GRV
    ),

    [3] = LAYOUT(
        QK_BOOT, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,    XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, QK_BOOT,
        RGB_TOG, RGB_HUI, RGB_SAI, RGB_VAI, XXXXXXX, XXXXXXX,    XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        RGB_MOD, RGB_HUD, RGB_SAD, RGB_VAD, XXXXXXX,                      XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
                          _______, _______, _______, _______,    _______, _______, _______
    )
};
