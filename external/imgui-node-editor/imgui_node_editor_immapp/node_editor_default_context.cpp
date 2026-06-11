// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
#define IMGUI_DEFINE_MATH_OPERATORS
#include "node_editor_default_context.h"
#include "imgui-node-editor/imgui_node_editor_internal.h"


#ifndef IMGUI_BUNDLE_DISABLE_IMMAPP
namespace ImmApp
{
    ax::NodeEditor::EditorContext* DefaultNodeEditorContext();
}

ax::NodeEditor::EditorContext* DefaultNodeEditorContext_Immapp()
{
    return ImmApp::DefaultNodeEditorContext();
}
#else
ax::NodeEditor::EditorContext* DefaultNodeEditorContext_Immapp()
{
    return nullptr; // immapp not available
}
#endif

void SuspendNodeEditorCanvas_Immapp()
{
    auto context  = ax::NodeEditor::GetCurrentEditor();
    auto context_cast = (ax::NodeEditor::Detail::EditorContext *)context;
    context_cast->Suspend();
}

void ResumeNodeEditorCanvas_Immapp()
{
    auto context  = ax::NodeEditor::GetCurrentEditor();
    auto context_cast = (ax::NodeEditor::Detail::EditorContext *)context;
    context_cast->Resume();
}

void DisableUserInputThisFrame()
{
    namespace ed = ax::NodeEditor;
    ed::Detail::EditorContext *nodeContext = (ed::Detail::EditorContext *)ed::GetCurrentEditor();
    if (nodeContext)
        nodeContext->DisableUserInputThisFrame();
}


namespace
{
    struct Hsv
    {
        float h, s, v;
    };

    static ImVec4 ColorWithAlphaMultiplier(ImVec4 col, float k)
    {
        return ImVec4(col.x, col.y, col.z, col.w * k);
    }

    static ImVec4 ColorValueMultiply(ImVec4 col, float value_multiplier)
    {
        float h, s, v;
        ImGui::ColorConvertRGBtoHSV(col.x, col.y, col.z, h, s, v);
        v = v * value_multiplier;
        if (v > 1.0)
            v = 1.0;
        ImVec4 r = col;
        ImGui::ColorConvertHSVtoRGB(h, s, v, r.x, r.y, r.z);
        return r;
    }

    static Hsv ColorToHsv(ImVec4 col)
    {
        Hsv hsv;
        ImGui::ColorConvertRGBtoHSV(col.x, col.y, col.z, hsv.h, hsv.s, hsv.v);
        return hsv;
    }

    static ImVec4 HsvToColor(Hsv hsv, float alpha = 1.0)
    {
        ImVec4 col;
        ImGui::ColorConvertHSVtoRGB(hsv.h, hsv.s, hsv.v, col.x, col.y, col.z);
        col.w = alpha;
        return col;
    }
}



