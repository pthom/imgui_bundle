// Slide 8: Web Deployment — static screenshot
// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "hello_imgui/hello_imgui.h"
#include "immapp/browse_to_url.h"
#include "immapp/immapp.h"
#include "demo_utils/animate_logo.h"
#include "demo_utils/api_demos.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include "implot/implot.h"
#endif

#include "implot3d/implot3d.h"

#ifdef IMGUI_BUNDLE_WITH_IMMVISION
#include "immvision/immvision.h"
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>
#endif

#include "imgui-knobs/imgui-knobs.h"
#include "imgui_toggle/imgui_toggle.h"
#include "imgui_toggle/imgui_toggle_presets.h"

#ifdef HELLOIMGUI_HAS_OPENGL
#include "hello_imgui/hello_imgui_include_opengl.h"
#include <iostream>
#endif

#include <cmath>
#include <vector>
#include <memory>

#include "hello_imgui/icons_font_awesome_6.h"


// ============================================================================
// Test engine automation (unchanged)
// ============================================================================

#ifdef HELLOIMGUI_WITH_TEST_ENGINE
#include "imgui_test_engine/imgui_te_engine.h"
#include "imgui_test_engine/imgui_te_context.h"
#include "imgui_test_engine/imgui_te_ui.h"

ImGuiTest* AutomationShowMeImmediateApps()
{
    ImGuiTestEngine *engine = HelloImGui::GetImGuiTestEngine();

    ImGuiTest* automation = IM_REGISTER_TEST(engine, "Automation", "ShowMeImmediateApps");
    auto testFunc = [](ImGuiTestContext *ctx) {
        const char* tabImmAppsName = "//**/Demo Apps";
        const char* tabIntroName = "//**/Intro";

        ctx->MouseMove(tabImmAppsName);
        ctx->MouseClick(0);
        ctx->ItemClick("//**/demo_docking/View code");
        ctx->ItemClick("//**/demo_assets_addons/View code");
        ctx->ItemClick("//**/demo_hello_world/View code");
        ctx->MouseMove("//**/demo_hello_world/Run");
        ctx->MouseMove(tabIntroName);
        ctx->MouseClick(0);
    };
    automation->TestFunc = testFunc;
    return automation;
}
#endif // #ifdef HELLOIMGUI_WITH_TEST_ENGINE


// ============================================================================
// Carousel infrastructure
// ============================================================================

struct CarouselSlide
{
    const char* title;       // bold heading
    const char* description; // one-liner below
    void (*guiFunc)(ImVec2 contentSize);
};

// Exponential smoothing: approaches target with a given speed (higher = faster)
static float SmoothDamp(float current, float target, float speed, float dt)
{
    return current + (target - current) * (1.0f - expf(-speed * dt));
}

// Draw a colored rounded-rect background, then run drawWidgets inside a child window.
template<typename F>
static void DrawSidePanel(const char* id, float width, float height, F drawWidgets)
{
    float em = HelloImGui::EmSize();
    ImVec2 panelPos = ImGui::GetCursorScreenPos();
    ImDrawList* dl = ImGui::GetWindowDrawList();

    ImVec4 accent = ImGui::GetStyleColorVec4(ImGuiCol_ButtonHovered);
    ImU32 bg = ImGui::ColorConvertFloat4ToU32(ImVec4(accent.x, accent.y, accent.z, 0.08f));
    ImU32 border = ImGui::ColorConvertFloat4ToU32(ImVec4(accent.x, accent.y, accent.z, 0.3f));
    float rounding = em * 0.4f;

    dl->AddRectFilled(panelPos, ImVec2(panelPos.x + width, panelPos.y + height), bg, rounding);
    dl->AddRect(panelPos, ImVec2(panelPos.x + width, panelPos.y + height), border, rounding, 0, 1.5f);

    ImGui::BeginChild(id, ImVec2(width, height), false,
                      ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoBackground);
    float pad = em * 0.5f;
    ImGui::SetCursorPos(ImVec2(pad, pad));
    ImGui::PushItemWidth((width - pad * 2.f) * 0.5f);
    drawWidgets();
    ImGui::PopItemWidth();
    ImGui::EndChild();
}


// ============================================================================
// Slide 1: Lorenz — ImPlot3D attractor with dual trajectories
// ============================================================================

namespace IntroLorenz
{
    struct LorenzParams {
        float sigma = 10.0f;
        float rho = 28.0f;
        float beta = 8.0f / 3.0f;
        float dt = 0.01f;
        int max_size = 2000;
    };

    static LorenzParams sParams;

    class AnimatedLorenzTrajectory {
    public:
        AnimatedLorenzTrajectory(float x, float y, float z) : xs({x}), ys({y}), zs({z}) {}
        void step() {
            float x = xs.back(), y = ys.back(), z = zs.back();
            float dx = sParams.sigma * (y - x);
            float dy = x * (sParams.rho - z) - y;
            float dz = x * y - sParams.beta * z;
            x += dx * sParams.dt;
            y += dy * sParams.dt;
            z += dz * sParams.dt;
            xs.push_back(x); ys.push_back(y); zs.push_back(z);
            if (xs.size() > (size_t)sParams.max_size) {
                xs.erase(xs.begin()); ys.erase(ys.begin()); zs.erase(zs.begin());
            }
        }
        std::vector<float> xs, ys, zs;
    };

    static std::unique_ptr<AnimatedLorenzTrajectory> sTraj1, sTraj2;
    static bool sInited = false;
    static float sInitialDelta = 0.1f;

    void InitTrajectories()
    {
        sTraj1 = std::make_unique<AnimatedLorenzTrajectory>(0.f, 1.f, 1.05f);
        sTraj2 = std::make_unique<AnimatedLorenzTrajectory>(0.f + sInitialDelta, 1.f, 1.05f);
    }

    void GuiMainPart(ImVec2 plotSize)
    {
        if (!sInited)
        {
            sInited = true;
            InitTrajectories();
        }

        if (ImPlot3D::BeginPlot("Lorenz##intro", plotSize))
        {
            ImPlot3D::SetupAxes("X", "Y", "Z",
                                ImPlot3DAxisFlags_AutoFit,
                                ImPlot3DAxisFlags_AutoFit,
                                ImPlot3DAxisFlags_AutoFit);
            ImPlot3D::PlotLine("Trajectory", sTraj1->xs.data(), sTraj1->ys.data(), sTraj1->zs.data(), (int)sTraj1->xs.size());
            ImPlot3D::PlotLine("Trajectory2", sTraj2->xs.data(), sTraj2->ys.data(), sTraj2->zs.data(), (int)sTraj2->xs.size());
            ImPlot3D::EndPlot();
        }
        sTraj1->step();
        sTraj2->step();
    }

    void GuiSidePanel()
    {
        ImGui::TextDisabled("Butterfly Effect");
        ImGui::SetItemTooltip(
            "Tiny changes in initial conditions lead to\n"
            "completely different trajectories \xe2\x80\x94\n"
            "the hallmark of deterministic chaos.");
        ImGui::Spacing();
        ImGui::SliderFloat("Sigma", &sParams.sigma, 0.0f, 100.0f);
        ImGui::SetItemTooltip("Rate of divergence (chaos level)");
        ImGui::SliderFloat("Rho", &sParams.rho, 0.0f, 100.0f);
        ImGui::SetItemTooltip("Size and shape of the attractor");
        ImGui::SliderFloat("Beta", &sParams.beta, 0.0f, 10.0f);
        ImGui::SetItemTooltip("Damping on vertical movement");
        ImGui::SliderFloat("dt", &sParams.dt, 0.0f, 0.05f);
        ImGui::SetItemTooltip("Time step (smaller = smoother)");
        ImGui::SliderFloat("Delta", &sInitialDelta, 0.0f, 0.2f);
        ImGui::SetItemTooltip("Initial difference between trajectories");
        if (ImGui::Button("Reset"))
            InitTrajectories();
    }

