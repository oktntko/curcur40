# curcur40 Inertia Wheel Evaluation Pod (`curcur40_wheel_eval`)

Standalone QMK firmware for the **Passive Magnetic Inertia Scroll Wheel Desktop Evaluation Pod** (`Waveshare RP2040-Zero` + `AS5600-ASOT` 12-bit contactless Hall encoder + `Kailh Square Silent` middle-click micro switch).

## Pin Assignment (`curcur40-wheel-eval` Carrier PCB)

| RP2040-Zero Pin | Signal | Destination (`J1` JST SH 6-Pin / Onboard) |
| :---: | :---: | :--- |
| `3V3` | `+3V3` | `J1` Pin 1 -> `AS5600` (`VDD3V3` + `VDD5V`, 3.3V mode) |
| `GND` | `GND` | `J1` Pin 2 -> `AS5600` `GND` & `SW1` Common |
| `GP4` | `I2C0 SDA` | `J1` Pin 3 (`4.7 kΩ` pull-up `R1` to `+3V3`) -> `AS5600` Pin 6 (`SDA`) |
| `GP5` | `I2C0 SCL` | `J1` Pin 4 (`4.7 kΩ` pull-up `R2` to `+3V3`) -> `AS5600` Pin 7 (`SCL`) |
| `GP6` | `SW_MID` | `J1` Pin 5 / Onboard `SW1` (`Kailh Square Silent`, active-low internal pull-up -> `MS_BTN3`) |

## Build Instructions

From `kbd_firmware/`:
```sh
kb=curcur40_wheel_eval make qmk-init
kb=curcur40_wheel_eval kr=rev1 km=default make qmk-compile
```
Flash the resulting `.uf2` file to the `Waveshare RP2040-Zero` by holding `BOOT` while plugging in USB-C (or double-tapping `RESET`).
