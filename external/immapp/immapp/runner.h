#pragma once
#include "hello_imgui/hello_imgui.h"
#ifdef IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR
#include "imgui-node-editor/imgui_node_editor.h"
#endif
#include "imgui_md_wrapper/imgui_md_wrapper.h"

#include <optional>


namespace ImmApp
{
#ifdef IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR
    using NodeEditorConfig = ax::NodeEditor::Config;
    using NodeEditorContext = ax::NodeEditor::EditorContext;
#endif

    using VoidFunction = std::function<void(void)>;

    using ScreenSize = HelloImGui::ScreenSize;
    using HelloImGui::DefaultWindowSize;

    /////////////////////////////////////////////////////////////////////////////////////////
    //
    // AddOnParams: require specific ImGuiBundle packages (markdown, node editor, texture viewer)
    // to be initialized at startup.
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

        // Set withTexInspect=true if you need to use imgui_tex_inspect
        bool withTexInspect = false;

#ifdef IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR
        // You can tweak NodeEditorConfig (but this is optional)
        std::optional<NodeEditorConfig> withNodeEditorConfig = std::nullopt;

        // If true, the node editor colors will be updated from the ImGui colors
        // (i.e. if using a light theme, the node editor will use a light theme, etc.)
        // This is called after runnerParams.callbacks.SetupImGuiStyle, in which you can set the ImGui style.
        // If you set this to false, you can set the node editor style manually.
        // (Note: you can also the theme via RunnerParams.imguiParams.tweakedTheme)
        bool updateNodeEditorColorsFromImguiColors = true;
#endif

        // You can tweak MarkdownOptions (but this is optional)
        std::optional<ImGuiMd::MarkdownOptions> withMarkdownOptions = std::nullopt;
    };


    /////////////////////////////////////////////////////////////////////////////////////////
    //
    // Helpers to run an app from C++
    //
    /////////////////////////////////////////////////////////////////////////////////////////
    // Run an application using HelloImGui params + some addons
    void Run(HelloImGui::RunnerParams& runnerParams, const AddOnsParams& addOnsParams = AddOnsParams());
    void Run(const HelloImGui::SimpleRunnerParams& simpleParams, const AddOnsParams& addOnsParams = AddOnsParams());

    /////////////////////////////////////////////////////////////////////////////////////////
    //
    // Helpers to run an app from Python (using named parameters)
    //
    /////////////////////////////////////////////////////////////////////////////////////////
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
    // (ImmApp::AddOnsParams)
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
        const ScreenSize& windowSize = DefaultWindowSize,
        float fpsIdle = 10.f,

        // AddOnsParams below:
        bool withImplot = false,
        bool withMarkdown = false,
        bool withNodeEditor = false,
        bool withTexInspect = false,
#ifdef IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR
        const std::optional<NodeEditorConfig>& withNodeEditorConfig = std::nullopt,
#endif
        const std::optional<ImGuiMd::MarkdownOptions> & withMarkdownOptions = std::nullopt
    );

    // Run an application with markdown
    void RunWithMarkdown(
        // HelloImGui::SimpleRunnerParams below:
        const VoidFunction& guiFunction,
        const std::string& windowTitle = "",
        bool windowSizeAuto = false,
        bool windowRestorePreviousGeometry = false,
        const ScreenSize& windowSize = DefaultWindowSize,
        float fpsIdle = 10.f,

        // AddOnsParams below:
        bool withImplot = false,
        bool withNodeEditor = false,
        bool withTexInspect = false,
#ifdef IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR
        const std::optional<NodeEditorConfig>& withNodeEditorConfig = std::nullopt,
#endif
        const std::optional<ImGuiMd::MarkdownOptions> & withMarkdownOptions = std::nullopt
    );


    /////////////////////////////////////////////////////////////////////////////////////////
    //
    // Dpi aware utilities (which call the same utilities from HelloImGui)
    //
    /////////////////////////////////////////////////////////////////////////////////////////

    // EmSize() returns the visible font size on the screen. For good results on HighDPI screens, always scale your
    // widgets and windows relatively to this size.
    // It is somewhat comparable to the [em CSS Unit](https://lyty.dev/css/css-unit.html).
    // EmSize() = ImGui::GetFontSize()
    float EmSize();

    // EmSize(nbLines) returns a size corresponding to nbLines text lines
    float EmSize(float nbLines);

    // EmToVec2() returns an ImVec2 that you can use to size or place your widgets in a DPI independent way
    // (pass sizes that are proportional to the font height)
    ImVec2 EmToVec2(float x, float y);
    ImVec2 EmToVec2(ImVec2 v);

    // PixelsToEm() converts a Vec2 in pixels to a Vec2 in em
    ImVec2 PixelsToEm(ImVec2 pixels);
    // PixelSizeToEm() converts a size in pixels to a size in em
    float  PixelSizeToEm(float pixelSize);

    /////////////////////////////////////////////////////////////////////////////////////////
    //
    // Utility for ImGui node editor & NanoVG
    //
    /////////////////////////////////////////////////////////////////////////////////////////
#ifdef IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR
    NodeEditorContext* DefaultNodeEditorContext();
    NodeEditorConfig* DefaultNodeEditorConfig();

    // NodeEditorSettingsLocation returns the path to the json file for the node editor settings.
    std::string NodeEditorSettingsLocation(const HelloImGui::RunnerParams& runnerParams);

    // HasNodeEditorSettings returns true if the json file for the node editor settings exists.
    bool HasNodeEditorSettings(const HelloImGui::RunnerParams& runnerParams);

    // DeleteNodeEditorSettings deletes the json file for the node editor settings.
    void DeleteNodeEditorSettings(const HelloImGui::RunnerParams& runnerParams);

#endif
} // namespace ImmApp