    void SlideGui(ImVec2 contentSize)
    {
        float em = HelloImGui::EmSize();
        float mainSide = contentSize.y;
        float gap = em * 0.5f;
        float sidePanelW = contentSize.x - mainSide - gap;

        GuiMainPart(ImVec2(mainSide, mainSide));

        if (sidePanelW > em * 4.f)
        {
            ImGui::SameLine(0.f, gap);
            DrawSidePanel("##lorenz_side", sidePanelW, mainSide, GuiSidePanel);
        }
    }
} // namespace IntroLorenz


// ============================================================================
// Slide 3: Telemetry — ImPlot subplots with scrolling signals
// ============================================================================
#ifdef IMGUI_BUNDLE_WITH_IMPLOT

namespace IntroTelemetry
{
    struct Channel {
        std::vector<float> times, values;
        int maxSize = 2000;
        void AddPoint(float t, float v) {
            times.push_back(t);
            values.push_back(v);
            if ((int)times.size() > maxSize) {
                times.erase(times.begin());
                values.erase(values.begin());
            }
        }
    };

    static Channel sChannels[4];
    static float sTime = 0.f;
    static float sSpeed = 20.0f;
    static bool sPaused = false;
    static float sHistory = 10.0f;

    static float PseudoNoise(float t) {
        return sinf(t * 37.1f) * sinf(t * 53.7f);
    }

    static void Update()
    {
        if (sPaused) return;
        float dt = ImGui::GetIO().DeltaTime * sSpeed;
        sTime += dt;
        float pi = 3.14159265f;
        sChannels[0].AddPoint(sTime, sinf(2.f * pi * 0.5f * sTime));
        sChannels[1].AddPoint(sTime, 0.5f * sinf(2.f * pi * 0.3f * sTime) + 0.3f * PseudoNoise(sTime));
        sChannels[2].AddPoint(sTime, sinf(2.f * pi * 0.4f * sTime) > 0.f ? 1.f : -1.f);
        sChannels[3].AddPoint(sTime, 0.6f * sinf(2.f * pi * 0.7f * sTime) + 0.3f * sinf(2.f * pi * 2.3f * sTime));
    }

    void GuiMainPart(ImVec2 plotSize)
    {
        Update();

        static const char* labels[] = {"Voltage", "Pressure", "Digital", "Vibration"};
        static const ImVec4 colors[] = {
            ImVec4(0.2f, 0.9f, 0.4f, 1.f),
            ImVec4(0.3f, 0.6f, 1.0f, 1.f),
            ImVec4(1.0f, 0.6f, 0.1f, 1.f),
            ImVec4(0.9f, 0.3f, 0.6f, 1.f),
        };

        ImPlotSubplotFlags subFlags = ImPlotSubplotFlags_LinkAllX | ImPlotSubplotFlags_NoResize;
        if (ImPlot::BeginSubplots("##Telemetry", 2, 2, plotSize, subFlags))
        {
            for (int i = 0; i < 4; i++)
            {
                if (ImPlot::BeginPlot(labels[i], ImVec2(), ImPlotFlags_NoLegend))
                {
                    ImPlot::SetupAxes(nullptr, nullptr,
                        ImPlotAxisFlags_NoTickLabels, ImPlotAxisFlags_AutoFit);
                    ImPlot::SetupAxisLimits(ImAxis_X1, sTime - sHistory, sTime, ImGuiCond_Always);

                    if (!sChannels[i].times.empty())
                    {
                        ImPlot::PlotLine(labels[i],
                            sChannels[i].times.data(), sChannels[i].values.data(),
                            (int)sChannels[i].times.size(), {ImPlotProp_LineColor, colors[i]});
                    }
                    ImPlot::EndPlot();
                }
            }
            ImPlot::EndSubplots();
        }
    }

    void GuiSidePanel()
    {
        ImGui::Checkbox("Pause", &sPaused);
        ImGui::SliderFloat("Speed", &sSpeed, 0.5f, 40.0f);
        ImGui::SliderFloat("History", &sHistory, 2.0f, 20.0f, "%.0f s");
    }

    void SlideGui(ImVec2 contentSize)
    {
        float em = HelloImGui::EmSize();
        float mainSide = contentSize.y;
        float gap = em * 0.5f;
        float sidePanelW = contentSize.x - mainSide - gap;

        GuiMainPart(ImVec2(mainSide, mainSide));

        if (sidePanelW > em * 4.f)
        {
            ImGui::SameLine(0.f, gap);
            DrawSidePanel("##telemetry_side", sidePanelW, mainSide, GuiSidePanel);
        }
    }
} // namespace IntroTelemetry

#endif // IMGUI_BUNDLE_WITH_IMPLOT


// ============================================================================
// Slide 4: Angled Headers Table — drum sequencer
// ============================================================================

namespace IntroTable
{
    static const char* instruments[] = {"kick", "snare", "hihat", "open-hh", "tom", "clap", "rim", "crash"};
    static const int kNumInstr = 8;
    static const int kNumBeats = 8;
    static bool sPattern[kNumBeats][kNumInstr];
    static bool sInited = false;
    static int sPlayhead = 0;
    static float sBpm = 140.f;
    static bool sPlaying = true;
    static float sAccum = 0.f;
    static ImVec4 sHlColor = ImVec4(0.3f, 0.5f, 1.0f, 0.25f);

    static void Init()
    {
        memset(sPattern, 0, sizeof(sPattern));
        sPattern[0][0] = sPattern[4][0] = true;  // kick
        sPattern[2][1] = sPattern[6][1] = true;  // snare
        for (int i = 0; i < kNumBeats; i += 2)
            sPattern[i][2] = true;                 // hihat
        sPattern[1][3] = sPattern[5][3] = true;   // open-hh
        sPattern[3][4] = true;                     // tom
        sPattern[6][5] = true;                     // clap
        sPattern[4][6] = sPattern[7][6] = true;   // rim
        sPattern[0][7] = true;                     // crash
    }

    static void Update()
    {
        if (!sPlaying) return;
        sAccum += ImGui::GetIO().DeltaTime;
        float beatInterval = 60.f / sBpm;
        if (sAccum >= beatInterval) {
            sAccum -= beatInterval;
            sPlayhead = (sPlayhead + 1) % kNumBeats;
        }
    }

    void GuiMainPart(ImVec2 size)
    {
        if (!sInited) { sInited = true; Init(); }
        Update();

        int totalCols = kNumInstr + 1;
        ImGuiTableFlags flags = ImGuiTableFlags_SizingFixedFit
            | ImGuiTableFlags_ScrollX | ImGuiTableFlags_ScrollY
            | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH
            | ImGuiTableFlags_HighlightHoveredColumn;

        if (ImGui::BeginTable("##drum_seq", totalCols, flags, size))
        {
            ImGui::TableSetupColumn("Beat", ImGuiTableColumnFlags_NoHide);
            for (int n = 0; n < kNumInstr; n++)
                ImGui::TableSetupColumn(instruments[n],
                    ImGuiTableColumnFlags_AngledHeader | ImGuiTableColumnFlags_WidthFixed);
            ImGui::TableSetupScrollFreeze(1, 2);

            ImGui::TableAngledHeadersRow();
            ImGui::TableHeadersRow();

            ImU32 hlCol = ImGui::ColorConvertFloat4ToU32(sHlColor);

            for (int row = 0; row < kNumBeats; row++)
            {
                ImGui::PushID(row);
                ImGui::TableNextRow();

                bool isPlayhead = (row == sPlayhead) && sPlaying;

                ImGui::TableSetColumnIndex(0);
                if (isPlayhead)
                    ImGui::TableSetBgColor(ImGuiTableBgTarget_CellBg, hlCol);
                ImGui::AlignTextToFramePadding();
                ImGui::Text("%d", row + 1);

                for (int col = 0; col < kNumInstr; col++)
                {
                    if (ImGui::TableSetColumnIndex(col + 1))
                    {
                        if (isPlayhead)
                            ImGui::TableSetBgColor(ImGuiTableBgTarget_CellBg, hlCol);
                        ImGui::PushID(col);
                        ImGui::Checkbox("", &sPattern[row][col]);
                        ImGui::PopID();
                    }
                }
                ImGui::PopID();
            }
            ImGui::EndTable();
        }
    }

