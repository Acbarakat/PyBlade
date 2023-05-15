//
//  SwitchBlade.h
//
//  Copyright© 2012, Razer USA Ltd. All rights reserved.
//
//	This is the main header file for the SwitchBlade SDK. No other
//	include files are required for Switchblade SDK support.
//

#pragma once

#define BOOST_PYTHON_STATIC_LIB
//#define WIN32_LEAN_AND_MEAN

#include <Windows.h>

#include <SwitchBlade.h>

typedef HRESULT(STDMETHODCALLTYPE AppEvent)(RZSBSDK_EVENTTYPETYPE, DWORD, DWORD);
typedef HRESULT(STDMETHODCALLTYPE DKEvent)(RZSBSDK_DKTYPE, RZSBSDK_KEYSTATETYPE);
typedef HRESULT(STDMETHODCALLTYPE GestureEvent)(RZSBSDK_GESTURETYPE, DWORD, WORD, WORD, WORD);
typedef HRESULT(STDMETHODCALLTYPE KeyboardEvent)(UINT uMsg, WPARAM wParam, LPARAM lParam);

#define InvalidDynamicKey(a) (RZSBSDK_DK_NONE > a || a >= RZSBSDK_DK_INVALID)
#define InvalidKeyState(a) (RZSBSDK_KEYSTATE_NONE > a || a >= RZSBSDK_KEYSTATE_INVALID)
