// Copyright 2024 foostan
// Copyright 2026 oktntko
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

#define SERIAL_USART_TX_PIN GP12
#define USB_VBUS_PIN GP13

/* SPI1 & PMW3360 25mm Trackball Sensor Configuration (Right Half, rJ3) */
#define SPI_DRIVER SPID1
#define SPI_SCK_PIN GP14
#define SPI_MOSI_PIN GP11
#define SPI_MISO_PIN GP8
#define POINTING_DEVICE_CS_PIN GP6
#define PMW33XX_CS_PIN GP6

/* I2C0 & AS5600 Passive Magnetic Inertia Wheel Configuration (Right Half, rJ5) */
#define I2C_DRIVER I2CD0
#define I2C1_SDA_PIN GP24
#define I2C1_SCL_PIN GP25
#define I2C1_CLOCK_SPEED 400000

#define SPLIT_POINTING_ENABLE
#define POINTING_DEVICE_RIGHT
#define POINTING_DEVICE_TASK_THROTTLE_MS 1
#define PMW33XX_CPI 1200
#define MOUSE_EXTENDED_REPORT

/*
 * Trackball Sensor (U1: PMW3360DM-T2QU) Orientation on Right Sub-PCB:
 * - Mounted on B.Cu with optical aperture facing up (+Z) toward the 25mm trackball.
 * - Pin 1..8 row is at West, Pin 9..16 row is at East, with Pin 1/16 at South (+Y_kicad)
 *   and Pin 8/9 at North (-Y_kicad).
 * - Rolling Up (-Y_kicad) moves the ball bottom surface South (+Y_kicad -> -Y_report),
 *   and rolling Right (+X_kicad) moves the ball bottom surface West (-X_kicad -> -X_report).
 * - Therefore Y is naturally aligned (-Y_report = cursor Up), and X is inverted:
 */
#define POINTING_DEVICE_INVERT_X
// #define POINTING_DEVICE_INVERT_Y
// #define POINTING_DEVICE_ROTATION_90
// #define POINTING_DEVICE_ROTATION_180
// #define POINTING_DEVICE_ROTATION_270

/* RP2040- and hardware-specific config */
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET_TIMEOUT 500U
#define PICO_XOSC_STARTUP_DELAY_MULTIPLIER 64