    void GuiSidePanel()
    {
        float em = HelloImGui::EmSize();

        // Play/Pause toggle
        ImGui::Text("Play");
        auto toggleConfig = ImGuiTogglePresets::MaterialStyle();
        toggleConfig.Size = ImVec2(em * 2.5f, em * 1.2f);
        ImGui::Toggle("##play", &sPlaying, toggleConfig);

        // BPM knob
        ImGui::Spacing();
        ImGui::Text("Tempo");
        ImGuiKnobs::Knob("##bpm", &sBpm, 60.f, 300.f, 0.f, "%.0f",
            ImGuiKnobVariant_WiperDot, em * 3.5f, ImGuiKnobFlags_AlwaysClamp);

        // Highlight color picker
        ImGui::Spacing();
        ImGui::Text("Highlight");
        ImGuiColorEditFlags pickerFlags = ImGuiColorEditFlags_NoSidePreview
            | ImGuiColorEditFlags_NoInputs
            | ImGuiColorEditFlags_NoLabel
            | ImGuiColorEditFlags_AlphaBar
            | ImGuiColorEditFlags_PickerHueWheel;
        ImGui::ColorPicker4("##hl_wheel", &sHlColor.x, pickerFlags);
    }

    void SlideGui(ImVec2 contentSize)
    {
        float em = HelloImGui::EmSize();
        float mainSide = contentSize.y;
        float gap = em * 0.5f;
        float sidePanelW = contentSize.x - mainSide - gap;

        GuiMainPart(ImVec2(mainSide, mainSide));

        if (sidePanelW > em * 4.f)
        {
            ImGui::SameLine(0.f, gap);
            DrawSidePanel("##table_side", sidePanelW, mainSide, GuiSidePanel);
        }
    }
} // namespace IntroTable


// ============================================================================
// Slide 5: ImmVision — Image debugging with animated zoom
// ============================================================================
#ifdef IMGUI_BUNDLE_WITH_IMMVISION

namespace IntroImmVision
{
    static cv::Mat sImage;
    static cv::Mat sImageSobel;
    static ImmVision::ImageParams sParams;
    static ImmVision::ImageParams sParamsSobel;
    static bool sInited = false;
    static bool sAnimating = true;
    static double sStartTime = 0.;

    // Sobel params
    static float sBlurSize = 1.25f;
    static int sDerivOrder = 1;
    static int sKSize = 7;

    // Zoom animation
    static constexpr double kZoomInDuration = 1.5;
    static constexpr double kHoldDuration = 1.5;
    static constexpr double kZoomOutDuration = 1.5;
    static constexpr double kPauseDuration = 1.5;
    static constexpr double kTotalCycle = kZoomInDuration + kHoldDuration + kZoomOutDuration + kPauseDuration;
    static constexpr double kMinZoom = 1.0;
    static constexpr double kMaxZoom = 70.0;

    static cv::Point2d sZoomCenter;

    static cv::Mat ComputeSobel()
    {
        cv::Mat gray;
        cv::cvtColor(sImage, gray, cv::COLOR_BGR2GRAY);
        cv::Mat imgFloat;
        gray.convertTo(imgFloat, CV_32F, 1.0 / 255.0);
        cv::Mat blurred;
        cv::GaussianBlur(imgFloat, blurred, cv::Size(), sBlurSize, sBlurSize);
        double goodScale = 1.0 / std::pow(2.0, (sKSize - 2 * sDerivOrder - 2));
        cv::Mat r;
        cv::Sobel(blurred, r, CV_64F, sDerivOrder, 0, sKSize, goodScale);
        return r;
    }

    static void Init()
    {
        ImmVision::UseBgrColorOrder();
        sImage = cv::imread(DemosAssetsFolder() + "/images/house.jpg");
        sImageSobel = ComputeSobel();

        int dispW = (int)HelloImGui::EmSize(20.f);
        sParams.ImageDisplaySize = cv::Size(dispW, 0);
        sParams.ShowOptionsPanel = false;
        sParams.ShowImageInfo = false;
        sParams.ShowPixelInfo = true;
        sParams.ShowZoomButtons = false;
        sParams.ZoomKey = "intro_immvision";

        sParamsSobel.ImageDisplaySize = cv::Size(dispW, 0);
        sParamsSobel.ShowOptionsPanel = false;
        sParamsSobel.ShowImageInfo = false;
        sParamsSobel.ShowPixelInfo = true;
        sParamsSobel.ShowZoomButtons = false;
        sParamsSobel.ZoomKey = "intro_immvision";

        sZoomCenter = cv::Point2d(sImage.cols * 0.35, sImage.rows * 0.45);
        sStartTime = ImmApp::ClockSeconds();
    }

    static double CurrentZoomRatio()
    {
        double elapsed = fmod(ImmApp::ClockSeconds() - sStartTime, kTotalCycle);

        if (elapsed < kZoomInDuration) {
            double t = elapsed / kZoomInDuration;
            double eased = 1.0 - (1.0 - t) * (1.0 - t);
            return kMinZoom + (kMaxZoom - kMinZoom) * eased;
        }
        elapsed -= kZoomInDuration;
        if (elapsed < kHoldDuration)
            return kMaxZoom;
        elapsed -= kHoldDuration;
        if (elapsed < kZoomOutDuration) {
            double t = elapsed / kZoomOutDuration;
            double eased = t * t;
            return kMaxZoom - (kMaxZoom - kMinZoom) * eased;
        }
        return kMinZoom;
    }

    static bool CheckUserInteraction()
    {
        bool hovering = sParams.MouseInfo.IsMouseHovering
                     || sParamsSobel.MouseInfo.IsMouseHovering;
        if (hovering && (ImGui::IsMouseDragging(0) || ImGui::GetIO().MouseWheel != 0.f))
            return true;
        return false;
    }

    void GuiMainPart(ImVec2 size)
    {
        if (!sInited) { sInited = true; Init(); }

        // Stop animation on user interaction
        if (sAnimating && CheckUserInteraction())
            sAnimating = false;

        // Update zoom matrix while animating
        if (sAnimating)
        {
            double zoom = CurrentZoomRatio();
            sParams.ZoomPanMatrix = ImmVision::MakeZoomPanMatrix(
                sZoomCenter, zoom, sParams.ImageDisplaySize);
            sParamsSobel.ZoomPanMatrix = sParams.ZoomPanMatrix;
        }

        // Size each image to half the available width
        int halfW = (int)(size.x * 0.5f - HelloImGui::EmSize(1.5f));
        sParams.ImageDisplaySize = cv::Size(halfW, 0);
        sParamsSobel.ImageDisplaySize = cv::Size(halfW, 0);

        ImmVision::Image("Original##intro", sImage, &sParams);
        ImGui::SameLine();
        ImmVision::Image("Sobel##intro", sImageSobel, &sParamsSobel);
    }

    void GuiSidePanel()
    {
        ImGui::TextDisabled("Drag to pan, scroll to zoom");
        if (!sAnimating)
        {
            if (ImGui::Button("Restart animation"))
            {
                sAnimating = true;
                sStartTime = ImmApp::ClockSeconds();
            }
        }
        ImGui::Separator();

        bool changed = false;
        if (ImGui::SliderFloat("Blur", &sBlurSize, 0.5f, 10.0f))
            changed = true;

        ImGui::Text("Deriv order:");
        for (int order = 1; order <= 4; order++)
        {
            ImGui::SameLine();
            if (ImGui::RadioButton(std::to_string(order).c_str(), sDerivOrder == order))
            {
                sDerivOrder = order;
                changed = true;
            }
        }

        if (changed)
        {
            sImageSobel = ComputeSobel();
            sParamsSobel.RefreshImage = true;
        }
    }

    void SlideGui(ImVec2 contentSize)
    {
        float em = HelloImGui::EmSize();
        float mainW = contentSize.x;          // images use full width (they're side by side internally)
        float mainH = contentSize.y * 0.7f;   // images take ~70% height
        float gap = em * 0.5f;
        float sidePanelH = contentSize.y - mainH - gap;

        GuiMainPart(ImVec2(mainW, mainH));

        if (sidePanelH > em * 3.f)
        {
            ImGui::Spacing();
            DrawSidePanel("##immvision_side", mainW, sidePanelH, GuiSidePanel);
        }
    }
} // namespace IntroImmVision

#endif // IMGUI_BUNDLE_WITH_IMMVISION


