// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// Welcome to Dear ImGui Bundle
//
// The tour you see when you arrive: a carousel of live mini demos, from plots and a shader to a neural network. Each
// slide opens its full demo.
//
// The first screen of the explorer: the tagline, the carousel, a button to the catalog of demos, and the prose of
// demos_assets/welcome.md behind "More info & links". The page that shows it gives it a WelcomeHost: what the button
// and the links do. The twin of demos_python/demo_imgui_bundle_intro.py.
#include "demo_imgui_bundle_intro.h"

#include "imgui.h"
#include "imgui_internal.h"  // IM_PI, SeparatorEx
#include "imgui_rich_md/rich_md.h"
#include "hello_imgui/hello_imgui.h"
#include "hello_imgui/icons_font_awesome_4.h"
#include "immapp/immapp.h"
#include "demo_utils/api_demos.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#include "imgui-knobs/imgui-knobs.h"
#include "imgui_toggle/imgui_toggle.h"
#include "imgui_toggle/imgui_toggle_presets.h"
#include "implot/implot.h"
#include "implot3d/implot3d.h"
#include "imgui-node-editor/imgui_node_editor.h"
#ifdef IMGUI_BUNDLE_WITH_IMMVISION
#include "immvision/immvision.h"
#endif
#ifdef HELLOIMGUI_HAS_OPENGL
#include "hello_imgui/hello_imgui_include_opengl.h"
#endif

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <deque>
#include <fstream>
#include <functional>
#include <memory>
#include <optional>
#include <random>
#include <sstream>
#include <string>
#include <vector>

#ifdef HELLOIMGUI_WITH_TEST_ENGINE
#include "imgui_test_engine/imgui_te_engine.h"
#include "imgui_test_engine/imgui_te_context.h"
#include "imgui_test_engine/imgui_te_ui.h"
#ifdef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY  // the automations drive the explorer's page: none in the welcome alone
#include "demo_imgui_bundle.h"
#include "demo_immapp_launcher.h"
#endif
#endif


namespace
{
    // The interactive manuals, by their filename in the catalog (examples.json)
    const std::vector<std::pair<const char*, const char*>> MANUALS = {
        {"Dear ImGui", "manual_imgui.py"}, {"ImPlot", "manual_implot.py"}, {"ImPlot3D", "manual_implot3d.py"}};
    const float SLIDE_DURATION = 5.f;  // s: the carousel moves to the next slide by itself, until the user touches it
    const char* SITE = "https://imgui-bundle.pages.dev";

    WelcomeHost gHost;  // the page that shows the welcome (WelcomeGui sets it): the slides' own links use it

    bool IsSmallScreen()  // a phone or a small tablet (under about 800 px)
    {
        return ImGui::GetIO().DisplaySize.x < HelloImGui::EmSize() * 50.f;
    }

    bool IsTouchScreen() { return (ImGui::GetIO().ConfigFlags & ImGuiConfigFlags_IsTouchScreen) != 0; }

    ImVec4 WithAlpha(ImVec4 color, float alpha) { return ImVec4(color.x, color.y, color.z, alpha); }


    // ============================================================================
    // Test engine automations: "Show me" walks the explorer's demos (the explorer only)
    // ============================================================================
#ifdef HELLOIMGUI_WITH_TEST_ENGINE
#ifdef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
    // Goes to the demos, selects this one (its category's chip scrolls to it, a click on its card) and shows its code
    void ShowDemoCode(ImGuiTestContext* ctx, const std::string& filename)
    {
        DemoLauncher* launcher = BundleExplorer::Launcher();
        if (launcher == nullptr)
            return;
        while (launcher->Depth() > 0)  // as a previous automation may have left the code view open
            launcher->Back();
        if (!BundleExplorer::OnDemos())
        {
            ctx->ItemClick((std::string("//**/") + BundleExplorer::DEMOS_LABEL).c_str());
            ctx->Sleep(1.5f);  // the change of page, then the cards dealt
        }
        for (const auto& category : launcher->Categories())
        {
            bool holds = false;
            for (const auto& demo : category.demos)
                holds = holds || demo.filename == filename;
            if (!holds)
                continue;
            ctx->ItemClick(("//**/" + launcher->ChipLabel(category)).c_str());
            ctx->Sleep(0.8f);  // the scroll
        }
        if (!launcher->CardRects().count(filename))
            return;
        auto [topLeft, bottomRight] = launcher->CardRects().at(filename);
        ctx->MouseMoveToPos(ImVec2((topLeft.x + bottomRight.x) / 2, (topLeft.y + bottomRight.y) / 2));
        ctx->MouseClick(0);
        ctx->Sleep(0.5f);
        ctx->ItemClick("//**/" ICON_FA_CODE "  View code");
    }

    ImGuiTest* AutomationShowMeImmediateApps()
    {
        ImGuiTest* automation = IM_REGISTER_TEST(HelloImGui::GetImGuiTestEngine(), "Automation", "ShowMeImmediateApps");
        automation->TestFunc = [](ImGuiTestContext* ctx) {
            const char* allTheDemos = "//**/" ICON_FA_ARROW_LEFT "  All the demos";
            ShowDemoCode(ctx, "demo_hello_world.py");
            ctx->Sleep(2.f);
            ctx->ItemClick(allTheDemos);
            ShowDemoCode(ctx, "demo_assets_addons.py");
            ctx->Sleep(2.f);
            ctx->ItemClick(allTheDemos);
            ctx->MouseMove("//**/" ICON_FA_PLAY "  Run in a new window");
            ctx->Sleep(1.f);
            ctx->ItemClick((std::string("//**/") + BundleExplorer::WELCOME_LABEL).c_str());
        };
        return automation;
    }

    ImGuiTest* AutomationShowDemo(const char* name, const char* filename)
    {
        ImGuiTest* automation = IM_REGISTER_TEST(HelloImGui::GetImGuiTestEngine(), "Automation", name);
        automation->UserData = (void*)filename;
        automation->TestFunc = [](ImGuiTestContext* ctx) {
            ShowDemoCode(ctx, (const char*)ctx->Test->UserData);
            ctx->MouseMove("//**/" ICON_FA_ARROW_LEFT "  All the demos");
        };
        return automation;
    }
#endif

    // The tours, registered once; "Show me" and the "More info" links queue them
    namespace IntroAutomations
    {
        ImGuiTest* showImmediateApps = nullptr;
        ImGuiTest* showCustomBackground = nullptr;
        ImGuiTest* showDocking = nullptr;
        bool inited = false;

        void Init()
        {
            if (inited || !HelloImGui::GetRunnerParams()->useImGuiTestEngine)
                return;
            inited = true;
#ifdef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
            if (BundleExplorer::Launcher() == nullptr)
                return;  // the automations drive the explorer's page
            showImmediateApps = AutomationShowMeImmediateApps();
            showCustomBackground = AutomationShowDemo("ShowMeCustomBackgroundExample", "demo_custom_background.py");
            showDocking = AutomationShowDemo("ShowMeDockingExample", "demo_docking.py");
            ImGuiTestEngine_GetIO(HelloImGui::GetImGuiTestEngine()).ConfigRunSpeed = ImGuiTestRunSpeed_Cinematic;
#endif
        }

        void ShowLink(const char* label, ImGuiTest* automation)
        {
            if (automation == nullptr)
                return;
            ImGui::Spacing();
            ImGui::PushStyleColor(ImGuiCol_Text, RichMd::LinkColor());
            ImGui::TextUnformatted(label);
            if (ImGui::IsItemHovered(ImGuiHoveredFlags_DelayNormal))
            {
                ImGui::SetMouseCursor(ImGuiMouseCursor_Hand);
                if (ImGui::IsMouseClicked(ImGuiMouseButton_Left))
                {
                    ImGui::SetWindowFocus(nullptr);
                    ImGuiTestEngine_QueueTest(HelloImGui::GetImGuiTestEngine(), automation);
                }
            }
            ImGui::PopStyleColor();
        }
    }
#endif  // HELLOIMGUI_WITH_TEST_ENGINE


    // ============================================================================
    // Carousel infrastructure
    // ============================================================================

    struct CarouselSlide
    {
        std::string title;
        std::string description;
        std::function<void(ImVec2)> guiFunc;
        std::string demo;  // the catalog's demo that goes further (its filename in examples.json), linked from the card
    };

    // Exponential smoothing: approaches target with a given speed (higher = faster)
    float SmoothDamp(float current, float target, float speed, float dt)
    {
        return current + (target - current) * (1.f - std::exp(-speed * dt));
    }

    // A rounded rectangle in the accent color, behind a part of a slide
    void PanelBg(ImVec2 topLeft, ImVec2 size, float alphaBg = 0.08f, float alphaBorder = 0.3f)
    {
        float em = HelloImGui::EmSize();
        ImVec4 accent = ImGui::GetStyleColorVec4(ImGuiCol_ButtonHovered);
        ImVec2 bottomRight(topLeft.x + size.x, topLeft.y + size.y);
        ImDrawList* dl = ImGui::GetWindowDrawList();
        dl->AddRectFilled(topLeft, bottomRight, ImGui::ColorConvertFloat4ToU32(WithAlpha(accent, alphaBg)), em * 0.4f);
        dl->AddRect(topLeft, bottomRight, ImGui::ColorConvertFloat4ToU32(WithAlpha(accent, alphaBorder)), em * 0.4f,
                    1.5f);
    }

    // A colored rounded rectangle, then drawWidgets inside a child window (with a padding)
    void DrawSidePanel(const char* id, float width, float height, const std::function<void()>& drawWidgets)
    {
        float em = HelloImGui::EmSize();
        PanelBg(ImGui::GetCursorScreenPos(), ImVec2(width, height));
        ImGui::BeginChild(id, ImVec2(width, height), false, ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoBackground);
        float pad = em * 0.5f;
        ImGui::SetCursorPos(ImVec2(pad, pad));
        ImGui::PushItemWidth((width - pad * 2.f) * 0.5f);
        drawWidgets();
        ImGui::PopItemWidth();
        ImGui::EndChild();
    }

    // A knob in the accent color of the style (the sequencer's tempo, Lorenz's parameters)
    bool AccentKnob(const char* label, float* value, float vMin, float vMax, const char* format, float size)
    {
        ImVec4 accent = ImGui::GetStyleColorVec4(ImGuiCol_SliderGrab);
        ImGui::PushStyleColor(ImGuiCol_FrameBg, WithAlpha(accent, 0.4f));
        ImGui::PushStyleColor(ImGuiCol_FrameBgHovered, WithAlpha(accent, 0.6f));
        ImGui::PushStyleColor(ImGuiCol_FrameBgActive, WithAlpha(accent, 0.8f));
        bool changed = ImGuiKnobs::Knob(label, value, vMin, vMax, 0.f, format, ImGuiKnobVariant_WiperDot, size,
                                        ImGuiKnobFlags_AlwaysClamp);
        ImGui::PopStyleColor(3);
        return changed;
    }

    // A button in the accent color of the style
    bool AccentButton(const char* label, ImVec2 size)
    {
        ImVec4 accent = ImGui::GetStyleColorVec4(ImGuiCol_ButtonHovered);
        ImGui::PushStyleColor(ImGuiCol_Button, WithAlpha(accent, 0.55f));
        ImGui::PushStyleColor(ImGuiCol_ButtonHovered, WithAlpha(accent, 0.8f));
        ImGui::PushStyleColor(ImGuiCol_ButtonActive, WithAlpha(accent, 1.f));
        bool clicked = ImGui::Button(label, size);
        ImGui::PopStyleColor(3);
        return clicked;
    }

    const float MANUAL_PICTURE_ASPECT = 640.f / 401.f;  // the manuals' pictures (their cards' in the catalog)

    // The picture of a manual (its card's, from the site), which opens it when the page can open a demo
    void ManualPicture(const std::string& demo, float width)
    {
        std::string stem = demo.substr(0, demo.rfind('.'));
        std::string url = std::string(SITE) + "/resources/playground/" + stem + ".jpg";
        ImVec2 topLeft = ImGui::GetCursorScreenPos();
        RichMd::Render("<img src=\"" + url + "\" width=\"" + std::to_string((int)width) + "\">");
        ImVec2 bottomRight(topLeft.x + width, ImGui::GetCursorScreenPos().y);
        // The rectangle alone is not enough: IsWindowHovered() is false when a window above (the prose's) covers it
        if (!gHost.openDemo || !ImGui::IsMouseHoveringRect(topLeft, bottomRight) || !ImGui::IsWindowHovered())
            return;
        ImGui::SetMouseCursor(ImGuiMouseCursor_Hand);
        ImGui::GetWindowDrawList()->AddRect(topLeft, bottomRight, ImGui::GetColorU32(ImGuiCol_ButtonHovered),
                                            HelloImGui::EmSize(0.3f), 2.f);
        if (ImGui::IsMouseClicked(ImGuiMouseButton_Left))
            gHost.openDemo(demo);
    }

    // A line of text, then the manual's picture below it, as large as the space left allows (none if too small)
    void ManualTeaser(const char* text, const std::string& demo)
    {
        float em = HelloImGui::EmSize();
        ImGui::PushTextWrapPos(ImGui::GetCursorPosX() + ImGui::GetContentRegionAvail().x);
        ImGui::TextWrapped("%s", text);
        ImGui::PopTextWrapPos();
        ImVec2 avail = ImGui::GetContentRegionAvail();
        float width = std::min(avail.x - em * 0.5f, (avail.y - em * 0.5f) * MANUAL_PICTURE_ASPECT);
        if (width < em * 6.f)
            return;
        ImGui::SetCursorPosX(ImGui::GetCursorPosX() + (avail.x - width) / 2);
        ManualPicture(demo, width);
    }

    // No legends on a phone: they would cover the small plots
    ImPlotFlags ImPlotPhoneFlags() { return IsSmallScreen() ? ImPlotFlags_NoLegend : 0; }


    // ============================================================================
    // Slide: ImPlot, three plots and the picture of its manual
    // ============================================================================
    namespace IntroImPlot
    {
        const int N = 1001, N_FILLED = 101;
        bool inited = false;
        std::vector<double> xs, filledXs, filledYs1, filledYs2, filledYs3;
        std::vector<double> shadedYs, shadedYs1, shadedYs2, shadedYs3, shadedYs4;

        void Init()
        {
            std::mt19937 rng(0);
            auto randomRange = [&rng](double low, double high) {
                return std::uniform_real_distribution<double>(low, high)(rng);
            };
            for (int i = 0; i < N; i++)
            {
                double x = (double)i / (N - 1);
                xs.push_back(x);
                double y = 0.25 + 0.25 * std::sin(25. * x) * std::sin(5. * x) + randomRange(-0.01, 0.01);
                shadedYs.push_back(y);
                shadedYs1.push_back(y + randomRange(0.1, 0.12));
                shadedYs2.push_back(y - randomRange(0.1, 0.12));
                shadedYs3.push_back(0.75 + 0.2 * std::sin(25. * x));
                shadedYs4.push_back(0.75 + 0.1 * std::cos(25. * x));
            }
            for (int i = 0; i < N_FILLED; i++)
            {
                filledXs.push_back(i);
                filledYs1.push_back(randomRange(400., 450.));
                filledYs2.push_back(randomRange(275., 350.));
                filledYs3.push_back(randomRange(150., 225.));
            }
            inited = true;
        }

        void LinePlots()  // three curves that move
        {
            double t = ImGui::GetTime() * 1.5;
            std::vector<double> ys1(N), ys2(N), ys3(N);
            for (int i = 0; i < N; i++)
            {
                double x = xs[i];
                ys1[i] = 0.5 + 0.5 * std::sin(6. * (x + t));
                ys2[i] = 0.5 + 0.3 * std::cos(4. * (x + t));
                ys3[i] = 0.5 + 0.2 * std::sin(10. * x + t) * std::cos(3. * x + t);
            }
            if (ImPlot::BeginPlot("Line Plots", ImVec2(-1, 0), ImPlotPhoneFlags()))
            {
                ImPlot::SetupAxes("x", "y", ImPlotAxisFlags_NoTickLabels, ImPlotAxisFlags_NoTickLabels);
                ImPlot::SetupAxesLimits(0, 1, -0.1, 1.1);
                ImPlot::PlotLine("f(x)", xs.data(), ys1.data(), N);
                ImPlot::PlotLine("g(x)", xs.data(), ys2.data(), N);
                ImPlot::PlotLine("h(x)", xs.data(), ys3.data(), N);
                ImPlot::EndPlot();
                HelloImGui::SetItemIsLive();  // the curves move on their own
            }
        }

        void StockPrices()
        {
            if (ImPlot::BeginPlot("Stock Prices", ImVec2(-1, 0), ImPlotPhoneFlags()))
            {
                ImPlot::SetupAxes("Days", "Price");
                ImPlot::SetupAxesLimits(0, 100, 0, 500);
                if (IsSmallScreen())  // fewer ticks: in a narrow plot the default labels run together
                    ImPlot::SetupAxisTicks(ImAxis_X1, 0, 100, 3);
                ImPlotSpec spec;
                spec.FillAlpha = 0.25f;
                const std::vector<double>* ys[] = {&filledYs1, &filledYs2, &filledYs3};
                const char* labels[] = {"Stock 1", "Stock 2", "Stock 3"};
                for (int i = 0; i < 3; i++)
                {
                    ImPlot::PlotShaded(labels[i], filledXs.data(), ys[i]->data(), N_FILLED, 0.0, spec);
                    ImPlot::PlotLine(labels[i], filledXs.data(), ys[i]->data(), N_FILLED);
                }
                ImPlot::EndPlot();
            }
        }

        void ShadedPlots()
        {
            ImPlotSpec spec;
            spec.FillAlpha = 0.25f;
            if (ImPlot::BeginPlot("Shaded Plots", ImVec2(-1, 0), ImPlotPhoneFlags()))
            {
                ImPlot::SetupLegend(ImPlotLocation_NorthWest, ImPlotLegendFlags_Reverse);
                ImPlot::PlotShaded("Uncertain Data", xs.data(), shadedYs1.data(), shadedYs2.data(), N, spec);
                ImPlot::PlotLine("Uncertain Data", xs.data(), shadedYs.data(), N, spec);
                ImPlot::PlotShaded("Overlapping", xs.data(), shadedYs3.data(), shadedYs4.data(), N, spec);
                ImPlot::PlotLine("Overlapping", xs.data(), shadedYs3.data(), N, spec);
                ImPlot::PlotLine("Overlapping", xs.data(), shadedYs4.data(), N, spec);
                ImPlot::EndPlot();
            }
        }

