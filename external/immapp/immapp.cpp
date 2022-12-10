#include "immapp.h"

#include "implot/implot.h"
#include "imgui-node-editor/imgui_node_editor_internal.h"
#include "ImFileDialogTextureHelper.h"

#include "imgui_tex_inspect/imgui_tex_inspect.h"
#include "imgui_tex_inspect/backends/tex_inspect_opengl.h"
#include "hello_imgui/hello_imgui.h"

#include <chrono>


namespace HelloImGui
{
    // Private API, not mentioned in headers!
    std::string GlslVersion();
}


#include "imgui_tex_inspect/imgui_tex_inspect_demo.h"
namespace ImGuiTexInspect
{
    Texture LoadTexture(const char * path)
    {
        auto textureId = HelloImGui::ImTextureIdFromAsset(path);
        Texture r;
        r.size = ImVec2(512.f, 512.f); // This function is only by used the demo, which uses a 51x512 image
        r.texture = textureId;
        return r;
    }
}


namespace ImmApp
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

        if (addOnsParams.withTexInspect)
        {
            ImGuiTexInspect::Context * ctxTexInspect = nullptr;
            // Modify post-init: call ImGuiTexInspect::ImplOpenGL3_Init
            {
                auto oldPostInit = runnerParams.callbacks.PostInit;
                auto newPostInit = [oldPostInit, &ctxTexInspect]() {
                    ImGuiTexInspect::ImplOpenGL3_Init(HelloImGui::GlslVersion().c_str());
                    ImGuiTexInspect::Init();
                    ctxTexInspect = ImGuiTexInspect::CreateContext();

                    if (oldPostInit)
                        oldPostInit();
                };
                runnerParams.callbacks.PostInit = newPostInit;
            }
            // Modify before-exit: call ImGuiTexInspect::ImplOpenGL3_Init
            {
                auto oldBeforeExit = runnerParams.callbacks.BeforeExit;
                auto newBeforeExit = [oldBeforeExit, &ctxTexInspect]() {
                    ImGuiTexInspect::Shutdown();
                    ImGuiTexInspect::DestroyContext(ctxTexInspect);

                    ImGuiTexInspect::ImplOpenGl3_Shutdown();
                    if (oldBeforeExit)
                        oldBeforeExit();
                };
                runnerParams.callbacks.BeforeExit = newBeforeExit;
            }
        }

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


    ax::NodeEditor::EditorContext* CurrentNodeEditorContext()
    {
        if (!_NODE_EDITOR_CONTEXT.has_value())
            throw std::runtime_error("No current node editor context\n"
                                     "    Did you set with_node_editor_config when calling ImmApp::Run()?");
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

    float VisibleFontSize()
    {
        IM_ASSERT(GImGui != NULL); // Can only be called after ImGui context was created!
        float r = ImGui::GetFontSize() / ImGui::GetIO().FontGlobalScale;
        return r;
    }

    float EmSize()
    {
        return VisibleFontSize();
    }


} // namespace ImmApp