// ============================================================================
// Slide 6: Notebook — static screenshot
// ============================================================================

namespace IntroNotebook
{
    void SlideGui(ImVec2 contentSize)
    {
        // Display the screenshot, fitting it within the content area
        // The image is landscape (~16:10 aspect ratio from the screenshot)
        float imgAspect = 1680.f / 1050.f;  // approximate from screenshot
        float w = contentSize.x;
        float h = w / imgAspect;
        if (h > contentSize.y) { h = contentSize.y; w = h * imgAspect; }
        HelloImGui::ImageFromAsset("images/imgui_notebook.jpg", ImVec2(w, h));
    }
} // namespace IntroNotebook


// ============================================================================
// Slide 7: Node Editor — static screenshot
// ============================================================================

namespace IntroNodeEditor
{
    void SlideGui(ImVec2 contentSize)
    {
        float imgAspect = 800.f / 516.f;
        float linkH = ImGui::GetFrameHeight();
        float w = contentSize.x;
        float h = w / imgAspect;
        if (h > contentSize.y - linkH) { h = contentSize.y - linkH; w = h * imgAspect; }
        HelloImGui::ImageFromAsset("images/node_editor_fiat.jpg", ImVec2(w, h));
        ImGuiMd::RenderUnindented("Built with [fiatlight](https://pthom.github.io/fiatlight_doc/)");
    }
} // namespace IntroNodeEditor


// ============================================================================
// Slide 7: Markdown rendering — side-by-side source / rendered
// ============================================================================

namespace IntroMarkdown
{
    static const char* kMarkdownSample = R"(## Quick Start Guide

**ImGui Bundle** makes it easy to build
_beautiful_ apps with rich documentation.

Features:
- Headers, **bold**, *italic*, ~~strikethrough~~
- [Clickable links](https://github.com/pthom/imgui_bundle)
- Syntax-highlighted code blocks

```python
import imgui_bundle
imgui_md.render("# Hello!")
```

Tip: *You can resize the columns on the table below!*

| Library   | Domain          |
|-----------|-----------------|
| ImPlot    | 2D plots        |
| ImPlot3D  | 3D plots        |
| ImmVision | Image analysis  |

)";

    // Markdown editor with syntax highlighting
    static TextEditor* sMarkdownEditor = nullptr;
    static bool sMarkdownEditorInitialized = false;

    void InitMarkdownEditor()
    {
        if (!sMarkdownEditorInitialized)
        {
            sMarkdownEditor = new TextEditor();
            sMarkdownEditor->SetText(kMarkdownSample);
            // Use C++ language definition as a reasonable approximation for markdown
            // (it will highlight code blocks and some syntax)
            sMarkdownEditor->SetLanguageDefinition(TextEditor::LanguageDefinitionId::Cpp);
            sMarkdownEditor->SetPalette(TextEditor::PaletteId::Dark);
            sMarkdownEditorInitialized = true;
        }
    }

    void SlideGui(ImVec2 contentSize)
    {
        InitMarkdownEditor();

        float em = HelloImGui::EmSize();
        float gap = em * 0.5f;
        float halfW = (contentSize.x - gap) * 0.5f;
        float h = contentSize.y;

        // Left panel background
        ImVec4 accent = ImGui::GetStyleColorVec4(ImGuiCol_ButtonHovered);
        ImU32 bg     = ImGui::ColorConvertFloat4ToU32(ImVec4(accent.x, accent.y, accent.z, 0.08f));
        ImU32 border = ImGui::ColorConvertFloat4ToU32(ImVec4(accent.x, accent.y, accent.z, 0.3f));
        float rounding = em * 0.4f;

        ImVec2 panelPos = ImGui::GetCursorScreenPos();
        ImDrawList* dl = ImGui::GetWindowDrawList();
        dl->AddRectFilled(panelPos, ImVec2(panelPos.x + halfW, panelPos.y + h), bg, rounding);
        dl->AddRect(panelPos, ImVec2(panelPos.x + halfW, panelPos.y + h), border, rounding, 0, 1.5f);

        // Left child: editable source with syntax highlighting
        ImGui::BeginChild("##md_source", ImVec2(halfW, h), false, ImGuiWindowFlags_NoBackground);

        // Use code font for better readability
        auto codeFont = ImGuiMd::GetCodeFont();
        ImGui::PushFont(codeFont.font, codeFont.size * 0.9f);

        // Render the text editor (it will fill the child window)
        sMarkdownEditor->Render("##md_editor");

        ImGui::PopFont();
        ImGui::EndChild();

        ImGui::SameLine(0, gap);

        // Right child: rendered markdown
        ImGui::BeginChild("##md_rendered", ImVec2(halfW, h), false, ImGuiWindowFlags_NoScrollbar);
        // Get the current text from the editor
        std::string currentMarkdown = sMarkdownEditor->GetText();
        ImGuiMd::RenderUnindented(currentMarkdown.c_str());
        ImGui::EndChild();
    }
} // namespace IntroMarkdown


// ============================================================================
// Slide 8: Source Code Viewer — Self-documenting demo
// ============================================================================

namespace IntroSourceCode
{
    void SlideGui(ImVec2 contentSize)
    {
        ImGui::BeginChild("##source_code", contentSize, false);
        ShowPythonVsCppFile("demo_imgui_bundle_intro", 25);
        ImGui::EndChild();
    }
} // namespace IntroSourceCode


// ============================================================================
// Slide 9: Web Deployment — static screenshot
// ============================================================================

namespace IntroWebDeploy
{
    void SlideGui(ImVec2 contentSize)
    {
        float imgAspect = 1024.f / 768.f;
        float w = contentSize.x;
        float h = w / imgAspect;
        if (h > contentSize.y) { h = contentSize.y; w = h * imgAspect; }
        HelloImGui::ImageFromAsset("images/bundle_playground.jpg", ImVec2(w, h));
    }
} // namespace IntroWebDeploy


// ============================================================================
// Slide 8: Seascape shader — FBO + OpenGL
// ============================================================================
#ifdef HELLOIMGUI_HAS_OPENGL

namespace IntroShader
{
    // --- OpenGL helpers ---

    struct Fbo
    {
        GLuint fbo = 0;
        GLuint texture = 0;
        int width = 0, height = 0;

        void Create(int w, int h)
        {
            width = w; height = h;
            glGenFramebuffers(1, &fbo);
            glBindFramebuffer(GL_FRAMEBUFFER, fbo);
            glGenTextures(1, &texture);
            glBindTexture(GL_TEXTURE_2D, texture);
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0);
            if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE)
                std::cerr << "FBO incomplete!" << std::endl;
            glBindFramebuffer(GL_FRAMEBUFFER, 0);
        }

        void Destroy()
        {
            if (texture) glDeleteTextures(1, &texture);
            if (fbo) glDeleteFramebuffers(1, &fbo);
            texture = fbo = 0;
        }

        void Bind() { glBindFramebuffer(GL_FRAMEBUFFER, fbo); glViewport(0, 0, width, height); }
        static void Unbind() { glBindFramebuffer(GL_FRAMEBUFFER, 0); }
    };

    GLuint CompileShader(GLuint type, const char* source)
    {
        GLuint shader = glCreateShader(type);
        glShaderSource(shader, 1, &source, NULL);
        glCompileShader(shader);
        GLint ok; glGetShaderiv(shader, GL_COMPILE_STATUS, &ok);
        if (!ok) { GLchar log[512]; glGetShaderInfoLog(shader, 512, NULL, log); std::cerr << "Shader error:\n" << log << std::endl; }
        return shader;
    }

    GLuint CreateShaderProgram(const char* vs, const char* fs)
    {
        GLuint v = CompileShader(GL_VERTEX_SHADER, vs);
        GLuint f = CompileShader(GL_FRAGMENT_SHADER, fs);
        GLuint prog = glCreateProgram();
        glAttachShader(prog, v); glAttachShader(prog, f);
        glLinkProgram(prog);
        glDeleteShader(v); glDeleteShader(f);
        return prog;
    }

    GLuint CreateQuadVAO()
    {
        float verts[] = { -1,-1,0,0, 1,-1,1,0, -1,1,0,1, 1,1,1,1 };
        GLuint vao, vbo;
        glGenVertexArrays(1, &vao); glGenBuffers(1, &vbo);
        glBindVertexArray(vao);
        glBindBuffer(GL_ARRAY_BUFFER, vbo);
        glBufferData(GL_ARRAY_BUFFER, sizeof(verts), verts, GL_STATIC_DRAW);
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, (void*)0);
        glEnableVertexAttribArray(0);
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, (void*)8);
        glEnableVertexAttribArray(1);
        glBindVertexArray(0);
        return vao;
    }

    // --- GLSL sources (GLSL 100 for max compatibility) ---

    const char* kVertSrc = R"(#version 100
