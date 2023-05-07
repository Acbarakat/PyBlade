# -*- coding: utf-8 -*-
"""
Objects used by python to work with RzSwitchbladeSDK.

Todo:
    * Interpret error codes to python Exceptions

"""
import ctypes

SWITCHBLADE_DLL_PATH = "C:\\ProgramData\\Razer\\SwitchBlade\\SDK\\RzSwitchbladeSDK2.dll"  # noqa: E501
KEYBOARD_DLL_PATH = "C:\\Program Files (x86)\\Razer\\SwitchBlade\\RzAPISwitchBlade.dll"  # noqa: E501

S_OK = 0
E_FAIL = -2147467259  # 0x80004005L

# defines taken from <SwitchBladeSDK_errors.h>
# define RZSB_OK                               S_OK
# define RZSB_UNSUCCESSFUL                     E_FAIL
# define RZSB_INVALID_PARAMETER                E_INVALIDARG
# // points to data that is either not fully readable or writable
# define RZSB_INVALID_POINTER                  E_POINTER
# define RZSB_ABORTED                          E_ABORT
# define RZSB_NO_INTERFACE                     E_NOINTERFACE
# define RZSB_NOT_IMPLEMENTED                  E_NOTIMPL
# define RZSB_FILE_NOT_FOUND                   ERROR_FILE_NOT_FOUND


class BufferObj(ctypes.Structure):
    """
    A python version of '_RZSBSDK_BUFFERPARAMS'.

    <SwitchBladeSDK_types.h>
    enum PIXEL_TYPE		{ RGB565 = 0 };
    typedef struct _RZSBSDK_BUFFERPARAMS
    {
        PIXEL_TYPE	PixelType;
        DWORD		DataSize;	// Buffer size
        BYTE		*pData;
    } RZSBSDK_BUFFERPARAMS, *PRZSBSDK_BUFFERPARAMS;
    <
    """

    _fields_ = [("PixelType", ctypes.c_uint),
                ("DataSize", ctypes.c_ulong),  # DWORD
                ("pData", ctypes.c_char_p)]


class SwitchBladeApp(object):
    """Python object to run and reference the app."""

    TOUCHPAD = (1 << 16) | 0
    DK_1 = (1 << 16) | 1
    DK_2 = (1 << 16) | 2
    DK_3 = (1 << 16) | 3
    DK_4 = (1 << 16) | 4
    DK_5 = (1 << 16) | 5
    DK_6 = (1 << 16) | 6
    DK_7 = (1 << 16) | 7
    DK_8 = (1 << 16) | 8
    DK_9 = (1 << 16) | 9
    DK_10 = (1 << 16) | 10

    def __init__(self):
        self._SwitchBladeDLL = ctypes.CDLL(SWITCHBLADE_DLL_PATH)
        self._SwitchBladeDLL.RzSBStart.restype = ctypes.HRESULT
        self._SwitchBladeDLL.RzSBStop.restype = ctypes.HRESULT
        self._SwitchBladeDLL.RzSBRenderBuffer.restype = ctypes.HRESULT
        self._SwitchBladeDLL.RzSBRenderBuffer.argtype = [ctypes.c_int,
                                                         BufferObj]

    def __repr__(self):
        return "<SwitchBladeApp (%s)>" % self._SwitchBladeDLL

    def __enter__(self):
        hresult = self._SwitchBladeDLL.RzSBStart()
        # print(hresult)
        if hresult != S_OK:
            raise RuntimeError()
        return self

    def __exit__(self, type, value, traceback):
        hresult = self._SwitchBladeDLL.RzSBStop()
        # print(hresult)
        if hresult != S_OK:
            raise RuntimeError()
        return hresult
