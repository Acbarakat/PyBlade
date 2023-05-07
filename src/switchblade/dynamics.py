# -*- coding: utf-8 -*-
"""
Enablement of Dynamic Keys.

Todo:
    * Interpret error codes to python Exceptions

"""
from abc import ABC

import struct
from PIL import Image

# defines taken from <SwitchBladeSDK_defines.h>
# // definitions for the Dynamic Key display region of the Switchblade
# define SWITCHBLADE_DYNAMIC_KEYS_PER_ROW	5
# define SWITCHBLADE_DYNAMIC_KEYS_ROWS		2
# define SWITCHBLADE_DYNAMIC_KEY_X_SIZE		115
# define SWITCHBLADE_DYNAMIC_KEY_Y_SIZE		115
# define SWITCHBLADE_DK_SIZE_IMAGEDATA		(SWITCHBLADE_DYNAMIC_KEY_X_SIZE * SWITCHBLADE_DYNAMIC_KEY_Y_SIZE * sizeof(WORD))  # noqa: E501
# definitions for the Touchpad display region of the Switchblade
# define SWITCHBLADE_TOUCHPAD_X_SIZE			800
# define SWITCHBLADE_TOUCHPAD_Y_SIZE			480
# define SWITCHBLADE_TOUCHPAD_SIZE_IMAGEDATA (SWITCHBLADE_TOUCHPAD_X_SIZE * SWITCHBLADE_TOUCHPAD_Y_SIZE * sizeof(WORD))  # noqa: E501
# define SWITCHBLADE_DISPLAY_COLOR_DEPTH		16 // 16 bpp
# define MAX_STRING_LENGTH					260 // no paths allowed long than this


class AbstractDK(ABC):
    """Abstract class for Dynamic objects."""

    IMAGE_HEIGHT = 115
    IMAGE_WIDTH = 115

    def __init__(self) -> None:
        self.IMAGE_BUFFER = Image.new("RGB",
                                      (self.IMAGE_WIDTH, self.IMAGE_HEIGHT),
                                      0x00FF00)

    @property
    def IMAGEDATA_SIZE(self) -> tuple:
        return self.IMAGE_HEIGHT * self.IMAGE_WIDTH * struct.calcsize("H")

    def toRGB565(self) -> bytes:
        """Convert image to RGB565 format."""
        data = []

        for pix in list(self.IMAGE_BUFFER.getdata()):
            r = (pix[0] >> 3) & 0x1F
            g = (pix[1] >> 2) & 0x3F
            b = (pix[2] >> 3) & 0x1F

            x = struct.pack('H', (r << 11) + (g << 5) + b)

            data.append(x)

        return b''.join(data)


class DynamicKeyImage(AbstractDK):
    """Image class for Dynamic Keys."""

    KEY_SIZE = (115, 115)


class TouchPadImage(AbstractDK):
    """Image class for the Touch Pad."""

    IMAGE_HEIGHT = 480
    IMAGE_WIDTH = 800
    TOUCH_SIZE = (800, 480)


if __name__ == "__main__":
    from PIL import ImageOps

    DK = DynamicKeyImage()
    DK.IMAGE_BUFFER.show()
    print(DK.IMAGEDATA_SIZE)
    print(len(DK.toRGB565()) == DK.IMAGEDATA_SIZE)

    i = ImageOps.invert(DK.IMAGE_BUFFER)
    i.show()
