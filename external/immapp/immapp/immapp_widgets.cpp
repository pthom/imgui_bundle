#define IMGUI_DEFINE_MATH_OPERATORS
#include "immapp/immapp_widgets.h"
#include "hello_imgui/hello_imgui.h"
#include "implot/implot.h"
#include "implot/implot_internal.h"
#include "imgui-node-editor/imgui_node_editor.h"
#include "imgui-node-editor/imgui_node_editor_internal.h"

namespace ImmApp
{
    namespace ed = ax::NodeEditor;

    static void DisableUserInputInNodeEditor()
    {
        ax::NodeEditor::Detail::EditorContext *nodeContext = (ax::NodeEditor::Detail::EditorContext *)ed::GetCurrentEditor();
        if (nodeContext)
            nodeContext->DisableUserInputThisFrame();
    }


    bool BeginPlotInNodeEditor(const char* title_id, const ImVec2& size, ImPlotFlags flags)
    {
        ImPlot::GetCurrentContext()->CanDragPlotInNodeEditor = true;
        return ImPlot::BeginPlot(title_id, size, flags);
    }

    void EndPlotInNodeEditor()
    {
        ImPlot::EndPlot();
        if (ImGui::IsMouseHoveringRect(ImGui::GetItemRectMin(), ImGui::GetItemRectMax()))
            DisableUserInputInNodeEditor();
    }

    // ShowResizablePlotInNodeEditor: shows a resizable plot inside a node
    // (the plot content is also draggable)
    // Will return true if the plot is visible
    ImVec2 ShowResizablePlotInNodeEditor(
        const char* title_id,        // plot title
        const ImVec2& size_pixels,          // plot size (will be updated if resized by the user)
        VoidFunction plotFunction,   // your function to draw the plot
        ImPlotFlags flags,
        float resizeHandleSizeEm
    )
    {
        bool visible = false;
        ImPlot::GetCurrentContext()->CanDragPlotInNodeEditor = true;

        // Prepare function to be called by HelloImGui::WidgetWithResizeHandle
        auto widgetFunction = [&]()
        {
            visible = BeginPlotInNodeEditor(title_id, size_pixels, flags);
            if (visible)
            {
                plotFunction();
                EndPlotInNodeEditor();
            }
        };

        ImVec2 new_size = HelloImGui::WidgetWithResizeHandle(
            title_id,
            widgetFunction,
            resizeHandleSizeEm,
            DisableUserInputInNodeEditor,
            DisableUserInputInNodeEditor);
        return new_size;
    }

    ImVec2 ShowResizablePlotInNodeEditor_Em(
        const char* title_id,
        const ImVec2& size_em,
        VoidFunction plotFunction,
        ImPlotFlags flags,
        float resizeHandleSizeEm
    )
    {
        ImVec2 size_pixels = HelloImGui::EmToVec2(size_em);
        ImVec2 new_size_pixels = ShowResizablePlotInNodeEditor(title_id, size_pixels, plotFunction, flags, resizeHandleSizeEm);
        ImVec2 new_size_em = HelloImGui::PixelsToEm(new_size_pixels);
        return new_size_em;
    }


    ImVec2 WidgetWithResizeHandle_InNodeEditor(
        const char* id,
        VoidFunction guiFunction, // your function to draw the widget
        float resizeHandleSizeEm
    )
    {
        ImVec2 newSize = HelloImGui::WidgetWithResizeHandle(
            id,
            std::move(guiFunction),
            resizeHandleSizeEm,
            // We disable the inputs of the node editor when the user is resizing the widget
            // (otherwise the user could drag the node editor nodes while resizing the widget)
            DisableUserInputInNodeEditor
            //DisableUserInputInNodeEditor
            );
        return newSize;
    }

    ImVec2 WidgetWithResizeHandle_InNodeEditor_Em(
        const char* id,
        VoidFunction guiFunction,    // your function to draw the widget
        float resizeHandleSizeEm
    )
    {
        ImVec2 new_size_pixels = WidgetWithResizeHandle_InNodeEditor(id, std::move(guiFunction), resizeHandleSizeEm);
        ImVec2 new_size_em = HelloImGui::PixelsToEm(new_size_pixels);
        return new_size_em;
    }

}
