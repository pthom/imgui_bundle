#ifdef IMGUI_BUNDLE_WITH_IMGUI_TEX_INSPECT
// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include <nanobind/nanobind.h>
#include <nanobind/trampoline.h>
#include <nanobind/stl/array.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/optional.h>
#include <nanobind/stl/function.h>
#include <nanobind/stl/shared_ptr.h>
#include <nanobind/stl/unique_ptr.h>
#include <nanobind/stl/map.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/make_iterator.h>
#include <nanobind/ndarray.h>

#include "imgui_tex_inspect/imgui_tex_inspect_internal.h"
#include "imgui_tex_inspect/imgui_tex_inspect.h"
#include "imgui_tex_inspect/imgui_tex_inspect_demo.h"


namespace nb = nanobind;

// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// <litgen_glue_code>  // Autogenerated code below! Do not edit!

// </litgen_glue_code> // Autogenerated code end
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE END !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


NB_MAKE_OPAQUE(ImGuiTexInspect::Context);


void py_init_module_imgui_tex_inspect(nb::module_& m)
{
    using namespace ImGuiTexInspect;

    m.def("create_context", []() {
        Context* ctx = ImGuiTexInspect::CreateContext();
        uintptr_t address = (uintptr_t)ctx;
        return address;
    });

    m.def("destroy_context", [](uintptr_t address) {
        Context* ctx = (Context *) address;
        ImGuiTexInspect::DestroyContext(ctx);
    });

    m.def("set_current_context", [](uintptr_t address) {
        Context* ctx = (Context *) address;
        ImGuiTexInspect::SetCurrentContext(ctx);
    });

    // !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    // <litgen_pydef> // Autogenerated code below! Do not edit!
    ////////////////////    <generated_from:imgui_tex_inspect.h>    ////////////////////
    m.def("init",
        ImGuiTexInspect::Init);

    m.def("shutdown",
        ImGuiTexInspect::Shutdown);


    auto pyEnumInspectorAlphaMode =
        nb::enum_<ImGuiTexInspect::InspectorAlphaMode>(m, "InspectorAlphaMode", nb::is_arithmetic(), "")
            .value("im_gui", ImGuiTexInspect::InspectorAlphaMode_ImGui, "Alpha is transparency so you see the ImGui panel background behind image")
            .value("black", ImGuiTexInspect::InspectorAlphaMode_Black, "Alpha is used to blend over a black background")
            .value("white", ImGuiTexInspect::InspectorAlphaMode_White, "Alpha is used to blend over a white background")
            .value("custom_color", ImGuiTexInspect::InspectorAlphaMode_CustomColor, "Alpha is used to blend over a custom colour.");


    auto pyEnumInspectorFlags_ =
        nb::enum_<ImGuiTexInspect::InspectorFlags_>(m, "InspectorFlags_", nb::is_arithmetic(), "")
            .value("show_wrap", ImGuiTexInspect::InspectorFlags_ShowWrap, "Draw beyong the [0,1] uv range. What you see will depend on API")
            .value("no_force_filter_nearest", ImGuiTexInspect::InspectorFlags_NoForceFilterNearest, "Normally we force nearest neighbour sampling when zoomed in. Set to disable this.")
            .value("no_grid", ImGuiTexInspect::InspectorFlags_NoGrid, "By default a grid is shown at high zoom levels")
            .value("no_tooltip", ImGuiTexInspect::InspectorFlags_NoTooltip, "Disable tooltip on hover")
            .value("fill_horizontal", ImGuiTexInspect::InspectorFlags_FillHorizontal, "Scale to fill available space horizontally")
            .value("fill_vertical", ImGuiTexInspect::InspectorFlags_FillVertical, "Scale to fill available space vertically")
            .value("no_auto_read_texture", ImGuiTexInspect::InspectorFlags_NoAutoReadTexture, "By default texture data is read to CPU every frame for tooltip and annotations")
            .value("flip_x", ImGuiTexInspect::InspectorFlags_FlipX, "Horizontally flip the way the texture is displayed")
            .value("flip_y", ImGuiTexInspect::InspectorFlags_FlipY, "Vertically flip the way the texture is displayed");


    auto pyClassSizeIncludingBorder =
        nb::class_<ImGuiTexInspect::SizeIncludingBorder>
            (m, "SizeIncludingBorder", "")
        .def_rw("size", &ImGuiTexInspect::SizeIncludingBorder::Size, "")
        .def(nb::init<ImVec2>(),
            nb::arg("size"))
        ;


    auto pyClassSizeExcludingBorder =
        nb::class_<ImGuiTexInspect::SizeExcludingBorder>
            (m, "SizeExcludingBorder", "")
        .def_rw("size", &ImGuiTexInspect::SizeExcludingBorder::size, "")
        .def(nb::init<ImVec2>(),
            nb::arg("size"))
        ;


    m.def("begin_inspector_panel",
        nb::overload_cast<const char *, ImTextureID, ImVec2, InspectorFlags>(ImGuiTexInspect::BeginInspectorPanel), nb::arg("name"), nb::arg("param_1"), nb::arg("texture_size"), nb::arg("flags") = 0);

    m.def("begin_inspector_panel",
        nb::overload_cast<const char *, ImTextureID, ImVec2, InspectorFlags, ImGuiTexInspect::SizeIncludingBorder>(ImGuiTexInspect::BeginInspectorPanel), nb::arg("name"), nb::arg("param_1"), nb::arg("texture_size"), nb::arg("flags"), nb::arg("size"));

    m.def("begin_inspector_panel",
        nb::overload_cast<const char *, ImTextureID, ImVec2, InspectorFlags, ImGuiTexInspect::SizeExcludingBorder>(ImGuiTexInspect::BeginInspectorPanel), nb::arg("name"), nb::arg("param_1"), nb::arg("texture_size"), nb::arg("flags"), nb::arg("size"));

    m.def("end_inspector_panel",
        ImGuiTexInspect::EndInspectorPanel, " EndInspectorPanel\n * Always call after BeginInspectorPanel and after you have drawn any required annotations");

    m.def("release_inspector_data",
        ImGuiTexInspect::ReleaseInspectorData,
        nb::arg("id"),
        " ReleaseInspectorData\n * ImGuiTexInspect keeps texture data cached in memory.  If you know you won't\n * be displaying a particular panel for a while you can call this to release\n * the memory. It won't be allocated again until next time you call\n * BeginInspectorPanel.  If id is None then the current (most recent) inspector\n * will be affected.  Unless you have a lot of different Inspector instances\n * you can probably not worry about this. Call CurrentInspector_GetID to get\n * the ID of an inspector.\n");

    m.def("current_inspector_set_alpha_mode",
        ImGuiTexInspect::CurrentInspector_SetAlphaMode, nb::arg("param_0"));

    m.def("current_inspector_set_flags",
        ImGuiTexInspect::CurrentInspector_SetFlags, nb::arg("to_set"), nb::arg("to_clear") = 0);

    m.def("current_inspector_clear_flags",
        ImGuiTexInspect::CurrentInspector_ClearFlags, nb::arg("to_clear"));

    m.def("current_inspector_set_grid_color",
        ImGuiTexInspect::CurrentInspector_SetGridColor, nb::arg("color"));

    m.def("current_inspector_set_max_annotations",
        ImGuiTexInspect::CurrentInspector_SetMaxAnnotations, nb::arg("max_annotations"));

    m.def("current_inspector_invalidate_texture_cache",
        ImGuiTexInspect::CurrentInspector_InvalidateTextureCache, " CurrentInspector_InvalidateTextureCache\n * If using the InspectorFlags_NoAutoReadTexture flag then call this to\n * indicate your texture has changed context.\n");

    m.def("current_inspector_set_custom_background_color",
        nb::overload_cast<ImVec4>(ImGuiTexInspect::CurrentInspector_SetCustomBackgroundColor), nb::arg("color"));

    m.def("current_inspector_set_custom_background_color",
        nb::overload_cast<ImU32>(ImGuiTexInspect::CurrentInspector_SetCustomBackgroundColor), nb::arg("color"));

    m.def("current_inspector_get_id",
        ImGuiTexInspect::CurrentInspector_GetID, " CurrentInspector_GetID\n * Get the ID of the current inspector.  Currently only used for calling\n * ReleaseInspectorData.\n");

    m.def("draw_color_matrix_editor",
        ImGuiTexInspect::DrawColorMatrixEditor, "ColorMatrix editor.  See comments on ColorMatrix below.");

    m.def("draw_grid_editor",
        ImGuiTexInspect::DrawGridEditor, "Grid editor.  Enable/Disable grid. Set Grid Color.");

    m.def("draw_color_channel_selector",
        ImGuiTexInspect::DrawColorChannelSelector, "For toggling R,G,B channels");

    m.def("draw_alpha_mode_selector",
        ImGuiTexInspect::DrawAlphaModeSelector, "A combo box for selecting the alpha mode");

    m.def("set_zoom_rate",
        ImGuiTexInspect::SetZoomRate,
        nb::arg("factor"),
        "-------------------------------------------------------------------------\n [SECTION] CONTEXT-WIDE SETTINGS\n-------------------------------------------------------------------------\n/* SetZoomRate\n * factor should be greater than 1.  A value of 1.5 means one mouse wheel\n * scroll will increase zoom level by 50%. The factor used for zooming out is\n * 1/factor. */");

    m.def("draw_annotation_line",
        ImGuiTexInspect::DrawAnnotationLine,
        nb::arg("draw_list"), nb::arg("from_texel"), nb::arg("to_texel"), nb::arg("texels_to_pixels"), nb::arg("color"),
        " DrawAnnotationLine\n * Convenience function to add a line to draw list using texel coordinates.\n");


    auto pyClassValueText =
        nb::class_<ImGuiTexInspect::ValueText>
            (m, "ValueText", " ValueText\n * An annoation class that draws text inside each texel when zoom level is high enough for it to fit.\n * The text shows the value of the texel. E.g. \"R:255, G: 128, B:0, A:255\"\n");

    { // inner classes & enums of ValueText
        auto pyEnumFormat =
            nb::enum_<ImGuiTexInspect::ValueText::Format>(pyClassValueText, "Format", nb::is_arithmetic(), "")
                .value("hex_string", ImGuiTexInspect::ValueText::HexString, "E.g.  #EF97B9FF")
                .value("bytes_hex", ImGuiTexInspect::ValueText::BytesHex, "E.g.  R:#EF G:#97 B:#B9 A:#FF  (split over 4 lines)")
                .value("bytes_dec", ImGuiTexInspect::ValueText::BytesDec, "E.g.  R:239 G: 151 B:185 A:255  (split over 4 lines)")
                .value("floats", ImGuiTexInspect::ValueText::Floats, "E.g.  0.937 0.592 0.725 1.000 (split over 4 lines)");
    } // end of inner classes & enums of ValueText

    pyClassValueText
        .def(nb::init<ImGuiTexInspect::ValueText::Format>(),
            nb::arg("format") = ImGuiTexInspect::ValueText::HexString)
        .def("draw_annotation",
            &ImGuiTexInspect::ValueText::DrawAnnotation, nb::arg("draw_list"), nb::arg("texel"), nb::arg("texels_to_pixels"), nb::arg("value"))
        ;


    auto pyClassArrow =
        nb::class_<ImGuiTexInspect::Arrow>
            (m, "Arrow", " Arrow\n * An annotation class that draws an arrow inside each texel when zoom level is\n * high enough. The direction and length of the arrow are determined by texel\n * values.\n * The X and Y components of the arrow is determined by the VectorIndex_x, and\n * VectorIndex_y channels of the texel value.  Examples:\n\n * VectorIndex_x = 0,  VectorIndex_y = 1  means  X component is red and Y component is green\n * VectorIndex_x = 1,  VectorIndex_y = 2  means  X component is green and Y component is blue\n * VectorIndex_x = 0,  VectorIndex_y = 3  means  X component is red and Y component is alpha\n *\n * ZeroPoint is the texel value which corresponds to a zero length vector. E.g.\n * ZeroPoint = (0.5, 0.5) means (0.5, 0.5) will be drawn as a zero length arrow\n *\n * All public properties can be directly manipulated.  There are also presets that can be set\n * by calling UsePreset.\n\n");

    { // inner classes & enums of Arrow
        auto pyEnumPreset =
            nb::enum_<ImGuiTexInspect::Arrow::Preset>(pyClassArrow, "Preset", nb::is_arithmetic(), "")
                .value("normal_map", ImGuiTexInspect::Arrow::NormalMap, "For normal maps. I.e. Arrow is in (R,G) channels.  128, 128 is zero point")
                .value("normalized_float", ImGuiTexInspect::Arrow::NormalizedFloat, "Arrow in (R,G) channels. 0,0 is zero point, (1,0) will draw an arrow exactly to");
    } // end of inner classes & enums of Arrow

    pyClassArrow
        .def_rw("vector_index_x", &ImGuiTexInspect::Arrow::VectorIndex_x, "")
        .def_rw("vector_index_y", &ImGuiTexInspect::Arrow::VectorIndex_y, "")
        .def_rw("line_scale", &ImGuiTexInspect::Arrow::LineScale, "")
        .def_rw("zero_point", &ImGuiTexInspect::Arrow::ZeroPoint, "")
        .def("__init__",
            [](ImGuiTexInspect::Arrow * self, int xVectorIndex = 0, int yVectorIndex = 1, const std::optional<const ImVec2> & lineScale = std::nullopt)
            {
                auto ctor_wrapper = [](ImGuiTexInspect::Arrow* self, int xVectorIndex = 0, int yVectorIndex = 1, ImVec2 lineScale = ImVec2(1, 1)) ->  void
                {
                    new(self) ImGuiTexInspect::Arrow(xVectorIndex, yVectorIndex, lineScale); // placement new
                };
                auto ctor_wrapper_adapt_mutable_param_with_default_value = [&ctor_wrapper](ImGuiTexInspect::Arrow * self, int xVectorIndex = 0, int yVectorIndex = 1, const std::optional<const ImVec2> & lineScale = std::nullopt)
                {

                    const ImVec2& lineScale_or_default = [&]() -> const ImVec2 {
                        if (lineScale.has_value())
                            return lineScale.value();
                        else
                            return ImVec2(1, 1);
                    }();

                    ctor_wrapper(self, xVectorIndex, yVectorIndex, lineScale_or_default);
                };

                ctor_wrapper_adapt_mutable_param_with_default_value(self, xVectorIndex, yVectorIndex, lineScale);
            },
            nb::arg("x_vector_index") = 0, nb::arg("y_vector_index") = 1, nb::arg("line_scale") = nb::none(),
            "---\nPython bindings defaults:\n    If lineScale is None, then its default value will be: ImVec2(1, 1)")
        .def("use_preset",
            &ImGuiTexInspect::Arrow::UsePreset, nb::arg("param_0"))
        .def("draw_annotation",
            &ImGuiTexInspect::Arrow::DrawAnnotation, nb::arg("draw_list"), nb::arg("texel"), nb::arg("texels_to_pixels"), nb::arg("value"))
        ;


    auto pyClassTransform2D =
        nb::class_<ImGuiTexInspect::Transform2D>
            (m, "Transform2D", "")
        .def("__init__", [](ImGuiTexInspect::Transform2D * self, const std::optional<const ImVec2> & Scale = std::nullopt, const std::optional<const ImVec2> & Translate = std::nullopt)
        {
            new (self) ImGuiTexInspect::Transform2D();  // placement new
            auto r = self;
            if (Scale.has_value())
                r->Scale = Scale.value();
            else
                r->Scale = ImVec2();
            if (Translate.has_value())
                r->Translate = Translate.value();
            else
                r->Translate = ImVec2();
        },
        nb::arg("scale") = nb::none(), nb::arg("translate") = nb::none()
        )
        .def_rw("scale", &ImGuiTexInspect::Transform2D::Scale, "")
        .def_rw("translate", &ImGuiTexInspect::Transform2D::Translate, "")
        .def("__mul__",
            &ImGuiTexInspect::Transform2D::operator*,
            nb::arg("rhs"),
            "Transform a vector by this transform.  Scale is applied first")
        .def("inverse",
            &ImGuiTexInspect::Transform2D::Inverse, "Return an inverse transform such that transform.Inverse() * transform * vector == vector")
        ;
    ////////////////////    </generated_from:imgui_tex_inspect.h>    ////////////////////


    ////////////////////    <generated_from:imgui_tex_inspect_demo.h>    ////////////////////
    auto pyClassTexture =
        nb::class_<ImGuiTexInspect::Texture>
            (m, "Texture", "")
        .def("__init__", [](ImGuiTexInspect::Texture * self, const std::optional<const ImTextureID> & texture = std::nullopt, const std::optional<const ImVec2> & size = std::nullopt)
        {
            new (self) ImGuiTexInspect::Texture();  // placement new
            auto r = self;
            if (texture.has_value())
                r->texture = texture.value();
            else
                r->texture = ImTextureID();
            if (size.has_value())
                r->size = size.value();
            else
                r->size = ImVec2();
        },
        nb::arg("texture") = nb::none(), nb::arg("size") = nb::none()
        )
        .def_rw("texture", &ImGuiTexInspect::Texture::texture, "")
        .def_rw("size", &ImGuiTexInspect::Texture::size, "")
        ;


    m.def("show_demo_window",
        ImGuiTexInspect::ShowDemoWindow);
    ////////////////////    </generated_from:imgui_tex_inspect_demo.h>    ////////////////////

    // </litgen_pydef> // Autogenerated code end
    // !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE END !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
}
#endif // IMGUI_BUNDLE_WITH_IMGUI_TEX_INSPECT
