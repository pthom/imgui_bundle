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
        // Set withImplot=true if you need to plot graphs
        bool withImplot = false;

        // Set withMarkdown=true if you need to render Markdown
        // (alternatively, you can set withMarkdownOptions)
        bool withMarkdown = false;

        // Set withNodeEditor=true if you need to render a node editor
        // (alternatively, you can set withNodeEditorConfig)
        bool withNodeEditor = false;

        // You can tweak NodeEditorConfig (but this is optional)
        std::optional<NodeEditorConfig> withNodeEditorConfig = std::nullopt;

        // You can tweak MarkdownOptions (but this is optional)
        std::optional<ImGuiMd::MarkdownOptions> withMarkdownOptions = std::nullopt;
    };

    void Run(HelloImGui::RunnerParams& runnerParams, const AddOnsParams& addOnsParams = AddOnsParams());
    void Run(const HelloImGui::SimpleRunnerParams& simpleParams, const AddOnsParams& addOnsParams = AddOnsParams());


    /////////////////////////////////////////////////////////////////////////////////////////
    //
    // Helpers to run an app from Python (using named parameters)
    //
    /////////////////////////////////////////////////////////////////////////////////////////

    constexpr ScreenSize DefaultScreenSize = {800, 600};

    // Helper to run an app inside imgui_bundle, using HelloImGui:
    //
    // (HelloImGui::SimpleRunnerParams)
    //     - `guiFunction`: the function that will render the ImGui widgets
    //     - `windowTitle`: title of the window
    //     - `windowSizeAuto`: if true, autosize the window from its inner widgets
    //     - `windowRestorePreviousGeometry`: if true, restore window size and position from last run
    //     - `windowSize`: size of the window
    //     - `fpsIdle`: fps of the application when idle
    //
    // (ImGuiBundle::AddOnsParams)
    //     - `with_implot`: if True, then a context for implot will be created/destroyed automatically
    //     - `with_markdown` / `with_markdown_options`: if specified, then  the markdown context will be initialized
    //       (i.e. required fonts will be loaded)
    //     - `with_node_editor` / `with_node_editor_config`: if specified, then a context for imgui_node_editor
    //       will be created automatically.
    void Run(
        // HelloImGui::SimpleRunnerParams below:
        const VoidFunction& guiFunction,
        const std::string& windowTitle = "",
        bool windowSizeAuto = false,
        bool windowRestorePreviousGeometry = false,
        const ScreenSize& windowSize = DefaultScreenSize,
        float fpsIdle = 10.f,

        // AddOnsParams below:
        bool withImplot = false,
        bool withMarkdown = false,
        bool withNodeEditor = false,
        const std::optional<NodeEditorConfig>& withNodeEditorConfig = std::nullopt,
        const std::optional<ImGuiMd::MarkdownOptions> & withMarkdownOptions = std::nullopt
    );

    double ClockSeconds();
    ax::NodeEditor::EditorContext* CurrentNodeEditorContext();
}
