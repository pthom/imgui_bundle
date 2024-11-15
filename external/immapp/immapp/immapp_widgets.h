#pragma once
#include "imgui.h"
#ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include "implot/implot.h"
#endif

#include <functional>

#if defined(IMGUI_BUNDLE_WITH_IMPLOT) && defined(IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR)
#define IMGUI_BUNDLE_WITH_IMPLOT_AND_IMGUI_NODE_EDITOR
#endif


namespace ImmApp
{
    using VoidFunction = std::function<void(void)>;

#ifdef IMGUI_BUNDLE_WITH_IMPLOT_AND_IMGUI_NODE_EDITOR
    // These functions wrap ImPlot::BeginPlot and ImPlot::EndPlot,
    // but they enable to make the plot content draggable inside a node
    bool BeginPlotInNodeEditor(const char* title_id, const ImVec2& size=ImVec2(-1,0), ImPlotFlags flags=0);
    void EndPlotInNodeEditor();

    // ShowResizablePlotInNodeEditor: shows a resizable plot inside a node
    // Returns the new size of the plot
    ImVec2 ShowResizablePlotInNodeEditor(
        const char* title_id,        // plot title
        const ImVec2& size_pixels,   // plot size (will be updated if resized by the user)
        VoidFunction plotFunction,   // your function to draw the plot
        ImPlotFlags flags=0,
        float resizeHandleSizeEm=1.0f
    );

    // ShowResizablePlotInNodeEditor_Em: shows a resizable plot inside a node
    // Returns the new size of the plot. Units are in em.
    ImVec2 ShowResizablePlotInNodeEditor_Em(
        const char* title_id,        // plot title
        const ImVec2& size_em,       // plot size (will be updated if resized by the user)
        VoidFunction plotFunction,   // your function to draw the plot
        ImPlotFlags flags=0,
        float resizeHandleSizeEm=1.0f
    );
#endif // #ifdef IMGUI_BUNDLE_WITH_IMPLOT_AND_IMGUI_NODE_EDITOR

#ifdef IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR
    // WidgetWithResizeHandle_InNodeEditor: shows a resizable widget inside a node
    // Returns the new size of the widget.
    ImVec2 WidgetWithResizeHandle_InNodeEditor(
        const char* id,
        VoidFunction guiFunction,    // your function to draw the widget
        float resizeHandleSizeEm=1.0f
    );

    // WidgetWithResizeHandle_InNodeEditor_Em: shows a resizable widget inside a node
    // Returns the new size of the widget. Size is in em.
    ImVec2 WidgetWithResizeHandle_InNodeEditor_Em(
        const char* id,
        VoidFunction guiFunction,    // your function to draw the widget
        float resizeHandleSizeEm=1.0f
    );
#endif // #if defined(IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR)
}