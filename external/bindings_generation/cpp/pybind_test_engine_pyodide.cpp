// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
//
// The test engine's coroutine in Pyodide.
//
// The engine runs its tests in a coroutine, implemented with a std::thread by default. Pyodide has no threads:
// this implementation forwards ImGuiTestCoroutineInterface to imgui_bundle._pyodide_test_engine_coroutine,
// where the coroutine is a Pyodide task, and switching to it or back is a JSPI stack switch (pyodide.ffi.run_sync).
// The coroutine's stack holds Python frames (the test functions), so only a switch of the whole stack can work.

#include <nanobind/nanobind.h>

#include "imgui_test_engine/imgui_te_coroutine.h"
#include "hello_imgui_test_engine_integration/test_engine_integration.h"

namespace nb = nanobind;


namespace
{
    nb::object CoroutineModule()
    {
        return nb::module_::import_("imgui_bundle._pyodide_test_engine_coroutine");
    }

    ImGuiTestCoroutineHandle Create(ImGuiTestCoroutineMainFunc* func, const char* name, void* data)
    {
        nb::object main_func = nb::cpp_function([func, data]() { func(data); });
        nb::object coroutine = CoroutineModule().attr("create")(main_func, name);
        return coroutine.release().ptr();  // Destroy() drops this reference
    }

    void Destroy(ImGuiTestCoroutineHandle handle)
    {
        nb::steal((PyObject*)handle);
    }

    bool Run(ImGuiTestCoroutineHandle handle)
    {
        return nb::cast<bool>(CoroutineModule().attr("run")(nb::handle((PyObject*)handle)));
    }

    void Yield()
    {
        CoroutineModule().attr("yield_")();
    }
}


void py_init_test_engine_pyodide_coroutine()
{
    static ImGuiTestCoroutineInterface coroutineInterface = { Create, Destroy, Run, Yield };
    HelloImGui::TestEngineCallbacks::SetCoroutineInterface(&coroutineInterface);
}