precision mediump float;
attribute vec3 aPos;
attribute vec2 aTexCoord;
varying vec2 TexCoord;
void main() {
    gl_Position = vec4(aPos, 1.0);
    TexCoord = aTexCoord;
}
)";

    // Seascape by Alexander Alekseev aka TDM - 2014
    // https://www.shadertoy.com/view/Ms2SD1
    // SEA_HEIGHT, SEA_CHOPPY, SEA_BASE are uniforms for interactive sliders
    const char* kFragSrc = R"(#version 100
precision mediump float;
varying vec2 TexCoord;

uniform vec2 iResolution;
uniform float iTime;
uniform float SEA_HEIGHT;
uniform float SEA_CHOPPY;
uniform vec3 SEA_BASE;

const int NUM_STEPS = 8;
const float PI = 3.141592;
const float EPSILON = 1e-3;
#define EPSILON_NRM (0.1 / iResolution.x)

const int ITER_GEOMETRY = 3;
const int ITER_FRAGMENT = 5;
const float SEA_SPEED = 0.8;
const float SEA_FREQ = 0.16;
const vec3 SEA_WATER_COLOR = vec3(0.48, 0.54, 0.36);

#define SEA_TIME (1.0 + iTime * SEA_SPEED)
const mat2 octave_m = mat2(1.6,1.2,-1.2,1.6);

mat3 fromEuler(vec3 ang) {
    vec2 a1=vec2(sin(ang.x),cos(ang.x));
    vec2 a2=vec2(sin(ang.y),cos(ang.y));
    vec2 a3=vec2(sin(ang.z),cos(ang.z));
    mat3 m;
    m[0]=vec3(a1.y*a3.y+a1.x*a2.x*a3.x,a1.y*a2.x*a3.x+a3.y*a1.x,-a2.y*a3.x);
    m[1]=vec3(-a2.y*a1.x,a1.y*a2.y,a2.x);
    m[2]=vec3(a3.y*a1.x*a2.x+a1.y*a3.x,a1.x*a3.x-a1.y*a3.y*a2.x,a2.y*a3.y);
    return m;
}
float hash(vec2 p){float h=dot(p,vec2(127.1,311.7));return fract(sin(h)*43758.5453123);}
float noise(vec2 p){vec2 i=floor(p);vec2 f=fract(p);vec2 u=f*f*(3.0-2.0*f);return -1.0+2.0*mix(mix(hash(i+vec2(0,0)),hash(i+vec2(1,0)),u.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),u.x),u.y);}
float diffuse(vec3 n,vec3 l,float p){return pow(dot(n,l)*0.4+0.6,p);}
float specular(vec3 n,vec3 l,vec3 e,float s){float nrm=(s+8.0)/(PI*8.0);return pow(max(dot(reflect(e,n),l),0.0),s)*nrm;}
vec3 getSkyColor(vec3 e){e.y=(max(e.y,0.0)*0.8+0.2)*0.8;return vec3(pow(1.0-e.y,2.0),1.0-e.y,0.6+(1.0-e.y)*0.4)*1.1;}
float sea_octave(vec2 uv,float choppy){uv+=noise(uv);vec2 wv=1.0-abs(sin(uv));vec2 swv=abs(cos(uv));wv=mix(wv,swv,wv);return pow(1.0-pow(wv.x*wv.y,0.65),choppy);}

float map(vec3 p){float freq=SEA_FREQ;float amp=SEA_HEIGHT;float choppy=SEA_CHOPPY;vec2 uv=p.xz;uv.x*=0.75;float d,h=0.0;for(int i=0;i<ITER_GEOMETRY;i++){d=sea_octave((uv+SEA_TIME)*freq,choppy);d+=sea_octave((uv-SEA_TIME)*freq,choppy);h+=d*amp;uv*=octave_m;freq*=1.9;amp*=0.22;choppy=mix(choppy,1.0,0.2);}return p.y-h;}
float map_detailed(vec3 p){float freq=SEA_FREQ;float amp=SEA_HEIGHT;float choppy=SEA_CHOPPY;vec2 uv=p.xz;uv.x*=0.75;float d,h=0.0;for(int i=0;i<ITER_FRAGMENT;i++){d=sea_octave((uv+SEA_TIME)*freq,choppy);d+=sea_octave((uv-SEA_TIME)*freq,choppy);h+=d*amp;uv*=octave_m;freq*=1.9;amp*=0.22;choppy=mix(choppy,1.0,0.2);}return p.y-h;}

vec3 getSeaColor(vec3 p,vec3 n,vec3 l,vec3 eye,vec3 dist){float fresnel=clamp(1.0-dot(n,-eye),0.0,1.0);fresnel=min(pow(fresnel,3.0),0.5);vec3 reflected=getSkyColor(reflect(eye,n));vec3 refracted=SEA_BASE+diffuse(n,l,80.0)*SEA_WATER_COLOR*0.12;vec3 color=mix(refracted,reflected,fresnel);float atten=max(1.0-dot(dist,dist)*0.001,0.0);color+=SEA_WATER_COLOR*(p.y-SEA_HEIGHT)*0.18*atten;color+=vec3(specular(n,l,eye,60.0));return color;}
vec3 getNormal(vec3 p,float eps){vec3 n;n.y=map_detailed(p);n.x=map_detailed(vec3(p.x+eps,p.y,p.z))-n.y;n.z=map_detailed(vec3(p.x,p.y,p.z+eps))-n.y;n.y=eps;return normalize(n);}
float heightMapTracing(vec3 ori,vec3 dir,out vec3 p){float tm=0.0;float tx=1000.0;float hx=map(ori+dir*tx);if(hx>0.0){p=ori+dir*tx;return tx;}float hm=map(ori+dir*tm);float tmid=0.0;for(int i=0;i<NUM_STEPS;i++){tmid=mix(tm,tx,hm/(hm-hx));p=ori+dir*tmid;float hmid=map(p);if(hmid<0.0){tx=tmid;hx=hmid;}else{tm=tmid;hm=hmid;}}return tmid;}
vec3 getPixel(vec2 coord,float time){vec2 uv=coord/iResolution.xy;uv=uv*2.0-1.0;uv.x*=iResolution.x/iResolution.y;vec3 ang=vec3(sin(time*3.0)*0.1,sin(time)*0.2+0.3,time);vec3 ori=vec3(0.0,3.5,time*5.0);vec3 dir=normalize(vec3(uv.xy,-2.0));dir.z+=length(uv)*0.14;dir=normalize(dir)*fromEuler(ang);vec3 p;heightMapTracing(ori,dir,p);vec3 dist=p-ori;vec3 n=getNormal(p,dot(dist,dist)*EPSILON_NRM);vec3 light=normalize(vec3(0.0,1.0,0.8));return mix(getSkyColor(dir),getSeaColor(p,n,light,dir,dist),pow(smoothstep(0.0,-0.02,dir.y),0.2));}

