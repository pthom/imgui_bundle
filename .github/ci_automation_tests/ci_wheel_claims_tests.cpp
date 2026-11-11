// Tests of the zoomable widgets in a page that scrolls: each one must keep the wheel while hovered
//    ci_wheel_claims_tests                run all the cases, then exit (exit code 0 if they all passed)
//    ci_wheel_claims_tests implot         same, with a filter on the case names
//
// A widget that zooms with the wheel must own it (ImGui::SetKeyOwner, both axes) while hovered: otherwise the window
// around it scrolls instead, or Dear ImGui locks the wheel to that window after a trackpad gesture's sideways part.
// Each case shows a widget in a window that scrolls both ways, sends four wheel events over it with a sideways part
// (as a trackpad's zoom), and checks that each one zoomed the widget and that the page stayed still; then, beside
// the widget, that the wheel scrolls the page.
#ifdef HELLOIMGUI_WITH_TEST_ENGINE
#include "immapp/immapp.h"
#include "hello_imgui/hello_imgui.h"
#include "imgui.h"
#include "imgui_internal.h"
#include "imgui_test_engine/imgui_te_engine.h"
#include "imgui_test_engine/imgui_te_context.h"
#include "imgui_tex_inspect/imgui_tex_inspect.h"
#include "imgui_tex_inspect/imgui_tex_inspect_internal.h"
#include "ImCurveEdit.h"
#include "GraphEditor.h"
#include "ImVectorEditor.h"
#include "implot/implot.h"
#include "implot3d/implot3d.h"
#include "implot3d/implot3d_internal.h"

#include <cstdio>

// The context ImmApp created: imgui_tex_inspect has no getter for it (defined in imgui_tex_inspect.cpp)
namespace ImGuiTexInspect { extern Context* GContext; }

enum class Widget { None, TexInspect, CurveEdit, GraphEditor, VectorEditor, ImPlot, ImPlot3D };
static Widget gWidget = Widget::None;
static ImRect gWidgetRect;
static float gMetric = 0.f;  // the widget's zoom: it changes at each wheel event that reaches the widget
static bool gResetScroll = false;
static const char* gFilter = "wheel";
static int gCasesRun = 0, gFailures = 0;
static bool gTestsQueued = false;

struct CurveDelegate : ImCurveEdit::Delegate
{
    ImVec2 points[3] = {{0.f, 0.f}, {0.5f, 0.8f}, {1.f, 0.2f}};
    ImVec2 min = {0.f, 0.f}, max = {1.f, 1.f};
    size_t GetCurveCount() override { return 1; }
    ImVec2& GetMin() override { return min; }
    ImVec2& GetMax() override { return max; }
    size_t GetPointCount(size_t) override { return 3; }
    uint32_t GetCurveColor(size_t) override { return 0xFF00FF00; }
    ImVec2* GetPoints(size_t) override { return points; }
    int EditPoint(size_t, int, ImVec2) override { return 0; }
    void AddPoint(size_t, ImVec2) override {}
};
static CurveDelegate gCurveDelegate;

struct GraphDelegate : GraphEditor::Delegate  // an empty graph: the view zooms all the same
{
    using NodeIndex = GraphEditor::NodeIndex;
    using SlotIndex = GraphEditor::SlotIndex;
    bool AllowedLink(NodeIndex, NodeIndex) override { return false; }
    void SelectNode(NodeIndex, bool) override {}
    void MoveSelectedNodes(const ImVec2) override {}
    void AddLink(NodeIndex, SlotIndex, NodeIndex, SlotIndex) override {}
    void DelLink(GraphEditor::LinkIndex) override {}
    void CustomDraw(ImDrawList*, ImRect, NodeIndex) override {}
    void RightClick(NodeIndex, SlotIndex, SlotIndex) override {}
    const size_t GetTemplateCount() override { return 0; }
    const GraphEditor::Template GetTemplate(GraphEditor::TemplateIndex) override { return {}; }
    const size_t GetNodeCount() override { return 0; }
    const GraphEditor::Node GetNode(NodeIndex) override { return {}; }
    const size_t GetLinkCount() override { return 0; }
    const GraphEditor::Link GetLink(GraphEditor::LinkIndex) override { return {}; }
};
static GraphDelegate gGraphDelegate;
static GraphEditor::ViewState gGraphView;
static ImVectorEditor::Editor gVectorEditor;
static ImVectorEditor::Path gVectorPath;
static float gVectorZoom = 1.f;  // the product of the zoom factors the vector editor asked for

