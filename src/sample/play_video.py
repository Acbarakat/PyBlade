import sys
import os
import ctypes

import cv2

# WA: Relative import not workign correctly
sys.path.append(os.path.dirname(__file__) + os.sep + "..")

from switchblade import BufferObj, SwitchBladeApp  # noqa: E402
from switchblade.dynamics import TouchPadImage  # noqa: E402


def main() -> None:
    """Load and play video on the touchscreen.."""
    fpath = os.path.join(os.path.dirname(__file__),
                         "..",
                         "assets",
                         "alb_lightfx2201.mp4")
    fpath = os.path.abspath(fpath)
    assert os.path.exists(fpath), f"Cannot find {fpath}"

    TP = TouchPadImage()
    TP_BFO = BufferObj(0, TP.IMAGEDATA_SIZE, TP.toRGB565())

    cap = cv2.VideoCapture(fpath)
    # Check if camera opened successfully
    assert cap.isOpened(), "Error opening video file"

    with SwitchBladeApp() as sba:
        # Read until video is completed
        while cap.isOpened():
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret:
                # resize image
                frame = cv2.resize(frame, TP.SIZE,
                                   interpolation=cv2.INTER_AREA)

                TP._buffer = cv2.cvtColor(frame, cv2.COLOR_BGR2BGR565)

                TP_BFO.pData = TP._buffer.tobytes()
                # assert TP._buffer .nbytes == TP.IMAGEDATA_SIZE, f"Image is {TP._buffer .nbytes} bytes when it should be {TP.IMAGEDATA_SIZE}"  # noqa: E501
                sba._SwitchBladeDLL.RzSBRenderBuffer(sba.TOUCHPAD,
                                                     ctypes.byref(TP_BFO))

                # Display the resulting frame
                # TODO: Cannot show window and render to touchpad concurrently
                # cv2.imshow('Frame', frame)

                # Press Q on keyboard to exit
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
