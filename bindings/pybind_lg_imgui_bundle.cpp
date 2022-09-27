#include <pybind11/pybind11.h>

namespace py = pybind11;

void py_init_module_hello_imgui(py::module& m);
void py_init_module_imgui(py::module& m);
void py_init_module_implot(py::module& m);

void py_init_module_lg_imgui_bundle(py::module& m)
{
    auto module_imgui =  m.def_submodule("imgui");
    py_init_module_imgui(module_imgui);

    auto module_himgui =  m.def_submodule("hello_imgui");
    py_init_module_hello_imgui(module_himgui);

    auto module_implot =  m.def_submodule("implot");
    py_init_module_implot(module_implot);
}
