#include "boostedblade.h"

#include <boost/python.hpp>
#include <boost/python/list.hpp>
#include <boost/python/extract.hpp>
#include <boost/python/numpy.hpp>
#include <boost/python/enum.hpp>

#include <boost/lockfree/queue.hpp>

#include <iostream>

using namespace std;
using namespace boost::python;
namespace np = boost::python::numpy;

static boost::lockfree::queue <dk_state> dkq;
static boost::lockfree::queue <app_event> aeq;

struct App
{
public:
    // Constructor
    App() {
        // Set the buffer parameters for SwitchBlade LCD
        memset(&lcd_bp, 0, sizeof(RZSBSDK_BUFFERPARAMS));
        lcd_bp.DataSize = 800 * 480 * sizeof(WORD);
        lcd_bp.PixelType = RGB565;

        memset(&dk_bp, 0, sizeof(RZSBSDK_BUFFERPARAMS));
        dk_bp.DataSize = 115 * 115 * sizeof(WORD);
        dk_bp.PixelType = RGB565;

        std::cout << "created"; 
    };
    // Destructor
    ~App() { 
        while (!dkq.empty()) dkq.consume_all([](dk_state i) {NULL; });
        std::cout << "destoyed";
    };
    void check_callbacks() {
        //dynamic keys
        dk_state dk;
        dkq.pop(dk);
        if (!InvalidDynamicKey(dk.dk) && !InvalidKeyState(dk.dkState)) dkcallback(dk);

        //app event
        app_event ae;
        aeq.pop(ae);
        if (!InvalidAppEvent(ae.rzEvent)) aecallback(ae);
    }
    virtual boost::python::tuple dkcallback(dk_state y) {
        if (InvalidDynamicKey(y.dk) || InvalidKeyState(y.dkState)) return boost::python::make_tuple(0, 0);
        std::cout << "DK_" << std::to_string(y.dk) << " with state" << std::to_string(y.dkState) << std::endl << std::flush;
        return boost::python::make_tuple(y.dk, y.dkState);
    };
    virtual boost::python::tuple aecallback(app_event y) {
        //if (InvalidDynamicKey(y.dk) || InvalidKeyState(y.dkState)) return boost::python::make_tuple(0, 0);
        //std::cout << "DK_" << std::to_string(y.dk) << " with state" << std::to_string(y.dkState) << std::endl << std::flush;
        return boost::python::make_tuple(y.rzEvent, y.dwAppMode, y.dwProcessID);
    };
    HRESULT start() {
        HRESULT hReturn = S_OK;
        hReturn = RzSBStart();
        set_callbacks();
        return hReturn;
    }
    HRESULT stop() { return RzSBStop(); }
    void render_touchpad(std::string data) {
        HRESULT ret = S_OK;

        const unsigned char* g_rgb565 = reinterpret_cast<const unsigned char*> (data.c_str());
        lcd_bp.pData = (BYTE*)g_rgb565;

        ret = RzSBRenderBuffer(RZSBSDK_DISPLAY_WIDGET, &lcd_bp);
        if (!RZSB_SUCCESS(ret))
        {
            std::cout << "Failed to render!";
        }
    }
private:
    RZSBSDK_BUFFERPARAMS lcd_bp;
    RZSBSDK_BUFFERPARAMS dk_bp;
    void set_callbacks() {
        HRESULT hReturn = S_OK;
        // callbacks set here!
        hReturn = RzSBAppEventSetCallback(reinterpret_cast<AppEvent*>(MyAppEventCallback));
        if (!RZSB_SUCCESS(hReturn))
        {
            std::cout << "Failed to app callback!" << std::to_string(hReturn);
        }

        hReturn = RzSBDynamicKeySetCallback(reinterpret_cast<DKEvent*>(MyDynamicKeyCallback));
        if (!RZSB_SUCCESS(hReturn))
        {
            std::cout << "Failed to set key callback!" << std::to_string(hReturn);
        }
        
        hReturn = RzSBGestureSetCallback(reinterpret_cast<GestureEvent*>(MyGestureCallback));
        if (!RZSB_SUCCESS(hReturn))
        {
            std::cout << "Failed to set gesture callback!" << std::to_string(hReturn);
        }

        hReturn = RzSBKeyboardCaptureSetCallback(reinterpret_cast<KeyboardEvent*>(MyKeyboardCallback));
        if (!RZSB_SUCCESS(hReturn))
        {
            std::cout << "Failed to set keyboard callback!" << std::to_string(hReturn);
        }
    }
    static HRESULT STDMETHODCALLTYPE
    MyDynamicKeyCallback(RZSBSDK_DKTYPE dk, RZSBSDK_KEYSTATETYPE dkState)
    {
        dk_state d;
        d.dk = InvalidDynamicKey(dk) ? RZSBSDK_DK_INVALID : dk;
        d.dkState = InvalidKeyState(dkState) ? RZSBSDK_KEYSTATE_INVALID : dkState;

        if (d.dk != RZSBSDK_DK_INVALID && d.dkState != RZSBSDK_KEYSTATE_INVALID) dkq.push(d);

        return S_OK;
    }
    static HRESULT STDMETHODCALLTYPE
    MyAppEventCallback(
        RZSBSDK_EVENTTYPETYPE rzEvent,
        DWORD dwAppMode,
        DWORD dwProcessID
    )
    {
        HRESULT hr = S_OK;

        app_event ae;
        ae.rzEvent = InvalidAppEvent(rzEvent) ? RZSBSDK_EVENT_INVALID : rzEvent;
        ae.dwAppMode = dwAppMode;
        ae.dwProcessID = dwProcessID;

        if (ae.rzEvent != RZSBSDK_EVENT_INVALID) aeq.push(ae);

        return hr;
    }
    static HRESULT STDMETHODCALLTYPE
    MyGestureCallback(
        RZSBSDK_GESTURETYPE gesture,
        DWORD dwParameters,
        WORD wXPos,
        WORD wYPos,
        WORD wZPos
    )
    {
        HRESULT hr = S_OK;

        //hr = CFunctionTestDlg::GestureEventCallback(gesture, dwParameters, wXPos, wYPos, wZPos);

        return hr;
    }
    static HRESULT STDMETHODCALLTYPE
    MyKeyboardCallback(UINT uMsg, WPARAM wParam, LPARAM lParam)
    {
        HRESULT hr = S_OK;

        // hr = CFunctionTestDlg::KeyboardEventCallback(uMsg, wParam, lParam);

        return hr;
    }
};

