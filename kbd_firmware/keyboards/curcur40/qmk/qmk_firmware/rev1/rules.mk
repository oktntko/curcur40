POINTING_DEVICE_ENABLE = yes
POINTING_DEVICE_DRIVER = pmw3360
ENCODER_MAP_ENABLE     = yes

SRC     += curcur40_scroll.c
LDFLAGS += -Wl,--wrap=pmw33xx_get_cpi -Wl,--wrap=pmw33xx_set_cpi