        void SlideGui(ImVec2 contentSize)  // three plots, and in the place of the fourth the picture of the manual
        {
            if (!inited)
                Init();
            if (!ImPlot::BeginSubplots("##ImPlotShowcase", 2, 2, contentSize, ImPlotSubplotFlags_NoResize))
                return;
            LinePlots();
            StockPrices();
            ShadedPlots();
            ImPlot::EndSubplots();
            ImVec2 after = ImGui::GetCursorScreenPos();
            ImVec2 topLeft = ImGui::GetItemRectMin(), bottomRight = ImGui::GetItemRectMax();
            float em = HelloImGui::EmSize();
            ImVec2 cellMin((topLeft.x + bottomRight.x) / 2 + em, (topLeft.y + bottomRight.y) / 2 + em * 0.5f);
            ImGui::SetCursorScreenPos(cellMin);
            ImVec2 cellSize(bottomRight.x - cellMin.x - em * 0.5f, bottomRight.y - cellMin.y - em * 0.5f);
            ImGui::BeginChild("##implot_manual", cellSize, false,
                              ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoBackground);
            ManualTeaser("Every plot type, with its code: the ImPlot manual", "manual_implot.py");
            ImGui::EndChild();
            ImGui::SetCursorScreenPos(after);
            ImGui::Dummy(ImVec2(0, 0));  // ImGui wants an item where the cursor was moved
        }
    }


    // ============================================================================
    // Slide: the seascape shader, rendered to a texture (OpenGL on the desktop, WebGL with Emscripten)
    // ============================================================================
#ifdef HELLOIMGUI_HAS_OPENGL
    namespace IntroShader
    {
        // GLSL 100 for Emscripten (WebGL), GLSL 330 for the desktop
#ifdef __EMSCRIPTEN__
#define SHADER_HEADER "#version 100\nprecision mediump float;\n"
#define VERT_IN "attribute"
#define VERT_OUT "varying"
#define FRAG_IN "varying"
#define FRAG_OUT_DECL ""
#define FRAG_OUT_ASSIGN "gl_FragColor="
#else
#define SHADER_HEADER "#version 330 core\n"
#define VERT_IN "in"
#define VERT_OUT "out"
#define FRAG_IN "in"
#define FRAG_OUT_DECL "out vec4 FragColor;\n"
#define FRAG_OUT_ASSIGN "FragColor="
#endif

        const char* VERT_SRC =
            SHADER_HEADER
            VERT_IN " vec2 aPos;\n"
            VERT_IN " vec2 aTexCoord;\n"
            VERT_OUT " vec2 TexCoord;\n"
            "void main() { gl_Position = vec4(aPos, 0.0, 1.0); TexCoord = aTexCoord; }\n";

        // Seascape by Alexander Alekseev aka TDM - 2014, https://www.shadertoy.com/view/Ms2SD1
        // License: Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported
        const char* FRAG_SRC =
            SHADER_HEADER
            FRAG_IN " vec2 TexCoord;\n"
            FRAG_OUT_DECL
            R"(
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
    )" FRAG_OUT_ASSIGN R"(vec4(pow(color,vec3(0.65)),1.0);
}
)";

        GLuint CompileShader(GLuint type, const char* source)
        {
            GLuint shader = glCreateShader(type);
            glShaderSource(shader, 1, &source, nullptr);
            glCompileShader(shader);
            GLint ok;
            glGetShaderiv(shader, GL_COMPILE_STATUS, &ok);
            if (!ok)
            {
                GLchar log[512];
                glGetShaderInfoLog(shader, 512, nullptr, log);
                fprintf(stderr, "Seascape shader: %s\n", log);
            }
            return shader;
        }

        struct ShaderState
        {
            GLuint program = 0, quadVao = 0, quadVbo = 0, fbo = 0, texture = 0;
            int fboSize = 600;
            GLint locResolution = -1, locTime = -1, locSeaHeight = -1, locSeaChoppy = -1, locSeaBase = -1;
            float seaHeight = 0.6f, seaChoppy = 4.f;
            float seaBase[3] = {0.f, 0.09f, 0.18f};

            void Init(int size)
            {
                fboSize = size;
                GLuint vs = CompileShader(GL_VERTEX_SHADER, VERT_SRC), fs = CompileShader(GL_FRAGMENT_SHADER, FRAG_SRC);
                program = glCreateProgram();
                glAttachShader(program, vs);
                glAttachShader(program, fs);
                glBindAttribLocation(program, 0, "aPos");  // GLSL 100 has no layout(location)
                glBindAttribLocation(program, 1, "aTexCoord");
                glLinkProgram(program);
                glDeleteShader(vs);
                glDeleteShader(fs);

                // A quad over the whole texture: x, y, u, v
                float vertices[] = {-1, -1, 0, 0, 1, -1, 1, 0, -1, 1, 0, 1, 1, 1, 1, 1};
                glGenVertexArrays(1, &quadVao);
                glGenBuffers(1, &quadVbo);
                glBindVertexArray(quadVao);
                glBindBuffer(GL_ARRAY_BUFFER, quadVbo);
                glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
                glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, (void*)0);
                glEnableVertexAttribArray(0);
                glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, (void*)8);
                glEnableVertexAttribArray(1);
                glBindVertexArray(0);

                locResolution = glGetUniformLocation(program, "iResolution");
                locTime = glGetUniformLocation(program, "iTime");
                locSeaHeight = glGetUniformLocation(program, "SEA_HEIGHT");
                locSeaChoppy = glGetUniformLocation(program, "SEA_CHOPPY");
                locSeaBase = glGetUniformLocation(program, "SEA_BASE");

                // The texture the shader draws into
                glGenFramebuffers(1, &fbo);
                glBindFramebuffer(GL_FRAMEBUFFER, fbo);
                glGenTextures(1, &texture);
                glBindTexture(GL_TEXTURE_2D, texture);
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, fboSize, fboSize, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
                glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0);
                glBindFramebuffer(GL_FRAMEBUFFER, 0);
            }

            void Destroy()
            {
                if (texture) glDeleteTextures(1, &texture);
                if (fbo) glDeleteFramebuffers(1, &fbo);
                if (program) glDeleteProgram(program);
                if (quadVbo) glDeleteBuffers(1, &quadVbo);
                if (quadVao) glDeleteVertexArrays(1, &quadVao);
                texture = fbo = program = quadVbo = quadVao = 0;
            }

            void RenderToFbo()
            {
                GLint previousViewport[4];
                glGetIntegerv(GL_VIEWPORT, previousViewport);
                glBindFramebuffer(GL_FRAMEBUFFER, fbo);
                glViewport(0, 0, fboSize, fboSize);
                glClear(GL_COLOR_BUFFER_BIT);
                glUseProgram(program);
                glUniform2f(locResolution, (float)fboSize, (float)fboSize);
                glUniform1f(locTime, (float)ImGui::GetTime());
                glUniform1f(locSeaHeight, seaHeight);
                glUniform1f(locSeaChoppy, seaChoppy);
                glUniform3f(locSeaBase, seaBase[0], seaBase[1], seaBase[2]);
                glDisable(GL_DEPTH_TEST);
                glBindVertexArray(quadVao);
                glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
                glBindVertexArray(0);
                glUseProgram(0);
                glBindFramebuffer(GL_FRAMEBUFFER, 0);
                glViewport(previousViewport[0], previousViewport[1], previousViewport[2], previousViewport[3]);
            }
        };

        std::unique_ptr<ShaderState> state;
        bool inited = false;

        void LazyInit()
        {
            if (inited)
                return;
            inited = true;
            state = std::make_unique<ShaderState>();
            state->Init(IsSmallScreen() ? 300 : 600);  // a phone's GPU ray-marches the sea at a quarter of the pixels
            HelloImGui::GetRunnerParams()->callbacks.EnqueueBeforeExit([]() {  // with the GL context that made them
                if (state)
                    state->Destroy();
                state.reset();
                inited = false;  // an app run after this one makes them again
            });
        }

        void Controls(bool narrow)
        {
            ImGui::TextUnformatted(narrow ? "\"Seascape\" by TDM" : "\"Seascape\" by Alexander Alekseev aka TDM");
            ImGui::SetItemTooltip("Alexander Alekseev aka TDM, https://www.shadertoy.com/view/Ms2SD1\n"
                                  "License: Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported\n"
                                  "Contact: tdmaav@gmail.com");
            if (!state)
                return;
            ImGui::SetNextItemWidth(HelloImGui::EmSize(7.f));
            ImGui::SliderFloat("Wave height", &state->seaHeight, 0.1f, 2.f);
            if (narrow)
                return;
            ImGui::SetNextItemWidth(HelloImGui::EmSize(7.f));
            ImGui::SliderFloat("Choppiness", &state->seaChoppy, 0.5f, 8.f);
            ImGui::SetNextItemWidth(HelloImGui::EmSize(7.f));
            ImGui::ColorEdit3("Sea base color", state->seaBase);
#ifdef HELLOIMGUI_WITH_TEST_ENGINE
            IntroAutomations::ShowLink("More info & code", IntroAutomations::showCustomBackground);
#endif
        }

        void SlideGui(ImVec2 contentSize)
        {
            float em = HelloImGui::EmSize();
            LazyInit();
            state->RenderToFbo();
            ImGui::Image(ImTextureRef((ImTextureID)(intptr_t)state->texture), contentSize, ImVec2(0, 1), ImVec2(1, 0));
            HelloImGui::SetItemIsLive();  // the sea moves on its own

            // The controls, in a translucent window over the sea
            bool narrow = IsSmallScreen();
            float pad = em * 0.8f;
            float overlayW = em * (narrow ? 13.f : 18.f);
            ImGui::SetNextWindowPos(ImVec2(ImGui::GetItemRectMax().x - overlayW - pad, ImGui::GetItemRectMin().y + pad),
                                    ImGuiCond_Always);
            ImGui::SetNextWindowBgAlpha(0.45f);
            ImGui::PushStyleVar(ImGuiStyleVar_WindowRounding, em * 0.5f);
            // No focus when it appears: the slide comes into view during a swipe, and a focused window would end it
            if (ImGui::Begin("##seascape_overlay", nullptr,
                             ImGuiWindowFlags_AlwaysAutoResize | ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoMove
                             | ImGuiWindowFlags_NoSavedSettings | ImGuiWindowFlags_NoFocusOnAppearing))
            {
                ImGui::PushItemWidth(overlayW - em * 2.f);
                Controls(narrow);
                ImGui::PopItemWidth();
            }
            ImGui::End();
            ImGui::PopStyleVar();
        }
    }