void main(){
    vec2 fragCoord=TexCoord*iResolution;
    float time=iTime*0.3;
    vec3 color=getPixel(fragCoord,time);
    gl_FragColor=vec4(pow(color,vec3(0.65)),1.0);
}
)";

    // --- Shader state ---

    struct ShaderState
    {
        GLuint shaderProgram = 0;
        GLuint quadVAO = 0;
        Fbo fbo;
        GLint locResolution = -1, locTime = -1;
        GLint locSeaHeight = -1, locSeaChoppy = -1, locSeaBase = -1;
        int fboWidth = 600, fboHeight = 600;

        float seaHeight = 0.6f;
        float seaChoppy = 4.0f;
        float seaBase[3] = {0.0f, 0.09f, 0.18f};

        void Init()
        {
            shaderProgram = CreateShaderProgram(kVertSrc, kFragSrc);
            quadVAO = CreateQuadVAO();
            locResolution = glGetUniformLocation(shaderProgram, "iResolution");
            locTime = glGetUniformLocation(shaderProgram, "iTime");
            locSeaHeight = glGetUniformLocation(shaderProgram, "SEA_HEIGHT");
            locSeaChoppy = glGetUniformLocation(shaderProgram, "SEA_CHOPPY");
            locSeaBase = glGetUniformLocation(shaderProgram, "SEA_BASE");
            fbo.Create(fboWidth, fboHeight);
        }

        void Destroy()
        {
            fbo.Destroy();
            if (shaderProgram) glDeleteProgram(shaderProgram);
            if (quadVAO) glDeleteVertexArrays(1, &quadVAO);
            shaderProgram = 0; quadVAO = 0;
        }

        void RenderToFbo()
        {
            fbo.Bind();
            glClear(GL_COLOR_BUFFER_BIT);
            glUseProgram(shaderProgram);
            glUniform2f(locResolution, (float)fboWidth, (float)fboHeight);
            glUniform1f(locTime, (float)ImGui::GetTime());
            glUniform1f(locSeaHeight, seaHeight);
            glUniform1f(locSeaChoppy, seaChoppy);
            glUniform3f(locSeaBase, seaBase[0], seaBase[1], seaBase[2]);
            glDisable(GL_DEPTH_TEST);
            glBindVertexArray(quadVAO);
            glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
            glBindVertexArray(0);
            glUseProgram(0);
            glEnable(GL_DEPTH_TEST);
            Fbo::Unbind();
        }
    };

    static ShaderState* sState = nullptr;
    static bool sInited = false;

    void LazyInit()
    {
        if (sInited) return;
        sInited = true;
        sState = new ShaderState();
        sState->Init();
        HelloImGui::GetRunnerParams()->callbacks.EnqueueBeforeExit([]() {
            if (sState) { sState->Destroy(); delete sState; sState = nullptr; }
        });
    }

    void GuiMainPart(float width, float height)
    {
        LazyInit();
        if (sState)
        {
            sState->RenderToFbo();
            ImGui::Image(
                (ImTextureID)(intptr_t)sState->fbo.texture,
                ImVec2(width, height),
                ImVec2(0, 1), ImVec2(1, 0)  // flip Y for FBO
            );
        }
    }

    void GuiSidePanel()
    {
        ImGui::Text("\"Seascape\" by Alexander Alekseev aka TDM");
        ImGui::SetItemTooltip(
            "License: Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported\n"
            "Contact: tdmaav@gmail.com");
        ImGui::Spacing();
        if (sState)
        {
            float sliderW = HelloImGui::EmSize(7.f);
            ImGui::SetNextItemWidth(sliderW);
            ImGui::SliderFloat("Wave height", &sState->seaHeight, 0.1f, 2.0f);
            ImGui::SetNextItemWidth(sliderW);
            ImGui::SliderFloat("Choppiness", &sState->seaChoppy, 0.5f, 8.0f);
            ImGui::SetNextItemWidth(sliderW);
            ImGui::ColorEdit3("Sea base color", sState->seaBase);
        }
    }

    void SlideGui(ImVec2 contentSize)
    {
        float em = HelloImGui::EmSize();

        // Render shader filling the full content area
        GuiMainPart(contentSize.x, contentSize.y);

        // Overlay controls on top of the shader
        float overlayW = em * 18.f;
        float overlayH = em * 6.5f;
        float pad = em * 0.8f;
        float overlayX = ImGui::GetItemRectMin().x + contentSize.x - overlayW - pad;
        float overlayY = ImGui::GetItemRectMin().y + pad;

        ImDrawList* dl = ImGui::GetWindowDrawList();
        float rounding = em * 0.5f;
        float bgMargin = em * 0.3f;
        ImU32 bg = ImGui::ColorConvertFloat4ToU32(ImVec4(0.f, 0.f, 0.f, 0.35f));
        ImU32 border = ImGui::ColorConvertFloat4ToU32(ImVec4(1.f, 1.f, 1.f, 0.15f));
        dl->AddRectFilled(
            ImVec2(overlayX - bgMargin, overlayY),
            ImVec2(overlayX + overlayW, overlayY + overlayH + bgMargin),
            bg, rounding);
        dl->AddRect(
            ImVec2(overlayX - bgMargin, overlayY),
            ImVec2(overlayX + overlayW, overlayY + overlayH + bgMargin),
            border, rounding, 0, 1.f);

        ImGui::SetCursorScreenPos(ImVec2(overlayX, overlayY));
        ImGui::BeginChild("##shader_overlay", ImVec2(overlayW, overlayH), false,
                          ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoBackground);
        float innerPad = em * 0.5f;
        ImGui::SetCursorPos(ImVec2(innerPad, innerPad));
        ImGui::PushItemWidth(overlayW - innerPad * 2.f);
        GuiSidePanel();
        ImGui::PopItemWidth();
        ImGui::EndChild();
    }
} // namespace IntroShader

#endif // HELLOIMGUI_HAS_OPENGL


// ============================================================================
// Slide wrappers with #ifdef fallbacks
// ============================================================================
// These thin wrappers exist only to handle #ifdef guards for slides that
// depend on optional libraries, providing a fallback message.

#ifdef IMGUI_BUNDLE_WITH_IMPLOT
static void TelemetrySlideGui(ImVec2 cs) { IntroTelemetry::SlideGui(cs); }
#else
static void TelemetrySlideGui(ImVec2) { ImGui::TextWrapped("ImPlot not available."); }
#endif

static void LorenzSlideGui(ImVec2 cs)    { IntroLorenz::SlideGui(cs); }
static void TableSlideGui(ImVec2 cs)     { IntroTable::SlideGui(cs); }

#ifdef IMGUI_BUNDLE_WITH_IMMVISION
static void ImmVisionSlideGui(ImVec2 cs) { IntroImmVision::SlideGui(cs); }
#else
static void ImmVisionSlideGui(ImVec2)    { ImGui::TextWrapped("ImmVision not available (requires OpenCV)."); }
#endif

static void NotebookSlideGui(ImVec2 cs)    { IntroNotebook::SlideGui(cs); }
static void NodeEditorSlideGui(ImVec2 cs)  { IntroNodeEditor::SlideGui(cs); }
static void MarkdownSlideGui(ImVec2 cs)    { IntroMarkdown::SlideGui(cs); }
static void WebDeploySlideGui(ImVec2 cs)   { IntroWebDeploy::SlideGui(cs); }

#ifdef HELLOIMGUI_HAS_OPENGL
static void ShaderSlideGui(ImVec2 cs) { IntroShader::SlideGui(cs); }
#else
static void ShaderSlideGui(ImVec2)    { ImGui::TextWrapped("Shader demo requires OpenGL backend."); }
#endif


// ============================================================================
// Top section
// ============================================================================

bool IsSmallScreen()
{
    return ImGui::GetIO().DisplaySize.x < HelloImGui::EmSize() * 50.f;
}

void ShowBadges()
{
    // Push badges to the bottom of the available window space
    ImVec2 btnSize = HelloImGui::EmToVec2(0.f, 1.5f);
    float badgesHeight = btnSize.y + ImGui::GetStyle().ItemSpacing.y * 2.f;
    float availableY = ImGui::GetContentRegionAvail().y;
    if (availableY > badgesHeight)
        ImGui::SetCursorPosY(ImGui::GetCursorPosY() + availableY - badgesHeight);

    if (HelloImGui::ImageButtonFromAsset("images/badge_view_sources.png", btnSize))
        ImmApp::BrowseToUrl("https://github.com/pthom/imgui_bundle");
    ImGui::SameLine();
    if (HelloImGui::ImageButtonFromAsset("images/badge_view_docs.png", btnSize))
        ImmApp::BrowseToUrl("https://pthom.github.io/imgui_bundle");
    ImGui::SameLine();
    if (HelloImGui::ImageButtonFromAsset("images/badge_interactive_manual.png", btnSize))
        ImmApp::BrowseToUrl("https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html");
}

