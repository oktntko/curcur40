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

### For Standalone Inertia Wheel Eval Pod (`curcur40_wheel_eval`)
```sh
kb=curcur40_wheel_eval make qmk-init
kb=curcur40_wheel_eval kr=rev1 km=default make qmk-compile
```
The compiled `.uf2` firmware will be stored in `keyboards/curcur40_wheel_eval/qmk/qmk_firmware/.build/curcur40_wheel_eval_rev1_default.uf2`.

### Clean & Build All
```sh
make update-all
```

## 4. Dual Pointing & High-Speed Scrolling Features (`rev1/curcur40_scroll.c`)

1. **AS5600 Passive Magnetic Inertia Wheel (`rJ5`, Right Half I2C0 `GP24`/`GP25` @ 400 kHz + Silent Middle Click `GP7`)**:
   - Reads the 12-bit contactless Hall angle sensor (`0x36`, `RAW ANGLE 0x0C`) at up to `1000 Hz` (`CONF = 0x0704`: 0.286 ms fast step response + 6-LSB rest deadband) alongside `PMW3360` on `SPI1`.
   - Physical cup-shaped `SUS304` flywheel + internal 9-ball axial magnetic ratchet hub provides tactile detents on slow rolls, long physical free-spin coasting on flicks, and instant mechanical stop when touched by a finger.
   - Pressing down the wheel actuates the hinged silent switch (`[4, 6]` on `GP7`, mapped to `MS_BTN3` / `KC_BTN3` by default). Holding `WHL_HRZ` (`QK_KB_3` / `USER03`, Layer 1 `[5, 6]`) converts wheel rotation to horizontal scrolling.
2. **PMW3360 25mm Trackball 2D Inertia Drag-Scroll (`rJ3`, Right Half SPI1 `GP14`/`GP11`/`GP8`/`GP6`)**:
   - **Custom Keycodes** (available in Vial / VIA **User** tab and pre-assigned on Layer 1):
     - `SCRL_MO` (`QK_KB_0` / `USER00`): Hold for 2D inertia high-speed scroll; releasing immediately brakes and restores normal cursor tracking.
     - `SCRL_TG` (`QK_KB_1` / `USER01`): Toggle hands-free 2D inertia high-speed scroll.
     - `SCRL_SL` (`QK_KB_2` / `USER02`): Hold for slow precision 2D drag-scroll (inertia disabled).
     - `WHL_HRZ` (`QK_KB_3` / `USER03`): Hold to convert AS5600 passive magnetic inertia wheel rotation to horizontal scroll.
   - **Layer Activation**: Entering `CURCUR40_SCROLL_LAYER` (default Layer `3`) also enables 2D inertia scroll automatically.
   - **Touch-to-Stop & Zoom Guard**: Touching the trackball (or clicking a mouse button) during inertia coasting immediately stops movement; pressing `Ctrl`/`Alt`/`GUI` during coasting cancels inertia to prevent accidental OS zoom.
   - Tuning parameters can be overridden in `rev1/config.h` (see `rev1/curcur40_scroll.h`).
