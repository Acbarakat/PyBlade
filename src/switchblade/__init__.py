# -*- coding: utf-8 -*-
"""
Objects used by python to work with RzSwitchbladeSDK.

Todo:
    * Interpret error codes to python Exceptions

"""
import os
import sys
import ctypes

os.add_dll_directory("D:\\cpp\\boost_1_82_0\\stage\\lib")
os.add_dll_directory("C:\\ProgramData\\Razer\\SwitchBlade\\SDK\\")

try:
    from .boostedblade import App, DKTYPE, KEYSTATE, EVENTTYPE
except ImportError:
    from boostedblade import App, DKTYPE, KEYSTATE, EVENTTYPE

if (is_64bits := sys.maxsize > 2**32):
    raise RuntimeError("This cannot be run in 64-bit python.")

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


class SwitchBladeApp(App):
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

    def __init__(self) -> None:
        super(SwitchBladeApp, self).__init__()
        self.active = True

    def __repr__(self) -> str:
        return "<SwitchBladeApp>"

    def __enter__(self) -> object:
        hresult = self.start()
        print(hresult)
        if hresult != S_OK:
            raise RuntimeError()
        return self

    def __exit__(self, type, value, traceback) -> int:
        hresult = self.stop()
        # print(hresult)
        if hresult != S_OK:
            raise RuntimeError()
        return hresult

    def dkcallback(self, key, state):
        # if key == DKTYPE.NONE or state == KEYSTATE.NONE:
        #    return (key, state)

        print(key, state)
        return (key, state)

    def aecallback(self, event, appMode, processId):
        # if event == EVENTTYPE.NONE:
        #    return (event, appMode, processId)
        if event == EVENTTYPE.DEACTIVATED:
            self.active = False
        print(event, appMode, processId)
        return (event, appMode, processId)
