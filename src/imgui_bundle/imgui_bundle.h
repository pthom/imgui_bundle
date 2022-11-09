#pragma once
#include "hello_imgui/hello_imgui.h"
#include "imgui-node-editor/imgui_node_editor.h"
#include "imgui_md/imgui_md_wrapper.h"

#include <optional>

namespace ImGuiBundle
{
    using NodeEditorConfig = ax::NodeEditor::Config;
    using VoidFunction = std::function<void(void)>;
    using ScreenSize = std::array<int, 2>;

    /////////////////////////////////////////////////////////////////////////////////////////
    //
    // Helper to run an app with "named params emulation" in C++
    // (call it using designated initializers!)
    //
    /////////////////////////////////////////////////////////////////////////////////////////

    struct AddOnsParams
    {
        bool withImplot = false;
        bool withMarkdown = false;
        bool withNodeEditor = false;
        std::optional<NodeEditorConfig> withNodeEditorConfig = std::nullopt;
        std::optional<ImGuiMd::MarkdownOptions> withMarkdownOptions = std::nullopt;
    };

    void Run(HelloImGui::RunnerParams& runnerParams, const AddOnsParams& addOnsParams = AddOnsParams());
    void Run(const HelloImGui::SimpleRunnerParams& simpleParams, const AddOnsParams& addOnsParams = AddOnsParams());


    /////////////////////////////////////////////////////////////////////////////////////////
    //
    // Helpers to run an app from Python (using named parameters)
    //
    /////////////////////////////////////////////////////////////////////////////////////////

    // Helper to run an app inside imgui_bundle, using HelloImGui
    //
    // - if `window_size` is not specified (i.e None or nullopt), then the window size will be computed to fit its widgets
    // - if `with_implot` is True, then a context for implot will be created/destroyed automatically
    // - if `with_markdown` or `with_markdown_options` is specified, then  the markdown context will be initialized
    //    (i.e. required fonts will be loaded)
    // - if `with_node_editor` or with_node_editor_config` is specified, then a context for imgui_node_editor
    //    will be created automatically.
    // - `fpsIdle` enables to set the app FPS when it is idle (set it to 0 for maximum FPS).
    void Run(
        // HelloImGui::SimpleRunnerParams below:
        const VoidFunction& guiFunction,
        const std::string& windowTitle = "",
        bool windowSizeAuto = false,
        bool windowRestorePreviousGeometry = false,
        const ScreenSize& windowSize = {800, 600},
        float fpsIdle = 10.f,

        // ImGuiBundle_AddOnsParams below:
        bool withImplot = false,
        bool withMarkdown = false,
        bool withNodeEditor = false,
        const std::optional<NodeEditorConfig>& withNodeEditorConfig = std::nullopt,
        const std::optional<ImGuiMd::MarkdownOptions> & withMarkdownOptions = std::nullopt
    );

    double ClockSeconds();
    ax::NodeEditor::EditorContext* CurrentNodeEditorContext();
}