#endif  // HELLOIMGUI_HAS_OPENGL


    // ============================================================================
    // Slide: Lorenz, an ImPlot3D attractor with two trajectories
    // ============================================================================
    namespace IntroLorenz
    {
        struct Params
        {
            float sigma = 10.f, rho = 28.f, beta = 8.f / 3.f, dt = 0.01f;
            size_t maxSize = 2000;
        };

        struct Trajectory
        {
            std::deque<double> xs, ys, zs;
            Trajectory(double x, double y, double z) : xs{x}, ys{y}, zs{z} {}

            void Step(const Params& p)
            {
                double x = xs.back(), y = ys.back(), z = zs.back();
                double dx = p.sigma * (y - x), dy = x * (p.rho - z) - y, dz = x * y - p.beta * z;
                xs.push_back(x + dx * p.dt);
                ys.push_back(y + dy * p.dt);
                zs.push_back(z + dz * p.dt);
                if (xs.size() > p.maxSize)
                {
                    xs.pop_front();
                    ys.pop_front();
                    zs.pop_front();
                }
            }

            void Plot(const char* label) const
            {
                std::vector<double> x(xs.begin(), xs.end()), y(ys.begin(), ys.end()), z(zs.begin(), zs.end());
                ImPlot3D::PlotLine(label, x.data(), y.data(), z.data(), (int)x.size());
            }
        };

        Params params;
        float initialDelta = 0.1f;
        std::optional<Trajectory> traj1, traj2;

        void InitTrajectories()
        {
            traj1.emplace(0.0, 1.0, 1.05);
            traj2.emplace(0.0 + initialDelta, 1.0, 1.05);
        }

        void GuiMain(ImVec2 plotSize)
        {
            if (!traj1)
                InitTrajectories();
            // On a touch screen, the gesture that rotates the plot, on a line under it (the plot and the line: one group)
            bool touch = IsTouchScreen();
            if (touch)
                plotSize.y -= ImGui::GetTextLineHeightWithSpacing();
            ImGui::BeginGroup();
            if (ImPlot3D::BeginPlot("Lorenz##intro", plotSize))
            {
                ImPlot3D::SetupAxes("X", "Y", "Z", ImPlot3DAxisFlags_AutoFit, ImPlot3DAxisFlags_AutoFit,
                                    ImPlot3DAxisFlags_AutoFit);
                traj1->Plot("Trajectory");
                traj2->Plot("Trajectory2");
                ImPlot3D::EndPlot();
                HelloImGui::SetItemIsLive();  // the trajectories move on their own
            }
            if (touch)
            {
                const char* note = "Drag with two fingers to rotate.";
                ImGui::SetCursorPosX(ImGui::GetCursorPosX() + (plotSize.x - ImGui::CalcTextSize(note).x) / 2);
                ImGui::TextDisabled("%s", note);
            }
            ImGui::EndGroup();
            traj1->Step(params);
            traj2->Step(params);
        }

        // The parameters as knobs, on one row: sigma, rho and beta (then dt and the initial gap, when allFive)
        void Knobs(float size, bool allFive)
        {
            AccentKnob("Sigma", &params.sigma, 0.f, 30.f, "%.1f", size);
            ImGui::SetItemTooltip("Rate of divergence (chaos level)");
            ImGui::SameLine();
            AccentKnob("Rho", &params.rho, 0.f, 60.f, "%.1f", size);
            ImGui::SetItemTooltip("Size and shape of the attractor");
            ImGui::SameLine();
            AccentKnob("Beta", &params.beta, 0.f, 8.f, "%.2f", size);
            ImGui::SetItemTooltip("Damping on vertical movement");
            if (!allFive)
                return;
            AccentKnob("dt", &params.dt, 0.001f, 0.03f, "%.3f", size);
            ImGui::SetItemTooltip("Time step (smaller = smoother)");
            ImGui::SameLine();
            AccentKnob("Gap", &initialDelta, 0.f, 0.2f, "%.2f", size);
            ImGui::SetItemTooltip("The initial gap between the two trajectories (Restart applies it)");
        }

        void GuiSide()
        {
            float em = HelloImGui::EmSize(), pad = em * 0.5f;
            ImGui::TextUnformatted("Butterfly effect");
            ImGui::PushStyleColor(ImGuiCol_Text, ImGui::GetStyleColorVec4(ImGuiCol_TextDisabled));
            ImGui::PushTextWrapPos(ImGui::GetWindowWidth() - pad);
            ImGui::TextWrapped("Two trajectories start %.2f apart, then part ways: deterministic chaos.", initialDelta);
            ImGui::PopTextWrapPos();
            ImGui::PopStyleColor();
            ImGui::Spacing();
            float avail = ImGui::GetWindowWidth() - 2 * pad, spacing = ImGui::GetStyle().ItemSpacing.x;
            Knobs(std::min(em * 3.6f, (avail - 2 * spacing) / 3), true);
            ImGui::Spacing();
            if (AccentButton(ICON_FA_SYNC "  Restart", ImVec2(avail, em * 1.8f)))
                InitTrajectories();
            ImGui::Spacing();
            ImGui::Separator();
            ImGui::Spacing();
            ManualTeaser("Every 3D plot type, with its code: the ImPlot3D manual", "manual_implot3d.py");
        }

        void GuiSideNarrow()  // sigma, rho and beta, and the Restart button, on one row
        {
            float em = HelloImGui::EmSize(), pad = em * 0.5f, buttonW = em * 5.5f;
            float spacing = ImGui::GetStyle().ItemSpacing.x;
            float size = std::min(em * 2.4f, (ImGui::GetWindowWidth() - 2 * pad - buttonW - 3 * spacing) / 3);
            float top = ImGui::GetCursorPosY();
            Knobs(size, false);
            ImGui::SameLine();
            ImGui::SetCursorPosY(top + em * 1.4f);  // level with the knobs, below their titles
            if (AccentButton(ICON_FA_SYNC " Restart", ImVec2(buttonW, em * 1.8f)))
                InitTrajectories();
        }

        void SlideGui(ImVec2 contentSize)
        {
            float em = HelloImGui::EmSize(), gap = em * 0.5f;
            if (IsSmallScreen())  // the plot, then the parameters under it
            {
                float panelH = em * 5.9f;
                GuiMain(ImVec2(contentSize.x, contentSize.y - panelH - gap));
                DrawSidePanel("##lorenz_side", contentSize.x, panelH, GuiSideNarrow);
                return;
            }
            float mainSide = contentSize.y, sidePanelW = contentSize.x - mainSide - gap;
            GuiMain(ImVec2(mainSide, mainSide));
            if (sidePanelW > em * 4.f)
            {
                ImGui::SameLine(0.f, gap);
                DrawSidePanel("##lorenz_side", sidePanelW, mainSide, GuiSide);
            }
        }
    }


    // ============================================================================
    // Slide: a live data stream, plotted at the screen's rate (as beside a Jupyter notebook, whose cells feed it)
    // ============================================================================
    namespace IntroStream
    {
        const double WINDOW = 1.0;  // seconds of data on the plot
        const float RATE_MIN = 10.f, RATE_MAX = 10000.f;  // samples per second: the slider's range (logarithmic)

        // Two sensors, sampled at `rate` samples per second: the samples of the last frame are added at each frame
        struct Stream
        {
            std::mt19937 rng{1};
            std::normal_distribution<double> noise{0.0, 1.0};
            float rate = 1000.f;
            std::vector<double> t, a, b;
            double tEnd = 0.0;  // the time of the last sample
            double debt = 0.0;  // the samples due, less those taken
            std::optional<double> lastTime;

            void Step()
            {
                double now = ImGui::GetTime();
                if (!lastTime.has_value())  // the first frame: the plot full at once
                {
                    lastTime = now;
                    debt = WINDOW * rate;
                }
                debt += std::clamp(now - *lastTime, 0.0, 0.1) * rate;  // (a pause of the app adds no burst)
                lastTime = now;
                int n = (int)debt;
                if (n <= 0)
                    return;
                debt -= n;
                for (int i = 1; i <= n; i++)
                {
                    double ti = tEnd + i / (double)rate;
                    t.push_back(ti);
                    a.push_back(std::sin(2 * IM_PI * 1.5 * ti) + 0.35 * std::sin(2 * IM_PI * 9.3 * ti)
                                + 0.07 * noise(rng));
                    b.push_back(0.8 * std::sin(2 * IM_PI * 0.63 * ti + 1.0) * std::cos(2 * IM_PI * 5.1 * ti) - 0.2
                                + 0.05 * noise(rng));
                }
                tEnd = t.back();
                // The samples older than the window go
                size_t first = std::lower_bound(t.begin(), t.end(), tEnd - WINDOW) - t.begin();
                t.erase(t.begin(), t.begin() + first);
                a.erase(a.begin(), a.begin() + first);
                b.erase(b.begin(), b.begin() + first);
            }
        };

        std::optional<Stream> stream;

        void Plot(ImVec2 size)
        {
            if (ImPlot::BeginPlot("##stream", size, ImPlotFlags_NoMenus | ImPlotFlags_NoMouseText | ImPlotPhoneFlags()))
            {
                ImPlot::SetupAxes("", "", ImPlotAxisFlags_NoTickLabels, 0);
                ImPlot::SetupAxisLimits(ImAxis_X1, stream->tEnd - WINDOW, stream->tEnd, ImGuiCond_Always);
                ImPlot::SetupAxisLimits(ImAxis_Y1, -1.7, 1.7, ImGuiCond_Always);
                if (stream->t.size() > 1)
                {
                    ImPlot::PlotLine("sensor 1", stream->t.data(), stream->a.data(), (int)stream->t.size());
                    ImPlot::PlotLine("sensor 2", stream->t.data(), stream->b.data(), (int)stream->t.size());
                }
                ImPlot::EndPlot();
                HelloImGui::SetItemIsLive();  // the data flow on their own
            }
        }

        std::string FramesLine() { return std::to_string((int)std::round(ImGui::GetIO().Framerate)) + " frames per second"; }
        std::string SamplesLine()
        {
            char text[64];
            snprintf(text, sizeof(text), "%.0f samples per second", stream->rate);
            return text;
        }

        void RateSlider(float width)
        {
            ImGui::SetNextItemWidth(width);
            ImGui::SliderFloat("##rate", &stream->rate, RATE_MIN, RATE_MAX, "%.0f samples / s",
                               ImGuiSliderFlags_Logarithmic);
        }

        void Side()
        {
            float em = HelloImGui::EmSize(), width = ImGui::GetWindowWidth() - em;
            ImGui::Indent(em * 0.5f);  // the panel's padding, for the lines after the first
            ImGui::TextUnformatted("Live data stream");
            ImGui::Spacing();
            ImGui::TextDisabled("%s", FramesLine().c_str());
            ImGui::TextDisabled("%s", SamplesLine().c_str());
            ImGui::TextDisabled("%d points on the plot", (int)(2 * stream->t.size()));
            ImGui::Spacing();
            RateSlider(width);
            ImGui::Spacing();
            RichMd::Render("The same GUI runs beside a **Jupyter notebook**, in Python: `immapp.nb.start(gui)` returns "
                           "at once, and the cells keep feeding it.");
            ImGui::Unindent(em * 0.5f);
        }

        void SideNarrow()  // the figures on one line (on two when they do not fit), then the rate
        {
            float em = HelloImGui::EmSize(), width = ImGui::GetWindowWidth() - em;
            std::string line = FramesLine() + "  |  " + SamplesLine();
            ImGui::Indent(em * 0.5f);
            if (ImGui::CalcTextSize(line.c_str()).x <= width)
                ImGui::TextDisabled("%s", line.c_str());
            else
            {
                ImGui::TextDisabled("%s", FramesLine().c_str());
                ImGui::TextDisabled("%s", SamplesLine().c_str());
            }
            RateSlider(width);
            ImGui::Unindent(em * 0.5f);
        }

        void SlideGui(ImVec2 contentSize)
        {
            if (!stream)
                stream.emplace();
            stream->Step();
            float em = HelloImGui::EmSize(), gap = em * 0.5f;
            if (IsSmallScreen())  // the plot, then the figures and the rate under it
            {
                std::string line = FramesLine() + "  |  " + SamplesLine();
                bool twoLines = ImGui::CalcTextSize(line.c_str()).x > contentSize.x - em;
                float panelH = ImGui::GetTextLineHeightWithSpacing() * (twoLines ? 2 : 1) + ImGui::GetFrameHeight()
                               + em * 1.3f;
                Plot(ImVec2(contentSize.x, contentSize.y - panelH - gap));
                DrawSidePanel("##stream_side", contentSize.x, panelH, SideNarrow);
                return;
            }
            float sideW = std::min(em * 17.f, contentSize.x * 0.4f);
            Plot(ImVec2(contentSize.x - sideW - gap, contentSize.y));
            ImGui::SameLine(0.f, gap);
            DrawSidePanel("##stream_side", sideW, contentSize.y, Side);
        }
    }


    // ============================================================================
    // Slide: a tiny neural network learns two spirals (the explorable's widget, see explorables/neural_spiral)
    // ============================================================================
    namespace IntroSpiral
    {
        const int HIDDEN = 16;  // the hidden units
        const int STEPS_PER_FRAME = 20;
        const float EXTENT = 1.2f;  // the plane shown: [-EXTENT, EXTENT] on both axes
        const int GRID = 80;  // the network's answer is drawn on a GRID x GRID heatmap

        // Two inputs, one hidden layer of HIDDEN units (tanh), one output (a sigmoid: the probability of class 1)
        struct Network
        {
            std::vector<double> w1x, w1y, b1, w2;  // w1: (2, HIDDEN), as its two rows
            double b2 = 0.0;

            // The probability of class 1 at (x, y), and the hidden units' answers h
            double Forward(double x, double y, std::vector<double>* h = nullptr) const
            {
                double s = b2;
                for (int j = 0; j < HIDDEN; j++)
                {
                    double hj = std::tanh(x * w1x[j] + y * w1y[j] + b1[j]);
                    if (h)
                        (*h)[j] = hj;
                    s += hj * w2[j];
                }
                return 1.0 / (1.0 + std::exp(-s));
            }
        };

        struct State
        {
            std::mt19937 rng{0};
            std::vector<double> xs, ys, labels;  // the points and their classes (0 on the first spiral, 1 on the other)
            float rate = 1.f;
            bool training = true;  // the slide trains as soon as it shows
            Network net;
            int steps = 0;
            std::vector<double> losses;
            double accuracy = 0.0;

            State()
            {
                // Two spirals of 100 points each, with a little noise
                std::normal_distribution<double> noise(0.0, 0.02);
                const int n = 200;
                for (int k = 0; k < n; k++)
                {
                    int cls = k / (n / 2);
                    double radius = 0.08 + (1.0 - 0.08) * (k % (n / 2)) / (n / 2 - 1);
                    double angle = 2 * IM_PI * 2.0 * radius + IM_PI * cls;
                    xs.push_back(radius * std::cos(angle) + noise(rng));
                    ys.push_back(radius * std::sin(angle) + noise(rng));
                    labels.push_back(cls);
                }
                Reset();
            }

            void Reset()
            {
                std::normal_distribution<double> n1(0.0, 1.0), n05(0.0, 0.5), nw2(0.0, 1.0 / std::sqrt((double)HIDDEN));
                net = Network();
                for (int j = 0; j < HIDDEN; j++)
                {
                    net.w1x.push_back(n1(rng));
                    net.w1y.push_back(n1(rng));
                }
                for (int j = 0; j < HIDDEN; j++)
                    net.b1.push_back(n05(rng));
                for (int j = 0; j < HIDDEN; j++)
                    net.w2.push_back(nw2(rng));
                steps = 0;
                losses.clear();
                Record();
            }

            void Record()  // the loss (the cross-entropy) and the share of the points classified right
            {
                double loss = 0.0, right = 0.0;
                for (size_t i = 0; i < xs.size(); i++)
                {
                    double p = std::clamp(net.Forward(xs[i], ys[i]), 1e-7, 1 - 1e-7);
                    loss -= labels[i] * std::log(p) + (1 - labels[i]) * std::log(1 - p);
                    right += ((p > 0.5) == (labels[i] > 0.5)) ? 1.0 : 0.0;
                }
                losses.push_back(loss / xs.size());
                accuracy = right / xs.size();
            }

            void GradientStep()  // one step of gradient descent on all the points (backpropagation, by hand)
            {
                std::vector<double> gw1x(HIDDEN, 0.0), gw1y(HIDDEN, 0.0), gb1(HIDDEN, 0.0), gw2(HIDDEN, 0.0), h(HIDDEN);
                double gb2 = 0.0, nb = (double)xs.size();
                for (size_t i = 0; i < xs.size(); i++)
                {
                    double p = net.Forward(xs[i], ys[i], &h);
                    double ds = (p - labels[i]) / nb;
                    for (int j = 0; j < HIDDEN; j++)
                    {
                        double da = ds * net.w2[j] * (1 - h[j] * h[j]);
                        gw1x[j] += xs[i] * da;
                        gw1y[j] += ys[i] * da;
                        gb1[j] += da;
                        gw2[j] += h[j] * ds;
                    }
                    gb2 += ds;
                }
                for (int j = 0; j < HIDDEN; j++)
                {
                    net.w1x[j] -= rate * gw1x[j];
                    net.w1y[j] -= rate * gw1y[j];
                    net.b1[j] -= rate * gb1[j];
                    net.w2[j] -= rate * gw2[j];
                }
                net.b2 -= rate * gb2;
            }

            void Train()
            {
                for (int k = 0; k < STEPS_PER_FRAME; k++)
                    GradientStep();
                steps += STEPS_PER_FRAME;
                Record();
            }
        };

        std::unique_ptr<State> state;

        // Muted red (class 0), dark grey where the network hesitates, muted blue (class 1): the points stay visible
        ImPlotColormap Colormap()
        {
            ImPlotColormap cmap = ImPlot::GetColormapIndex("answer");
            if (cmap == -1)
            {
                ImVec4 colors[] = {{0.5f, 0.15f, 0.15f, 1.f}, {0.15f, 0.15f, 0.15f, 1.f}, {0.15f, 0.25f, 0.55f, 1.f}};
                cmap = ImPlot::AddColormap("answer", colors, 3, false);
            }
            return cmap;
        }

        void Plane(ImVec2 size)
        {
            ImPlotFlags flags = ImPlotFlags_NoLegend | ImPlotFlags_NoMenus | ImPlotFlags_NoMouseText | ImPlotFlags_Equal;
            if (!ImPlot::BeginPlot("##plane", size, flags))
                return;
            ImPlot::SetupAxesLimits(-EXTENT, EXTENT, -EXTENT, EXTENT, ImGuiCond_Always);
            static std::vector<double> answer(GRID * GRID);
            for (int row = 0; row < GRID; row++)  // row 0 on top
                for (int col = 0; col < GRID; col++)
                {
                    double x = -EXTENT + 2 * EXTENT * col / (GRID - 1), y = EXTENT - 2 * EXTENT * row / (GRID - 1);
                    answer[row * GRID + col] = state->net.Forward(x, y);
                }
            ImPlot::PushColormap(Colormap());
            ImPlot::PlotHeatmap("##answer", answer.data(), GRID, GRID, 0.0, 1.0, "", ImPlotPoint(-EXTENT, -EXTENT),
                                ImPlotPoint(EXTENT, EXTENT));
            ImPlot::PopColormap();
            struct ClassStyle { const char* label; double cls; ImVec4 color; };
            for (ClassStyle c : {ClassStyle{"class 0", 0.0, {1.f, 0.35f, 0.35f, 1.f}},
                                 ClassStyle{"class 1", 1.0, {0.35f, 0.6f, 1.f, 1.f}}})
            {
                std::vector<double> px, py;
                for (size_t i = 0; i < state->xs.size(); i++)
                    if (state->labels[i] == c.cls)
                    {
                        px.push_back(state->xs[i]);
                        py.push_back(state->ys[i]);
                    }
                ImPlotSpec spec;
                spec.Marker = ImPlotMarker_Circle;
                spec.MarkerSize = 3;
                spec.MarkerFillColor = c.color;
                spec.MarkerLineColor = ImVec4(1, 1, 1, 1);
                ImPlot::PlotScatter(c.label, px.data(), py.data(), (int)px.size(), spec);
            }
            ImPlot::EndPlot();
            HelloImGui::SetItemIsLive(state->training);  // the network learns on its own while it trains
        }

        void Loss(ImVec2 size)
        {
            if (!ImPlot::BeginPlot("Loss", size, ImPlotFlags_NoLegend | ImPlotFlags_NoMenus | ImPlotFlags_NoMouseText))
                return;
            ImPlot::SetupAxes("step", "", ImPlotAxisFlags_AutoFit, ImPlotAxisFlags_AutoFit);
            ImPlot::PlotLine("loss", state->losses.data(), (int)state->losses.size(), STEPS_PER_FRAME);
            ImPlot::EndPlot();
        }

        std::string Status()
        {
            char text[96];
            snprintf(text, sizeof(text), "step %d  |  loss %.3f  |  %.0f%% right", state->steps, state->losses.back(),
                     state->accuracy * 100);
            return text;
        }

        void Controls(float width)
        {
            float em = HelloImGui::EmSize();
            float rowLeft = ImGui::GetCursorScreenPos().x;
            if (ImGui::Button(state->training ? "Pause" : "Train", ImVec2(em * 5, 0)))
                state->training = !state->training;
            ImGui::SameLine();
            if (ImGui::Button("Reset"))
                state->Reset();
            std::string status = Status();
            float buttonsW = ImGui::GetItemRectMax().x - rowLeft + ImGui::GetStyle().ItemSpacing.x;
            if (buttonsW + ImGui::CalcTextSize(status.c_str()).x <= width)
                ImGui::SameLine();  // else on its own line (a phone)
            ImGui::TextUnformatted(status.c_str());
            ImGui::SetNextItemWidth(width - em * 9);
            ImGui::SliderFloat("learning rate", &state->rate, 0.01f, 10.f, "%.2f", ImGuiSliderFlags_Logarithmic);
        }

        void SlideGui(ImVec2 contentSize)
        {
            if (!state)
                state = std::make_unique<State>();
            if (state->training)
                state->Train();
            float em = HelloImGui::EmSize(), gap = em * 0.5f;
            bool statusFits = em * 9.5f + ImGui::CalcTextSize("step 99999  |  loss 0.000  |  100% right").x
                              <= contentSize.x;
            float controlsH = ImGui::GetFrameHeightWithSpacing() * (statusFits ? 2 : 3) + em * 0.2f;
            float plotsH = contentSize.y - controlsH;
            if (IsSmallScreen())  // the plane, then the loss under it (when there is room for a curve)
            {
                float side = std::min(contentSize.x, plotsH * 0.65f);
                if (plotsH - side - gap < em * 7)
                    side = std::min(contentSize.x, plotsH);
                Plane(ImVec2(side, side));
                if (plotsH - side - gap >= em * 7)
                    Loss(ImVec2(contentSize.x, plotsH - side - gap));
            }
            else
            {
                float side = std::min(plotsH, contentSize.x * 0.55f);
                Plane(ImVec2(side, side));
                ImGui::SameLine(0.f, gap);
                Loss(ImVec2(contentSize.x - side - gap, side));
            }
            Controls(contentSize.x);
        }
    }


