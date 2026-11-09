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

## 4. High-Speed Scrolling Features (`rev1/curcur40_scroll.c`)

1. **CKW12 Ballistic Wheel Scroll (Method A — Deterministic Speed Multiplier, No Runaway Coasting)**:
   - Layer 0 defaults to vertical scroll (`MS_WHLU` / `MS_WHLD`), and Layer 1 defaults to horizontal scroll (`MS_WHLL` / `MS_WHLR`).
   - Slow turning ($\Delta t \ge 95\text{ ms}$) emits exact `1x` steps; fast flicks scale smoothly up to `12x` (`CURCUR40_ENC_MAX_STEP`) based on pulse interval and same-direction streak, stopping immediately when the wheel stops.
2. **PMW3360 25mm Trackball 2D Inertia Drag-Scroll**:
   - **Custom Keycodes** (available in Vial / VIA **User** tab and pre-assigned on Layer 1):
     - `SCRL_MO` (`QK_KB_0` / `USER00`): Hold for 2D inertia high-speed scroll; releasing immediately brakes and restores normal cursor tracking.
     - `SCRL_TG` (`QK_KB_1` / `USER01`): Toggle hands-free 2D inertia high-speed scroll.
     - `SCRL_SL` (`QK_KB_2` / `USER02`): Hold for slow precision 2D drag-scroll (inertia disabled).
   - **Layer Activation**: Entering `CURCUR40_SCROLL_LAYER` (default Layer `3`) also enables 2D inertia scroll automatically.
   - **Touch-to-Stop & Zoom Guard**: Touching the trackball (or clicking a mouse button) during inertia coasting immediately stops movement; pressing `Ctrl`/`Alt`/`GUI` during coasting cancels inertia to prevent accidental OS zoom.
   - Tuning parameters can be overridden in `rev1/config.h` (see `rev1/curcur40_scroll.h`).

## 5. PMW3360 Lift-Off / SQUAL Threshold Presets & Live Notepad Diagnostics

1. **Sensitivity / Lift-Off Presets (`m0`..`m3`)**:
   - `m0` (Boot Default): `Lift_Config=0x03` (`+3 mm`), `Min_SQ_Run=6`, `Raw_Data_Threshold=7`
   - `m1` (Ultra Sensitivity): `Lift_Config=0x03` (`+3 mm`), `Min_SQ_Run=1`, `Raw_Data_Threshold=4`
   - `m2` (`+3 mm` Lift Only): `Lift_Config=0x03` (`+3 mm`), `Min_SQ_Run=16`, `Raw_Data_Threshold=10`
   - `m3` (`v0.2.2` Stock Baseline): `Lift_Config=0x02` (`+2 mm`), `Min_SQ_Run=16`, `Raw_Data_Threshold=10`
2. **Triggers (Works on Left Half USB via TRRS Split RPC or Right Half USB — flash both halves with the same `.uf2`, open Notepad in Half-Width English)**:
   - **Left-Hand Chord (Recommended when USB is plugged into Left Half)**:
     - **Left `MO(1)` Thumb (`[3,4]`) + `B` (`[2,5]`)** (or `TB_DBG` / `USER03`): Toggle `1.0 s` live telemetry streaming ON/OFF (`Esc` also stops streaming immediately).
     - **Left `MO(1)` Thumb (`[3,4]`) + `V` (`[2,4]`)** (or `TB_MOD` / `USER04`): Cycle `m0 -> m1 -> m2 -> m3 -> m0` and emit a single-line snapshot.
   - **Right-Hand Chord**:
     - **Right Middle Thumb (`[7,4]`) + `CKW12` Wheel Click (`[4,6]`)** (or `TB_DBG` / `USER03`): Toggle `1.0 s` live telemetry streaming ON/OFF.
     - **Right Middle Thumb (`[7,4]`) + Inner Key Below Wheel (`[5,6]`)** (or `TB_MOD` / `USER04`): Cycle `m0 -> m1 -> m2 -> m3 -> m0` and emit a single-line snapshot.
