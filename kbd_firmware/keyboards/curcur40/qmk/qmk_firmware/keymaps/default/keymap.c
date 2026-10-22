// Copyright 2024 foostan
// Copyright 2026 oktntko
// SPDX-License-Identifier: GPL-2.0-or-later

#include QMK_KEYBOARD_H

#ifndef RM_TOGG
#    define RM_TOGG RGB_TOG
#    define RM_NEXT RGB_MOD
#    define RM_PREV RGB_RMOD
#    define RM_HUEU RGB_HUI
#    define RM_HUED RGB_HUD
#    define RM_SATU RGB_SAI
#    define RM_SATD RGB_SAD
#    define RM_VALU RGB_VAI
#    define RM_VALD RGB_VAD
#endif

#ifndef MS_BTN1
#    define MS_BTN1 KC_BTN1
#    define MS_BTN2 KC_BTN2
#    define MS_BTN3 KC_BTN3
#endif

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [0] = LAYOUT(
        KC_Q,    KC_W,    KC_E,    KC_R,    KC_T,    KC_TAB,     KC_MUTE, KC_Y,    KC_U,    KC_I,    KC_O,    KC_P,
        KC_A,    KC_S,    KC_D,    KC_F,    KC_G,    KC_LCTL,    MS_BTN3, KC_H,    KC_J,    KC_K,    KC_L,    KC_SCLN,
        KC_Z,    KC_X,    KC_C,    KC_V,    KC_B,                         KC_N,    KC_M,    KC_COMM, KC_DOT,  KC_SLSH,
                          KC_LGUI, MO(1),   KC_SPC,  KC_LSFT,    KC_ENT,  MO(2),   KC_BSPC
    ),

    [1] = LAYOUT(
        KC_1,    KC_2,    KC_3,    KC_4,    KC_5,    KC_ESC,     _______, KC_6,    KC_7,    KC_8,    KC_9,    KC_0,
        XXXXXXX, XXXXXXX, MS_BTN2, MS_BTN1, XXXXXXX, _______,    _______, KC_LEFT, KC_DOWN, KC_UP,   KC_RGHT, KC_QUOT,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                      MS_BTN1, MS_BTN2, XXXXXXX, XXXXXXX, KC_ESC,
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
        RM_TOGG, RM_HUEU, RM_SATU, RM_VALU, XXXXXXX, XXXXXXX,    XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        RM_NEXT, RM_HUED, RM_SATD, RM_VALD, XXXXXXX,                      XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
                          _______, _______, _______, _______,    _______, _______, _______
    )
};

#ifdef ENCODER_MAP_ENABLE
const uint16_t PROGMEM encoder_map[][NUM_ENCODERS][NUM_DIRECTIONS] = {
    [0] = { ENCODER_CCW_CW(KC_VOLD, KC_VOLU), ENCODER_CCW_CW(KC_VOLD, KC_VOLU) },
    [1] = { ENCODER_CCW_CW(RM_PREV, RM_NEXT), ENCODER_CCW_CW(KC_PGUP, KC_PGDN) },
    [2] = { ENCODER_CCW_CW(RM_HUED, RM_HUEU), ENCODER_CCW_CW(RM_VALD, RM_VALU) },
    [3] = { ENCODER_CCW_CW(RM_SATD, RM_SATU), ENCODER_CCW_CW(RM_PREV, RM_NEXT) },
};
#endif
