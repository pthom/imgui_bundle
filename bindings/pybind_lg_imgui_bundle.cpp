#include <pybind11/pybind11.h>

namespace py = pybind11;

void py_init_module_hello_imgui(py::module& m);
void py_init_module_imgui_main(py::module& m);
void py_init_module_imgui_internal(py::module& m);
void py_init_module_implot(py::module& m);
void py_init_module_imgui_color_text_edit(py::module& m);
void py_init_module_imgui_node_editor(py::module& m);
void py_init_module_imgui_knobs(py::module& m);
void py_init_module_im_file_dialog(py::module& m);

void py_init_module_lg_imgui_bundle(py::module& m)
{
    auto module_imgui =  m.def_submodule("imgui");
    py_init_module_imgui_main(module_imgui);

    auto module_imgui_internal =  m.def_submodule("imgui_internal");
    py_init_module_imgui_internal(module_imgui_internal);

    auto module_himgui =  m.def_submodule("hello_imgui");
    py_init_module_hello_imgui(module_himgui);

    auto module_implot =  m.def_submodule("implot");
    py_init_module_implot(module_implot);

    auto module_imgui_color_text_edit =  m.def_submodule("imgui_color_text_edit");
    py_init_module_imgui_color_text_edit(module_imgui_color_text_edit);

    auto module_imgui_node_editor =  m.def_submodule("imgui_node_editor");
    py_init_module_imgui_node_editor(module_imgui_node_editor);

    auto module_imgui_knobs =  m.def_submodule("imgui_knobs");
    py_init_module_imgui_knobs(module_imgui_knobs);

	auto module_im_file_dialog =  m.def_submodule("im_file_dialog");
	py_init_module_im_file_dialog(module_im_file_dialog);
}