#ifdef IMGUI_BUNDLE_WITH_IMMVISION
    // A Julia set, colored by its smooth escape time: an RGB uint8 image
    ImmVision::ImageBuffer JuliaImage(int w, int h, double cRe = -0.8, double cIm = 0.156, int maxIter = 100)
    {
        ImmVision::ImageBuffer image = ImmVision::ImageBuffer::Zeros(w, h, 3, ImmVision::ImageDepth::uint8);
        for (int row = 0; row < h; row++)
        {
            uint8_t* pixels = image.ptr<uint8_t>(row);
            for (int col = 0; col < w; col++)
            {
                double zr = -1.6 + 3.2 * col / (w - 1), zi = -1.2 + 2.4 * row / (h - 1);
                double count = maxIter;
                for (int i = 0; i < maxIter; i++)
                {
                    double r = zr * zr - zi * zi + cRe;
                    zi = 2 * zr * zi + cIm;
                    zr = r;
                    double modulus = std::sqrt(zr * zr + zi * zi);
                    if (modulus > 4.0)
                    {
                        count = i + 1 - std::log2(std::log(modulus));
                        break;
                    }
                }
                double t = std::clamp(count / maxIter, 0.0, 1.0);
                double rgb[3] = {9 * (1 - t) * t * t * t, 15 * (1 - t) * (1 - t) * t * t, 8.5 * (1 - t) * (1 - t) * (1 - t) * t};
                for (int k = 0; k < 3; k++)
                    pixels[3 * col + k] = (uint8_t)std::clamp(rgb[k] * 255.0, 0.0, 255.0);
            }
        }
        return image;
    }

    // The magnitude of the gradient of the gray image (central differences): a float image
    ImmVision::ImageBuffer Gradient(const ImmVision::ImageBuffer& image)
    {
        int w = image.width, h = image.height;
        std::vector<float> gray((size_t)w * h);
        for (int row = 0; row < h; row++)
        {
            const uint8_t* pixels = image.ptr<uint8_t>(row);
            for (int col = 0; col < w; col++)
            {
                float sum = 0.f;
                for (int k = 0; k < image.channels; k++)
                    sum += pixels[image.channels * col + k];
                gray[(size_t)row * w + col] = sum / image.channels / 255.f;
            }
        }
        ImmVision::ImageBuffer edges = ImmVision::ImageBuffer::Zeros(w, h, 1, ImmVision::ImageDepth::float32);
        auto at = [&](int row, int col) { return gray[(size_t)std::clamp(row, 0, h - 1) * w + std::clamp(col, 0, w - 1)]; };
        for (int row = 0; row < h; row++)
        {
            float* out = edges.ptr<float>(row);
            for (int col = 0; col < w; col++)
            {
                // Central differences inside, one-sided ones on the border (as numpy.gradient)
                float dx = (col == 0 || col == w - 1) ? at(row, col + 1) - at(row, col - 1)
                                                      : (at(row, col + 1) - at(row, col - 1)) / 2;
                float dy = (row == 0 || row == h - 1) ? at(row + 1, col) - at(row - 1, col)
                                                      : (at(row + 1, col) - at(row - 1, col)) / 2;
                out[col] = std::sqrt(dx * dx + dy * dy);
            }
        }
        return edges;
    }


    // ============================================================================
    // Slide: ImmVision, an image and its edges, inspected (a Julia set)
    // ============================================================================
    namespace IntroImmVision
    {
        const double ZOOM_IN = 1.5, HOLD = 1.5, ZOOM_OUT = 1.5, PAUSE = 3.0;  // s: the animation's phases
        const double CYCLE = ZOOM_IN + HOLD + ZOOM_OUT + PAUSE;
        // Display pixels per image pixel at the end of the zoom: ImmVision draws the pixels' values from 36 (uint8
        // images) or 48 (float images), whatever the size of the image on screen
        const double PIXEL_VALUES_ZOOM = 60.0;

        ImmVision::ImageBuffer image, edges;
        ImmVision::ImageParams params, paramsEdges;
        bool inited = false, animating = true;
        double startTime = 0.0;
        ImmVision::Point2d zoomCenter;

        void Init()
        {
            image = JuliaImage(320, 240);
            edges = Gradient(image);  // a float image: ImmVision applies a colormap to it
            for (ImmVision::ImageParams* p : {&params, &paramsEdges})
            {
                p->ShowOptionsPanel = false;
                p->ShowImageInfo = false;
                p->ShowPixelInfo = true;
                p->ShowZoomButtons = true;  // below the image: zoom in, out, to fit, at 1:1
                p->ZoomKey = "intro_immvision";  // the two images zoom and pan together
            }
            paramsEdges.ColormapSettings.Colormap = "Viridis";
            zoomCenter = ImmVision::Point2d(image.width * 0.56, image.height * 0.42);
            startTime = ImmApp::ClockSeconds();
            inited = true;
        }

        // From 0 (the whole image) to 1 (its pixels and their values): the whole image first, then the zoom in, a
        // hold, and the zoom out
        double ZoomProgress()
        {
            double elapsed = std::fmod(ImmApp::ClockSeconds() - startTime, CYCLE);
            if (elapsed < PAUSE)
                return 0.0;
            elapsed -= PAUSE;
            if (elapsed < ZOOM_IN)
            {
                double t = elapsed / ZOOM_IN;
                return 1.0 - (1.0 - t) * (1.0 - t);
            }
            elapsed -= ZOOM_IN;
            if (elapsed < HOLD)
                return 1.0;
            elapsed -= HOLD;
            if (elapsed < ZOOM_OUT)
            {
                double t = elapsed / ZOOM_OUT;
                return 1.0 - t * t;
            }
            return 0.0;
        }

        bool UserInteracts()
        {
            bool hovering = params.MouseInfo.IsMouseHovering || paramsEdges.MouseInfo.IsMouseHovering;
            return hovering && (ImGui::IsMouseDragging(0) || ImGui::GetIO().MouseWheel != 0.f);
        }

        void GuiMain(ImVec2 size, bool both)
        {
            if (!inited)
                Init();
            if (animating && UserInteracts())
                animating = false;
            float em = HelloImGui::EmSize();
            int imgW = image.width, imgH = image.height;
            int displayW = both ? (int)(size.x * 0.5f - em) : (int)(size.x - em * 2.2f);  // the frame around an image
            int displayH = (int)std::min((float)displayW * imgH / imgW, size.y);
            displayW = displayH * imgW / imgH;
            params.ImageDisplaySize = paramsEdges.ImageDisplaySize = ImmVision::Size(displayW, displayH);
            if (animating)  // from the whole image (the zoom that fits it, centered) to the pixels around the target
            {
                double fitZoom = (double)displayW / imgW, t = ZoomProgress();
                double zoom = fitZoom + (std::max(PIXEL_VALUES_ZOOM, fitZoom) - fitZoom) * t;
                ImmVision::Point2d center(imgW * 0.5 + (zoomCenter.x - imgW * 0.5) * t,
                                          imgH * 0.5 + (zoomCenter.y - imgH * 0.5) * t);
                params.ZoomPanMatrix = ImmVision::MakeZoomPanMatrix(center, zoom, params.ImageDisplaySize);
                paramsEdges.ZoomPanMatrix = params.ZoomPanMatrix;
            }
            ImmVision::Image("Julia set##intro", image, &params);
            if (both)
            {
                ImGui::SameLine();
                ImmVision::Image("Its edges##intro", edges, &paramsEdges);
            }
            HelloImGui::SetItemIsLive(animating);  // the zoom moves on its own
        }

        void GuiSide()
        {
            ImGui::PushStyleColor(ImGuiCol_Text, ImGui::GetStyleColorVec4(ImGuiCol_TextDisabled));
            const char* hint = IsSmallScreen() ? "Drag to pan, the buttons zoom" : "Drag to pan, scroll to zoom";
            ImGui::TextWrapped("%s: at a high zoom, the pixels show their values", hint);
            ImGui::PopStyleColor();
            if (!animating)
            {
                ImGui::SameLine();
                if (ImGui::SmallButton("Restart the animation"))
                {
                    animating = true;
                    startTime = ImmApp::ClockSeconds();
                }
            }
        }

        void SlideGui(ImVec2 contentSize)
        {
            float em = HelloImGui::EmSize();
            bool narrow = IsSmallScreen();
            // The zoom buttons under the images, then the hint (on two lines on a phone). On a phone, no pixel info:
            // it shows the pixel under the mouse, and a finger does not hover
            params.ShowPixelInfo = !narrow;
            float sideH = em * (narrow ? 5.f : 3.8f);
            GuiMain(ImVec2(contentSize.x, contentSize.y - sideH), !narrow);
            GuiSide();
        }
    }


    // ============================================================================
    // Slide: a node editor, an image through a pipeline of filters (a mini version of
    // demos_node_editor/demo_node_editor_image_pipeline.cpp, with filters written as loops)
    // ============================================================================
    namespace IntroPipeline
    {
        namespace ed = ax::NodeEditor;

        const int IMAGE_W = 200, IMAGE_H = 150;  // the image that enters the pipeline (a half of the picture)
        const char* PICTURE = "images/golden_gate.jpg";  // an asset; from picsum.photos (Chris Brignola, Unsplash)
        const float IMAGE_WIDTH_EM = 7.f;  // the width of the images in the nodes (it gives the nodes their width)
        const ImVec4 LINK_COLOR(0.4f, 0.75f, 1.f, 1.f);
        const ImVec4 UNLINKED(0.3f, 0.3f, 0.3f, 1.f);

        using Image = ImmVision::ImageBuffer;

        // A gaussian blur, in two passes (one per axis), the borders repeated
        Image Blur(const Image& image, float sigma)
        {
            if (sigma < 0.3f)
                return image;
            int radius = (int)std::ceil(3.f * sigma), w = image.width, h = image.height, ch = image.channels;
            std::vector<float> kernel;
            float sum = 0.f;
            for (int k = -radius; k <= radius; k++)
            {
                kernel.push_back(std::exp(-0.5f * (k / sigma) * (k / sigma)));
                sum += kernel.back();
            }
            for (float& weight : kernel)
                weight /= sum;
            std::vector<float> a((size_t)w * h * ch), b(a.size());
            for (int row = 0; row < h; row++)
                for (int i = 0; i < w * ch; i++)
                    a[(size_t)row * w * ch + i] = image.ptr<uint8_t>(row)[i];
            for (int pass = 0; pass < 2; pass++)  // along the rows, then along the columns
            {
                for (int row = 0; row < h; row++)
                    for (int col = 0; col < w; col++)
                        for (int c = 0; c < ch; c++)
                        {
                            float acc = 0.f;
                            for (int k = -radius; k <= radius; k++)
                            {
                                int r = pass == 0 ? row : std::clamp(row + k, 0, h - 1);
                                int q = pass == 0 ? std::clamp(col + k, 0, w - 1) : col;
                                acc += kernel[k + radius] * a[((size_t)r * w + q) * ch + c];
                            }
                            b[((size_t)row * w + col) * ch + c] = acc;
                        }
                std::swap(a, b);
            }
            Image out = Image::Zeros(w, h, ch, ImmVision::ImageDepth::uint8);
            for (int row = 0; row < h; row++)
                for (int i = 0; i < w * ch; i++)
                    out.ptr<uint8_t>(row)[i] = (uint8_t)std::clamp(a[(size_t)row * w * ch + i], 0.f, 255.f);
            return out;
        }

        // The magnitude of the gradient of the gray image, scaled to 0..255: a gray image
        Image Edges(const Image& image)
        {
            Image gradient = Gradient(image);
            float maxValue = 1e-6f;
            for (int row = 0; row < gradient.height; row++)
                for (int col = 0; col < gradient.width; col++)
                    maxValue = std::max(maxValue, gradient.ptr<float>(row)[col]);
            Image out = Image::Zeros(gradient.width, gradient.height, 1, ImmVision::ImageDepth::uint8);
            for (int row = 0; row < gradient.height; row++)
                for (int col = 0; col < gradient.width; col++)
                    out.ptr<uint8_t>(row)[col] = (uint8_t)(255.f * gradient.ptr<float>(row)[col] / maxValue);
            return out;
        }

        // The edges painted in yellow over the image
        Image Overlay(const Image& image, const Image& edges, float strength)
        {
            if (image.width != edges.width || image.height != edges.height)
                return image;
            Image out = Image::Zeros(image.width, image.height, 3, ImmVision::ImageDepth::uint8);
            const float yellow[3] = {255.f, 220.f, 60.f};
            for (int row = 0; row < image.height; row++)
                for (int col = 0; col < image.width; col++)
                {
                    float edge = 0.f;
                    for (int k = 0; k < edges.channels; k++)
                        edge += edges.ptr<uint8_t>(row)[edges.channels * col + k];
                    float mask = std::clamp(edge / edges.channels / 255.f * strength * 2.f, 0.f, 1.f);
                    for (int c = 0; c < 3; c++)
                    {
                        float v = image.ptr<uint8_t>(row)[image.channels * col + std::min(c, image.channels - 1)];
                        out.ptr<uint8_t>(row)[3 * col + c] = (uint8_t)(v * (1.f - mask) + yellow[c] * mask);
                    }
                }
            return out;
        }

        // The image at half its size (each pixel the mean of 2 x 2): the filters run four times faster
        Image HalfSize(const Image& image)
        {
            int w = image.width / 2, h = image.height / 2, ch = image.channels;
            Image out = Image::Zeros(w, h, ch, ImmVision::ImageDepth::uint8);
            for (int row = 0; row < h; row++)
                for (int col = 0; col < w; col++)
                    for (int c = 0; c < ch; c++)
                    {
                        int sum = image.ptr<uint8_t>(2 * row)[ch * 2 * col + c] + image.ptr<uint8_t>(2 * row)[ch * (2 * col + 1) + c]
                                + image.ptr<uint8_t>(2 * row + 1)[ch * 2 * col + c] + image.ptr<uint8_t>(2 * row + 1)[ch * (2 * col + 1) + c];
                        out.ptr<uint8_t>(row)[ch * col + c] = (uint8_t)(sum / 4);
                    }
            return out;
        }

        // The asset's picture at half its size, or a Julia set when it cannot be read
        Image DefaultPicture()
        {
            Image picture;
            if (HelloImGui::AssetExists(PICTURE))
                picture = ImmVision::ImRead(HelloImGui::AssetFileFullPath(PICTURE));
            if (picture.empty() || picture.depth != ImmVision::ImageDepth::uint8)
                return JuliaImage(IMAGE_W, IMAGE_H, -0.8, 0.156, 60);
            return HalfSize(picture);
        }

        int NextId()
        {
            static int id = 1;
            return id++;
        }

        // A node of the pipeline: its pins, its parameter, and its result (computed again when an input or the
        // parameter changes)
        struct Node
        {
            std::string kind;
            ed::NodeId id = ed::NodeId(NextId());
            std::vector<std::pair<ed::PinId, std::string>> inputs;
            ed::PinId output = ed::PinId(NextId());
            std::optional<float> param;  // the blur's sigma, the overlay's strength
            std::optional<Image> result;
            std::vector<std::pair<int, int>> key;  // what the result was computed from: its sources and their versions
            float keyParam = -1.f;
            int version = 0;  // one more at each new result: its image is sent again to the GPU
            int shownVersion = -1;

            Node(std::string kind_, std::vector<std::string> inputNames, std::optional<float> param_)
                : kind(std::move(kind_)), param(param_)
            {
                for (const auto& name : inputNames)
                    inputs.emplace_back(ed::PinId(NextId()), name);
            }

            Image Compute(const std::vector<const Image*>& in) const
            {
                if (kind == "Image")
                    return DefaultPicture();
                if (kind == "Blur")
                    return Blur(*in[0], *param);
                if (kind == "Edges")
                    return Edges(*in[0]);
                return Overlay(*in[0], *in[1], *param);  // Overlay
            }
        };

        struct Link { ed::LinkId id; ed::PinId output, input; };

        struct Graph
        {
            std::vector<std::unique_ptr<Node>> nodes;
            std::vector<Link> links;

            Graph()
            {
                Node* image = Add("Image", {}, std::nullopt);
                Node* blur = Add("Blur", {"in"}, 1.5f);
                Node* edges = Add("Edges", {"in"}, std::nullopt);
                Node* overlay = Add("Overlay", {"image", "edges"}, 0.8f);
                // Two levels, so that the link from the image to the overlay passes under the blur and the edges; on
                // a phone, two rows of two (the graph is fitted to the view: in a row of four, the nodes would be too
                // small to read)
                std::vector<ImVec2> positions = IsSmallScreen()
                    ? std::vector<ImVec2>{{0, 0}, {10, 0}, {0, 13}, {10, 13}}
                    : std::vector<ImVec2>{{0, 6}, {11, 0}, {22, 0}, {33, 11}};
                for (size_t i = 0; i < nodes.size(); i++)  // in the editor's coordinates
                    ed::SetNodePosition(nodes[i]->id, ImVec2(positions[i].x * HelloImGui::EmSize(),
                                                             positions[i].y * HelloImGui::EmSize()));
                Connect(image->output, blur->inputs[0].first);
                Connect(blur->output, edges->inputs[0].first);
                Connect(image->output, overlay->inputs[0].first);
                Connect(edges->output, overlay->inputs[1].first);
            }

            Node* Add(const char* kind, std::vector<std::string> inputs, std::optional<float> param)
            {
                nodes.push_back(std::make_unique<Node>(kind, std::move(inputs), param));
                return nodes.back().get();
            }

            void Connect(ed::PinId output, ed::PinId input)  // an input receives one link at most
            {
                links.erase(std::remove_if(links.begin(), links.end(), [&](const Link& l) { return l.input == input; }),
                            links.end());
                links.push_back({ed::LinkId(NextId()), output, input});
            }

            Node* NodeOfPin(ed::PinId pin)
            {
                for (auto& node : nodes)
                {
                    if (node->output == pin)
                        return node.get();
                    for (auto& [inputPin, name] : node->inputs)
                        if (inputPin == pin)
                            return node.get();
                }
                return nullptr;
            }

            bool IsOutput(ed::PinId pin)
            {
                for (auto& node : nodes)
                    if (node->output == pin)
                        return true;
                return false;
            }

            Node* Source(ed::PinId input)  // the node whose output reaches this input
            {
                for (auto& link : links)
                    if (link.input == input)
                        return NodeOfPin(link.output);
                return nullptr;
            }

            bool Feeds(Node* node, Node* other)  // true if node is other, or feeds it through links
            {
                if (node == other)
                    return true;
                for (auto& [pin, name] : other->inputs)
                {
                    Node* source = Source(pin);
                    if (source != nullptr && Feeds(node, source))
                        return true;
                }
                return false;
            }

            // The node's result, computed again only when its parameter or one of its sources changed
            const Image* Evaluate(Node* node)
            {
                std::vector<const Image*> in;
                std::vector<std::pair<int, int>> key;
                for (auto& [pin, name] : node->inputs)
                {
                    Node* source = Source(pin);
                    const Image* image = source ? Evaluate(source) : nullptr;
                    if (image == nullptr)
                    {
                        node->result.reset();
                        node->key.clear();
                        return nullptr;
                    }
                    in.push_back(image);
                    key.emplace_back(source->id.Get(), source->version);
                }
                float keyParam = node->param.value_or(0.f);
                if (!node->result.has_value() || key != node->key || keyParam != node->keyParam)
                {
                    node->result = node->Compute(in);
                    node->key = key;
                    node->keyParam = keyParam;
                    node->version++;
                }
                return &*node->result;
            }
        };

        ed::EditorContext* editor = nullptr;
        std::unique_ptr<Graph> graph;
        int frames = 0;
        ImVec2 lastSize(0, 0);

        void Pin(ed::PinId pin, ed::PinKind kind, bool linked)
        {
            ed::BeginPin(pin, kind);
            ed::PinPivotAlignment(ImVec2(0.5f, 0.5f));  // the links reach the center of the circle
            ed::PinPivotSize(ImVec2(0, 0));
            float radius = HelloImGui::EmSize(0.4f);
            ImVec2 topLeft = ImGui::GetCursorScreenPos();
            ImGui::Dummy(ImVec2(2 * radius, 2 * radius));
            ImVec2 center(topLeft.x + radius, topLeft.y + radius);
            ImDrawList* dl = ImGui::GetWindowDrawList();
            dl->AddCircleFilled(center, radius, ImGui::GetColorU32(linked ? LINK_COLOR : UNLINKED));
            dl->AddCircle(center, radius, ImGui::GetColorU32(ImGuiCol_Text), 0, 1.5f);
            ed::EndPin();
        }

        void DrawNode(Node& node)
        {
            float width = HelloImGui::EmSize(IMAGE_WIDTH_EM);
            ed::BeginNode(node.id);
            ImGui::PushID((int)node.id.Get());
            ImGui::TextUnformatted(node.kind.c_str());
            for (auto& [pin, name] : node.inputs)  // the inputs, on the left
            {
                Pin(pin, ed::PinKind::Input, graph->Source(pin) != nullptr);
                ImGui::SameLine();
                ImGui::TextUnformatted(name.c_str());
            }
            if (node.param.has_value())
            {
                ImGui::SetNextItemWidth(width);
                if (node.kind == "Blur")
                    ImGui::SliderFloat("##param", &*node.param, 0.f, 4.f, "sigma %.1f");
                else
                    ImGui::SliderFloat("##param", &*node.param, 0.f, 1.f, "strength %.2f");
            }
            float height = width * IMAGE_H / IMAGE_W;
            if (node.result.has_value())
            {
                ImmVision::ImageDisplay("##image", *node.result, ImmVision::Size((int)width, (int)height),
                                        node.version != node.shownVersion);
                node.shownVersion = node.version;
            }
            else
            {
                ImGui::Dummy(ImVec2(width, height * 0.5f));
                ImGui::TextDisabled("(no input)");
            }
            ImGui::BeginHorizontal("output", ImVec2(width, 0));  // the output, on the right
            ImGui::Spring();
            ImGui::TextUnformatted("out");
            bool linked = false;
            for (auto& link : graph->links)
                linked = linked || link.output == node.output;
            Pin(node.output, ed::PinKind::Output, linked);
            ImGui::EndHorizontal();
            ImGui::PopID();
            ed::EndNode();
        }

        // The editor's colors from the ImGui theme: its own are dark, and its text unreadable under a light theme.
        // Returns how many colors were pushed
        int PushThemeColors()
        {
            ImVec4 window = ImGui::GetStyleColorVec4(ImGuiCol_WindowBg), text = ImGui::GetStyleColorVec4(ImGuiCol_Text);
            auto towardsText = [&](float t, float alpha = 1.f) {
                return ImVec4(window.x + (text.x - window.x) * t, window.y + (text.y - window.y) * t,
                              window.z + (text.z - window.z) * t, alpha);
            };
            ed::PushStyleColor(ed::StyleColor_Bg, towardsText(0.04f));
            ed::PushStyleColor(ed::StyleColor_Grid, towardsText(0.5f, 0.12f));
            ed::PushStyleColor(ed::StyleColor_NodeBg, towardsText(0.10f));
            ed::PushStyleColor(ed::StyleColor_NodeBorder, towardsText(0.5f));
            return 4;
        }

        // A link dragged from a pin to another: accepted from an output to an input, unless it makes a loop
        void NewLinks()
        {
            if (!ed::BeginCreate(LINK_COLOR, 2.f))
                return;
            ed::PinId startId, endId;
            if (ed::QueryNewLink(&startId, &endId))
            {
                ed::PinId output = graph->IsOutput(endId) ? endId : startId;
                ed::PinId input = graph->IsOutput(endId) ? startId : endId;
                Node* outputNode = graph->NodeOfPin(output);
                Node* inputNode = graph->NodeOfPin(input);
                if (outputNode != nullptr && inputNode != nullptr)
                {
                    if (graph->IsOutput(output) && !graph->IsOutput(input) && !graph->Feeds(inputNode, outputNode))
                    {
                        if (ed::AcceptNewItem())
                            graph->Connect(output, input);
                    }
                    else
                        ed::RejectNewItem(ImVec4(1.f, 0.3f, 0.3f, 1.f), 2.f);
                }
            }
            ed::EndCreate();
        }

        void Deletions()
        {
            if (!ed::BeginDelete())
                return;
            ed::LinkId linkId;
            while (ed::QueryDeletedLink(&linkId))
                if (ed::AcceptDeletedItem())
                    graph->links.erase(std::remove_if(graph->links.begin(), graph->links.end(),
                                                      [&](const Link& l) { return l.id == linkId; }),
                                       graph->links.end());
            ed::NodeId nodeId;
            while (ed::QueryDeletedNode(&nodeId))
                ed::RejectDeletedItem();  // the four nodes stay
            ed::EndDelete();
        }

        void SlideGui(ImVec2 contentSize)
        {
            float em = HelloImGui::EmSize();
            if (editor == nullptr)
            {
                ed::Config config;
                config.SettingsFile = nullptr;  // the slide places its nodes: nothing to save
                editor = ed::CreateEditor(&config);
            }
            ed::EditorContext* previousEditor = ed::GetCurrentEditor();
            ed::SetCurrentEditor(editor);
            float hintH = em * (IsSmallScreen() ? 2.8f : 1.5f);
            ImVec2 editorSize(contentSize.x, contentSize.y - hintH);
            int nbColors = PushThemeColors();
            ed::Begin("##pipeline", editorSize);
            if (!graph)
                graph = std::make_unique<Graph>();
            for (auto& node : graph->nodes)
                graph->Evaluate(node.get());
            for (auto& node : graph->nodes)
                DrawNode(*node);
            for (auto& link : graph->links)
                ed::Link(link.id, link.output, link.input, LINK_COLOR, 3.f);
            NewLinks();
            Deletions();
            ed::End();
            ed::PopStyleColor(nbColors);
            // Fit the graph in the view once the editor knows the size of the nodes (the third frame), and when the
            // slide's size changes (a phone turned). The navigation functions work after End().
            bool sizeChanged = std::fabs(lastSize.x - editorSize.x) > 1.f || std::fabs(lastSize.y - editorSize.y) > 1.f;
            if (frames == 2 || (sizeChanged && frames > 2))
                ed::NavigateToContent(0.f);
            lastSize = editorSize;
            frames++;
            if (previousEditor != nullptr)  // the app's own editor, if it has one
                ed::SetCurrentEditor(previousEditor);
            ImGui::PushStyleColor(ImGuiCol_Text, ImGui::GetStyleColorVec4(ImGuiCol_TextDisabled));
            ImGui::TextWrapped("Move a slider: the nodes downstream follow. Drag from a pin to another to link them; "
                               "right-drag to pan, the wheel to zoom.");
            ImGui::PopStyleColor();
        }
    }