void IntroTopSection()
{
    bool small = IsSmallScreen();

    ImGuiMd::RenderUnindented(R"(
# Dear ImGui Bundle

*From expressive code to powerful GUIs in no time*
)");

    if (small)
    {
        static bool showFull = false;
        if (!showFull)
        {
            ImGui::TextDisabled("20+ libraries, C++ & Python, desktop/mobile/web.");
            ImGui::SameLine();
            if (ImGui::SmallButton("More..."))
                showFull = true;
        }
        if (showFull)
        {
            ImGuiMd::RenderUnindented(R"(
        A batteries-included framework built on Dear ImGui, bundling 20+ libraries - plotting, markdown, node editors, 3D gizmos, and more. Works in C++ and Python, on desktop, mobile, and web.
        Dear ImGui Bundle's immediate mode paradigm naturally leads to code that is concise, and [easy to understand](https://pthom.github.io/imgui_bundle/#code-that-reads-like-a-book), both for humans and for AI tools.
)");
            ImGui::SameLine();
            if (ImGui::SmallButton("Less"))
                showFull = false;
        }
    }
    else
    {
        ImGuiMd::RenderUnindented(R"(
        A batteries-included framework built on Dear ImGui, bundling 20+ libraries - plotting, markdown, node editors, 3D gizmos, and more. Works in C++ and Python, on desktop, mobile, and web.
        Dear ImGui Bundle's immediate mode paradigm naturally leads to code that is concise, and [easy to understand](https://pthom.github.io/imgui_bundle/#code-that-reads-like-a-book), both for humans and for AI tools.
)");
        ImGui::SameLine();
        ImGui::TextDisabled("Start your first app in 2 or 3 lines of code.");

        if (ImGui::IsItemHovered(ImGuiHoveredFlags_DelayNormal))
        {
            ImGui::BeginTooltip();
            ImGui::Dummy(HelloImGui::EmToVec2(80.f, 0.f));
            ShowPythonVsCppCode(R"(
from imgui_bundle import imgui, immapp
immapp.run(lambda: imgui.text("Hello!"))
)", R"(
#include "immapp/immapp.h"
#include "imgui.h"
int main() { ImmApp::Run([] { ImGui::Text("Hello"); }); }
)", 5);
            ImGui::EndTooltip();
        }
    }

#ifdef HELLOIMGUI_WITH_TEST_ENGINE
    static ImGuiTest *automationShowMeImmediateApps = nullptr;
    static bool wasAutomationInited = false;
    if (HelloImGui::GetRunnerParams()->useImGuiTestEngine)
    {
        if (!wasAutomationInited)
        {
            wasAutomationInited = true;
            automationShowMeImmediateApps = AutomationShowMeImmediateApps();
        }
        ImGuiTestEngineIO& engineIo = ImGuiTestEngine_GetIO(HelloImGui::GetImGuiTestEngine());
        engineIo.ConfigRunSpeed = ImGuiTestRunSpeed_Cinematic;
    }
#endif

    if (!small)
    {
        ImGui::NewLine();
        ImGuiMd::RenderUnindented(R"(
The "Demo Apps" tab provide sample starter apps from which you can take inspiration. Click on the "View Code" button to view the apps code, and click on "Run" to run them
)");

#ifdef HELLOIMGUI_WITH_TEST_ENGINE
        if (HelloImGui::GetRunnerParams()->useImGuiTestEngine)
        {
            ImGui::SameLine();
            if (ImGui::SmallButton("?"))
                ImGuiTestEngine_QueueTest(HelloImGui::GetImGuiTestEngine(), automationShowMeImmediateApps);
        }
#endif

        AnimateLogo("images/logo_imgui_bundle_512.png", 1., ImVec2(0.5f, 3.f), 0.30f, "https://github.com/pthom/imgui_bundle");
    }
}


// ============================================================================
// Carousel rendering
// ============================================================================

static float DrawSlideMottoCard(const CarouselSlide& slide, float slideWidth)
{
    float em = HelloImGui::EmSize();
    ImDrawList* dl = ImGui::GetWindowDrawList();
    float fontSize = ImGui::GetFontSize();

    float titleFontSize = fontSize * 1.2f;
    ImFont* font = ImGui::GetFont();
    ImVec2 titleSize = font->CalcTextSizeA(titleFontSize, FLT_MAX, 0.f, slide.title);
    ImVec2 descSize = font->CalcTextSizeA(fontSize, FLT_MAX, slideWidth - em * 2.f, slide.description);

    float cardPadX = em * 1.0f;
    float cardPadY = em * 0.4f;
    float innerH = titleSize.y + descSize.y + em * 0.3f;
    float cardW = slideWidth - em * 1.f;
    float cardH = innerH + cardPadY * 2.f;
    float cardX = ImGui::GetCursorScreenPos().x + (slideWidth - cardW) * 0.5f;
    float cardY = ImGui::GetCursorScreenPos().y;

    ImVec4 accentCol = ImGui::GetStyleColorVec4(ImGuiCol_ButtonHovered);
    ImU32 cardBg = ImGui::ColorConvertFloat4ToU32(ImVec4(accentCol.x, accentCol.y, accentCol.z, 0.12f));
    ImU32 cardBorder = ImGui::ColorConvertFloat4ToU32(ImVec4(accentCol.x, accentCol.y, accentCol.z, 0.4f));
    ImU32 titleCol = ImGui::GetColorU32(ImGuiCol_Text);
    ImU32 descCol = ImGui::GetColorU32(ImGuiCol_TextDisabled);

    dl->AddRectFilled(ImVec2(cardX, cardY), ImVec2(cardX + cardW, cardY + cardH), cardBg, em * 0.4f);
    dl->AddRect(ImVec2(cardX, cardY), ImVec2(cardX + cardW, cardY + cardH), cardBorder, em * 0.4f, 0, 1.5f);

    dl->AddText(font, titleFontSize,
                ImVec2(cardX + cardPadX, cardY + cardPadY), titleCol, slide.title);
    dl->AddText(font, fontSize,
                ImVec2(cardX + cardPadX, cardY + cardPadY + titleSize.y + em * 0.3f),
                descCol, slide.description, nullptr, slideWidth - em * 2.f);

    float totalH = cardH + em * 0.4f;
    ImGui::Dummy(ImVec2(slideWidth, totalH));
    return totalH;
}

