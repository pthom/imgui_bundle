#include "immapp.h"

#include "implot/implot.h"
#include "bundle_integration/ImFileDialogTextureHelper.h"

#include "imgui_tex_inspect/imgui_tex_inspect.h"
#include "imgui_tex_inspect/backends/tex_inspect_opengl.h"
#include "hello_imgui/hello_imgui.h"
#include "hello_imgui/internal/functional_utils.h"
#ifdef IMGUI_BUNDLE_WITH_IMMVISION
#include "immvision/immvision.h"
#endif

#include <chrono>
#include <cassert>


// Private API used by ImGuiTexInspect (not mentioned in headers!)
namespace HelloImGui { std::string GlslVersion(); }


namespace ImmApp
{

    struct ImmAppContext
    {
        std::optional<ax::NodeEditor::EditorContext *> _NodeEditorContext;
        ax::NodeEditor::Config _NodeEditorConfig;
        ImGuiTexInspect::Context * _ImGuiTextInspect_Context = nullptr;
    };

    ImmAppContext gImmAppContext;


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
                gImmAppContext._NodeEditorConfig = addOnsParams.withNodeEditorConfig.value();
            gImmAppContext._NodeEditorContext = ax::NodeEditor::CreateEditor(&gImmAppContext._NodeEditorConfig);
            ax::NodeEditor::SetCurrentEditor(gImmAppContext._NodeEditorContext.value());
        }

        // load markdown fonts if needed
        if (addOnsParams.withMarkdown || addOnsParams.withMarkdownOptions.has_value())
        {
            if (!addOnsParams.withMarkdownOptions.has_value())
                addOnsParams.withMarkdownOptions = ImGuiMd::MarkdownOptions();
            ImGuiMd::InitializeMarkdown(addOnsParams.withMarkdownOptions.value());

            runnerParams.callbacks.LoadAdditionalFonts = HelloImGui::FunctionalUtils::sequence_functions(
                runnerParams.callbacks.LoadAdditionalFonts,
                ImGuiMd::GetFontLoaderFunction());
        }

        ImFileDialogSetupTextureLoader();

        if (addOnsParams.withTexInspect)
        {
            // Modify post-init: Init ImGuiTexInspect
            {
                auto fn_ImGuiTextInspect_Init = [](){
                    ImGuiTexInspect::ImplOpenGL3_Init(HelloImGui::GlslVersion().c_str());
                    ImGuiTexInspect::Init();
                    gImmAppContext._ImGuiTextInspect_Context = ImGuiTexInspect::CreateContext();
                };
                runnerParams.callbacks.PostInit = HelloImGui::FunctionalUtils::sequence_functions(
                    fn_ImGuiTextInspect_Init,
                    runnerParams.callbacks.PostInit
                    );
            }

            // Modify before-exit: DeInit ImGuiTexInspect
            {
                auto fn_ImGuiTextInspect_DeInit = [](){
                    ImGuiTexInspect::Shutdown();
                    ImGuiTexInspect::DestroyContext(gImmAppContext._ImGuiTextInspect_Context);
                    ImGuiTexInspect::ImplOpenGl3_Shutdown();
                };
                runnerParams.callbacks.BeforeExit = HelloImGui::FunctionalUtils::sequence_functions(
                    fn_ImGuiTextInspect_DeInit,
                    runnerParams.callbacks.BeforeExit
                    );
            }
        }

#ifdef IMGUI_BUNDLE_WITH_IMMVISION
        // Clear ImmVision cache, before OpenGl is uninitialized
        runnerParams.callbacks.BeforeExit = HelloImGui::FunctionalUtils::sequence_functions(
            runnerParams.callbacks.BeforeExit,
            ImmVision::ClearTextureCache);
#endif
        HelloImGui::Run(runnerParams);

        if (addOnsParams.withImplot)
            ImPlot::DestroyContext();

        if (addOnsParams.withNodeEditor)
        {
            assert(gImmAppContext._NodeEditorContext.has_value());
            ax::NodeEditor::DestroyEditor(*gImmAppContext._NodeEditorContext);
            gImmAppContext._NodeEditorContext = std::nullopt;
        }

        if (addOnsParams.withMarkdown || addOnsParams.withMarkdownOptions.has_value())
            ImGuiMd::DeInitializeMarkdown();

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
        bool withTexInspect,
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
        addOnsParams.withTexInspect = withTexInspect;
        addOnsParams.withNodeEditorConfig = withNodeEditorConfig;
        addOnsParams.withMarkdownOptions = withMarkdownOptions;

        Run(simpleRunnerParams, addOnsParams);
    }


    void RunWithMarkdown(
        // HelloImGui::SimpleRunnerParams below:
        const VoidFunction& guiFunction,
        const std::string& windowTitle,
        bool windowSizeAuto,
        bool windowRestorePreviousGeometry,
        const ScreenSize& windowSize,
        float fpsIdle,

        // ImGuiBundle_AddOnsParams below:
        bool withImplot,
        bool withNodeEditor,
        bool withTexInspect,
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
        addOnsParams.withMarkdown = true;
        addOnsParams.withNodeEditor = withNodeEditor;
        addOnsParams.withTexInspect = withTexInspect;
        addOnsParams.withNodeEditorConfig = withNodeEditorConfig;
        addOnsParams.withMarkdownOptions = withMarkdownOptions;

        Run(simpleRunnerParams, addOnsParams);
    }

    float EmSize()
    {
        return HelloImGui::EmSize();
    }
    ImVec2 EmToVec2(float x, float y)
    {
        return HelloImGui::EmToVec2(x, y);
    }
    ImVec2 EmToVec2(ImVec2 v)
    {
        return HelloImGui::EmToVec2(v);
    }
    float EmSize(float nbLines)
    {
        return HelloImGui::EmSize(nbLines);
    }


    ax::NodeEditor::EditorContext* DefaultNodeEditorContext()
    {
        if (!gImmAppContext._NodeEditorContext.has_value())
            throw std::runtime_error("No current node editor context\n"
                                     "    Did you set with_node_editor_config when calling ImmApp::Run()?");
        return *gImmAppContext._NodeEditorContext;
    }

} // namespace ImmApp