#endif  // IMGUI_BUNDLE_WITH_IMMVISION


    // ============================================================================
    // Slide: the drum sequencer (a table with angled headers, checkboxes, a toggle, a knob, a color wheel)
    // ============================================================================
    namespace IntroTable
    {
        const char* INSTRUMENTS[] = {"kick", "snare", "hihat", "open-hh", "tom", "clap", "rim", "crash"};
        const int NUM_INSTR = 8, NUM_BEATS = 16;
        bool pattern[NUM_BEATS][NUM_INSTR];
        float volume[NUM_INSTR] = {8.f, 7.f, 5.f, 4.f, 6.f, 7.f, 5.f, 3.f};  // per instrument, 0 to 10
        bool inited = false, playing = true;
        int playhead = 0;
        float bpm = 140.f, accum = 0.f;
        ImVec4 hlColor(0.3f, 0.5f, 1.f, 0.25f);

        void Init()  // a pattern of 8 steps, played twice
        {
            bool bar[8][NUM_INSTR] = {};
            bar[0][0] = bar[4][0] = true;  // kick
            bar[2][1] = bar[6][1] = true;  // snare
            for (int i = 0; i < 8; i += 2)
                bar[i][2] = true;  // hihat
            bar[1][3] = bar[5][3] = true;  // open-hh
            bar[3][4] = true;  // tom
            bar[6][5] = true;  // clap
            bar[4][6] = bar[7][6] = true;  // rim
            bar[0][7] = true;  // crash
            for (int row = 0; row < NUM_BEATS; row++)
                for (int col = 0; col < NUM_INSTR; col++)
                    pattern[row][col] = bar[row % 8][col];
            pattern[15][4] = pattern[14][4] = true;  // a tom fill at the end
            inited = true;
        }

        void Update()
        {
            if (!playing)
                return;
            accum += std::min(ImGui::GetIO().DeltaTime, 0.1f);  // clamped: no drift when the tab is in the background
            if (accum >= 60.f / bpm)
            {
                accum = 0.f;  // reset instead of subtract, to prevent an accumulated drift
                playhead = (playhead + 1) % NUM_BEATS;
            }
        }

        void GuiMain(ImVec2 size, int numInstr)
        {
            if (!inited)
                Init();
            Update();
            ImGuiTableFlags flags = ImGuiTableFlags_SizingFixedFit | ImGuiTableFlags_ScrollX | ImGuiTableFlags_ScrollY
                                    | ImGuiTableFlags_BordersOuter | ImGuiTableFlags_BordersInnerH
                                    | ImGuiTableFlags_HighlightHoveredColumn;
            if (!ImGui::BeginTable("##drum_seq", numInstr + 1, flags, size))
                return;
            ImGui::TableSetupColumn("Beat", ImGuiTableColumnFlags_NoHide);
            for (int n = 0; n < numInstr; n++)
                ImGui::TableSetupColumn(INSTRUMENTS[n], ImGuiTableColumnFlags_AngledHeader | ImGuiTableColumnFlags_WidthFixed);
            ImGui::TableSetupScrollFreeze(1, 2);
            ImGui::TableAngledHeadersRow();
            ImGui::TableHeadersRow();
            ImU32 hl = ImGui::ColorConvertFloat4ToU32(hlColor);
            for (int row = 0; row < NUM_BEATS; row++)
            {
                ImGui::PushID(row);
                ImGui::TableNextRow();
                bool isPlayhead = row == playhead && playing;
                ImGui::TableSetColumnIndex(0);
                if (isPlayhead)
                    ImGui::TableSetBgColor(ImGuiTableBgTarget_CellBg, hl);
                ImGui::AlignTextToFramePadding();
                ImGui::Text("%d", row + 1);
                for (int col = 0; col < numInstr; col++)
                    if (ImGui::TableSetColumnIndex(col + 1))
                    {
                        if (isPlayhead)
                            ImGui::TableSetBgColor(ImGuiTableBgTarget_CellBg, hl);
                        ImGui::PushID(col);
                        ImGui::Checkbox("", &pattern[row][col]);
                        ImGui::PopID();
                    }
                ImGui::PopID();
            }
            // The last row: a volume knob per instrument
            ImGui::TableNextRow();
            ImGui::TableSetColumnIndex(0);
            ImGui::AlignTextToFramePadding();
            ImGui::TextDisabled("Vol");
            for (int col = 0; col < numInstr; col++)
                if (ImGui::TableSetColumnIndex(col + 1))
                {
                    ImGui::PushID(col);
                    ImGuiKnobs::Knob("##vol", &volume[col], 0.f, 10.f, 0.f, "%.0f", ImGuiKnobVariant_WiperDot,
                                     ImGui::GetFrameHeight(), ImGuiKnobFlags_NoTitle | ImGuiKnobFlags_NoInput);
                    ImGui::PopID();
                }
            ImGui::EndTable();
            HelloImGui::SetItemIsLive(playing);  // the playhead moves on its own
        }

        void PlayToggle()
        {
            float em = HelloImGui::EmSize();
            ImGuiToggleConfig config = ImGuiTogglePresets::MaterialStyle();
            config.Size = ImVec2(em * 2.5f, em * 1.2f);
            ImGui::Toggle("##play", &playing, config);
        }

        void BpmKnob(float sizeEm) { AccentKnob("##bpm", &bpm, 60.f, 300.f, "%.0f", HelloImGui::EmSize(sizeEm)); }

        void GuiSide()  // play, the tempo and the highlight's color on one row; below, the picture of the manual
        {
            float em = HelloImGui::EmSize();
            ImGui::BeginGroup();
            ImGui::TextUnformatted("Play");
            PlayToggle();
            ImGui::EndGroup();
            ImGui::SameLine(0.f, em * 1.5f);
            ImGui::BeginGroup();
            ImGui::TextUnformatted("Tempo");
            BpmKnob(3.5f);
            ImGui::EndGroup();
            ImGui::SameLine(0.f, em * 1.5f);
            ImGui::BeginGroup();
            ImGui::TextUnformatted("Highlight");
            ImGui::SetNextItemWidth(em * 7.f);
            ImGui::ColorPicker4("##hl_wheel", &hlColor.x,
                                ImGuiColorEditFlags_NoSidePreview | ImGuiColorEditFlags_NoInputs | ImGuiColorEditFlags_NoLabel
                                | ImGuiColorEditFlags_AlphaBar | ImGuiColorEditFlags_PickerHueWheel);
            ImGui::EndGroup();
#ifdef HELLOIMGUI_WITH_TEST_ENGINE
            IntroAutomations::ShowLink("More info: complex app layout", IntroAutomations::showDocking);
#endif
            // The manual of all the widgets, below: as wide as the panel, or as tall as the space left
            ImGui::Spacing();
            ImGui::Separator();
            ImGui::Spacing();
            ManualTeaser("All of Dear ImGui's widgets, with their code: the interactive manual", "manual_imgui.py");
        }

        void GuiSideNarrow()  // play and the tempo, on one line
        {
            ImGui::TextUnformatted("Play");
            ImGui::SameLine();
            PlayToggle();
            ImGui::SameLine(0.f, HelloImGui::EmSize(1.5f));
            ImGui::TextUnformatted("Tempo");
            ImGui::SameLine();
            BpmKnob(2.5f);
        }

        void SlideGui(ImVec2 contentSize)
        {
            float em = HelloImGui::EmSize(), gap = em * 0.5f;
            if (IsSmallScreen())  // six instruments fit the width; the controls under the table
            {
                float panelH = em * 4.6f;  // the tempo knob and its value under it
                GuiMain(ImVec2(contentSize.x, contentSize.y - panelH - gap), 6);
                DrawSidePanel("##table_side", contentSize.x, panelH, GuiSideNarrow);
                return;
            }
            float tableW = std::min(em * 21.f, contentSize.x * 0.5f);  // its columns and their angled headers
            GuiMain(ImVec2(tableW, contentSize.y), NUM_INSTR);
            ImGui::SameLine(0.f, gap);
            DrawSidePanel("##table_side", contentSize.x - tableW - gap, contentSize.y, GuiSide);
        }
    }


    // A read-only editor, for a page of code to read
    std::unique_ptr<TextEditor> MakeCodeEditor(const std::string& code, const TextEditor::Language* language)
    {
        auto editor = std::make_unique<TextEditor>();
        editor->SetText(code);
        editor->SetLanguage(language);
        editor->SetPalette(TextEditor::GetDarkPalette());
        return editor;
    }


    // ============================================================================
    // Slide: markdown, the source and its live render
    // ============================================================================
    namespace IntroMarkdown
    {
        const char* SAMPLE = R"md(
## Dear ImGui Bundle — live markdown
> *Edit the source, and watch the render follow in real time.*
### What you can write
- **Bold**, *italic*, ~~strike~~, <u>underline</u>, <mark>highlight</mark>, `code`
- Keyboard shortcuts: <kbd>Ctrl</kbd>+<kbd>S</kbd>, <kbd>Cmd</kbd>+<kbd>K</kbd>
- Chemistry & exponents: H<sub>2</sub>O, x<sup>2</sup>+y<sup>2</sup>=r<sup>2</sup>
- [Clickable links](https://github.com/pthom/imgui_bundle) and bare URLs: https://dearimgui.org
### A little code
```cpp
#include "imgui.h"
#include "immapp/immapp.h"
int main() { ImmApp::Run([] { ImGui::Text("Hello, World!"); }); }
```
### A little math
Euler's identity $e^{i\pi} + 1 = 0$ generalizes to:
$$
e^{i\theta} = \cos\theta + i\sin\theta
$$
### A diagram
```mermaid
flowchart LR
    A[Markdown] --> B{rich_md}
    B --> C[Text and math]
    B --> D[Diagrams]
```
## Tables with *resizable* columns and *alignment*
|Id| Library    | What it does        |
|-:|:----------:|---------------------|
|1| ImGui      | Core widgets        |
|2| ImPlot     | 2D plots            |
|3| ImPlot3D   | 3D plots            |
|4| ImmVision  | Image analysis      |
|5| rich_md   | This renderer       |
> [!TIP]
> Click the triangle below to unfold. Try adding your own collapsible section.
<details>
<summary>Images, including from the web</summary>
<img src="https://picsum.photos/id/1019/200/130" height="100" />
</details>
)md";

        std::unique_ptr<TextEditor> editor;
        bool showSource = false;  // on a phone: the source or the render, one at a time

        void Source(ImVec2 size)
        {
            float em = HelloImGui::EmSize();
            PanelBg(ImGui::GetCursorScreenPos(), size);
            ImGui::BeginChild("##md_source", size, false, ImGuiWindowFlags_NoBackground);
            auto codeFont = RichMd::GetCodeFont();
            ImGui::PushFont(codeFont.font, codeFont.size * 0.9f);
            editor->Render("##md_editor", ImVec2(size.x - em * 0.2f, size.y));
            ImGui::PopFont();
            ImGui::EndChild();
        }

        // The render, as a document: its table of contents beside it (or above it, when narrow)
        void Rendered(ImVec2 size) { RichMd::RenderDocument("##md_rendered", editor->GetText(), size); }

        void SlideGui(ImVec2 contentSize)
        {
            if (!editor)
            {
                editor = MakeCodeEditor(SAMPLE, TextEditor::Language::Markdown());
            }
            float em = HelloImGui::EmSize(), gap = em * 0.5f;
            if (IsSmallScreen())  // one panel at a time
            {
                if (ImGui::RadioButton("Rendered", !showSource))
                    showSource = false;
                ImGui::SameLine();
                if (ImGui::RadioButton("Source", showSource))
                    showSource = true;
                ImVec2 size(contentSize.x, contentSize.y - ImGui::GetFrameHeightWithSpacing());
                if (showSource)
                    Source(size);
                else
                    Rendered(size);
                return;
            }
            float halfW = (contentSize.x - gap) * 0.5f;
            Source(ImVec2(halfW, contentSize.y));
            ImGui::SameLine(0, gap);
            Rendered(ImVec2(halfW, contentSize.y));
        }
    }


    // ============================================================================
    // Slide: a whole app, the heart haiku (demos_immapp/haiku_implot_heart): its complete code, and beside it the
    // app that this code runs
    // ============================================================================
    namespace IntroHaiku
    {
        const char* CODE_PYTHON = R"code(import time
import numpy as np
from imgui_bundle import implot, imgui_knobs, imgui, immapp, hello_imgui

# Fill x and y whose plot is a heart
vals = np.arange(0, np.pi * 2, 0.01)
x = np.power(np.sin(vals), 3) * 16
y = 13 * np.cos(vals) - 5 * np.cos(2 * vals) - 2 * np.cos(3 * vals) - np.cos(4 * vals)
# Heart pulse rate and time tracking
phase = 0.0
t0 = time.time() + 0.2
heart_pulse_rate = 80.0
heart_thickness = 0.15
LARGEST_SCALE = 0.9 * 1.3  # of the heart: the pulse scales it up to 0.9, the thickness up to 1.3

def gui():
    global heart_pulse_rate, phase, t0, heart_thickness
    t = time.time()
    phase += (t - t0) * heart_pulse_rate / (np.pi * 2)
    k = 0.8 + 0.1 * np.cos(phase)
    t0 = t

    if implot.begin_plot("Heart", immapp.em_to_vec2(21, 21)):
        implot.setup_axes_limits(x.min() * LARGEST_SCALE, x.max() * LARGEST_SCALE,
                                 y.min() * LARGEST_SCALE, y.max() * LARGEST_SCALE)
        for k2 in np.arange(1 - heart_thickness, 1 + heart_thickness, 0.01):
            implot.plot_line("", x * k * k2, y * k * k2)  # some thickness
        implot.end_plot()
        hello_imgui.set_item_is_live()  # the heart beats on its own

    _, heart_pulse_rate = imgui_knobs.knob("Pulse", heart_pulse_rate, 30, 180,
        variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot, size=immapp.em_size(4.0))
    imgui.same_line()
    _, heart_thickness = imgui_knobs.knob("Line Thickness", heart_thickness, 0.01, 0.3,
        variant=imgui_knobs.ImGuiKnobVariant_.wiper_dot, size=immapp.em_size(4.0))

if __name__ == "__main__":
    immapp.run(gui, window_size=(380, 470), with_implot=True)
)code";

        // The C++ app shown, and run beside it by Gui() below: the two must stay the same
        const char* CODE_CPP = R"code(#include "imgui.h"