static void ShowWidget()
{
    const ImVec2 size(300.f, 250.f);
    if (gWidget == Widget::TexInspect)
    {
        ImTextureData* atlas = ImGui::GetIO().Fonts->TexData;  // the font atlas: a texture to inspect
        if (atlas->TexID != ImTextureID_Invalid)
        {
            ImVec2 textureSize((float)atlas->Width, (float)atlas->Height);
            if (ImGuiTexInspect::BeginInspectorPanel("inspector", atlas->TexID, textureSize, 0,
                                                     ImGuiTexInspect::SizeIncludingBorder(size)))
            {
                auto* inspector = ImGuiTexInspect::GetByKey(ImGuiTexInspect::GContext,
                                                            ImGuiTexInspect::CurrentInspector_GetID());
                gMetric = inspector->Scale.y;
            }
            ImGuiTexInspect::EndInspectorPanel();
            gWidgetRect = ImRect(ImGui::GetItemRectMin(), ImGui::GetItemRectMax());
        }
    }
    else if (gWidget == Widget::CurveEdit)
    {
        ImCurveEdit::Edit(gCurveDelegate, size, 1234);
        gWidgetRect = ImRect(ImGui::GetItemRectMin(), ImGui::GetItemRectMax());
        gMetric = gCurveDelegate.max.y - gCurveDelegate.min.y;
    }
    else if (gWidget == Widget::GraphEditor)
    {
        // The graph fills the space it is given: a child of a fixed size
        ImGui::BeginChild("graph_host", size, 0, ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoScrollWithMouse);
        GraphEditor::Options options;
        options.mMaxZoom = 10.f;  // the default (1.1) stops the zoom after one step
        GraphEditor::Show(gGraphDelegate, options, gGraphView, true);
        ImGui::EndChild();
        gWidgetRect = ImRect(ImGui::GetItemRectMin(), ImGui::GetItemRectMax());
        gMetric = gGraphView.mFactorTarget;
    }
    else if (gWidget == Widget::VectorEditor)
    {
        ImVectorEditor::Config config;
        config.canvasSize = size;
        ImVec2 origin = ImGui::GetCursorScreenPos();
        ImVectorEditor::Result result = gVectorEditor.Draw("vector", gVectorPath, config);
        gVectorZoom *= result.viewZoomFactor;
        gWidgetRect = ImRect(origin, ImVec2(origin.x + size.x, origin.y + size.y));
        gMetric = gVectorZoom;
    }
    else if (gWidget == Widget::ImPlot)
    {
        if (ImPlot::BeginPlot("plot", size))
        {
            gMetric = (float)ImPlot::GetPlotLimits().Y.Size();
            ImVec2 pos = ImPlot::GetPlotPos(), plotSize = ImPlot::GetPlotSize();
            gWidgetRect = ImRect(pos, ImVec2(pos.x + plotSize.x, pos.y + plotSize.y));
            ImPlot::EndPlot();
        }
    }
    else if (gWidget == Widget::ImPlot3D)
    {
        if (ImPlot3D::BeginPlot("plot3d", size))
        {
            ImPlot3DPlot* plot = ImPlot3D::GetCurrentPlot();
            gMetric = (float)plot->Axes[0].Range.Size();
            gWidgetRect = plot->PlotRect;
            ImPlot3D::EndPlot();
        }
    }
}

static void Gui()
{
    ImGui::SetNextWindowPos(ImVec2(0.f, 0.f));
    ImGui::SetNextWindowSize(ImVec2(500.f, 400.f));
    if (gResetScroll)
    {
        ImGui::SetNextWindowScroll(ImVec2(0.f, 0.f));
        gResetScroll = false;
    }
    ImGui::Begin("Page", nullptr, ImGuiWindowFlags_HorizontalScrollbar | ImGuiWindowFlags_NoSavedSettings);
    ImGui::Dummy(ImVec2(0.f, 30.f));
    ShowWidget();
    ImGui::Dummy(ImVec2(900.f, 400.f));  // the page scrolls both ways
    ImGui::End();

    // Queue the cases once the app is settled, exit when they are done
    ImGuiTestEngine* engine = HelloImGui::GetImGuiTestEngine();
    if (!gTestsQueued && ImGui::GetFrameCount() > 3)
    {
        ImGuiTestEngineIO& io = ImGuiTestEngine_GetIO(engine);
        io.ConfigLogToTTY = true;                    // so that a failure can be read in the CI log
        io.ConfigRunSpeed = ImGuiTestRunSpeed_Fast;  // teleport the mouse, skip the delays
        io.ConfigNoThrottle = true;
        ImGuiTestEngine_QueueTests(engine, ImGuiTestGroup_Tests, gFilter);
        gTestsQueued = true;
    }
    else if (gTestsQueued && ImGuiTestEngine_IsTestQueueEmpty(engine))
        HelloImGui::GetRunnerParams()->appShallExit = true;
}

