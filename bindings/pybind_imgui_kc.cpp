#include <pybind11/pybind11.h>
namespace py = pybind11;


struct ImVec2
{
    float                                   x, y;
    ImVec2(float _x, float _y)    : x(_x), y(_y) { }
};


void py_init_module_imgui_main(py::module& m)
{
    m.def("foo",
          [](const ImVec2 & size = ImVec2(0, 0)) -> bool
          {
              return true;
          });
}
