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

static HRESULT STDMETHODCALLTYPE MyAppEventCallback(
    RZSBSDK_EVENTTYPETYPE rzEvent,
    DWORD dwAppMode,
    DWORD dwProcessID
)
{
    HRESULT hr = S_OK;

    //hr = CFunctionTestDlg::ApplicationEventCallback(rzEvent, dwAppMode, dwProcessID);
    std::cout << "app event" << std::flush;

    return hr;
}

struct dk_state {
    RZSBSDK_DKTYPE dk;
    RZSBSDK_KEYSTATETYPE state;
};

static boost::lockfree::queue <dk_state> dkq;

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
        dk_state y;
        dkq.pop(y);
        dkcallback(y);
    }
    virtual boost::python::tuple dkcallback(dk_state y) {
        if (InvalidDynamicKey(y.dk) || InvalidKeyState(y.state)) return boost::python::make_tuple(0, 0);
        std::cout << "DK_" << std::to_string(y.dk) << " with state" << std::to_string(y.state) << std::endl << std::flush;
        return boost::python::make_tuple(y.dk, y.state);
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
        
        //hReturn = RzSBGestureSetCallback(reinterpret_cast<GestureEvent*>(MyGestureCallback));
        //hReturn = RzSBKeyboardCaptureSetCallback(reinterpret_cast<KeyboardEvent*>(MyKeyboardCallback));
    }
    static HRESULT STDMETHODCALLTYPE
    MyDynamicKeyCallback(RZSBSDK_DKTYPE dk, RZSBSDK_KEYSTATETYPE dkState)
    {
        HRESULT hr = S_OK;

        dk_state x;
        x.dk = InvalidDynamicKey(dk) ? RZSBSDK_DK_INVALID : dk;
        x.state = InvalidKeyState(dkState) ? RZSBSDK_KEYSTATE_INVALID : dkState;

        dkq.push(x);

        return hr;
    }
};

struct AppWrap : App, public boost::python::wrapper<App> {
    AppWrap() : App() {};
    virtual boost::python::tuple dkcallback(dk_state y) override {
        if (override f = this->get_override("dkcallback")) {
            if (InvalidDynamicKey(y.dk)) return this->get_override("dkcallback")(RZSBSDK_DK_NONE, RZSBSDK_KEYSTATE_NONE);
            if (InvalidKeyState(y.state)) return this->get_override("dkcallback")(y.dk, RZSBSDK_KEYSTATE_NONE);
            return this->get_override("dkcallback")(y.dk, y.state);
        }
        else {
            return App::dkcallback(y);
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
        .value("Up", RZSBSDK_KEYSTATETYPE::RZSBSDK_KEYSTATE_UP)
        .value("Down", RZSBSDK_KEYSTATETYPE::RZSBSDK_KEYSTATE_DOWN)
        .value("Hold", RZSBSDK_KEYSTATETYPE::RZSBSDK_KEYSTATE_HOLD)
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