static void RunWheelCase(ImGuiTestContext* ctx, Widget widget, const char* name)
{
    gWidget = widget;
    gResetScroll = true;
    ctx->Yield(5);
    ctx->MouseMoveToPos(gWidgetRect.GetCenter());
    ctx->Yield(5);  // the widget claims the wheel while hovered: the claim holds from the next frame
    int zooms = 0;
    for (int i = 0; i < 4; i++)
    {
        float before = gMetric;
        ctx->MouseWheel(ImVec2(-0.3f, 1.f));
        ctx->Yield(3);
        if (gMetric != before)
            zooms++;
    }
    ImGuiWindow* page = ImGui::FindWindowByName("Page");
    ImVec2 scrollAfterZoom = page->Scroll;

    // Beside the widget, the wheel scrolls the page: the claim holds only while the widget is hovered
    ctx->MouseMoveToPos(ImVec2(gWidgetRect.GetCenter().x, gWidgetRect.Max.y + 30.f));
    ctx->Yield(5);
    ctx->MouseWheel(ImVec2(0.f, -1.f));
    ctx->Yield(5);
    float pageScrolledBy = page->Scroll.y - scrollAfterZoom.y;

    bool ok = (zooms == 4) && (scrollAfterZoom.x == 0.f) && (scrollAfterZoom.y == 0.f) && (pageScrolledBy > 0.f);
    printf("%-11s %s: %d/4 wheel events zoomed, page scroll (%.1f, %.1f); beside it, the page scrolled by %.1f\n",
           name, ok ? "PASS" : "FAIL", zooms, scrollAfterZoom.x, scrollAfterZoom.y, pageScrolledBy);
    gCasesRun++;
    if (!ok)
        gFailures++;
    gWidget = Widget::None;
}

static void RegisterTests()
{
    ImGuiTestEngine* engine = HelloImGui::GetImGuiTestEngine();
    struct Case { const char* name; Widget widget; };
    static const Case cases[] = {{"tex_inspect", Widget::TexInspect}, {"curve_edit", Widget::CurveEdit},
                                 {"graph_edit", Widget::GraphEditor}, {"vector_edit", Widget::VectorEditor},
                                 {"implot", Widget::ImPlot}, {"implot3d", Widget::ImPlot3D}};
    for (const Case& c : cases)
    {
        ImGuiTest* t = IM_REGISTER_TEST(engine, "wheel", c.name);
        t->UserData = (void*)&c;
        t->TestFunc = [](ImGuiTestContext* ctx) {
            const Case* c = (const Case*)ctx->Test->UserData;
            RunWheelCase(ctx, c->widget, c->name);
        };
    }
}

int main(int argc, char** argv)
{
    if (argc > 1)
        gFilter = argv[1];
    HelloImGui::RunnerParams params;
    params.appWindowParams.windowTitle = "wheel claims tests";
    params.appWindowParams.windowGeometry.size = {520, 420};
    params.imGuiWindowParams.defaultImGuiWindowType = HelloImGui::DefaultImGuiWindowType::NoDefaultWindow;
    params.iniDisable = true;
    params.useImGuiTestEngine = true;
    params.fpsIdling.enableIdling = false;  // run as fast as possible: the duration is mostly a number of frames
    params.callbacks.ShowGui = Gui;
    params.callbacks.RegisterTests = RegisterTests;
    ImmApp::AddOnsParams addons;
    addons.withImplot = true;
    addons.withImplot3d = true;
    addons.withTexInspect = true;
    ImmApp::Run(params, addons);

    printf("wheel claims tests: %d / %d passed\n", gCasesRun - gFailures, gCasesRun);
    return (gCasesRun > 0 && gFailures == 0) ? 0 : 1;
}
#else // HELLOIMGUI_WITH_TEST_ENGINE
#include <cstdio>
int main() {
    fprintf(stderr, "This app is not built with HELLOIMGUI_WITH_TEST_ENGINE\n");
}
#endif // HELLOIMGUI_WITH_TEST_ENGINE
