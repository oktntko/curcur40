// Copyright 2024 foostan
// Copyright 2026 oktntko
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

#define SERIAL_USART_TX_PIN GP12
#define USB_VBUS_PIN GP13

/* SPI1 & PMW3360 Pointing Device Configuration (Right Half) */
#define SPI_DRIVER SPID1
#define SPI_SCK_PIN GP14
#define SPI_MOSI_PIN GP11
#define SPI_MISO_PIN GP8
#define POINTING_DEVICE_CS_PIN GP6
#define PMW33XX_CS_PIN GP6

#define SPLIT_POINTING_ENABLE
#define POINTING_DEVICE_RIGHT
#define PMW33XX_CPI 600
#define MOUSE_EXTENDED_REPORT
#define ENCODER_MAP_KEY_DELAY 2

/*
 * Trackball Sensor (U1: PMW3360DM-T2QU) Orientation on Right Sensor Sub-PCB:
 * - Mounted on B.Cu with optical aperture facing up (+Z) toward the 25mm trackball
 *   (equivalent to a 180 deg flip around the East-West X axis from standard mouse orientation).
 * - Pin 1..8 row is at West (-X), Pin 9..16 row is at East (+X),
 *   with Pin 1/16 (IR LED) at South (+Y_kicad) and Pin 8/9 (Camera) at North (-Y_kicad).
 * - Rolling Right (+X_kicad) moves the ball's bottom surface West (Pin 9..16 -> Pin 1..8 = +X_report, naturally aligned).
 * - Rolling Up (-Y_kicad) moves the ball's bottom surface South (Pin 8/9 -> Pin 1/16 = +Y_report, inverted vs -Y_report = Up):
 */
// #define POINTING_DEVICE_INVERT_X
#define POINTING_DEVICE_INVERT_Y
// #define POINTING_DEVICE_ROTATION_90
// #define POINTING_DEVICE_ROTATION_180
// #define POINTING_DEVICE_ROTATION_270

/* RP2040- and hardware-specific config */
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET_TIMEOUT 500U
#define PICO_XOSC_STARTUP_DELAY_MULTIPLIER 64