struct AppWrap : App, public boost::python::wrapper<App> {
    AppWrap() : App() {};
    virtual boost::python::tuple dkcallback(dk_state y) override {
        if (override f = this->get_override("dkcallback")) {
            if (InvalidDynamicKey(y.dk)) return this->get_override("dkcallback")(RZSBSDK_DK_NONE, RZSBSDK_KEYSTATE_NONE);
            if (InvalidKeyState(y.dkState)) return this->get_override("dkcallback")(y.dk, RZSBSDK_KEYSTATE_NONE);
            return this->get_override("dkcallback")(y.dk, y.dkState);
        }
        else {
            return App::dkcallback(y);
        };
    };
    virtual boost::python::tuple aecallback(app_event y) override {
        if (override f = this->get_override("aecallback")) {
            if (InvalidAppEvent(y.rzEvent)) return this->get_override("aecallback")(RZSBSDK_EVENT_NONE, y.dwAppMode, y.dwProcessID);
            return this->get_override("aecallback")(y.rzEvent, y.dwAppMode, y.dwProcessID);
        }
        else {
            return App::aecallback(y);
        };
    };
};

BOOST_PYTHON_MODULE(boostedblade)
{
    Py_Initialize();
    np::initialize();

    enum_<RZSBSDK_DKTYPE>("DKTYPE")
        .value("NONE", RZSBSDK_DKTYPE::RZSBSDK_DK_NONE)
        .value("DK_1", RZSBSDK_DKTYPE::RZSBSDK_DK_1)
        .value("DK_2", RZSBSDK_DKTYPE::RZSBSDK_DK_2)
        .value("DK_3", RZSBSDK_DKTYPE::RZSBSDK_DK_3)
        .value("DK_4", RZSBSDK_DKTYPE::RZSBSDK_DK_4)
        .value("DK_5", RZSBSDK_DKTYPE::RZSBSDK_DK_5)
        .value("DK_6", RZSBSDK_DKTYPE::RZSBSDK_DK_6)
        .value("DK_7", RZSBSDK_DKTYPE::RZSBSDK_DK_7)
        .value("DK_8", RZSBSDK_DKTYPE::RZSBSDK_DK_8)
        .value("DK_9", RZSBSDK_DKTYPE::RZSBSDK_DK_9)
        .value("DK_10", RZSBSDK_DKTYPE::RZSBSDK_DK_10)
        .export_values()
        ;

    enum_<RZSBSDK_KEYSTATETYPE>("KEYSTATE")
        .value("NONE", RZSBSDK_KEYSTATETYPE::RZSBSDK_KEYSTATE_NONE)
        .value("UP", RZSBSDK_KEYSTATETYPE::RZSBSDK_KEYSTATE_UP)
        .value("DOWN", RZSBSDK_KEYSTATETYPE::RZSBSDK_KEYSTATE_DOWN)
        .value("HOLD", RZSBSDK_KEYSTATETYPE::RZSBSDK_KEYSTATE_HOLD)
        .export_values()
        ;

    enum_<RZSBSDK_EVENTTYPETYPE>("EVENTTYPE")
        .value("NONE", RZSBSDK_EVENTTYPETYPE::RZSBSDK_EVENT_NONE)
        .value("ACTIVATED", RZSBSDK_EVENTTYPETYPE::RZSBSDK_EVENT_ACTIVATED)
        .value("DEACTIVATED", RZSBSDK_EVENTTYPETYPE::RZSBSDK_EVENT_DEACTIVATED)
        .value("CLOSE", RZSBSDK_EVENTTYPETYPE::RZSBSDK_EVENT_CLOSE)
        .value("EXIT", RZSBSDK_EVENTTYPETYPE::RZSBSDK_EVENT_EXIT)
        .export_values()
        ;

    class_<AppWrap, boost::noncopyable>("App", init<>())
        .def("start", &AppWrap::start)
        .def("stop", &AppWrap::stop)
        .def("render_touchpad", &AppWrap::render_touchpad)
        .def("check_callbacks", &AppWrap::check_callbacks)
        .def("dkcallback", &AppWrap::dkcallback)
        ;
};