#include "implot/implot.h"
#include "imgui-knobs/imgui-knobs.h"
#include "immapp/immapp.h"
#include <algorithm>
#include <cmath>

const double LARGEST_SCALE = 0.9 * 1.3;  // of the heart: the pulse scales it up to 0.9, the thickness up to 1.3

std::vector<double> VectorTimesK(const std::vector<double>& values, double k) {
    std::vector<double> r(values.size(), 0.);
    for (size_t i = 0; i < values.size(); ++i)
        r[i] = k * values[i];
    return r;
}

void Gui() {
    // Fill x and y whose plot is a heart
    const double pi = 3.1415926535;
    static std::vector<double> x, y;
    if (x.empty()) {
        for (double t = 0.; t < pi * 2.; t += 0.01) {
            x.push_back(pow(sin(t), 3.) * 16.);
            y.push_back(13. * cos(t) - 5 * cos(2. * t) - 2 * cos(3. * t) - cos(4. * t));
        }
    }
    // Heart pulse rate and time tracking
    static double phase = 0., t0 = ImmApp::ClockSeconds() + 0.2;
    static float heart_pulse_rate = 80., heart_thickness = 0.15;
    double t = ImmApp::ClockSeconds();
    phase += (t - t0) * (double)heart_pulse_rate / (pi * 2.);
    double k = 0.8 + 0.1 * cos(phase);
    t0 = t;

    if (ImPlot::BeginPlot("Heart", ImmApp::EmToVec2(21, 21))) {
        auto [xMin, xMax] = std::minmax_element(x.begin(), x.end());
        auto [yMin, yMax] = std::minmax_element(y.begin(), y.end());
        ImPlot::SetupAxesLimits(*xMin * LARGEST_SCALE, *xMax * LARGEST_SCALE,
                                *yMin * LARGEST_SCALE, *yMax * LARGEST_SCALE);
        for (double k2 = 1 - heart_thickness; k2 <= 1. + heart_thickness; k2 += 0.01) {
            auto xk = VectorTimesK(x, k * k2), yk = VectorTimesK(y, k * k2);
            ImPlot::PlotLine("", xk.data(), yk.data(), (int)xk.size());  // some thickness
        }
        ImPlot::EndPlot();
        HelloImGui::SetItemIsLive();  // the heart beats on its own
    }

    ImGuiKnobs::Knob("Pulse", &heart_pulse_rate, 30., 180.);
    ImGui::SameLine();
    ImGuiKnobs::Knob("Line Thickness", &heart_thickness, 0.01, 0.3);
}

int main() {
    HelloImGui::SimpleRunnerParams runnerParams;
    runnerParams.guiFunction = Gui;
    runnerParams.windowTitle = "Hello!";
    runnerParams.windowSize = {380, 470};
    ImmApp::AddOnsParams addOnsParams;
    addOnsParams.withImplot = true;
    ImmApp::Run(runnerParams, addOnsParams);
}
)code";

        // CODE_CPP's app, compiled here
        const double LARGEST_SCALE = 0.9 * 1.3;
        std::vector<double> VectorTimesK(const std::vector<double>& values, double k)
        {
            std::vector<double> r(values.size(), 0.);
            for (size_t i = 0; i < values.size(); ++i)
                r[i] = k * values[i];
            return r;
        }
        void Gui()
        {
            const double pi = 3.1415926535;
            static std::vector<double> x, y;
            if (x.empty())
                for (double t = 0.; t < pi * 2.; t += 0.01)
                {
                    x.push_back(pow(sin(t), 3.) * 16.);
                    y.push_back(13. * cos(t) - 5 * cos(2. * t) - 2 * cos(3. * t) - cos(4. * t));
                }
            static double phase = 0., t0 = ImmApp::ClockSeconds() + 0.2;
            static float heart_pulse_rate = 80., heart_thickness = 0.15f;
            double t = ImmApp::ClockSeconds();
            phase += (t - t0) * (double)heart_pulse_rate / (pi * 2.);
            double k = 0.8 + 0.1 * cos(phase);
            t0 = t;
            if (ImPlot::BeginPlot("Heart", ImmApp::EmToVec2(21, 21)))
            {
                auto [xMin, xMax] = std::minmax_element(x.begin(), x.end());
                auto [yMin, yMax] = std::minmax_element(y.begin(), y.end());
                ImPlot::SetupAxesLimits(*xMin * LARGEST_SCALE, *xMax * LARGEST_SCALE, *yMin * LARGEST_SCALE,
                                        *yMax * LARGEST_SCALE);
                for (double k2 = 1 - heart_thickness; k2 <= 1. + heart_thickness; k2 += 0.01)
                {
                    auto xk = VectorTimesK(x, k * k2), yk = VectorTimesK(y, k * k2);
                    ImPlot::PlotLine("", xk.data(), yk.data(), (int)xk.size());
                }
                ImPlot::EndPlot();
                HelloImGui::SetItemIsLive();
            }
            ImGuiKnobs::Knob("Pulse", &heart_pulse_rate, 30., 180.);
            ImGui::SameLine();
            ImGuiKnobs::Knob("Line Thickness", &heart_thickness, 0.01f, 0.3f);
        }

        std::vector<std::unique_ptr<TextEditor>> editors;  // the code, read only: Python, C++
        int view = -1;  // 0: Python, 1: C++ (on a phone, 2: the app); -1 until the first frame: the app on a phone
        const ImVec2 APP_SIZE_EM(22.f, 31.5f);  // what the heart app needs: its 21 em plot, its knobs below, a margin

        void Init()
        {
            for (auto [code, language] : {std::pair{CODE_PYTHON, TextEditor::Language::Python()},
                                          std::pair{CODE_CPP, TextEditor::Language::Cpp()}})
            {
                auto editor = MakeCodeEditor(code, language);
                editor->SetReadOnlyEnabled(true);
                editor->SetShowWhitespacesEnabled(false);  // a page of code, to be read
                editors.push_back(std::move(editor));
            }
        }

        void Code(int index, ImVec2 size)
        {
            PanelBg(ImGui::GetCursorScreenPos(), size);
            ImGui::BeginChild("##haiku_code", size, false, ImGuiWindowFlags_NoBackground);
            auto codeFont = RichMd::GetCodeFont();
            ImGui::PushFont(codeFont.font, codeFont.size * 0.85f);
            editors[index]->Render("##haiku_editor", size);
            ImGui::PopFont();
            ImGui::EndChild();
        }

        // The app, in a frame, under a smaller font when the frame is too small for it (its sizes are in em)
        void RunningApp(ImVec2 size)
        {
            float em = HelloImGui::EmSize();
            float scale = std::min({1.f, size.x / (APP_SIZE_EM.x * em), size.y / (APP_SIZE_EM.y * em)});
            PanelBg(ImGui::GetCursorScreenPos(), size, 0.04f, 0.3f);
            ImGui::BeginChild("##haiku_app", size, false, ImGuiWindowFlags_NoBackground | ImGuiWindowFlags_NoScrollbar);
            ImGui::PushFont(nullptr, ImGui::GetStyle().FontSizeBase * scale);
            ImGui::SetCursorPos(ImVec2(HelloImGui::EmSize(0.5f), HelloImGui::EmSize(0.5f)));
            ImGui::BeginGroup();
            Gui();
            ImGui::EndGroup();
            ImGui::PopFont();
            ImGui::EndChild();
        }

        void SlideGui(ImVec2 contentSize)
        {
            if (editors.empty())
                Init();
            float em = HelloImGui::EmSize(), gap = em * 0.5f;
            bool narrow = IsSmallScreen();
            std::vector<const char*> labels = {"Python", "C++"};
            if (narrow)
                labels.push_back("The app");
            if (view < 0)
                view = narrow ? 2 : 1;  // the C++ code first, in the C++ explorer
            for (int i = 0; i < (int)labels.size(); i++)
            {
                if (i > 0)
                    ImGui::SameLine();
                if (ImGui::RadioButton(labels[i], view == i))
                    view = i;
            }
            if (!narrow && view == 2)
                view = 1;
            ImVec2 size(contentSize.x, contentSize.y - ImGui::GetFrameHeightWithSpacing());
            if (narrow)  // one at a time: the code, or the app
            {
                if (view == 2)
                    RunningApp(size);
                else
                    Code(view, size);
                return;
            }
            float appW = std::min(em * 23.f, size.x * 0.45f);  // the heart is 21 em wide
            Code(view, ImVec2(size.x - appW - gap, size.y));
            ImGui::SameLine(0, gap);
            RunningApp(ImVec2(appW, size.y));
        }
    }


    // ============================================================================
    // Slide: "Code that reads like a book": four snippets, each beside the widget it draws
    // ============================================================================
    namespace IntroGallery
    {
        struct Snippet { const char* title; const char* pythonCode; const char* cppCode; };

        // The code shown is the code that draws the widget beside it
        const Snippet SNIPPETS[] = {
            {"Animated Plot",
             R"code(t = imgui.get_time() * 3
x = np.linspace(0, 4 * np.pi, 200)
if implot.begin_plot("##wave", ImVec2(-1, -1)):
    implot.plot_line("sin", x, np.sin(x + t))
    implot.plot_line("cos", x, np.cos(x + t * 0.7))
    implot.end_plot())code",
             R"code(float t = ImGui::GetTime() * 3.f;
std::vector<float> x(200), s(200), c(200);
for (int i = 0; i < 200; i++) {
    x[i] = i * 4.f * IM_PI / 199.f;
    s[i] = sinf(x[i] + t);
    c[i] = cosf(x[i] + t * 0.7f);
}
if (ImPlot::BeginPlot("##wave", ImVec2(-1, -1))) {
    ImPlot::PlotLine("sin", x.data(), s.data(), 200);
    ImPlot::PlotLine("cos", x.data(), c.data(), 200);
    ImPlot::EndPlot();
})code"},
            {"Knob",
             R"code(_, value = imgui_knobs.knob(
    "Volume", value, 0, 100, 1,
    "%.0f%%", imgui_knobs.ImGuiKnobVariant_.wiper_dot)
imgui.same_line()
imgui.v_slider_float("##vslider",
    ImVec2(em * 1.5, em * 5), value, 0, 100, "%.0f"))code",
             R"code(ImGuiKnobs::Knob(
    "Volume", &value, 0, 100, 1,
    "%.0f%%", ImGuiKnobVariant_WiperDot);
ImGui::SameLine();
ImGui::VSliderFloat("##vslider",
    ImVec2(em * 1.5f, em * 5.f), &value, 0, 100, "%.0f");)code"},
            {"Color Picker",
             R"code(# c is an ImVec4
imgui.text(f"({c[0]:.2f}, {c[1]:.2f}, {c[2]:.2f})")
_, c = imgui.color_picker4("##color", c)
)code",
             R"code(// c is an ImVec4
ImGui::Text("(%.2f, %.2f, %.2f)", c.x, c.y, c.z);
ImGui::ColorPicker4("##color", &c.x);
)code"},
            {"Mini Form",
             R"code(_changed, name = imgui.input_text("Name", name)
if imgui.button("Greet") and name:
    greeting = f"Hello, {name}!"
imgui.text_colored(ImVec4(0.4, 1, 0.4, 1), greeting)
_, agreed = imgui.checkbox("I agree", agreed)
_, choice = imgui.combo("Fruit", choice,
                        ["Apple", "Banana", "Cherry"]))code",
             R"code(ImGui::InputText("Name", name, sizeof(name));
if (ImGui::Button("Greet") && name[0])
    snprintf(greeting, sizeof(greeting), "Hello, %s!", name);
