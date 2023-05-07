# -*- coding: utf-8 -*-
"""
Simple pyblade app that runs for 30 seconds.

It assigns random colors to dynamic keys,
and setting the LCD screen to green.

Todo:
    * Dynamic key press events
    * Dynamic key up and key down images
    * LCD touch events
    * LCD gesture events

"""
import ctypes
import random
from time import sleep

from PIL import Image

from switchblade import SwitchBladeApp, BufferObj
from switchblade.dynamics import DynamicKeyImage, TouchPadImage


DK = DynamicKeyImage()
TP = TouchPadImage()

DK_BFO = BufferObj(0, DK.IMAGEDATA_SIZE, DK.toRGB565())
TP_BFO = BufferObj(0, TP.IMAGEDATA_SIZE, TP.toRGB565())


def main():
    """Run the simple pyBlade app."""
    with SwitchBladeApp() as sba:
        sba._SwitchBladeDLL.RzSBRenderBuffer(sba.SCREEN, ctypes.byref(TP_BFO))

        for i in range(10):
            DK.IMAGE_BUFFER = Image.new("RGB", DK.KEY_SIZE,
                                        f"#{random.randrange(0x1000000):06x}")
            DK_BFO.pData = DK.toRGB565()
            sba._SwitchBladeDLL.RzSBRenderBuffer(getattr(sba, f"DK_{i + 1}"),
                                                 ctypes.byref(DK_BFO))
        sleep(30)


if __name__ == "__main__":
    main()
