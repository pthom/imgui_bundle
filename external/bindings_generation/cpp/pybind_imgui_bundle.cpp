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
void py_init_module_implot_internal(nb::module_& m);
void py_init_module_implot3d(nb::module_& m);
void py_init_module_implot3d_internal(nb::module_& m);
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
void py_init_module_imcoolbar(nb::module_& m);
void py_init_module_nanovg(nb::module_& m);


std::vector<std::string> gAvailableSubmodules;
std::vector<std::string> gDisabledSubmodules;

void _register_submodule(const std::string& submodule_name, bool available = true)
{
    if (available)
        gAvailableSubmodules.push_back(submodule_name);
    else
        gDisabledSubmodules.push_back(submodule_name);
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
#else
    _register_submodule("imgui.test_engine", false);
#endif

#ifndef IMGUI_BUNDLE_DISABLE_HELLO_IMGUI
    _register_submodule("hello_imgui");
    auto module_himgui =  m.def_submodule("hello_imgui");
    py_init_module_hello_imgui(module_himgui);
#else
    _register_submodule("hello_imgui", false);
#endif

#ifdef IMGUI_BUNDLE_WITH_IMPLOT
    _register_submodule("implot");
    auto module_implot =  m.def_submodule("implot");
    py_init_module_implot(module_implot);

    _register_submodule("implot.internal");
    auto module_implot_internal = module_implot.def_submodule("internal");
    py_init_module_implot_internal(module_implot_internal);
#else
    _register_submodule("implot", false);
    _register_submodule("implot.internal", false);
#endif

#ifdef IMGUI_BUNDLE_WITH_IMPLOT3D
    _register_submodule("implot3d");
    auto module_implot3d =  m.def_submodule("implot3d");
    py_init_module_implot3d(module_implot3d);

    _register_submodule("implot3d.internal");
    auto module_implot3d_internal = module_implot3d.def_submodule("internal");
    py_init_module_implot3d_internal(module_implot3d_internal);
#else
    _register_submodule("implot3d", false);
    _register_submodule("implot3d.internal", false);
#endif

    _register_submodule("imgui_color_text_edit");
    auto module_imgui_color_text_edit =  m.def_submodule("imgui_color_text_edit");
    py_init_module_imgui_color_text_edit(module_imgui_color_text_edit);

#ifdef IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR
    _register_submodule("imgui_node_editor");
    auto module_imgui_node_editor =  m.def_submodule("imgui_node_editor");
    py_init_module_imgui_node_editor(module_imgui_node_editor);
#else
    _register_submodule("imgui_node_editor", false);
#endif

    _register_submodule("imgui_knobs");
    auto module_imgui_knobs =  m.def_submodule("imgui_knobs");
    py_init_module_imgui_knobs(module_imgui_knobs);

#ifdef IMGUI_BUNDLE_WITH_IMFILEDIALOG
    _register_submodule("im_file_dialog");
	auto module_im_file_dialog =  m.def_submodule("im_file_dialog");
	py_init_module_im_file_dialog(module_im_file_dialog);
#else
    _register_submodule("im_file_dialog", false);
#endif

    _register_submodule("imspinner");
    auto module_imspinner =  m.def_submodule("imspinner");
    py_init_module_imspinner(module_imspinner);

#ifdef IMGUI_BUNDLE_WITH_IMGUI_MD
    _register_submodule("imgui_md");
    auto module_imgui_md =  m.def_submodule("imgui_md");
    py_init_module_imgui_md(module_imgui_md);
#else
    _register_submodule("imgui_md", false);
#endif

#ifdef IMGUI_BUNDLE_WITH_IMMVISION
    _register_submodule("immvision");
    auto module_immvision =  m.def_submodule("immvision");
    py_init_module_immvision(module_immvision);
#else
    _register_submodule("immvision", false);
#endif

#ifdef IMGUI_BUNDLE_WITH_IMGUIZMO
    _register_submodule("imguizmo");
    auto module_imguizmo = m.def_submodule("imguizmo");
    py_init_module_imguizmo(module_imguizmo);
#else
    _register_submodule("imguizmo", false);
#endif

#ifdef IMGUI_BUNDLE_WITH_IMGUI_TEX_INSPECT
    _register_submodule("imgui_tex_inspect");
    auto module_imgui_tex_inspect = m.def_submodule("imgui_tex_inspect");
    py_init_module_imgui_tex_inspect(module_imgui_tex_inspect);
#else
    _register_submodule("imgui_tex_inspect", false);
#endif

#ifndef IMGUI_BUNDLE_DISABLE_IMMAPP
    _register_submodule("immapp_cpp");
    auto module_immapp_cpp = m.def_submodule("immapp_cpp");
    py_init_module_immapp_cpp(module_immapp_cpp);
#else
    _register_submodule("immapp_cpp", false);
#endif

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
#else
    _register_submodule("nanovg", false);
#endif

#if defined(HELLOIMGUI_USE_GLFW3) && !defined(IMGUI_BUNDLE_DISABLE_HELLO_IMGUI)
    _register_submodule("with_glfw");
#endif

    m.attr("__bundle_submodules_available__") = gAvailableSubmodules;
    m.attr("__bundle_submodules_disabled__") = gDisabledSubmodules;

#ifdef IMGUI_BUNDLE_BUILD_PYODIDE
    m.attr("__bundle_pyodide__") = true;
#else
    m.attr("__bundle_pyodide__") = false;
#endif
}


// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// <litgen_glue_code>  // Autogenerated code below! Do not edit!

// </litgen_glue_code> // Autogenerated code end
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE END !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