ImGui::TextColored(ImVec4(0.4f,1,0.4f,1), "%s", greeting);
ImGui::Checkbox("I agree", &agreed);
ImGui::Combo("Fruit", &choice, "Apple\0Banana\0Cherry\0");)code"},
        };
        const int NB_SNIPPETS = IM_ARRAYSIZE(SNIPPETS);

        std::vector<std::unique_ptr<TextEditor>> editors[2];  // [language][snippet], language 0: Python, 1: C++
        int lang = 1;  // C++ first, in the C++ explorer
        int snippetShown = 0;  // on a phone: the one snippet shown
        double copyTimes[NB_SNIPPETS] = {-1.0, -1.0, -1.0, -1.0};

        // The widgets' state
        float knobValue = 42.f;
        ImVec4 color(0.4f, 0.6f, 1.f, 1.f);
        char name[128] = "World";
        char greeting[256] = "Hello, World!";
        bool agreed = true;
        int choice = 0;

        void GuiPlot()
        {
            float em = HelloImGui::EmSize();
            float t = (float)ImGui::GetTime() * 3.f;
            std::vector<float> x(200), s(200), c(200);
            for (int i = 0; i < 200; i++)
            {
                x[i] = i * 4.f * IM_PI / 199.f;
                s[i] = sinf(x[i] + t);
                c[i] = cosf(x[i] + t * 0.7f);
            }
            ImPlot::PushStyleVar(ImPlotStyleVar_PlotMinSize, ImVec2(em * 8, em * 5));  // (ImPlot's own minimum is taller)
            if (ImPlot::BeginPlot("##wave", ImVec2(-1, -1)))
            {
                ImPlot::PlotLine("sin", x.data(), s.data(), 200);
                ImPlot::PlotLine("cos", x.data(), c.data(), 200);
                ImPlot::EndPlot();
                HelloImGui::SetItemIsLive();  // the waves move on their own
            }
            ImPlot::PopStyleVar();
        }

        void GuiKnob()
        {
            float em = HelloImGui::EmSize();
            ImGuiKnobs::Knob("Volume", &knobValue, 0, 100, 1, "%.0f%%", ImGuiKnobVariant_WiperDot);
            ImGui::SameLine();
            ImGui::VSliderFloat("##vslider", ImVec2(em * 1.5f, em * 5.f), &knobValue, 0, 100, "%.0f");
        }

        void GuiColor()
        {
            ImGui::Text("(%.2f, %.2f, %.2f)", color.x, color.y, color.z);
            ImGui::ColorPicker4("##color", &color.x);
        }

        void GuiForm()
        {
            ImGui::SetNextItemWidth(-1);
            ImGui::InputText("Name", name, sizeof(name));
            if (ImGui::Button("Greet") && name[0])
                snprintf(greeting, sizeof(greeting), "Hello, %s!", name);
            ImGui::TextColored(ImVec4(0.4f, 1.f, 0.4f, 1.f), "%s", greeting);
            ImGui::Checkbox("I agree", &agreed);
            ImGui::SetNextItemWidth(-1);
            ImGui::Combo("Fruit", &choice, "Apple\0Banana\0Cherry\0");
        }

        void (*const GUIS[])() = {GuiPlot, GuiKnob, GuiColor, GuiForm};

        // A snippet's code and its widget, side by side (the code at the left, resizable) or stacked (the code above)
        void RenderCell(int idx, float w, float h, bool stacked)
        {
            float em = HelloImGui::EmSize();
            PanelBg(ImGui::GetCursorScreenPos(), ImVec2(w, h), 0.06f, 0.25f);
            ImGui::BeginChild(("##gallery_" + std::to_string(idx)).c_str(), ImVec2(w, h), false,
                              ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoBackground);
            float pad = em * 0.4f, availH = h - ImGui::GetCursorPosY() - pad;
            auto codeFont = RichMd::GetCodeFont();
            float codeFontSize = codeFont.size * (stacked ? 0.7f : 0.8f);
            const char* code = lang == 0 ? SNIPPETS[idx].pythonCode : SNIPPETS[idx].cppCode;
            ImVec2 codeSize;
            ImGuiChildFlags codeFlags = ImGuiChildFlags_Borders;
            if (stacked)  // the code as tall as its lines (and a horizontal scroll bar), at most 55% of the cell
            {
                int nbLines = 1 + (int)std::count(code, code + strlen(code), '\n');
                float codeH = ImGui::GetFrameHeightWithSpacing() + (nbLines + 1.6f) * codeFontSize * 1.1f + em * 0.6f;
                codeSize = ImVec2(w - pad, std::min(codeH, availH * 0.55f));
            }
            else
            {
                codeSize = ImVec2((w - pad * 2) * 0.5f, availH);
                codeFlags |= ImGuiChildFlags_ResizeX;
            }
            ImGui::BeginChild(("##code_" + std::to_string(idx)).c_str(), codeSize, codeFlags);
            ImGui::TextDisabled("%s", SNIPPETS[idx].title);  // the title and the copy button
            ImGui::SameLine(ImGui::GetContentRegionAvail().x - ImGui::GetFrameHeight());
            if (ImGui::SmallButton((ICON_FA_COPY "##copy_" + std::to_string(idx)).c_str()))
            {
                ImGui::SetClipboardText(code);
                copyTimes[idx] = ImGui::GetTime();
            }
            ImGui::SetItemTooltip(ImGui::GetTime() - copyTimes[idx] < 0.7 ? "Copied!" : "Copy");
            ImGui::PushFont(codeFont.font, codeFontSize);
            editors[lang][idx]->Render(("##ed_gallery_" + std::to_string(idx)).c_str(), ImVec2(-1, -1));
            ImGui::PopFont();
            ImGui::EndChild();
            if (!stacked)
                ImGui::SameLine();
            // The widget, in the remaining space
            ImGui::BeginChild(("##live_" + std::to_string(idx)).c_str(), ImVec2(0, stacked ? 0 : availH), false,
                              ImGuiWindowFlags_NoScrollbar);
            GUIS[idx]();
            ImGui::EndChild();
            ImGui::EndChild();
        }

        void SlideGui(ImVec2 contentSize)
        {
            if (editors[0].empty())
                for (int l = 0; l < 2; l++)
                    for (const auto& snippet : SNIPPETS)
                        editors[l].push_back(MakeCodeEditor(l == 0 ? snippet.pythonCode : snippet.cppCode,
                                                            l == 0 ? TextEditor::Language::Python()
                                                                   : TextEditor::Language::Cpp()));
            float em = HelloImGui::EmSize();
            bool narrow = IsSmallScreen();
            float topY = ImGui::GetCursorPosY();  // contentSize starts here (below the title card)
            ImGui::RadioButton("Python", &lang, 0);  // the language (and on a phone, the snippet shown)
            ImGui::SameLine();
            ImGui::RadioButton("C++", &lang, 1);
            if (narrow)
            {
                ImGui::SameLine(0.f, em);
                ImGui::SetNextItemWidth(-1);
                if (ImGui::BeginCombo("##snippet", SNIPPETS[snippetShown].title))
                {
                    for (int i = 0; i < NB_SNIPPETS; i++)
                        if (ImGui::Selectable(SNIPPETS[i].title, i == snippetShown))
                            snippetShown = i;
                    ImGui::EndCombo();
                }
            }
            float remainingH = contentSize.y - (ImGui::GetCursorPosY() - topY);
            if (narrow)  // one snippet, its code above its widget
            {
                RenderCell(snippetShown, contentSize.x, remainingH, true);
                return;
            }
            const int cols = 2, rows = 2;
            float gap = em * 0.4f;
            float cellW = (contentSize.x - gap * (cols - 1)) / cols, cellH = (remainingH - gap * (rows - 1)) / rows;
            ImVec2 origin = ImGui::GetCursorScreenPos();
            for (int idx = 0; idx < NB_SNIPPETS; idx++)
            {
                int row = idx / cols, col = idx % cols;
                ImGui::SetCursorScreenPos(ImVec2(origin.x + col * (cellW + gap), origin.y + row * (cellH + gap)));
                RenderCell(idx, cellW, cellH, false);
            }
        }
    }


    // ============================================================================
    // The head: the tagline and the subtitle, and the prose of welcome.md in a window
    // ============================================================================
    const char* ABOUT_TITLE = "About Dear ImGui Bundle";  // the window of the prose
    const float ABOUT_ANIMATION = 0.3f;  // s: the window of the prose slides up and fades in
    const float HEAD_SCALE_SMALL_SCREEN = 0.75f;  // the tagline's size on a phone, where it would take a third of it
    const float HEAD_EXPANDED_DURATION = 8.f;  // s: on a phone, a tap on the short tagline shows all of it for that long

    std::vector<std::string> gWelcomeHead;  // the tagline and the subtitle: welcome.md's paragraphs before its sections
    std::string gWelcomeRest;  // its sections, in the window of the prose
    bool gWelcomeLoaded = false;
    std::optional<double> gAboutOpenedAt;  // when the window of the prose opened (none: closed)
    bool gAboutPressOutside = false;  // the last press, while the window of the prose is open, was outside it
    float gCtaHeight = 0.f;  // the height of the button and the manuals' line, measured at the last frame
    double gHeadExpandedUntil = 0.0;  // the time until which the whole head shows, on a phone

    std::string Trim(const std::string& s)
    {
        size_t first = s.find_first_not_of(" \n\r\t"), last = s.find_last_not_of(" \n\r\t");
        return first == std::string::npos ? "" : s.substr(first, last - first + 1);
    }

    // welcome.md, an asset (demos_assets): its paragraphs before the first "## " heading are the head (one line of
    // text each, *italic* for the whole paragraph), the rest is the prose
    void LoadWelcomeText()
    {
        gWelcomeLoaded = true;
        if (!HelloImGui::AssetExists("welcome.md"))
        {
            gWelcomeHead = {"*Interactive Python & C++ apps for desktop, mobile, and the web.*"};
            return;
        }
        HelloImGui::AssetFileData data = HelloImGui::LoadAssetFileData("welcome.md");
        std::string text((const char*)data.data, data.dataSize);
        HelloImGui::FreeAssetFileData(&data);
        size_t cut = text.find("\n## ");
        std::string head = cut == std::string::npos ? text : text.substr(0, cut);
        gWelcomeRest = cut == std::string::npos ? "" : text.substr(cut + 1);
        size_t start = 0;
        while (start < head.size())
        {
            size_t end = head.find("\n\n", start);
            std::string paragraph = Trim(head.substr(start, end == std::string::npos ? std::string::npos : end - start));
            if (!paragraph.empty())
                gWelcomeHead.push_back(paragraph);
            if (end == std::string::npos)
                break;
            start = end + 2;
        }
    }

    bool IsItalic(const std::string& p) { return p.size() > 2 && p.front() == '*' && p.back() == '*'; }

    // On a phone: the tagline's first sentence only (it ends at its first ". ")
    std::vector<std::string> ShortHead()
    {
        if (gWelcomeHead.empty())
            return {};
        const std::string& first = gWelcomeHead[0];
        bool italic = IsItalic(first);
        std::string text = italic ? first.substr(1, first.size() - 2) : first;
        size_t cut = text.find(". ");
        if (cut == std::string::npos)
            return {first};
        std::string sentence = text.substr(0, cut + 1);
        return {italic ? "*" + sentence + "*" : sentence};
    }

    // The tagline and the subtitle, and at the right of their last line the button that opens the prose. Drawn with
    // the markdown fonts, not rendered as markdown: a phone shows them smaller, and only the tagline's first sentence,
    // until a tap shows the rest for a while
    void RenderHead()
    {
        if (!gWelcomeLoaded)
            LoadWelcomeText();
        float em = HelloImGui::EmSize();
        bool small = IsSmallScreen();
        bool expanded = !small || ImGui::GetTime() < gHeadExpandedUntil;
        std::vector<std::string> paragraphs = expanded ? gWelcomeHead : ShortHead();
        if (small && expanded)
            HelloImGui::RequestRefresh();  // the head folds back on its own
        std::string label = small ? ICON_FA_INFO_CIRCLE : "More info & links " ICON_FA_EXPAND;
        float buttonW = ImGui::CalcTextSize(label.c_str()).x + ImGui::GetStyle().FramePadding.x * 2.f;
        ImVec2 topLeft = ImGui::GetCursorScreenPos();
        float availX = ImGui::GetContentRegionAvail().x;
        ImGui::PushTextWrapPos(ImGui::GetCursorPosX() + availX - (gWelcomeRest.empty() ? 0.f : buttonW + em));
        float lastLineEnd = 0.f;  // where the last paragraph ends, when it takes one line (else the button goes right)
        for (size_t i = 0; i < paragraphs.size(); i++)
        {
            bool italic = IsItalic(paragraphs[i]);
            std::string text = italic ? paragraphs[i].substr(1, paragraphs[i].size() - 2) : paragraphs[i];
            RichMd::SizedFont font = RichMd::GetFont(RichMd::MarkdownFontSpec(italic));
            ImGui::PushFont(font.font, font.size * (small ? HEAD_SCALE_SMALL_SCREEN : 1.f));
            if (i > 0)
                ImGui::Dummy(ImVec2(0, em * 0.2f));
            float width = ImGui::CalcTextSize(text.c_str()).x;
            lastLineEnd = width + buttonW + em <= availX ? width : 0.f;
            ImGui::TextWrapped("%s", text.c_str());
            ImGui::PopFont();
        }
        ImGui::PopTextWrapPos();
        if (small)  // a tap on the text shows all of it, or folds it back
        {
            float headBottom = ImGui::GetCursorScreenPos().y;
            if (ImGui::IsMouseHoveringRect(topLeft, ImVec2(topLeft.x + availX - buttonW - em, headBottom))
                && ImGui::IsWindowHovered() && ImGui::IsMouseReleased(ImGuiMouseButton_Left)
                && ImGui::GetMouseDragDelta(0).y == 0.f)
                gHeadExpandedUntil = expanded ? 0.0 : ImGui::GetTime() + HEAD_EXPANDED_DURATION;
        }
        if (gWelcomeRest.empty())
            return;
        ImVec2 below = ImGui::GetCursorScreenPos();
        float buttonX = topLeft.x + (lastLineEnd > 0.f ? lastLineEnd + em : availX - buttonW);
        ImGui::SetCursorScreenPos(ImVec2(buttonX, below.y - ImGui::GetTextLineHeightWithSpacing()));
        if (ImGui::SmallButton(label.c_str()))
            gAboutOpenedAt = ImGui::GetTime();
        ImGui::SetCursorScreenPos(below);
    }

    // The prose of welcome.md, in a modal window that slides up as it fades in; a tap outside, Escape or its close
    // button closes it
    void AboutWindow()
    {
        if (!gAboutOpenedAt.has_value())
            return;
        if (!ImGui::IsPopupOpen(ABOUT_TITLE))
            ImGui::OpenPopup(ABOUT_TITLE);
        float em = HelloImGui::EmSize();
        float t = std::min((float)(ImGui::GetTime() - *gAboutOpenedAt) / ABOUT_ANIMATION, 1.f);
        float eased = 1.f - (1.f - t) * (1.f - t) * (1.f - t);
        if (t < 1.f)
            HelloImGui::RequestRefresh();  // the window arrives on its own
        ImGuiViewport* viewport = ImGui::GetMainViewport();
        ImVec2 center = viewport->GetCenter();
        ImGui::SetNextWindowPos(ImVec2(center.x, center.y + em * 3.f * (1.f - eased)), ImGuiCond_Always,
                                ImVec2(0.5f, 0.5f));
        ImGui::SetNextWindowSize(ImVec2(std::min(em * 56.f, viewport->Size.x * 0.94f), viewport->Size.y * 0.82f),
                                 ImGuiCond_Always);
        ImGui::PushStyleVar(ImGuiStyleVar_Alpha, std::max(eased, 0.01f));
        ImGui::PushStyleVar(ImGuiStyleVar_WindowRounding, em * 0.6f);
        ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(em * 1.2f, em * 0.8f));
        ImGui::PushStyleColor(ImGuiCol_PopupBg, WithAlpha(ImGui::GetStyleColorVec4(ImGuiCol_WindowBg), 1.f));  // opaque
        bool keepOpen = true;
        if (!ImGui::BeginPopupModal(ABOUT_TITLE, &keepOpen, ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoSavedSettings))
            gAboutOpenedAt.reset();  // its close button
        else
        {
            RichMd::Render(gWelcomeRest);
            // A tap outside its rectangle closes it: the press and the release both outside, the press after it opened
            // (the release of the click that opened it must not close it). By the position, not the hover: on a touch
            // screen, a press that swipes the window's text to scroll it is not hovering.
            ImVec2 windowMin = ImGui::GetWindowPos(), windowSize = ImGui::GetWindowSize();
            ImVec2 mouse = ImGui::GetIO().MousePos;
            bool inside = mouse.x >= windowMin.x && mouse.x <= windowMin.x + windowSize.x && mouse.y >= windowMin.y
                          && mouse.y <= windowMin.y + windowSize.y;
            if (ImGui::IsMouseClicked(ImGuiMouseButton_Left))
                gAboutPressOutside = !inside;
            bool clickedOutside = ImGui::IsMouseReleased(ImGuiMouseButton_Left) && gAboutPressOutside && !inside;
            if (!keepOpen || clickedOutside || ImGui::IsKeyPressed(ImGuiKey_Escape))
            {
                ImGui::CloseCurrentPopup();
                gAboutOpenedAt.reset();
                gAboutPressOutside = false;
            }
            ImGui::EndPopup();
        }
        ImGui::PopStyleColor();
        ImGui::PopStyleVar(3);
    }


    // ============================================================================
    // The carousel
    // ============================================================================
    int gCurrentSlide = 0;
    float gAnimatedOffset = 0.f, gAutoTimer = 0.f;
    bool gAutoStopped = false;
    std::optional<float> gDragOffset;  // while a swipe drags the slides: where they are (in slides)

    std::vector<CarouselSlide>& Slides();

    // A drag on a slide's title card (a swipe, on a touch screen) moves the carousel with it; released past 3 em, the
    // next or the previous slide comes
    void CardSwipe(ImVec2 topLeft, ImVec2 size, float slideWidth)
    {
        ImGui::SetCursorScreenPos(topLeft);
        ImGui::InvisibleButton("##swipe", size);
        HelloImGui::SetItemTakesTouchDrags(false);  // on a touch screen, the finger's drag is this button's at once
        if (!(ImGui::IsItemActive() || ImGui::IsItemDeactivated()))
            return;
        float dx = ImGui::GetMouseDragDelta(ImGuiMouseButton_Left).x;
        if (ImGui::IsItemActive())
        {
            gDragOffset = gCurrentSlide - dx / slideWidth;
            gAutoStopped = true;
            return;
        }
        gDragOffset.reset();
        int count = (int)Slides().size();
        float em = HelloImGui::EmSize();
        if (dx < -em * 3)
            gCurrentSlide = (gCurrentSlide + 1) % count;
        else if (dx > em * 3)
            gCurrentSlide = (gCurrentSlide - 1 + count) % count;
    }

    // The title card of a slide: its title, its description and, when the host can open it, a link to its full demo.
    // Returns the height taken.
    float DrawSlideTitleCard(const CarouselSlide& slide, float slideWidth)
    {
        float em = HelloImGui::EmSize();
        ImDrawList* dl = ImGui::GetWindowDrawList();
        float fontSize = ImGui::GetFontSize();
        bool narrow = IsSmallScreen();  // a phone: the title and the link, smaller, no description
        float titleFontSize = fontSize * (narrow ? 1.f : 1.2f);
        ImFont* font = ImGui::GetFont();

        // The link to the full demo: on a phone, a small "Full demo" badge on the title's line
        std::string link = (!slide.demo.empty() && gHost.openDemo)
            ? std::string(narrow ? "Full demo " : "Open the full demo ") + ICON_FA_CHEVRON_RIGHT : "";
        float linkFontSize = fontSize * (narrow ? 0.85f : 1.f);
        ImVec2 badgePad = narrow ? ImVec2(em * 0.45f, em * 0.15f) : ImVec2(0, 0);
        ImVec2 linkSize(0, 0);
        if (!link.empty())
        {
            ImVec2 s = ImGui::CalcTextSize(link.c_str());
            linkSize = ImVec2(s.x * linkFontSize / fontSize + badgePad.x * 2, s.y * linkFontSize / fontSize + badgePad.y * 2);
        }
        ImVec2 titleSize = ImGui::CalcTextSize(slide.title.c_str());
        float titleH = titleSize.y * titleFontSize / fontSize;
        ImVec2 descSize = narrow ? ImVec2(0, 0)
                                 : ImGui::CalcTextSize(slide.description.c_str(), nullptr, false, slideWidth - em * 2.f);

        float cardPadX = em * (narrow ? 0.6f : 1.f), cardPadY = em * (narrow ? 0.25f : 0.4f);
        float cardW = slideWidth - em;
        // The link at the right of the title when both fit on the line, else on a line of its own under the text
        bool linkOnTitle = narrow || linkSize.x + titleSize.x * titleFontSize / fontSize + em <= cardW - 2 * cardPadX;
        float innerH = titleH + descSize.y + (narrow ? 0.f : em * 0.3f);
        if (!link.empty() && !linkOnTitle)
            innerH += linkSize.y + em * 0.3f;
        float cardH = innerH + cardPadY * 2.f;
        float cardX = ImGui::GetCursorScreenPos().x + (slideWidth - cardW) * 0.5f, cardY = ImGui::GetCursorScreenPos().y;

        ImVec4 accent = ImGui::GetStyleColorVec4(ImGuiCol_ButtonHovered);
        ImU32 titleCol = ImGui::GetColorU32(ImGuiCol_Text);
        dl->AddRectFilled(ImVec2(cardX, cardY), ImVec2(cardX + cardW, cardY + cardH),
                          ImGui::ColorConvertFloat4ToU32(WithAlpha(accent, 0.12f)), em * 0.4f);
        dl->AddRect(ImVec2(cardX, cardY), ImVec2(cardX + cardW, cardY + cardH),
                    ImGui::ColorConvertFloat4ToU32(WithAlpha(accent, 0.4f)), em * 0.4f, 1.5f);
        dl->AddText(font, titleFontSize, ImVec2(cardX + cardPadX, cardY + cardPadY), titleCol, slide.title.c_str());
        if (!narrow)
            dl->AddText(font, fontSize, ImVec2(cardX + cardPadX, cardY + cardPadY + titleH + em * 0.3f),
                        ImGui::GetColorU32(ImGuiCol_TextDisabled), slide.description.c_str(), nullptr,
                        slideWidth - em * 2.f);

        float totalH = cardH + em * 0.4f;
        ImVec2 cursor = ImGui::GetCursorScreenPos();
        if (!link.empty())  // at the right of the card: on the title's line, or on its own line under the text
        {
            float linkY = linkOnTitle ? cardY + cardPadY + (titleH - linkSize.y) / 2 : cardY + cardH - cardPadY - linkSize.y;
            ImVec2 linkPos(cardX + cardW - cardPadX - linkSize.x, linkY);
            ImGui::SetCursorScreenPos(linkPos);
            if (ImGui::InvisibleButton(("##open_" + slide.demo).c_str(), linkSize))
                gHost.openDemo(slide.demo);
            bool hovered = ImGui::IsItemHovered();
            if (hovered)
                ImGui::SetMouseCursor(ImGuiMouseCursor_Hand);
            ImU32 color = ImGui::ColorConvertFloat4ToU32(RichMd::LinkColor());
            if (narrow)  // a pill in the accent color
            {
                dl->AddRectFilled(linkPos, ImVec2(linkPos.x + linkSize.x, linkPos.y + linkSize.y),
                                  ImGui::ColorConvertFloat4ToU32(WithAlpha(accent, hovered ? 0.55f : 0.35f)),
                                  linkSize.y * 0.5f);
                dl->AddText(font, linkFontSize, ImVec2(linkPos.x + badgePad.x, linkPos.y + badgePad.y), titleCol,
                            link.c_str());
            }
            else
            {
                dl->AddText(linkPos, color, link.c_str());
                if (hovered)
                    dl->AddLine(ImVec2(linkPos.x, linkPos.y + linkSize.y),
                                ImVec2(linkPos.x + linkSize.x, linkPos.y + linkSize.y), color);
            }
        }
        // After the link: ImGui gives the hover to the first item submitted, so the link keeps its click
        CardSwipe(ImVec2(cardX, cardY), ImVec2(cardW, cardH), slideWidth);
        ImGui::SetCursorScreenPos(cursor);
        ImGui::Dummy(ImVec2(slideWidth, totalH));
        return totalH;
    }

    // The slides, in their order; the ones whose library is missing are left out
    std::vector<CarouselSlide>& Slides()
    {
        static std::vector<CarouselSlide> slides;
        if (!slides.empty())
            return slides;
        slides.push_back({"Rich Interactive Plots",
                          "ImPlot delivers animated, interactive 2D charts with minimal code. It is extremely fast, and "
                          "ideal for real-time data monitoring, diagnostics, and dashboards.",
                          IntroImPlot::SlideGui, "manual_implot.py"});
#ifdef HELLOIMGUI_HAS_OPENGL
        slides.push_back({"GPU-Accelerated Rendering",
                          "Dear ImGui renders directly on the GPU, fast enough to blend custom shaders and 3D content "
                          "into your UI.",
                          IntroShader::SlideGui, "demo_custom_background.py"});
#endif
        slides.push_back({"3D Data Exploration",
                          "ImPlot3D adds rotatable, zoomable 3D plots. Navigate complex datasets with intuitive controls.",
                          IntroLorenz::SlideGui, "manual_implot3d.py"});
        slides.push_back({"Real-Time Data Streams",
                          "Thousands of samples per second, plotted at your screen's refresh rate. In Python, the same "
                          "GUI runs beside a Jupyter notebook, live while your cells compute.",
                          IntroStream::SlideGui, "notebooks.md"});
        slides.push_back({"Interactive Science",
                          "A tiny neural network learns two spirals, live: a model with its knobs, in a few lines. The "
                          "explorable tells how it works, formula by formula.",
                          IntroSpiral::SlideGui, "explorables/neural_spiral/neural_spiral.py"});
#ifdef IMGUI_BUNDLE_WITH_IMMVISION
        slides.push_back({"Image Analysis",
                          "ImmVision lets you zoom, pan, and inspect pixel values in real time, with linked views and "
                          "colormaps.",
                          IntroImmVision::SlideGui, "demo_immvision_inspector.py"});
        slides.push_back({"Visual Node Editors",  // its nodes show their images with ImmVision
                          "Explore ideas in graph form with imgui-node-editor: an image flows through filters, and each "
                          "node shows its result.",
                          IntroPipeline::SlideGui, "demo_node_editor_image_pipeline.py"});
#endif
        slides.push_back({"Feature-Rich Widgets",
                          "Dear ImGui ships with advanced tables featuring angled headers, column reordering, sorting, "
                          "and much more.",
                          IntroTable::SlideGui, "demo_widgets.py"});
        slides.push_back({"Rich Documentation, Built In",
                          "Render markdown directly in your UI - headers, code blocks, tables, links, math and images, "
                          "all from a simple string.",
                          IntroMarkdown::SlideGui, "demo_imgui_md.py"});
        slides.push_back({"A Whole App in a Few Lines",
                          "The complete program of a beating heart, includes and window included, and beside it the "
                          "app it runs. No boilerplate: the GUI is a function that draws each frame.",
                          IntroHaiku::SlideGui, "haiku_implot_heart.py"});
        slides.push_back({"Code That Reads Like a Book",
                          "No widget trees, no callbacks, no state sync. Each snippet below is the complete code for "
                          "the live demo beside it. The interactive manuals read the same way: every section with its "
                          "code.",
                          IntroGallery::SlideGui, "manual_imgui.py"});
        return slides;
    }

    // The slides' background: the page's, a little darker (more so in a dark theme), so that they stand out
    ImU32 SlidesBgColor()
    {
        ImVec4 bg = ImGui::GetStyleColorVec4(ImGuiCol_WindowBg);
        float k = 0.299f * bg.x + 0.587f * bg.y + 0.114f * bg.z < 0.5f ? 0.75f : 0.93f;
        return ImGui::ColorConvertFloat4ToU32(ImVec4(bg.x * k, bg.y * k, bg.z * k, 1.f));
    }

    // The carousel, 4:3 and centered, as tall as the space left above bottomMargin
    void IntroMiniDemos(float bottomMargin)
    {
        std::vector<CarouselSlide>& slides = Slides();
        int slideCount = (int)slides.size();
        float dt = std::clamp(ImGui::GetIO().DeltaTime, 0.f, 0.1f);
        if (dt <= 0.f)
            dt = 1.f / 60.f;
        float em = HelloImGui::EmSize();
        ImDrawList* dl = ImGui::GetWindowDrawList();

        // The carousel's zone: the height left, 4:3. On a phone the welcome fits the screen, even with a large text
        // setting: the arrows, the dots and the button stay in view, and nothing needs a vertical swipe (most of the
        // page takes the finger: plots, editors, the cards)
        float minHeight = em * (IsSmallScreen() ? 12.f : 15.f);
        float carouselHeight = std::max(ImGui::GetContentRegionAvail().y - bottomMargin, minHeight);
        float availWidth = ImGui::GetContentRegionAvail().x;
        float carouselWidth = std::min(carouselHeight * 4.f / 3.f, availWidth);
        float carouselOffsetX = std::max((availWidth - carouselWidth) * 0.5f, 0.f);
        if (carouselOffsetX > 0.f)  // Indent(0) indents by the style's default: the carousel would overflow
            ImGui::Indent(carouselOffsetX);

        // Auto-advance, until the user touches something (a slide's widget, an arrow): then the slide stays
        if (ImGui::IsAnyItemActive())
            gAutoStopped = true;
        if (!gAutoStopped)
        {
            gAutoTimer += dt;
            if (gAutoTimer > SLIDE_DURATION)
            {
                gCurrentSlide = (gCurrentSlide + 1) % slideCount;
                gAutoTimer = 0.f;
            }
        }

        // The slides' animation (none while a swipe holds them: they follow the finger)
        float target = (float)gCurrentSlide;
        gAnimatedOffset = gDragOffset.has_value() ? *gDragOffset : SmoothDamp(gAnimatedOffset, target, 8.f, dt);
        if (std::fabs(gAnimatedOffset - target) < 0.001f)
            gAnimatedOffset = target;
        if (gAnimatedOffset != target)
            HelloImGui::RequestRefresh();  // the slides slide on their own

        // The slides' area: a child that clips the slides (each one is a child of its own, which the draw list's clip
        // rect would not clip)
        float navBarHeight = em * 2.f;
        float slideHeight = std::max(carouselHeight - navBarHeight, em * 10.f), slideWidth = carouselWidth;
        ImVec2 slideAreaPos = ImGui::GetCursorScreenPos();
        dl->AddRectFilled(slideAreaPos, ImVec2(slideAreaPos.x + carouselWidth, slideAreaPos.y + slideHeight),
                          SlidesBgColor(), em * 0.5f);  // behind the slides, which have no background of their own
        ImGui::BeginChild("##carousel_zone", ImVec2(carouselWidth, slideHeight), false,
                          ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoScrollWithMouse | ImGuiWindowFlags_NoBackground);
        for (int i = 0; i < slideCount; i++)
        {
            float slideX = slideAreaPos.x + ((float)i - gAnimatedOffset) * slideWidth;
            if (slideX >= slideAreaPos.x + carouselWidth || slideX + slideWidth <= slideAreaPos.x)
                continue;
            ImGui::SetCursorScreenPos(ImVec2(slideX, slideAreaPos.y));
            ImGui::BeginChild(("##slide_" + std::to_string(i)).c_str(), ImVec2(slideWidth, slideHeight), false,
                              ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoBackground);
            float titleH = DrawSlideTitleCard(slides[i], slideWidth);
            ImGui::SetCursorPosX(ImGui::GetCursorPosX() + em * 0.5f);
            slides[i].guiFunc(ImVec2(slideWidth - em, slideHeight - titleH - em * 0.5f));
            ImGui::EndChild();
        }
        ImGui::EndChild();

        // The navigation: arrows and dots
        float dotRadius = em * 0.3f, dotSpacing = em * 1.5f, dotsWidth = slideCount * dotSpacing, arrowW = em * 2.f;
        float navStartX = slideAreaPos.x + (carouselWidth - (arrowW * 2.f + dotsWidth + em)) * 0.5f;
        float navY = slideAreaPos.y + slideHeight + em * 0.3f;
        ImGui::SetCursorScreenPos(ImVec2(navStartX, navY + em * 0.15f));
        if (ImGui::Button(ICON_FA_CHEVRON_LEFT "##carousel_prev", ImVec2(arrowW, em * 1.2f)))
        {
            gCurrentSlide = (gCurrentSlide - 1 + slideCount) % slideCount;
            gAutoStopped = true;
        }
        float dotsStartX = navStartX + arrowW + em * 0.5f, dotsCenterY = navY + em * 0.75f;
        ImVec4 accent = ImGui::GetStyleColorVec4(ImGuiCol_ButtonHovered);
        for (int i = 0; i < slideCount; i++)
        {
            ImVec2 center(dotsStartX + i * dotSpacing + dotSpacing * 0.5f, dotsCenterY);
            ImGui::SetCursorScreenPos(ImVec2(center.x - dotRadius * 2.f, center.y - dotRadius * 2.f));
            if (ImGui::InvisibleButton(("##dot" + std::to_string(i)).c_str(), ImVec2(dotRadius * 4.f, dotRadius * 4.f)))
            {
                gCurrentSlide = i;
                gAutoStopped = true;
            }
            bool hovered = ImGui::IsItemHovered();
            ImU32 color = i == gCurrentSlide ? ImGui::ColorConvertFloat4ToU32(accent)
                        : hovered            ? ImGui::ColorConvertFloat4ToU32(WithAlpha(accent, 0.6f))
                                             : ImGui::GetColorU32(ImGuiCol_TextDisabled);
            dl->AddCircleFilled(center, i == gCurrentSlide ? dotRadius * 1.3f : dotRadius, color);
        }
        ImGui::SetCursorScreenPos(ImVec2(dotsStartX + dotsWidth + em * 0.5f, navY + em * 0.15f));
        if (ImGui::Button(ICON_FA_CHEVRON_RIGHT "##carousel_next", ImVec2(arrowW, em * 1.2f)))
        {
            gCurrentSlide = (gCurrentSlide + 1) % slideCount;
            gAutoStopped = true;
        }
        // The cursor at the end of the navigation bar: exactly the height claimed above, so that no scrollbar appears
        ImGui::SetCursorScreenPos(ImVec2(slideAreaPos.x, navY + em * 1.7f));
        ImGui::Dummy(ImVec2(1, 0));

        // Shift and the horizontal wheel (a trackpad's swipe) change the slide, once a second at most
        if (ImGui::Shortcut(ImGuiMod_Shift | ImGuiKey_MouseWheelX, ImGuiInputFlags_RouteGlobal))
        {
            static double lastTrigger = -1.0;
            double now = ImGui::GetTime();
            if (now - lastTrigger > 1.0)
            {
                gAutoStopped = true;
                if (ImGui::GetIO().MouseWheelH > 0)
                    gCurrentSlide = std::max(gCurrentSlide - 1, 0);
                else
                    gCurrentSlide = (gCurrentSlide + 1) % slideCount;
                lastTrigger = now;
            }
        }
        if (carouselOffsetX > 0.f)
            ImGui::Unindent(carouselOffsetX);
    }


    // ============================================================================
    // The page
    // ============================================================================

    // The manuals: "or open an interactive manual: Dear ImGui | ImPlot | ImPlot3D" (shorter on a phone; centered when
    // it fits on one line, else wrapped as the links row)
    void ManualsLine(float availX, bool small)
    {
        float em = HelloImGui::EmSize();
        const char* intro = small ? "Interactive docs: " : "or open an interactive manual: ";
        float partsW = ImGui::CalcTextSize(intro).x + ImGui::CalcTextSize(" | ").x * (MANUALS.size() - 1);
        for (auto& [name, filename] : MANUALS)
            partsW += ImGui::CalcTextSize(name).x;
        // On a phone, one line: a smaller font when needed (down to 75%)
        float scale = small ? std::clamp(availX / partsW, 0.75f, 1.f) : 1.f;
        ImGui::PushFont(nullptr, ImGui::GetStyle().FontSizeBase * scale);
        partsW *= scale;
        if (partsW <= availX)
            ImGui::SetCursorPosX(ImGui::GetCursorPosX() + (availX - partsW) / 2);
        ImGui::TextDisabled("%s", intro);
        for (size_t i = 0; i < MANUALS.size(); i++)
        {
            ImGui::SameLine(0, 0);
            if (i > 0)
            {
                if (ImGui::CalcTextSize((std::string(" | ") + MANUALS[i].first).c_str()).x > ImGui::GetContentRegionAvail().x)
                    ImGui::NewLine();
                else
                {
                    ImGui::TextDisabled(" | ");
                    ImGui::SameLine(0, 0);
                }
            }
            ImGui::PushStyleColor(ImGuiCol_Text, RichMd::LinkColor());
            ImGui::TextUnformatted(MANUALS[i].first);
            ImGui::PopStyleColor();
            if (ImGui::IsItemHovered())
            {
                ImGui::SetMouseCursor(ImGuiMouseCursor_Hand);
                if (ImGui::IsMouseClicked(ImGuiMouseButton_Left))
                    gHost.openDemo(MANUALS[i].second);
            }
        }
        ImGui::PopFont();
#ifdef HELLOIMGUI_WITH_TEST_ENGINE
        IntroAutomations::Init();
        if (IntroAutomations::showImmediateApps != nullptr)  // the explorer with the test engine: a guided tour
        {
            ImGui::SameLine(0, em);
            if (ImGui::SmallButton("Show me " ICON_FA_EYE))
                ImGuiTestEngine_QueueTest(HelloImGui::GetImGuiTestEngine(), IntroAutomations::showImmediateApps);
        }
#endif
    }

    // Centered: the big "Browse the N demos" button, then the line of the interactive manuals
    void CallToAction()
    {
        if (!gHost.browse)
            return;
        float em = HelloImGui::EmSize();
        bool small = IsSmallScreen();
        float top = ImGui::GetCursorScreenPos().y, availX = ImGui::GetContentRegionAvail().x;
        std::string label = ICON_FA_TH_LARGE "  Browse the " + std::to_string(gHost.nbDemos) + " demos";
        ImGui::PushFont(nullptr, ImGui::GetStyle().FontSizeBase * (small ? 1.15f : 1.3f));
        ImGui::PushStyleVar(ImGuiStyleVar_FramePadding, ImVec2(em * 1.2f, em * (small ? 0.3f : 0.4f)));
        float width = ImGui::CalcTextSize(label.c_str()).x + em * 2.4f;
        ImGui::SetCursorPosX(ImGui::GetCursorPosX() + (availX - width) / 2);
        if (ImGui::Button(label.c_str()))
            gHost.browse();
        ImGui::PopStyleVar();
        ImGui::PopFont();
        if (gHost.openDemo)
            ManualsLine(availX, small);
        gCtaHeight = ImGui::GetCursorScreenPos().y - top;
    }
}  // namespace


