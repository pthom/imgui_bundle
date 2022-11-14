#include "imgui_bundle/imgui_bundle.h"

#include "implot/implot.h"
#include "imgui-node-editor/imgui_node_editor_internal.h"
#include "ImFileDialogTextureHelper.h"

#include <chrono>


namespace ImGuiBundle
{

    std::optional<ax::NodeEditor::EditorContext *> _NODE_EDITOR_CONTEXT;
    ax::NodeEditor::Config NODE_EDITOR_CONFIG;

    void Run(HelloImGui::RunnerParams& runnerParams, const AddOnsParams& addOnsParams_)
    {
        AddOnsParams addOnsParams = addOnsParams_;

        // create implot context if required
        if (addOnsParams.withImplot)
            ImPlot::CreateContext();

        // create imgui_node_editor context if required
        if (addOnsParams.withNodeEditor || addOnsParams.withNodeEditorConfig.has_value())
        {
            addOnsParams.withNodeEditor = true;
            if (addOnsParams.withNodeEditorConfig.has_value())
                NODE_EDITOR_CONFIG = addOnsParams.withNodeEditorConfig.value();
            _NODE_EDITOR_CONTEXT = ax::NodeEditor::CreateEditor(&NODE_EDITOR_CONFIG);
            ax::NodeEditor::SetCurrentEditor(_NODE_EDITOR_CONTEXT.value());
        }

        // load markdown fonts if needed
        if (addOnsParams.withMarkdown || addOnsParams.withMarkdownOptions.has_value())
        {
            if (!addOnsParams.withMarkdownOptions.has_value())
                addOnsParams.withMarkdownOptions = ImGuiMd::MarkdownOptions();
            ImGuiMd::InitializeMarkdown(addOnsParams.withMarkdownOptions.value());

            auto previousFontLoaderFunction = runnerParams.callbacks.LoadAdditionalFonts;
            runnerParams.callbacks.LoadAdditionalFonts = [previousFontLoaderFunction](){
                ImGuiMd::GetFontLoaderFunction()();
                previousFontLoaderFunction();
            };
        }

        ImFileDialogSetupTextureLoader();

        HelloImGui::Run(runnerParams);

        if (addOnsParams.withImplot)
            ImPlot::DestroyContext();

        if (addOnsParams.withNodeEditor)
        {
            assert(_NODE_EDITOR_CONTEXT.has_value());
            ax::NodeEditor::DestroyEditor(*_NODE_EDITOR_CONTEXT);
            _NODE_EDITOR_CONTEXT = std::nullopt;
        }
    }

    void Run(const HelloImGui::SimpleRunnerParams& simpleParams, const AddOnsParams& addOnsParams)
    {
        HelloImGui::RunnerParams runnerParams = simpleParams.ToRunnerParams();
        Run(runnerParams, addOnsParams);
    }


    void Run(
        // HelloImGui::SimpleRunnerParams below:
        const VoidFunction& guiFunction,
        const std::string& windowTitle,
        bool windowSizeAuto,
        bool windowRestorePreviousGeometry,
        const ScreenSize& windowSize,
        float fpsIdle,

        // ImGuiBundle_AddOnsParams below:
        bool withImplot,
        bool withMarkdown,
        bool withNodeEditor,
        const std::optional<NodeEditorConfig>& withNodeEditorConfig,
        const std::optional<ImGuiMd::MarkdownOptions> & withMarkdownOptions
    )
    {
        HelloImGui::SimpleRunnerParams simpleRunnerParams;
        simpleRunnerParams.guiFunction = guiFunction;
        simpleRunnerParams.windowTitle = windowTitle;
        simpleRunnerParams.windowSizeAuto = windowSizeAuto;
        simpleRunnerParams.windowRestorePreviousGeometry = windowRestorePreviousGeometry;
        simpleRunnerParams.windowSize = windowSize;
        simpleRunnerParams.fpsIdle = fpsIdle;

        AddOnsParams addOnsParams;
        addOnsParams.withImplot = withImplot;
        addOnsParams.withMarkdown = withMarkdown;
        addOnsParams.withNodeEditor = withNodeEditor;
        addOnsParams.withNodeEditorConfig = withNodeEditorConfig;
        addOnsParams.withMarkdownOptions = withMarkdownOptions;

        Run(simpleRunnerParams, addOnsParams);
    }


    ax::NodeEditor::EditorContext* CurrentNodeEditorContext()
    {
        if (!_NODE_EDITOR_CONTEXT.has_value())
            throw std::runtime_error("No current node editor context\n"
                                     "    Did you set with_node_editor_config when calling ImGuiBundle::Run()?");
        return *_NODE_EDITOR_CONTEXT;
    }


    class ClockSeconds_
    {
        // Typical C++ shamanic incantations to get a time in seconds
    private:
        using Clock = std::chrono::high_resolution_clock;
        using second = std::chrono::duration<double, std::ratio<1>>;
        std::chrono::time_point<Clock> mStart;

    public:
        ClockSeconds_() : mStart(Clock::now()) {}

        double elapsed() const
        {
            return std::chrono::duration_cast<second>
                (Clock::now() - mStart).count();
        }
    };

    double ClockSeconds()
    {
        static ClockSeconds_ watch;
        return watch.elapsed();
    }


}