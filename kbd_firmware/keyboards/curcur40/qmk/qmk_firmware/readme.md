# curcur40

A 40-key split ergonomic keyboard based on Corne v4.1 mini (RP2040), featuring Kailh Choc v1 low-profile hotswap switches, a horizontal CKW12 rotary encoder, and a PMW3360 trackball sensor on the right half.

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