void RenderLinksRow()
{
    if (IsSmallScreen())  // three lines there, and the prose has them all (the "Start here" of resources.md)
        return;
    struct LinkInfo { const char* label; const char* url; const char* tooltip; };
    const LinkInfo links[] = {
        {"imgui-bundle.pages.dev", "https://imgui-bundle.pages.dev", "Main project site"},
        {"Repository", "https://github.com/pthom/imgui_bundle", "Source code, issues, discussions"},
        {"Documentation", "https://imgui-bundle.pages.dev/doc/", "Full documentation for Dear ImGui Bundle"},
        {"Python Playground", "https://imgui-bundle.pages.dev/playground/", "Live Python sandbox with demos - edit and run in your browser"},
        {"Discord", "https://discord.gg/xkzpKMeYN3", "Join the community for questions, showcase, and discussion (new!)"},
        {"All the resources", "https://imgui-bundle.pages.dev/doc/intro/resources/", "Every documentation, manual, video and community link, in one page"},
    };
    for (int i = 0; i < IM_ARRAYSIZE(links); i++)
    {
        if (i > 0)
        {
            ImGui::SameLine();
            float needed = ImGui::CalcTextSize((std::string("| ") + links[i].label).c_str()).x + 2 * ImGui::GetStyle().ItemSpacing.x;
            if (needed > ImGui::GetContentRegionAvail().x)  // the row wraps on a narrow screen
                ImGui::NewLine();
            else
            {
                ImGui::TextDisabled("|");
                ImGui::SameLine();
            }
        }
        RichMd::RenderTextAsLink(links[i].label, links[i].url);
        if (ImGui::IsItemHovered())
            ImGui::SetTooltip("%s", links[i].tooltip);
    }
}


void WelcomeGui(const WelcomeHost& host)
{
    gHost = host;
    RenderHead();
    ImGui::Separator();
    float em = HelloImGui::EmSize();
    // The button and the manuals' line: their height at the last frame (an estimate at the first)
    float bottom = !host.browse ? 0.f : (gCtaHeight > 0.f ? gCtaHeight + em * 0.3f : em * 4.6f);
    IntroMiniDemos(bottom);
    CallToAction();
    AboutWindow();
}


void gui_demo_imgui_bundle_intro()
{
    if (IsSmallScreen())  // the title smaller, in the font of a markdown title
    {
        RichMd::SizedFont font = RichMd::GetFont(RichMd::MarkdownFontSpec(false, false, 1));
        ImGui::PushFont(font.font, font.size * 0.7f);
        ImGui::TextUnformatted("Dear ImGui Bundle");
        ImGui::PopFont();
        ImGui::Separator();
    }
    else
        RichMd::Render("# Dear ImGui Bundle");
    RenderLinksRow();
    WelcomeGui(WelcomeHost());
}


#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char**)
{
    ChdirBesideAssetsFolder();
    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.ShowGui = gui_demo_imgui_bundle_intro;
    runnerParams.appWindowParams.windowGeometry.size = {1200, 900};
    runnerParams.appWindowParams.windowTitle = "Dear ImGui Bundle - Welcome";
    ImmApp::AddOnsParams addOns;
    addOns.withMarkdown = true;
    addOns.withLatex = true;
    addOns.withNodeEditor = true;
    addOns.withImplot = true;
    addOns.withImplot3d = true;
    addOns.withImAnim = true;
    ImmApp::Run(runnerParams, addOns);
    return 0;
}
#endif
