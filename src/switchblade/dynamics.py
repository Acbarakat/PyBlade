# -*- coding: utf-8 -*-
"""
Enablement of Dynamic Keys.

Todo:
    * Interpret error codes to python Exceptions

"""
from abc import ABC

import struct
import cv2
import numpy as np
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
    SIZE = (115, 115)

    def __init__(self) -> None:
        self._buffer = Image.new("RGB",
                                 (self.IMAGE_WIDTH, self.IMAGE_HEIGHT),
                                 0x00FF00)
        self._buffer = np.array(self._buffer)

    @classmethod
    @property
    def IMAGEDATA_SIZE(cls) -> tuple:
        return cls.IMAGE_HEIGHT * cls.IMAGE_WIDTH * struct.calcsize("H")

    def load_file(self, fpath) -> None:
        im = Image.open(fpath).resize(self.SIZE)
        self._buffer = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

    def show(self) -> None:
        cv2.imshow("image", self._buffer)
        cv2.waitKey()

    def _fixImage(self):
        return self._buffer

    def toRGB565(self) -> bytes:
        """Convert image to RGB565 format."""
        buffer = self._fixImage()
        im = cv2.cvtColor(buffer, cv2.COLOR_BGR2BGR565)
        assert im.nbytes == self.IMAGEDATA_SIZE, f"Image is {im.nbytes} bytes when it should be {self.IMAGEDATA_SIZE}"  # noqa: E501
        return im.tobytes()


class DynamicKeyImage(AbstractDK):
    """Image class for Dynamic Keys."""
    def _fixImage(self):
        """Render method for dynamic keys is at a diagonal/two-triangle."""
        i = 0
        for row in self._buffer:
            if i > 0:
                self._buffer[i] = np.roll(row, i * 3)
            i += 1
        return self._buffer


class TouchPadImage(AbstractDK):
    """Image class for the Touch Pad."""

    IMAGE_HEIGHT = 480
    IMAGE_WIDTH = 800
    SIZE = (800, 480)


if __name__ == "__main__":
    import os

    DK = DynamicKeyImage()
    DK.show()

    fpath = os.path.join(os.path.dirname(__file__),
                         "..",
                         "assets",
                         "tonberry_115.png")
    fpath = os.path.abspath(fpath)
    DK.load_file(fpath)
    DK.show()