void UpdateNodeEditorColorsFromImguiColors()
{
    using namespace ax::NodeEditor;
    auto & styleNode = GetStyle();
    const auto & styleIm = ImGui::GetStyle();
    styleNode.Colors[StyleColor_Bg] = styleIm.Colors[ImGuiCol_WindowBg];
    styleNode.Colors[StyleColor_Grid] = ColorWithAlphaMultiplier(styleIm.Colors[ImGuiCol_Border], 0.15);

    auto bgHsv = ColorToHsv(styleNode.Colors[StyleColor_Bg]);
    bool isDark = bgHsv.v < 0.5;

    constexpr float kHov = 1.25;
    constexpr float kSel = 1.6;

    ImVec4 nodeBgColor;
    {
        auto frameBgColor = styleIm.Colors[ImGuiCol_FrameBg];

        auto hsvNodeBgColor = ColorToHsv(frameBgColor);
        if (hsvNodeBgColor.v > 0.5)
            hsvNodeBgColor.v -= 0.04;
        else
            hsvNodeBgColor.v += 0.08;

        hsvNodeBgColor.s -= 0.15;
        if (hsvNodeBgColor.s < 0.0)
            hsvNodeBgColor.s = 0.0;

        auto rgbNodeBgColor = HsvToColor(hsvNodeBgColor, 0.95);
        nodeBgColor = rgbNodeBgColor;
    }

    styleNode.Colors[StyleColor_NodeBg] = nodeBgColor;

    styleNode.Colors[StyleColor_NodeBorder] = styleIm.Colors[ImGuiCol_Border];
    styleNode.Colors[StyleColor_NodeBorder].w = 0.5;

    float HovNodeBorder = isDark ? kHov : 1.0 / kHov;
    styleNode.Colors[StyleColor_HovNodeBorder] = ColorValueMultiply(styleIm.Colors[ImGuiCol_ScrollbarGrabHovered], HovNodeBorder);

    if (isDark)
    {
        // Rectangle while lassoing around nodes
        styleNode.Colors[StyleColor_NodeSelRect] = ImVec4(1, 1, 1, 0.2);
        styleNode.Colors[StyleColor_NodeSelRectBorder] = ImVec4(1, 1, 1, 0.5);
        // Selected nodes in yellow
        styleNode.Colors[StyleColor_SelNodeBorder] = ImVec4(1, 1, 0, 1);

        // Rectangle while lassoing around links (using Shift)
        styleNode.Colors[StyleColor_LinkSelRect] = ImVec4(1, 1, 0.5, 0.2);
        styleNode.Colors[StyleColor_LinkSelRectBorder] = ImVec4(1, 1, 0.5, 0.5);
        // Selected links
        styleNode.Colors[StyleColor_SelLinkBorder] = ImVec4(1, 1, 0.3, 1);
        // Highlight links / sel
        styleNode.Colors[StyleColor_HovLinkBorder] = ImVec4(0, 0., 1, 0.5);
        styleNode.Colors[StyleColor_HighlightLinkBorder] = ImVec4(0, 0., 1, 0.5);

        styleNode.Colors[StyleColor_Flow] = ImVec4(1, 1, 0.6, 0.6);
        styleNode.Colors[StyleColor_FlowMarker] = ImVec4(1, 1, 0.6, 0.6);
    }
    else
    {
        // Rectangle while lassoing around nodes
        styleNode.Colors[StyleColor_NodeSelRect] = ImVec4(0, 0, 0, 0.15);
        styleNode.Colors[StyleColor_NodeSelRectBorder] = ImVec4(0, 0, 0, 0.5);
        // Selected nodes in blue
        styleNode.Colors[StyleColor_SelNodeBorder] = ImVec4(0, 0, 1, 1);

        // Rectangle while lassoing around links (using Shift)
        styleNode.Colors[StyleColor_LinkSelRect] = ImVec4(0, 0, 0.3, 0.15);
        styleNode.Colors[StyleColor_LinkSelRectBorder] = ImVec4(0, 0, 0.3, 0.5);
        // Selected links
        styleNode.Colors[StyleColor_SelLinkBorder] = ImVec4(0, 0.3, 1, 1);
        // Highlight links / sel
        styleNode.Colors[StyleColor_HovLinkBorder] = ImVec4(1, 0., 1, 0.5);
        styleNode.Colors[StyleColor_HighlightLinkBorder] = ImVec4(0, 0., 1, 0.5);

        styleNode.Colors[StyleColor_Flow] = ImVec4(0.6, 0.6, 1.0, 0.6);
        styleNode.Colors[StyleColor_FlowMarker] = ImVec4(0.6, 0.6, 1.0, 0.6);
    }

    styleNode.Colors[StyleColor_PinRect] = ColorWithAlphaMultiplier(styleIm.Colors[ImGuiCol_Button], 0.7);
    styleNode.Colors[StyleColor_PinRectBorder] = ColorWithAlphaMultiplier(styleIm.Colors[ImGuiCol_Button], 0.9);


    styleNode.Colors[StyleColor_GroupBg] = ColorWithAlphaMultiplier(styleIm.Colors[ImGuiCol_FrameBg], 0.6);
    styleNode.Colors[StyleColor_GroupBorder] = ColorWithAlphaMultiplier(styleIm.Colors[ImGuiCol_FrameBg], 0.8);
}
