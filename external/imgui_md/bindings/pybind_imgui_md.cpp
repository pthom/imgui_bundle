// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/array.h>
#include <nanobind/stl/optional.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/function.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/stl/optional.h>
#include <nanobind/make_iterator.h>
#include <nanobind/ndarray.h>

#include "imgui_md_wrapper/imgui_md_wrapper.h"
namespace nb = nanobind;


// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// <litgen_glue_code>  // Autogenerated code below! Do not edit!

// </litgen_glue_code> // Autogenerated code end
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE END !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



void py_init_module_imgui_md(nb::module_& m)
{
    using namespace ImGuiMd;
    // !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    // <litgen_pydef> // Autogenerated code below! Do not edit!
    ////////////////////    <generated_from:imgui_md_wrapper.h>    ////////////////////
    auto pyClassMarkdownFontOptions =
        nb::class_<ImGuiMd::MarkdownFontOptions>
            (m, "MarkdownFontOptions", "")
        .def(nb::init<>()) // implicit default constructor
        .def_rw("font_base_path", &ImGuiMd::MarkdownFontOptions::fontBasePath, "")
        .def_rw("max_header_level", &ImGuiMd::MarkdownFontOptions::maxHeaderLevel, "")
        .def_rw("size_diff_between_levels", &ImGuiMd::MarkdownFontOptions::sizeDiffBetweenLevels, "")
        .def_rw("regular_size", &ImGuiMd::MarkdownFontOptions::regularSize, "")
        ;


    auto pyClassMarkdownImage =
        nb::class_<ImGuiMd::MarkdownImage>
            (m, "MarkdownImage", "")
        .def(nb::init<>()) // implicit default constructor
        .def_rw("texture_id", &ImGuiMd::MarkdownImage::texture_id, "")
        .def_rw("size", &ImGuiMd::MarkdownImage::size, "")
        .def_rw("uv0", &ImGuiMd::MarkdownImage::uv0, "")
        .def_rw("uv1", &ImGuiMd::MarkdownImage::uv1, "")
        .def_rw("col_tint", &ImGuiMd::MarkdownImage::col_tint, "")
        .def_rw("col_border", &ImGuiMd::MarkdownImage::col_border, "")
        ;


    auto pyClassSizedFont =
        nb::class_<ImGuiMd::SizedFont>
            (m, "SizedFont", " Note: Since v1.92, Fonts can be displayed at any size:\n in order to display a font at a given size, we need to call\n   ImGui::PushFont(font, size) (or call separately ImGui::PushFontSize)")
        .def(nb::init<>()) // implicit default constructor
        .def_rw("font", &ImGuiMd::SizedFont::font, "")
        .def_rw("size", &ImGuiMd::SizedFont::size, "")
        ;


    m.def("on_image_default",
        ImGuiMd::OnImage_Default, nb::arg("image_path"));

    m.def("on_open_link_default",
        ImGuiMd::OnOpenLink_Default, nb::arg("url"));


    auto pyClassMarkdownCallbacks =
        nb::class_<ImGuiMd::MarkdownCallbacks>
            (m, "MarkdownCallbacks", "")
        .def(nb::init<>()) // implicit default constructor
        .def_rw("on_open_link", &ImGuiMd::MarkdownCallbacks::OnOpenLink, "The default version will open the link in a browser iif it starts with \"http\"")
        .def_rw("on_image", &ImGuiMd::MarkdownCallbacks::OnImage, "The default version will load the image as a cached texture and display it")
        .def_rw("on_html_div", &ImGuiMd::MarkdownCallbacks::OnHtmlDiv, " OnHtmlDiv does nothing by default, by you could write:\n     In  C++:\n        markdownOptions.callbacks.onHtmlDiv = [](const std::string& divClass, bool openingDiv)\n        {\n            if (divClass == \"red\")\n            {\n                if (openingDiv)\n                    ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(255, 0, 0, 255));\n                else\n                    ImGui::PopStyleColor();\n            }\n        };\n     In  Python:\n        def on_html_div(div_class: str, opening_div: bool) -> None:\n            if div_class == 'red':\n                if opening_div:\n                    imgui.push_style_color(imgui.Col_.text.value, imgui.ImColor(255, 0, 0, 255).value)\n                else:\n                    imgui.pop_style_color()\n        md_options = imgui_md.MarkdownOptions()\n        md_options.callbacks.on_html_div = on_html_div\n        immapp.run(\n            gui_function=gui, with_markdown_options=md_options #, more options here\n        )")
        ;


    auto pyClassMarkdownOptions =
        nb::class_<ImGuiMd::MarkdownOptions>
            (m, "MarkdownOptions", "")
        .def(nb::init<>()) // implicit default constructor
        .def_rw("font_options", &ImGuiMd::MarkdownOptions::fontOptions, "")
        .def_rw("callbacks", &ImGuiMd::MarkdownOptions::callbacks, "")
        ;


    m.def("initialize_markdown",
        [](const std::optional<const ImGuiMd::MarkdownOptions> & options = std::nullopt)
        {
            auto InitializeMarkdown_adapt_mutable_param_with_default_value = [](const std::optional<const ImGuiMd::MarkdownOptions> & options = std::nullopt)
            {

                const ImGuiMd::MarkdownOptions& options_or_default = [&]() -> const ImGuiMd::MarkdownOptions {
                    if (options.has_value())
                        return options.value();
                    else
                        return ImGuiMd::MarkdownOptions();
                }();

                ImGuiMd::InitializeMarkdown(options_or_default);
            };

            InitializeMarkdown_adapt_mutable_param_with_default_value(options);
        },
        nb::arg("options") = nb::none(),
        "Python bindings defaults:\n    If options is None, then its default value will be: MarkdownOptions()");

    m.def("de_initialize_markdown",
        ImGuiMd::DeInitializeMarkdown);

    m.def("get_font_loader_function",
        ImGuiMd::GetFontLoaderFunction, "GetFontLoaderFunction() will return a function that you should call during ImGui initialization.");

    m.def("render",
        ImGuiMd::Render,
        nb::arg("markdown_string"),
        "Renders a markdown string");

    m.def("render_unindented",
        ImGuiMd::RenderUnindented,
        nb::arg("markdown_string"),
        "Renders a markdown string (after having unindented its main indentation)");

    m.def("get_code_font",
        ImGuiMd::GetCodeFont);


    auto pyClassMarkdownFontSpec =
        nb::class_<ImGuiMd::MarkdownFontSpec>
            (m, "MarkdownFontSpec", "")
        .def_rw("italic", &ImGuiMd::MarkdownFontSpec::italic, "")
        .def_rw("bold", &ImGuiMd::MarkdownFontSpec::bold, "")
        .def_rw("header_level", &ImGuiMd::MarkdownFontSpec::headerLevel, "")
        .def(nb::init<bool, bool, int>(),
            nb::arg("italic_") = false, nb::arg("bold_") = false, nb::arg("header_level_") = 0)
        ;


    m.def("get_font",
        ImGuiMd::GetFont, nb::arg("font_spec"));
    ////////////////////    </generated_from:imgui_md_wrapper.h>    ////////////////////

    // </litgen_pydef> // Autogenerated code end
    // !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE END !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
}
