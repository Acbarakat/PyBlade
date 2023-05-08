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
import os
import ctypes
import random
from time import sleep

import numpy as np
from PIL import Image

from switchblade import SwitchBladeApp, BufferObj, S_OK
from switchblade.dynamics import DynamicKeyImage, TouchPadImage


DK = DynamicKeyImage()
TP = TouchPadImage()

DK_BFO = BufferObj(0, DK.IMAGEDATA_SIZE, DK.toRGB565())
TP_BFO = BufferObj(0, TP.IMAGEDATA_SIZE, TP.toRGB565())


def main() -> None:
    """Run the simple pyBlade app."""
    fpath = os.path.join(os.path.dirname(__file__),
                         "assets",
                         "tonberry_115.png")
    fpath = os.path.abspath(fpath)

    with SwitchBladeApp() as sba:
        sba._SwitchBladeDLL.RzSBRenderBuffer(sba.TOUCHPAD,
                                             ctypes.byref(TP_BFO))

        r = sba._SwitchBladeDLL.RzSBSetImageDynamicKey(1, 0, fpath)
        assert r == S_OK, "Could not load image to DK_1"

        DK.load_file(fpath)
        DK_BFO.pData = DK.toRGB565()
        sba._SwitchBladeDLL.RzSBRenderBuffer(sba.DK_6, ctypes.byref(DK_BFO))

        for i in range(10):
            if i in (0, 5):
                continue
            DK._buffer = Image.new("RGB", DK.SIZE,
                                   f"#{random.randrange(0x1000000):06x}")
            DK._buffer = np.array(DK._buffer)
            DK_BFO.pData = DK.toRGB565()
            sba._SwitchBladeDLL.RzSBRenderBuffer(getattr(sba, f"DK_{i + 1}"),
                                                 ctypes.byref(DK_BFO))
        sleep(30)


if __name__ == "__main__":
    main()
