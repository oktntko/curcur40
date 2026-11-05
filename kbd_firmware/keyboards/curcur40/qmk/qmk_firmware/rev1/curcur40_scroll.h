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
    WHL_HRZ = QK_KB_3, // Hold: convert passive magnetic inertia wheel rotation to horizontal scroll
};

/* =========================================================================
 * 1. Under-Plate 3D Hall Passive Magnetic Inertia Wheel
 *    (Right Half Main PCB B.Cu: rU6 on I2C0 GP24 SDA / GP25 SCL + rEXSW1 on GP7)
 *    - Primary sensor: TI TMAG5273 (A1/A2 0x35, B1/B2 0x22, D1/D2 0x44, C1/C2 0x78)
 *      in XZX pseudo-simultaneous continuous mode, sensing off-axis D4x1mm
 *      diametric shaft magnet via (Bx, Bz) quadrature vector.
 *    - Fallback sensor: Infineon TLV493D-A1B6 (0x5E / 0x1F, pin-compatible SOT-23-6)
 *      in Master Controlled continuous mode with /INT disabled, via (By, Bz).
 *    - 1-piece CNC 45# steel integral-shaft flywheel (24 outer flutes) + magnetic
 *      detent screw provides real physical free-spin momentum, 24 tactile notches/rev,
 *      and instant finger-touch braking.
 *    - Recommended CURCUR40_WHEEL_NOTCHES_PER_REV presets:
 *        12 : Coarse 30.0 deg/step (1 step per 2 physical detents)
 *        24 : Exact 1:1 HID scroll step per physical magnetic detent (15.0 deg, default)
 *        48 : High-density fast scroll (7.5 deg/step, 2 steps/detent)
 * ========================================================================= */
#define CURCUR40_TMAG5273_MFG_ID            0x5449U // "TI" in 0x0E (LSB=0x49) .. 0x0F (MSB=0x54)
#define CURCUR40_TMAG5273_REG_DEV_CFG_1     0x00U
#define CURCUR40_TMAG5273_REG_DEV_CFG_2     0x01U
#define CURCUR40_TMAG5273_REG_SNS_CFG_1     0x02U
#define CURCUR40_TMAG5273_REG_SNS_CFG_2     0x03U
#define CURCUR40_TMAG5273_REG_T_CFG         0x07U
#define CURCUR40_TMAG5273_REG_INT_CFG_1     0x08U
#define CURCUR40_TMAG5273_REG_DEVICE_ID     0x0DU
#define CURCUR40_TMAG5273_REG_X_MSB_RESULT  0x12U
#define CURCUR40_TMAG5273_CONV_RESULT_READY 0x01U

#ifndef CURCUR40_WHEEL_NOTCHES_PER_REV
#    define CURCUR40_WHEEL_NOTCHES_PER_REV 24
#endif
#ifndef CURCUR40_WHEEL_DEADBAND_LSB
#    define CURCUR40_WHEEL_DEADBAND_LSB 12
#endif
#ifndef CURCUR40_WHEEL_INVERT_DIR
#    define CURCUR40_WHEEL_INVERT_DIR 0
#endif
#ifndef CURCUR40_WHEEL_CLICK_PIN
#    define CURCUR40_WHEEL_CLICK_PIN GP7
#endif
#ifndef CURCUR40_WHEEL_CLICK_BLANK_MS
#    define CURCUR40_WHEEL_CLICK_BLANK_MS 25U
#endif
#ifndef CURCUR40_WHEEL_MIN_MAG_L1
#    define CURCUR40_WHEEL_MIN_MAG_L1 600
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
