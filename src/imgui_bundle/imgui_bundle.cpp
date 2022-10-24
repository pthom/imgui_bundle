#include "imgui_bundle/imgui_bundle.h"

#include "implot/implot.h"
#include "imgui-node-editor/imgui_node_editor_internal.h"

#include <chrono>


namespace ImGuiBundle
{

    std::optional<ax::NodeEditor::EditorContext *> _NODE_EDITOR_CONTEXT;
    ax::NodeEditor::Config NODE_EDITOR_CONFIG;


    void Run(
        HelloImGui::RunnerParams& runner_params,
        bool with_implot,
        bool with_node_editor,
        const std::optional<NodeEditorConfig>& with_node_editor_config_,
        bool with_markdown,
        const std::optional<ImGuiMd::MarkdownOptions> & with_markdown_options_
    )
    {
        // create implot context if required
        if (with_implot)
            ImPlot::CreateContext();

        // create imgui_node_editor context if required
        NodeEditorConfig with_node_editor_config;
        if (with_node_editor || with_node_editor_config_.has_value())
        {
            with_node_editor = true;
            if (with_node_editor_config_.has_value())
                NODE_EDITOR_CONFIG = *with_node_editor_config_;
            _NODE_EDITOR_CONTEXT = ax::NodeEditor::CreateEditor(&NODE_EDITOR_CONFIG);
            ax::NodeEditor::SetCurrentEditor(_NODE_EDITOR_CONTEXT.value());
        }

        // load markdown fonts if needed
        if (with_markdown || with_markdown_options_.has_value())
        {
            ImGuiMd::MarkdownOptions markdown_options;
            if (with_markdown_options_.has_value())
                markdown_options = *with_markdown_options_;
            ImGuiMd::InitializeMarkdown(markdown_options);
            runner_params.callbacks.LoadAdditionalFonts = ImGuiMd::GetFontLoaderFunction();
        }

        HelloImGui::Run(runner_params);

        if (with_implot)
            ImPlot::DestroyContext();

        if (with_node_editor)
        {
            assert(_NODE_EDITOR_CONTEXT.has_value());
            ax::NodeEditor::DestroyEditor(*_NODE_EDITOR_CONTEXT);
            _NODE_EDITOR_CONTEXT = std::nullopt;
        }
    }


    void Run(
        const HelloImGui::VoidFunction& gui_function,
        const std::optional<ImVec2>& window_size,
        const std::optional<std::string>& window_title,
        bool with_implot,
        bool with_node_editor,
        const std::optional<NodeEditorConfig>& with_node_editor_config,
        bool with_markdown,
        const std::optional<ImGuiMd::MarkdownOptions> & with_markdown_options
    )
    {
        HelloImGui::RunnerParams runnerParams;
        runnerParams.callbacks.ShowGui = gui_function;
        if (window_size.has_value())
            runnerParams.appWindowParams.windowSize = *window_size;
        if (window_title.has_value())
            runnerParams.appWindowParams.windowTitle = *window_title;

        Run(runnerParams,
            with_implot,
            with_node_editor,
            with_node_editor_config,
            with_markdown,
            with_markdown_options
            );
    }


    ax::NodeEditor::EditorContext* CurrentNodeEditorContext()
    {
        if (!_NODE_EDITOR_CONTEXT.has_value())
            throw std::runtime_error("No current node editor context\n"
                                     "    Did you set with_node_editor_config when calling ImGuiBundle::Run()?");
        return *_NODE_EDITOR_CONTEXT;
    }


    class StopWatch
    {
        // Typical C++ shamanic incantations to get a time in seconds
    private:
        using Clock = std::chrono::high_resolution_clock;
        using second = std::chrono::duration<double, std::ratio<1>>;
        std::chrono::time_point<Clock> mStart;

    public:
        StopWatch() : mStart(Clock::now()) {}

        double elapsed() const
        {
            return std::chrono::duration_cast<second>
                (Clock::now() - mStart).count();
        }
    };

    double Now()
    {
        static StopWatch watch;
        return watch.elapsed();
    }


}