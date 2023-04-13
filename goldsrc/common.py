"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""


# Commmon display resolutions up to 4K
DISPLAY_RESOLUTIONS = {
    "16:9": (
        (768, 432),
        (1024, 576),
        (1280, 720),
        (1366, 768),
        (1600, 900),
        (1920, 1080),
        (2560, 1440),
        (3840, 2160)
    ),
    "4:3": (
        (768, 576),
        (1024, 768),
        (1280, 960),
        (1366, 1024),
        (1600, 1200),
        (1920, 1440),
        (2560, 1920),
        (3840, 2880)
    )
}

# Common refresh rates of monitors
FPS_CAPS = (
    25,
    30,
    50,
    60,
    75,
    90,
    120,
    144,
    165,
    240,
    360
)