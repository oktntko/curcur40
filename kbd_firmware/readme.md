# curcur40 Firmware (QMK / Vial)

## 1. Setting Up Your QMK Environment

Please see https://docs.qmk.fm/#/newbs_getting_started and set up your QMK build environment.

## 2. Getting Source Files

Fetch the `qmk/qmk_firmware` and `vial-kb/vial-qmk` submodules:
```sh
make git-submodule
```

## 3. Building Firmware for curcur40

### For VIA
```sh
make qmk-clean
kb=curcur40 make qmk-init
kb=curcur40 kr=rev1 km=via make qmk-compile
```
The compiled `.uf2` firmware will be stored in `keyboards/curcur40/qmk/qmk_firmware/.build/curcur40_rev1_via.uf2`.

### For Vial (Recommended)
```sh
make vial-qmk-clean
kb=curcur40 make vial-qmk-init
kb=curcur40 kr=rev1 km=vial make vial-qmk-compile
```
The compiled `.uf2` firmware will be stored in `keyboards/curcur40/vial-kb/vial-qmk/.build/curcur40_rev1_vial.uf2`.

### Clean & Build All
```sh
make update-all
```

## 4. Dual Pointing & High-Speed Scrolling Features (`rev1/curcur40_scroll.c`)

1. **TMAG5273 / TLV493D-A1B6 3D Hall Under-Plate Inertia Wheel (`rU6` on `curcur40-right` `B.Cu`, Right Half I2C0 `GP24`/`GP25` @ 400 kHz + `rEXSW1` Silent Middle Click `GP7`)**:
   - Auto-detects `TMAG5273` (`A1/B1/C1/D1`, `XZX` pseudo-simultaneous continuous mode) or pin-compatible `TLV493D-A1B6` (3.3 kHz fast continuous mode) on `I2C0`, normalizes off-axis quadrature flux via adaptive peak-envelope tracking, and computes 12-bit angle via integer CORDIC (`24 notches/rev` aligned 1:1 with the 24 outer flutes of the `Ø22.0mm` `45# Steel` integral-shaft flywheel).
   - 1-piece `45# Steel` (`13.12 g`, electroless nickel plated) integral-shaft flywheel on degreased `DDL-520ZZ` bearings + glue-free `Ø2.0×2.0mm` axial magnetic detent provides tactile notches on slow rolls, long physical free-spin coasting on flicks, and instant mechanical stop when touched by a finger.
   - Pressing down the wheel actuates the main-PCB silent switch (`rEXSW1` `[4, 6]` on `GP7`, mapped to `MS_BTN3` / `KC_BTN3` by default, with real-time click-blanking to suppress scroll jitter). Holding `WHL_HRZ` (`QK_KB_3` / `USER03`, Layer 1 `[5, 6]`) converts wheel rotation to horizontal scrolling.
2. **PMW3360 25mm Trackball 2D Inertia Drag-Scroll (`rJ3`, Right Half SPI1 `GP14`/`GP11`/`GP8`/`GP6`)**:
   - **Custom Keycodes** (available in Vial / VIA **User** tab and pre-assigned on Layer 1):
     - `SCRL_MO` (`QK_KB_0` / `USER00`): Hold for 2D inertia high-speed scroll; releasing immediately brakes and restores normal cursor tracking.
     - `SCRL_TG` (`QK_KB_1` / `USER01`): Toggle hands-free 2D inertia high-speed scroll.
     - `SCRL_SL` (`QK_KB_2` / `USER02`): Hold for slow precision 2D drag-scroll (inertia disabled).
     - `WHL_HRZ` (`QK_KB_3` / `USER03`): Hold to convert passive magnetic inertia wheel rotation to horizontal scroll.
   - **Layer Activation**: Entering `CURCUR40_SCROLL_LAYER` (default Layer `3`) also enables 2D inertia scroll automatically.
   - **Touch-to-Stop & Zoom Guard**: Touching the trackball (or clicking a mouse button) during inertia coasting immediately stops movement; pressing `Ctrl`/`Alt`/`GUI` during coasting cancels inertia to prevent accidental OS zoom.
   - Tuning parameters can be overridden in `rev1/config.h` (see `rev1/curcur40_scroll.h`).
