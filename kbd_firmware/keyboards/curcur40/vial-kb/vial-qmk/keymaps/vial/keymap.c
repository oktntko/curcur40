// Copyright 2024 foostan
// Copyright 2026 oktntko
// SPDX-License-Identifier: GPL-2.0-or-later

#include QMK_KEYBOARD_H
#include "curcur40_scroll.h"
#ifdef VIAL_ENABLE
#    include "vial.h"
#    include "dynamic_keymap.h"
#endif
#ifdef QMK_SETTINGS
#    include "qmk_settings.h"
#endif

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [0] = LAYOUT(
        KC_TAB,  KC_W,    KC_E,    KC_R,    KC_F,    KC_MINS,            KC_BTN3, KC_J,    KC_U,    KC_I,    KC_O,    KC_Q,
        KC_A,    KC_S,    KC_D,    KC_T,    KC_G,    LSFT(KC_SCLN),      KC_BTN1, KC_H,    KC_Y,    KC_K,    KC_L,    KC_P,
        KC_LSFT, KC_Z,    KC_X,    KC_C,    KC_V,                                 KC_B,    KC_N,    KC_M,    KC_COMM, KC_DOT,
                          KC_LGUI, LALT_T(KC_INT5), LCTL_T(KC_ESC), LT(1, KC_SPC),         LT(2, KC_ENT), LT(3, KC_INT4)
    ),

    [1] = LAYOUT(
        _______, KC_F2,   KC_F4,   KC_F12,  _______, KC_F11,             _______, LSFT(KC_6),    LSFT(KC_8),    LSFT(KC_9),   KC_MINS,       KC_NUBS,
        KC_LBRC, KC_DEL,  KC_ENT,  KC_BSPC, _______, QK_MACRO_0,         _______, LSFT(KC_BSLS), KC_RBRC,       KC_NUHS,      LSFT(KC_MINS), _______,
        _______, LALT(KC_LEFT), LALT(KC_UP), LALT(KC_RGHT), _______,              LSFT(KC_4),    LSFT(KC_COMM), LSFT(KC_DOT), LSFT(KC_EQL),  _______,
                          LALT(KC_DOWN), _______, _______, _______,               _______,       _______
    ),

    [2] = LAYOUT(
        _______, _______, _______, _______, _______, _______,            _______, LSFT(KC_LBRC), LSFT(KC_7), LSFT(KC_2), KC_EQL,  _______,
        _______, _______, _______, _______, _______, _______,            _______, KC_QUOT,       KC_BSPC,    KC_UP,      KC_DEL,  _______,
        _______, _______, _______, _______, _______,                              _______,       KC_LEFT,    KC_DOWN,    KC_RGHT, KC_SCLN,
                          _______, _______, _______, _______,                     _______,       _______
    ),

    [3] = LAYOUT(
        _______,    _______, KC_PGUP, _______, _______, _______,         _______, LSFT(KC_QUOT), KC_7, KC_8, KC_9, LSFT(KC_5),
        LSFT(KC_3), KC_HOME, KC_PGDN, KC_END,  _______, _______,         _______, KC_SLSH,       KC_4, KC_5, KC_6, LSFT(KC_MINS),
        _______,    _______, _______, _______, _______,                           KC_0,          KC_1, KC_2, KC_3, _______,
                             _______, _______, _______, _______,                  _______,       _______
    )
};

#ifdef VIAL_ENABLE
void eeconfig_init_user(void) {
    /* Macro M0: down(LGUI, LALT) -> tap(SPACE) -> up(LGUI, LALT) */
    static const uint8_t default_m0[] = SS_DOWN(X_LGUI) SS_DOWN(X_LALT) SS_TAP(X_SPC) SS_UP(X_LGUI) SS_UP(X_LALT) "\0";
    dynamic_keymap_macro_set_buffer(0, sizeof(default_m0), (uint8_t *)default_m0);

#    ifdef VIAL_COMBO_ENABLE
    vial_combo_entry_t default_combo0 = {
        .input  = {KC_BTN1, KC_H, KC_NO, KC_NO},
        .output = KC_BTN2,
    };
    dynamic_keymap_set_combo(0, &default_combo0);
#    endif

#    ifdef VIAL_KEY_OVERRIDE_ENABLE
    static const vial_key_override_entry_t default_overrides[] = {
        {KC_Z,            KC_Y,            0xFFFF, 3, 0, 2, 135},
        {KC_D,            KC_SPC,          0xFFFF, 1, 0, 0, 135},
        {KC_COMM,         KC_1,            0xFFFF, 2, 0, 0, 135},
        {KC_DOT,          KC_SLSH,         0xFFFF, 2, 0, 0, 135},
        {KC_MINS,         KC_INT1,         0xFFFF, 2, 0, 0, 135},
        {LSFT(KC_MINS),   KC_SCLN,         0xFFFF, 2, 0, 0, 135},
        {LALT(KC_UP),     LGUI(KC_UP),     0xFFFF, 2, 0, 2, 135},
        {LALT(KC_LEFT),   LGUI(KC_LEFT),   0xFFFF, 2, 0, 2, 135},
        {LALT(KC_RGHT),   LGUI(KC_RGHT),   0xFFFF, 2, 0, 2, 135},
        {LALT(KC_DOWN),   LGUI(KC_DOWN),   0xFFFF, 2, 0, 2, 135},
        {KC_F4,           LALT(KC_F4),     0xFFFF, 2, 0, 2, 135},
    };
    for (uint8_t i = 0; i < ARRAY_SIZE(default_overrides); i++) {
        vial_key_override_entry_t entry = default_overrides[i];
        dynamic_keymap_set_key_override(i, &entry);
    }
#    endif

#    ifdef QMK_SETTINGS
    uint8_t enabled = 1;
    qmk_settings_set(22, &enabled, sizeof(enabled)); /* Permissive Hold */
    qmk_settings_set(23, &enabled, sizeof(enabled)); /* Hold On Other Key Press */
#    endif

    vial_init();
}
#endif
