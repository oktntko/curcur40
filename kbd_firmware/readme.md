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
