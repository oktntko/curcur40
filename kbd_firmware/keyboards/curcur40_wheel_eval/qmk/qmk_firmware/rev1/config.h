// Copyright 2026 oktntko
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

/* RP2040-Zero I2C0 Configuration (J1 JST SH 6-pin -> AS5600-ASOT Sub-PCB) */
#define I2C_DRIVER I2CD0
#define I2C1_SDA_PIN GP4
#define I2C1_SCL_PIN GP5
#define F_SCL 400000UL

/* High-rate 1 kHz polling for zero-loss tracking during 20+ rev/s inertia flicks */
#define POINTING_DEVICE_TASK_THROTTLE_MS 1
#define MOUSE_EXTENDED_REPORT

/*
 * Passive Magnetic Inertia Wheel Resolution & Filtering Tuning:
 * - Physical hub has 11 discrete Ø2.00 mm SUJ2 steel balls (32.73 deg/detent).
 * - Recommended WHEEL_NOTCHES_PER_REV presets:
 *     11 : Exact 1:1 HID scroll step per physical magnetic detent
 *     22 : Standard ~16.4 deg mouse wheel pitch (2 steps per physical detent, default)
 *     36 : High-density fast scroll (~10.0 deg per step, matches 36 rim flutes)
 */
#ifndef WHEEL_NOTCHES_PER_REV
#    define WHEEL_NOTCHES_PER_REV 22
#endif

/* Stationary thermal/Hall micro-jitter deadband in 12-bit LSBs (6 LSB ~= 0.53 deg) */
#ifndef WHEEL_DEADBAND_LSB
#    define WHEEL_DEADBAND_LSB 6
#endif

/* Set to 1 to invert scroll direction */
#ifndef WHEEL_INVERT_DIR
#    define WHEEL_INVERT_DIR 0
#endif

/* RP2040 double-tap reset bootloader entry */
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET_TIMEOUT 500U
