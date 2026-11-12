// Copyright 2024 foostan
// Copyright 2026 oktntko
// SPDX-License-Identifier: GPL-2.0-or-later

#include QMK_KEYBOARD_H
#include "curcur40_scroll.h"

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [0] = LAYOUT(
        KC_TAB,  KC_W,    KC_E,    KC_R,    KC_F,    KC_MINS,            MS_BTN3, KC_J,    KC_U,    KC_I,    KC_O,    KC_Q,
        KC_A,    KC_S,    KC_D,    KC_T,    KC_G,    LSFT(KC_SCLN),      MS_BTN1, KC_H,    KC_Y,    KC_K,    KC_L,    KC_P,
        KC_LSFT, KC_Z,    KC_X,    KC_C,    KC_V,                                 KC_B,    KC_N,    KC_M,    KC_COMM, KC_DOT,
                          KC_LGUI, LALT_T(KC_INT5), LCTL_T(KC_ESC), LT(1, KC_SPC), LT(2, KC_ENT), LT(3, KC_INT4), KC_LGUI
    ),

    [1] = LAYOUT(
        _______, KC_F2,   KC_F4,   KC_F12,  _______, KC_F11,             _______, LSFT(KC_6),    LSFT(KC_8),    LSFT(KC_9),   KC_MINS,       KC_NUBS,
        KC_LBRC, KC_DEL,  KC_ENT,  KC_BSPC, _______, LAG(KC_SPC),        _______, LSFT(KC_BSLS), KC_RBRC,       KC_NUHS,      LSFT(KC_MINS), _______,
        _______, LALT(KC_LEFT), LALT(KC_UP), LALT(KC_RGHT), _______,              LSFT(KC_4),    LSFT(KC_COMM), LSFT(KC_DOT), LSFT(KC_EQL),  _______,
                          LALT(KC_DOWN), _______, _______, _______,      _______, _______,       _______
    ),

    [2] = LAYOUT(
        _______, _______, _______, _______, _______, _______,            _______, LSFT(KC_LBRC), LSFT(KC_7), LSFT(KC_2), KC_EQL,  _______,
        _______, _______, _______, _______, _______, _______,            _______, KC_QUOT,       KC_BSPC,    KC_UP,      KC_DEL,  _______,
        _______, _______, _______, _______, _______,                              _______,       KC_LEFT,    KC_DOWN,    KC_RGHT, KC_SCLN,
                          _______, _______, _______, _______,            _______, _______,       _______
    ),

    [3] = LAYOUT(
        _______,    _______, KC_PGUP, _______, _______, _______,         _______, LSFT(KC_QUOT), KC_7, KC_8, KC_9, LSFT(KC_5),
        LSFT(KC_3), KC_HOME, KC_PGDN, KC_END,  _______, _______,         _______, KC_SLSH,       KC_4, KC_5, KC_6, LSFT(KC_MINS),
        _______,    _______, _______, _______, _______,                           KC_0,          KC_1, KC_2, KC_3, _______,
                             _______, _______, _______, _______,         _______, _______,       _______
    )
};

#ifdef ENCODER_MAP_ENABLE
const uint16_t PROGMEM encoder_map[][NUM_ENCODERS][NUM_DIRECTIONS] = {
    [0] = { ENCODER_CCW_CW(KC_NO, KC_NO), ENCODER_CCW_CW(MS_WHLD, MS_WHLU) },
    [1] = { ENCODER_CCW_CW(_______, _______), ENCODER_CCW_CW(_______, _______) },
    [2] = { ENCODER_CCW_CW(_______, _______), ENCODER_CCW_CW(_______, _______) },
    [3] = { ENCODER_CCW_CW(_______, _______), ENCODER_CCW_CW(_______, _______) },
};
#endif