void IntroMiniDemos()
{
    static const CarouselSlide slides[] = {
        { "Rich Interactive Plots",
          "ImPlot delivers animated, interactive 2D charts with minimal code. It is extremely fast, and ideal for real-time data monitoring, diagnostics, and dashboards.",
            TelemetrySlideGui },

        { "GPU-Accelerated Rendering",
        "Dear ImGui renders directly on the GPU \xe2\x80\x94 fast enough to blend custom shaders and 3D content into your UI.",
        ShaderSlideGui },

        { "3D Data Exploration",
          "ImPlot3D adds rotatable, zoomable 3D plots \xe2\x80\x94 navigate complex datasets with intuitive controls.",
          LorenzSlideGui },

        { "Image Analysis",
          "ImmVision lets you zoom, pan, and inspect pixel values in real time \xe2\x80\x94 with linked views and colormaps.",
          ImmVisionSlideGui },

        { "Feature-Rich Widgets",
          "Dear ImGui ships with advanced tables featuring angled headers, column reordering, sorting, and much more.",
          TableSlideGui },

        { "Explore Ideas in a Node Editor",
          "With imgui-node-editor, you can build complex applications such as blueprint editors. Here is an example of an image editing pipeline.",
          NodeEditorSlideGui },

        { "Rich Documentation, Built In",
          "Render markdown directly in your UI \xe2\x80\x94 headers, code blocks, tables, links, and images, all from a simple string.",
          MarkdownSlideGui },

        { "Integrated Text & Code Editor",
          "The built-in text editor supports syntax highlighting, line numbers, and search. Below is the source of this very demo \xe2\x80\x94 side by side in Python and C++.",
          IntroSourceCode::SlideGui },

        { "Deploy to the Web",
          "Python applications can be effortlessly deployed to the web using Pyodide, and C++ apps using Emscripten.",
          WebDeploySlideGui },

        { "Usage in Notebooks",
        "Dear ImGui Bundle can also be used from a notebook \xe2\x80\x94 here, it displays a real-time dashboard during an ML training session.",
            NotebookSlideGui },
    };
    static const int slideCount = IM_ARRAYSIZE(slides);

    static int currentSlide = 0;
    static float animatedOffset = 0.f;
    static float autoTimer = 0.f;
    static bool autoStopped = false; // stops permanently once user navigates manually

    float dt = ImGui::GetIO().DeltaTime;
    if (dt <= 0.f) dt = 1.f / 60.f;
    if (dt > 0.1f) dt = 0.1f;

    float em = HelloImGui::EmSize();
    ImDrawList* dl = ImGui::GetWindowDrawList();
    ImVec2 windowSize = ImGui::GetWindowSize();

    // --- Carousel zone: 4:3 aspect ratio, centered ---
    float carouselHeight;
    if (IsSmallScreen())
    {
        carouselHeight = windowSize.y * 0.55f;
        if (carouselHeight < em * 12.f) carouselHeight = em * 12.f;
    }
    else
    {
        carouselHeight = windowSize.y * 0.65f;
        if (carouselHeight < em * 15.f) carouselHeight = em * 15.f;
    }
    float carouselWidth = carouselHeight * (4.f / 3.f);
    float availWidth = ImGui::GetContentRegionAvail().x;
    if (carouselWidth > availWidth) carouselWidth = availWidth;

    float carouselOffsetX = (availWidth - carouselWidth) * 0.5f;
    if (carouselOffsetX < 0.f) carouselOffsetX = 0.f;

    ImGui::Indent(carouselOffsetX);

    // --- Auto-advance (pauses while user interacts, stops permanently on manual navigation) ---
    if (!autoStopped)
    {
        bool userInteracting = ImGui::IsAnyItemActive();
        if (!userInteracting)
        {
            autoTimer += dt;
            if (autoTimer > 5.0f)
            {
                currentSlide = (currentSlide + 1) % slideCount;
                autoTimer = 0.f;
            }
        }
    }

    // --- Smooth slide animation ---
    float target = (float)currentSlide;
    animatedOffset = SmoothDamp(animatedOffset, target, 8.f, dt);
    if (fabsf(animatedOffset - target) < 0.001f)
        animatedOffset = target;

    // --- Slide area (motto card + demo content, all scrolling together) ---
    float navBarHeight = em * 2.0f;
    float slideHeight = carouselHeight - navBarHeight;
    if (slideHeight < em * 10.f) slideHeight = em * 10.f;
    float slideWidth = carouselWidth;

    ImVec2 slideAreaPos = ImGui::GetCursorScreenPos();
    ImGui::Dummy(ImVec2(carouselWidth, slideHeight));

    // Clip to carousel bounds
    dl->PushClipRect(slideAreaPos, ImVec2(slideAreaPos.x + carouselWidth, slideAreaPos.y + slideHeight), true);

    for (int i = 0; i < slideCount; i++)
    {
        float slideX = slideAreaPos.x + ((float)i - animatedOffset) * slideWidth;
        if (slideX > slideAreaPos.x + carouselWidth || slideX + slideWidth < slideAreaPos.x)
            continue;

        ImGui::SetCursorScreenPos(ImVec2(slideX, slideAreaPos.y));
        char childId[32];
        snprintf(childId, sizeof(childId), "##slide_%d", i);
        ImGui::BeginChild(childId, ImVec2(slideWidth, slideHeight), false,
                          ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoBackground);

        float mottoH = DrawSlideMottoCard(slides[i], slideWidth);

        // Align demo content with the motto card (which is centered with em*0.5f margin)
        ImGui::SetCursorPosX(ImGui::GetCursorPosX() + em * 0.5f);
        ImVec2 demoSize(slideWidth - em * 1.f, slideHeight - mottoH - em * 0.5f);
        slides[i].guiFunc(demoSize);

        ImGui::EndChild();
    }

    dl->PopClipRect();

    // --- Navigation: arrows + dots ---
    {
        float dotRadius = em * 0.3f;
        float dotSpacing = em * 1.5f;
        float dotsWidth = slideCount * dotSpacing;
        float arrowBtnW = em * 2.f;
        float totalNavWidth = arrowBtnW * 2.f + dotsWidth + em * 1.f;
        float navStartX = slideAreaPos.x + (carouselWidth - totalNavWidth) * 0.5f;
        float navY = slideAreaPos.y + slideHeight + em * 0.3f;

        // Left arrow
        ImGui::SetCursorScreenPos(ImVec2(navStartX, navY));
        if (ImGui::Button(ICON_FA_CHEVRON_LEFT "##carousel_prev", ImVec2(arrowBtnW, em * 1.5f)))
        {
            currentSlide = (currentSlide - 1 + slideCount) % slideCount;
            autoStopped = true;
        }

        // Dots
        float dotsStartX = navStartX + arrowBtnW + em * 0.5f;
        float dotsCenterY = navY + em * 0.75f;

        for (int i = 0; i < slideCount; i++)
        {
            ImVec2 center(dotsStartX + i * dotSpacing + dotSpacing * 0.5f, dotsCenterY);

            ImGui::SetCursorScreenPos(ImVec2(center.x - dotRadius * 2.f, center.y - dotRadius * 2.f));
            char dotId[16];
            snprintf(dotId, sizeof(dotId), "##dot%d", i);
            if (ImGui::InvisibleButton(dotId, ImVec2(dotRadius * 4.f, dotRadius * 4.f)))
            {
                currentSlide = i;
                autoStopped = true;
            }

            bool hovered = ImGui::IsItemHovered();
            float r = (i == currentSlide) ? dotRadius * 1.3f : dotRadius;
            ImVec4 accent = ImGui::GetStyleColorVec4(ImGuiCol_ButtonHovered);
            ImU32 dotCol;
            if (i == currentSlide)
                dotCol = ImGui::ColorConvertFloat4ToU32(accent);
            else if (hovered)
                dotCol = ImGui::ColorConvertFloat4ToU32(ImVec4(accent.x, accent.y, accent.z, 0.6f));
            else
                dotCol = ImGui::GetColorU32(ImGuiCol_TextDisabled);
            dl->AddCircleFilled(center, r, dotCol);
        }

        // Right arrow
        float rightArrowX = dotsStartX + dotsWidth + em * 0.5f;
        ImGui::SetCursorScreenPos(ImVec2(rightArrowX, navY));
        if (ImGui::Button(ICON_FA_CHEVRON_RIGHT "##carousel_next", ImVec2(arrowBtnW, em * 1.5f)))
        {
            currentSlide = (currentSlide + 1) % slideCount;
            autoStopped = true;
        }

        // Advance cursor past nav bar
        ImGui::SetCursorScreenPos(ImVec2(slideAreaPos.x, navY + em * 1.8f));
        ImGui::Dummy(ImVec2(1, 1));
    }

    ImGui::Unindent(carouselOffsetX);
}


// ============================================================================
// Main entry point
// ============================================================================

void demo_imgui_bundle_intro()
{
    // Disable idling so animations run smoothly
    HelloImGui::GetRunnerParams()->fpsIdling.enableIdling = false;

    IntroTopSection();
    ImGui::Separator();
    ImGuiMd::Render("*Below are some examples showing what can be achieved with Dear ImGui Bundle*");
    IntroMiniDemos();

    ImGui::NewLine();
    ImGui::Separator();
    ShowBadges();
}


// ============================================================================
// Main entry point
// ============================================================================

#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char**)
{
    ChdirBesideAssetsFolder();

    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.ShowGui = demo_imgui_bundle_intro;
    runnerParams.appWindowParams.windowGeometry.size = {1000, 800};
    runnerParams.appWindowParams.windowTitle = "ImGui Bundle - Introduction";

    ImmApp::AddOnsParams addons;
    addons.withMarkdown = true;
    addons.withNodeEditor = true;
    addons.withImplot = true;
    addons.withImplot3d = true;
    addons.withTexInspect = true;
    addons.withImAnim = true;

    ImmApp::Run(runnerParams, addons);

    return 0;
}
#endif

