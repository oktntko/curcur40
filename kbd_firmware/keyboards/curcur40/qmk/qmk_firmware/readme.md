# curcur40

A 40-key split ergonomic keyboard based on Corne v4.1 mini (RP2040), featuring Kailh Choc v1/v2 low-profile hotswap switches, an under-plate 1-piece integral-shaft Passive Magnetic Inertia Wheel (`45# Steel` `Ø22.0mm` flywheel + main-PCB `TMAG5273` / `TLV493D-A1B6` 3D Hall angle sensor + main-PCB `Kailh Square Silent` middle click), and a `PMW3360` 25mm trackball sensor with 2D kinetic inertia drag-scrolling (`SCRL_MO` / `SCRL_TG` / `SCRL_SL` / `WHL_HRZ`) on the right half.

## Build & Flash

### VIA (QMK)

```sh
make qmk-clean
kb=curcur40 make qmk-init
kb=curcur40 kr=rev1 km=via make qmk-compile
```

### Vial (Vial-QMK)

```sh
make vial-qmk-clean
kb=curcur40 make vial-qmk-init
kb=curcur40 kr=rev1 km=vial make vial-qmk-compile
```
