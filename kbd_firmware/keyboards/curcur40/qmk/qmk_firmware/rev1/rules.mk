POINTING_DEVICE_ENABLE = yes
POINTING_DEVICE_DRIVER = custom
SPI_DRIVER_REQUIRED    = yes
I2C_DRIVER_REQUIRED    = yes

OPT_DEFS += -DPOINTING_DEVICE_DRIVER_pmw3360
SRC += drivers/sensors/pmw3360.c
SRC += drivers/sensors/pmw33xx_common.c
SRC += curcur40_scroll.c
