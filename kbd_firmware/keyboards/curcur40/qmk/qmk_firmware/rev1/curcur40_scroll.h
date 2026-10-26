// Copyright 2026 oktntko
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

#include QMK_KEYBOARD_H

/*
 * curcur40 Custom Keycodes (mapped to QK_KB_0..3 = 0x7E00..0x7E03 for full
 * compatibility across QMK, VIA USER00..03, and Vial customKeycodes).
 */
enum curcur40_keycodes {
    SCRL_MO = QK_KB_0, // Hold: 2D trackball inertia high-speed drag-scroll (release brakes & restores cursor)
    SCRL_TG = QK_KB_1, // Toggle: hands-free 2D trackball inertia high-speed drag-scroll
    SCRL_SL = QK_KB_2, // Hold: precision slow 2D trackball drag-scroll (inertia disabled)
    WHL_HRZ = QK_KB_3, // Hold: convert AS5600 passive magnetic inertia wheel rotation to horizontal scroll
};

/* =========================================================================
 * 1. AS5600 Passive Magnetic Inertia Wheel (Right Half I2C0: GP24 SDA / GP25 SCL)
 *    - 12-bit contactless Hall angle sensor (0x36) facing Ø3x2mm diametric magnet
 *    - Cup-shaped SUS304 flywheel + internal 9-ball axial magnetic ratchet hub
 *      provides real physical free-spin momentum and finger-touch braking.
 *    - Recommended CURCUR40_WHEEL_NOTCHES_PER_REV presets:
 *         9 : Exact 1:1 HID scroll step per physical magnetic detent (40.0 deg)
 *        18 : Standard 20.0 deg mouse wheel pitch (2 steps/detent, default)
 *        36 : High-density fast scroll (10.0 deg/step, 4 steps/detent)
 * ========================================================================= */
#define CURCUR40_AS5600_I2C_ADDR        (0x36 << 1)
#define CURCUR40_AS5600_REG_CONF_H      0x07
#define CURCUR40_AS5600_REG_STATUS      0x0B
#define CURCUR40_AS5600_REG_RAW_ANGLE_H 0x0C
#define CURCUR40_AS5600_STATUS_MD       (1U << 5)

#ifndef CURCUR40_WHEEL_NOTCHES_PER_REV
#    define CURCUR40_WHEEL_NOTCHES_PER_REV 18
#endif
#ifndef CURCUR40_WHEEL_DEADBAND_LSB
#    define CURCUR40_WHEEL_DEADBAND_LSB 6
#endif
#ifndef CURCUR40_WHEEL_INVERT_DIR
#    define CURCUR40_WHEEL_INVERT_DIR 1
#endif

/* =========================================================================
 * 2. PMW3360 25mm Trackball 2D Inertia Drag-Scroll (Kinetic Flick & Brake)
 *    - Activated by holding SCRL_MO, toggling SCRL_TG, or entering
 *      CURCUR40_SCROLL_LAYER (Layer 3 by default).
 *    - Flicking and lifting the thumb launches exponential-decay coasting;
 *      touching the ball (micro-motion / reverse nudge) or releasing the
 *      scroll layer brakes immediately to zero.
 * ========================================================================= */
#ifndef CURCUR40_SCROLL_LAYER
#    define CURCUR40_SCROLL_LAYER 3
#endif
#ifndef CURCUR40_DRAGSCROLL_DIVISOR
#    define CURCUR40_DRAGSCROLL_DIVISOR 24.0f
#endif
#ifndef CURCUR40_DRAGSCROLL_PRECISION_DIVISOR
#    define CURCUR40_DRAGSCROLL_PRECISION_DIVISOR 48.0f
#endif
#ifndef CURCUR40_SCROLL_AXIS_LOCK_RATIO
#    define CURCUR40_SCROLL_AXIS_LOCK_RATIO 2.5f
#endif
#ifndef CURCUR40_INERTIA_TICK_MS
#    define CURCUR40_INERTIA_TICK_MS 8U
#endif
#ifndef CURCUR40_INERTIA_LIFT_GAP_MS
#    define CURCUR40_INERTIA_LIFT_GAP_MS 14U
#endif
#ifndef CURCUR40_INERTIA_LAUNCH_VEL
#    define CURCUR40_INERTIA_LAUNCH_VEL 0.022f
#endif
#ifndef CURCUR40_INERTIA_BOOST
#    define CURCUR40_INERTIA_BOOST 1.25f
#endif
#ifndef CURCUR40_INERTIA_MAX_VEL
#    define CURCUR40_INERTIA_MAX_VEL 0.220f
#endif
#ifndef CURCUR40_INERTIA_MIN_VEL
#    define CURCUR40_INERTIA_MIN_VEL 0.0025f
#endif
#ifndef CURCUR40_INERTIA_DECAY_8MS
#    define CURCUR40_INERTIA_DECAY_8MS 0.988f
#endif
#ifndef CURCUR40_INERTIA_TOUCH_STOP_COUNTS
#    define CURCUR40_INERTIA_TOUCH_STOP_COUNTS 8
#endif
