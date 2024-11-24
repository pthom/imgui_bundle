// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include <string>
#include <vector>

#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>

namespace nb = nanobind;

void py_init_module_hello_imgui(nb::module_& m);
void py_init_module_imgui_main(nb::module_& m);
void py_init_module_imgui_internal(nb::module_& m);
void py_init_module_imgui_test_engine(nb::module_& m);
void py_init_module_implot(nb::module_& m);
void py_init_module_imgui_color_text_edit(nb::module_& m);
void py_init_module_imgui_node_editor(nb::module_& m);
void py_init_module_imgui_knobs(nb::module_& m);
void py_init_module_im_file_dialog(nb::module_& m);
void py_init_module_imspinner(nb::module_& m);
void py_init_module_imgui_md(nb::module_& m);
void py_init_module_immvision(nb::module_& m);
void py_init_module_imgui_backends(nb::module_& m);
void py_init_module_imguizmo(nb::module_& m);
void py_init_module_imgui_tex_inspect(nb::module_& m);
void py_init_module_immapp_cpp(nb::module_& m);
void py_init_module_imgui_toggle(nb::module_& m);
void py_init_module_portable_file_dialogs(nb::module_& m);
void py_init_module_imgui_command_palette(nb::module_& m);
void py_init_module_implot_internal(nb::module_& m);
void py_init_module_imcoolbar(nb::module_& m);
void py_init_module_nanovg(nb::module_& m);


std::vector<std::string> gAllSubmodules;

void _register_submodule(const std::string& submodule_name)
{
    gAllSubmodules.push_back(submodule_name);
}


void py_init_module_imgui_bundle(nb::module_& m)
{
    // Disable leak warnings (we may have a few, to be fixed later)
    nb::set_leak_warnings(false);

    m.def("compilation_time", []() {
        return std::string("imgui_bundle, compiled on ") + __DATE__ + " at " + __TIME__;
    });

    // imgui and its submodules
    _register_submodule("imgui");
    auto module_imgui =  m.def_submodule("imgui");
    py_init_module_imgui_main(module_imgui);

    // Submodule imgui.internal
    _register_submodule("imgui.internal");
    auto module_imgui_internal =  module_imgui.def_submodule("internal");
    py_init_module_imgui_internal(module_imgui_internal);

    // Submodule imgui.backends
    _register_submodule("imgui.backends");
    auto module_imgui_backends =  module_imgui.def_submodule("backends");
    py_init_module_imgui_backends(module_imgui_backends);

#ifdef HELLOIMGUI_WITH_TEST_ENGINE
    // Submodule imgui.test_engine
    _register_submodule("imgui.test_engine");
    auto module_imgui_test_engine =  module_imgui.def_submodule("test_engine");
    py_init_module_imgui_test_engine(module_imgui_test_engine);
#endif

    _register_submodule("hello_imgui");
    auto module_himgui =  m.def_submodule("hello_imgui");
    py_init_module_hello_imgui(module_himgui);

#ifdef IMGUI_BUNDLE_WITH_IMPLOT
    _register_submodule("implot");
    auto module_implot =  m.def_submodule("implot");
    py_init_module_implot(module_implot);

    _register_submodule("implot.internal");
    auto module_implot_internal = module_implot.def_submodule("internal");
    py_init_module_implot_internal(module_implot_internal);
#endif

    _register_submodule("imgui_color_text_edit");
    auto module_imgui_color_text_edit =  m.def_submodule("imgui_color_text_edit");
    py_init_module_imgui_color_text_edit(module_imgui_color_text_edit);

#ifdef IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR
    _register_submodule("imgui_node_editor");
    auto module_imgui_node_editor =  m.def_submodule("imgui_node_editor");
    py_init_module_imgui_node_editor(module_imgui_node_editor);
#endif

    _register_submodule("imgui_knobs");
    auto module_imgui_knobs =  m.def_submodule("imgui_knobs");
    py_init_module_imgui_knobs(module_imgui_knobs);

#ifdef IMGUI_BUNDLE_WITH_IMFILEDIALOG
    _register_submodule("im_file_dialog");
	auto module_im_file_dialog =  m.def_submodule("im_file_dialog");
	py_init_module_im_file_dialog(module_im_file_dialog);
#endif

    _register_submodule("imspinner");
    auto module_imspinner =  m.def_submodule("imspinner");
    py_init_module_imspinner(module_imspinner);

    _register_submodule("imgui_md");
    auto module_imgui_md =  m.def_submodule("imgui_md");
    py_init_module_imgui_md(module_imgui_md);

#ifdef IMGUI_BUNDLE_WITH_IMMVISION
    _register_submodule("immvision");
    auto module_immvision =  m.def_submodule("immvision");
    py_init_module_immvision(module_immvision);
#endif

#ifdef IMGUI_BUNDLE_WITH_IMGUIZMO
    _register_submodule("imguizmo");
    auto module_imguizmo = m.def_submodule("imguizmo");
    py_init_module_imguizmo(module_imguizmo);
#endif

#ifdef IMGUI_BUNDLE_WITH_IMGUI_TEX_INSPECT
    _register_submodule("imgui_tex_inspect");
    auto module_imgui_tex_inspect = m.def_submodule("imgui_tex_inspect");
    py_init_module_imgui_tex_inspect(module_imgui_tex_inspect);
#endif

    _register_submodule("immapp_cpp");
    auto module_immapp_cpp = m.def_submodule("immapp_cpp");
    py_init_module_immapp_cpp(module_immapp_cpp);

    _register_submodule("imgui_toggle");
    auto module_imgui_toggle = m.def_submodule("imgui_toggle");
    py_init_module_imgui_toggle(module_imgui_toggle);

    _register_submodule("portable_file_dialogs");
    auto module_portable_file_dialogs = m.def_submodule("portable_file_dialogs");
    py_init_module_portable_file_dialogs(module_portable_file_dialogs);

    _register_submodule("imgui_command_palette");
    auto module_imgui_command_palette = m.def_submodule("imgui_command_palette");
    py_init_module_imgui_command_palette(module_imgui_command_palette);

    _register_submodule("imcoolbar");
    auto module_imcooolbar = m.def_submodule("im_cool_bar");
    py_init_module_imcoolbar(module_imcooolbar);

#ifdef IMGUI_BUNDLE_WITH_NANOVG
    _register_submodule("nanovg");
    auto module_nanovg = m.def_submodule("nanovg");
    py_init_module_nanovg(module_nanovg);
#endif

#ifdef HELLOIMGUI_USE_GLFW3
    _register_submodule("with_glfw");
#endif

    m.attr("__bundle_submodules__") = gAllSubmodules;
}


// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// <litgen_glue_code>  // Autogenerated code below! Do not edit!

// </litgen_glue_code> // Autogenerated code end
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE END !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
