// Copyright 2026 oktntko
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

#include QMK_KEYBOARD_H

/*
 * curcur40 Custom Keycodes (mapped to QK_KB_0..2 = 0x7E00..0x7E02 for full
 * compatibility across QMK, VIA USER00..02, and Vial customKeycodes).
 */
enum curcur40_keycodes {
    SCRL_MO = QK_KB_0, // Hold: 2D trackball inertia high-speed drag-scroll (release brakes & restores cursor)
    SCRL_TG = QK_KB_1, // Toggle: hands-free 2D trackball inertia high-speed drag-scroll
    SCRL_SL = QK_KB_2, // Hold: precision slow 2D drag-scroll (inertia disabled)
};

/* =========================================================================
 * 1. CKW12 Roller Encoder Ballistic Acceleration (Method A: No Runaway Coast)
 *    - Slow clicks (>= 95 ms/detent): exact 1x per physical notch
 *    - Fast flicks (<  95 ms/detent): scales smoothly from 2x up to 12x
 *      based on inter-pulse dt and consecutive same-direction pulse streak.
 *    - Total scroll distance is strictly determined by physical wheel pulses.
 * ========================================================================= */
#ifndef CURCUR40_ENC_ACCEL_WINDOW_MS
#    define CURCUR40_ENC_ACCEL_WINDOW_MS 160U
#endif
#ifndef CURCUR40_ENC_SLOW_MS
#    define CURCUR40_ENC_SLOW_MS 95U
#endif
#ifndef CURCUR40_ENC_MID_MS
#    define CURCUR40_ENC_MID_MS 60U
#endif
#ifndef CURCUR40_ENC_FAST_MS
#    define CURCUR40_ENC_FAST_MS 35U
#endif
#ifndef CURCUR40_ENC_FLICK_MS
#    define CURCUR40_ENC_FLICK_MS 20U
#endif
#ifndef CURCUR40_ENC_MAX_STEP
#    define CURCUR40_ENC_MAX_STEP 12
#endif
#ifndef CURCUR40_ENC_MAX_PENDING
#    define CURCUR40_ENC_MAX_PENDING 36
#endif
#ifndef CURCUR40_ENC_BURST_TICK_MS
#    define CURCUR40_ENC_BURST_TICK_MS 4U
#endif
#ifndef CURCUR40_ENC_BURST_MAX_PER_TICK
#    define CURCUR40_ENC_BURST_MAX_PER_TICK 3
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
