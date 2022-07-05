#include <pybind11/pybind11.h>


namespace py = pybind11;


void py_init_module_hello_imgui(py::module& m);


// This builds the native python module (`_hello_imgui`),
//    it will be wrapped in a standard python module `hello_imgui,
PYBIND11_MODULE(_hello_imgui, m)
{
    #ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
    #else
    m.attr("__version__") = "dev";
    #endif

    py_init_module_hello_imgui(m);
}
