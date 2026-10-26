# curcur40

A 40-key split ergonomic keyboard based on Corne v4.1 mini (RP2040), featuring Kailh Choc v1/v2 low-profile hotswap switches, a sunk Passive Magnetic Inertia Wheel (`SUS304` cup flywheel + internal 9-ball magnetic ratchet + `AS5600` 12-bit contactless Hall angle sensor + silent middle click), and a `PMW3360` 25mm trackball sensor with 2D kinetic inertia drag-scrolling (`SCRL_MO` / `SCRL_TG` / `SCRL_SL` / `WHL_HRZ`) on the right half.

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
