// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// Dear ImGui Bundle Explorer: one page with a header, and three states below it (the twin of demo_imgui_bundle.py).
//
// Welcome: the intro (the carousel of live mini demos) and a button to the demos. Demos: the launcher (the catalog of
// demos, with their pictures, descriptions and code). A demo in place: a demo whose function is linked here, shown
// full size under a slim bar. Escape goes back one state (the code view, the demo, then Welcome).
#include "demo_imgui_bundle.h"
#include "demo_immapp_launcher.h"

#include "immapp/immapp.h"
#include "hello_imgui/hello_imgui.h"
#include "hello_imgui/icons_font_awesome_4.h"
#include "imgui_rich_md/rich_md.h"
#include "demo_utils/api_demos.h"
#ifdef IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB
#include "imgui_explorer.h"
#endif

#include <cmath>
#include <optional>
#include <string>
#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#include <cstdlib>
#endif

// The intro
void IntroWelcomeGui();  // its content without the title and the links
void RenderLinksRow();
// The demos whose function can be linked in the explorer (the catalog says which ones may run in place)
void gui_demo_widgets();
void gui_demo_imgui_md();
void gui_demo_text_edit();
void gui_demo_logger();
void gui_demo_node_editor_color_mixer();
void gui_demo_node_editor_image_pipeline();
void gui_demo_imgui_show_demo_window();
void gui_demo_im_anim();
#ifdef IMGUI_BUNDLE_WITH_IMMVISION
void gui_demo_immvision_display();
void gui_demo_immvision_inspector();
void gui_demo_immvision_link();
void gui_demo_immvision_process();
#endif


namespace
{
    // The ImPlot manual and the ImPlot3D manual, each alone (as in Python)
    void manual_implot()
    {
#ifdef IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB
        ShowImGuiExplorerGui_Cpp(ImGuiExplorerLibrary::ImPlot, false);
#else
        ImGui::Text("Demo unavailable, because Dear ImGui Manual library is not included in this build.");
#endif
    }

    void manual_implot3d()
    {
#ifdef IMGUI_BUNDLE_WITH_IMGUI_EXPLORER_LIB
        ShowImGuiExplorerGui_Cpp(ImGuiExplorerLibrary::ImPlot3D, false);
#else
        ImGui::Text("Demo unavailable, because Dear ImGui Manual library is not included in this build.");
#endif
    }

#ifdef __EMSCRIPTEN__
    // The route in the browser's address: its hash, without the '#'
    std::string BrowserRoute()
    {
        char* route = (char*)EM_ASM_PTR({
            var hash = window.location.hash.slice(1);
            var len = lengthBytesUTF8(hash) + 1;
            var buf = _malloc(len);
            stringToUTF8(hash, buf, len);
            return buf;
        });
        std::string r = route;
        free(route);
        return r;
    }

    // A new history entry with this route (or the current entry replaced); the Welcome's route is the bare address
    void SetBrowserRoute(const std::string& route, bool replace)
    {
        EM_ASM({
            var route = UTF8ToString($0);
            var url = route === "" ? window.location.pathname + window.location.search : "#" + route;
            if ($1)
                window.history.replaceState(null, "", url);
            else
                window.history.pushState(null, "", url);
        }, route.c_str(), replace);
    }
#endif

    const float CHANGE_DURATION = 0.4f;  // s: a change of state, through the background
    const float DRIFT = 3.f;  // em: the page leaving slides that much (up when going forward), the one arriving as far

    enum class State { Welcome, Demos, Demo };  // Demo: a demo in place

    struct Explorer
    {
        State state = State::Welcome;  // the one wanted
        State shown = State::Welcome;  // the one drawn: the previous state, during the first half of a change
        std::optional<double> changeStart;  // when the state last changed, while the change animates
        bool forward = true;  // the change goes deeper (Welcome, Demos, a demo: the pages slide up), or back
        DemoLauncher launcher;
        std::string demoInPlace;  // the stem of the demo shown by the Demo state
        // What a demo in place may change, saved when it is first drawn and restored when the page shows something
        // else, so that no demo has to clean up
        struct AppState { std::string stem; ImGuiStyle style; bool idling; };
        std::optional<AppState> savedAppState;
#ifdef __EMSCRIPTEN__
        std::string browserRoute;  // the route of the browser's current history entry
#endif
        float rightWidth = 0.f;  // of the header's switch, measured on the previous frame

        Explorer()
        {
            launcher.inPlaceFunctions = {
                {"demo_widgets", gui_demo_widgets}, {"demo_imgui_md", gui_demo_imgui_md},
                {"demo_text_edit", gui_demo_text_edit}, {"demo_logger", gui_demo_logger},
                {"demo_node_editor_color_mixer", gui_demo_node_editor_color_mixer},
                {"demo_node_editor_image_pipeline", gui_demo_node_editor_image_pipeline},
                {"manual_imgui", gui_demo_imgui_show_demo_window},
                {"manual_implot", manual_implot}, {"manual_implot3d", manual_implot3d},
                {"manual_im_anim", gui_demo_im_anim},
#ifdef IMGUI_BUNDLE_WITH_IMMVISION
                {"demo_immvision_display", gui_demo_immvision_display},
                {"demo_immvision_inspector", gui_demo_immvision_inspector},
                {"demo_immvision_link", gui_demo_immvision_link}, {"demo_immvision_process", gui_demo_immvision_process},
#endif
            };
        }

        void Go(State newState)
        {
            if (newState == state)
                return;
            forward = (int)newState > (int)state;
            state = newState;
            changeStart = ImGui::GetTime();
        }

        void Gui()
        {
            if (ImGui::GetFrameCount() < 2)  // cf https://github.com/pthom/imgui_bundle/issues/293
                return;
            if (launcher.demoToShowInPlace.has_value())  // "Run" on a demo whose function is linked here
            {
                demoInPlace = *launcher.demoToShowInPlace;
                launcher.demoToShowInPlace.reset();
                Go(State::Demo);
            }
            if (ImGui::IsKeyPressed(ImGuiKey_Escape) && !ImGui::IsAnyItemActive())
            {
                if (state == State::Demo)
                    Go(State::Demos);
                else if (state == State::Demos && launcher.Depth() == 0)  // else the launcher goes back one level
                    Go(State::Welcome);
            }
            Header();
            Page();
#ifdef __EMSCRIPTEN__
            FollowBrowserHistory();
#endif
        }

        void SaveAppState(const std::string& stem)
        {
            savedAppState = AppState{stem, ImGui::GetStyle(), HelloImGui::GetRunnerParams()->fpsIdling.enableIdling};
        }

        // The font sizes stay as they are: the reader may have changed them meanwhile (the status bar's font scale)
        void RestoreAppState()
        {
            ImGuiStyle& style = ImGui::GetStyle();
            float fontSizeBase = style.FontSizeBase, fontScaleMain = style.FontScaleMain;
            float fontScaleDpi = style.FontScaleDpi;
            style = savedAppState->style;
            style.FontSizeBase = fontSizeBase;
            style.FontScaleMain = fontScaleMain;
            style.FontScaleDpi = fontScaleDpi;
            HelloImGui::GetRunnerParams()->fpsIdling.enableIdling = savedAppState->idling;
            savedAppState.reset();
        }

        // The place shown, as a route: "" (Welcome), "demos" (and the launcher's level: "demos/code/<stem>"), or
        // "demo/<stem>" (a demo in place)
        std::string Route() const
        {
            if (state == State::Welcome)
                return "";
            if (state == State::Demo)
                return "demo/" + demoInPlace;
            std::string level = launcher.Route();
            return level.empty() ? "demos" : "demos/" + level;
        }

        // The place of a route; a route that leads nowhere leads to the Welcome
        void GoTo(const std::string& route)
        {
            if (route.rfind("demo/", 0) == 0 && launcher.inPlaceFunctions.count(route.substr(5)))
            {
                demoInPlace = route.substr(5);
                launcher.GoTo("");
                Go(State::Demo);
            }
            else if (route == "demos" || route.rfind("demos/", 0) == 0)
            {
                launcher.GoTo(route == "demos" ? "" : route.substr(6));
                Go(State::Demos);
            }
            else
            {
                launcher.GoTo("");
                Go(State::Welcome);
            }
        }

#ifdef __EMSCRIPTEN__
        // The browser's history follows the explorer: each move in the explorer adds a history entry (as a link would),
        // and the browser's back and forward, or an address with a route, move the explorer
        void FollowBrowserHistory()
        {
            std::string route = BrowserRoute();
            if (route != browserRoute)  // the browser moved
            {
                GoTo(route);
                browserRoute = Route();
                if (browserRoute != route)  // a route that leads nowhere: the address shows where the explorer went
                    SetBrowserRoute(browserRoute, true);
            }
            else if (Route() != browserRoute)  // the explorer moved
            {
                browserRoute = Route();
                SetBrowserRoute(browserRoute, false);
            }
        }
#endif

        // The state's content, in a child; during a change, it fades through the background with a drift: the page
        // leaving slides away under a veil, then the new one slides into place as the veil lifts
        void Page()
        {
            float drift = 0.f, veil = 0.f;
            if (changeStart.has_value())
            {
                float t = (float)(ImGui::GetTime() - *changeStart) / CHANGE_DURATION;
                if (t >= 1.f)
                {
                    changeStart.reset();
                    shown = state;
                }
                else if (t < 0.5f)
                {
                    float u = t / 0.5f;
                    u = u * u;  // eased in
                    drift = -DRIFT * u;
                    veil = u;
                }
                else
                {
                    if (shown != state)
                    {
                        shown = state;
                        if (shown == State::Demos)
                            launcher.Deal();
                    }
                    float u = (t - 0.5f) / 0.5f;
                    u = 1.f - (1.f - u) * (1.f - u);  // eased out
                    drift = DRIFT * (1.f - u);
                    veil = 1.f - u;
                }
                if (!forward)
                    drift = -drift;
            }
            drift = HelloImGui::EmSize(drift);
            ImVec2 topLeft = ImGui::GetCursorScreenPos();
            ImVec2 avail = ImGui::GetContentRegionAvail();
            ImVec2 bottomRight(topLeft.x + avail.x, topLeft.y + avail.y);
            // The page keeps its size while it drifts: a demo shown in place would otherwise see its size change during
            // the transition (a node editor adapts its view to its size, and would lose its fit). A frame without
            // scrollbar holds the page, and clips it.
            ImGui::BeginChild("page frame", avail, ImGuiChildFlags_None,
                              ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoScrollWithMouse);
            ImGui::SetCursorPos(ImVec2(0.f, drift));
            ImGui::BeginChild("page", avail);
            // Before the next page draws: the launcher saves the idling to restore it after its animation
            if (shown != State::Demo && savedAppState.has_value())
                RestoreAppState();
            if (shown == State::Welcome)
                Welcome();
            else if (shown == State::Demos)
                launcher.Gui(false);
            else
                DemoInPlace();
            ImGui::EndChild();
            ImGui::EndChild();
            if (veil > 0.f)  // over the child's own draw list, which comes after this window's
                ImGui::GetForegroundDrawList()->AddRectFilled(topLeft, bottomRight, Curtain(veil));
        }

        // The title, the sentence of the state, and at the right the switch between the states (on its own row when
        // the title leaves it no room: a phone)
        void Header()
        {
            float em = HelloImGui::EmSize();
            float top = ImGui::GetCursorPosY();
            BigText("Dear ImGui Bundle", 2.f);
            float titleWidth = ImGui::GetItemRectSize().x;
            float belowTitle = ImGui::GetCursorPosY();
            float width = ImGui::GetContentRegionAvail().x;
            float right = ImGui::GetCursorPosX() + width - em * 0.5f;
            bool oneRow = titleWidth + rightWidth + em * 1.5f <= width;
            if (oneRow)
            {
                const char* sentence = state == State::Welcome
                    ? "   Interactive apps in Python and C++, for desktop, web and mobile."
                    : "   Pick a demo: see it, run it, and read its code: each demo is a documented quickstart.";
                ImVec4 color = ImGui::GetStyleColorVec4(state == State::Welcome ? ImGuiCol_TextDisabled : ImGuiCol_Text);
                // Only when it does not reach the switch; SameLine only then: pending, it would make the title's row
                // the chips' line
                if (titleWidth + ImGui::CalcTextSize(sentence).x + rightWidth + em * 3.f <= width)
                {
                    ImGui::SameLine();
                    ImGui::SetCursorPosY(top + em * 0.75f);  // the sentence sits on the title's baseline
                    ImGui::TextColored(color, "%s", sentence);
                }
            }
            // The cursor is set, not put on the same line (see above)
            ImGui::SetCursorPos(ImVec2(right - rightWidth, oneRow ? top + em * 0.5f : belowTitle));
            ImGui::BeginGroup();
            // The switch: two chips as the launcher's category chips (wider, and never wrapped: the group's width
            // comes from the previous frame, and a wrapped group would measure too narrow forever), the state's in
            // the accent
            ImGui::PushStyleVar(ImGuiStyleVar_FramePadding, ImVec2(em * 0.8f, 0));
            const std::pair<State, const char*> switches[] = {{State::Welcome, BundleExplorer::WELCOME_LABEL},
                                                              {State::Demos, BundleExplorer::DEMOS_LABEL}};
            for (const auto& [target, label] : switches)
            {
                bool current = state == target || (state == State::Demo && target == State::Demos);
                float highlight = Tween((std::string("switch ") + label).c_str(), current ? 1.f : 0.f, 0.25f);
                ImVec4 button = ImGui::GetStyleColorVec4(ImGuiCol_Button);
                ImVec4 accent(LAUNCHER_ACCENT.x, LAUNCHER_ACCENT.y, LAUNCHER_ACCENT.z, 0.55f);
                ImGui::PushStyleColor(ImGuiCol_Button, Lerp(button, accent, highlight));
                if (ImGui::SmallButton(label))
                    Go(target);
                ImGui::PopStyleColor();
                ImGui::SameLine();
            }
            ImGui::PopStyleVar();
            ImGui::EndGroup();
            rightWidth = ImGui::GetItemRectSize().x;
            ImGui::SetCursorPosY(std::max(ImGui::GetCursorPosY(), belowTitle));  // the chips are shorter than the title
        }

        void Welcome()
        {
            float em = HelloImGui::EmSize();
            RenderLinksRow();
            ImVec2 avail = ImGui::GetContentRegionAvail();
            ImGui::BeginChild("welcome", ImVec2(0, avail.y - em * 3.5f));
            IntroWelcomeGui();
            ImGui::EndChild();
            // The call to action, centered
            std::string label = std::string(ICON_FA_TH_LARGE "  Browse the ") + std::to_string(launcher.NbDemos()) + " demos";
            ImGui::PushFont(nullptr, ImGui::GetStyle().FontSizeBase * 1.3f);
            ImGui::PushStyleVar(ImGuiStyleVar_FramePadding, ImVec2(em * 1.2f, em * 0.4f));
            float width = ImGui::CalcTextSize(label.c_str()).x + em * 2.4f;
            ImGui::SetCursorPosX(ImGui::GetCursorPosX() + (avail.x - width) / 2);
            if (ImGui::Button(label.c_str()))
                Go(State::Demos);
            ImGui::PopStyleVar();
            ImGui::PopFont();
            if (ImGui::IsItemHovered(ImGuiHoveredFlags_DelayNormal))
            {
                std::string categories;
                for (const auto& category : launcher.Categories())
                    categories += (categories.empty() ? "" : ", ") + category.name;
                ImGui::BeginTooltip();
                ImGui::BeginChild("tip", ImVec2(em * 30.f, 0), ImGuiChildFlags_AutoResizeY);  // wraps the text
                RichMd::Render("**" + std::to_string(launcher.NbDemos()) + " demos, in "
                               + std::to_string(launcher.Categories().size()) + " categories:** " + categories + ".\n\n"
                               "Each one is a documented quickstart: see it, run it, and read its code. Together they "
                               "are the tutorials and the interactive manuals of the bundle.");
                ImGui::EndChild();
                ImGui::EndTooltip();
            }
        }

        // A demo whose function is linked here, full size under a slim bar: the way back, its name, its code
        void DemoInPlace()
        {
            const DemoEntry* demo = launcher.Find(demoInPlace);
            if (demo == nullptr || !launcher.inPlaceFunctions.count(demo->stem))
            {
                Go(State::Demos);
                return;
            }
            if (ImGui::Button(ICON_FA_ARROW_LEFT "  All the demos"))
            {
                Go(State::Demos);
                return;
            }
            ImGui::SameLine();
            BigText(demo->label.c_str(), 1.3f);
            ImGui::SameLine(0, HelloImGui::EmSize(2.f));
            if (ImGui::SmallButton(ICON_FA_CODE "  Code"))
            {
                launcher.ShowCodeOf(*demo);
                Go(State::Demos);
            }
            ImGui::SetItemTooltip("Its code: Python, and C++ side by side");
#ifdef __EMSCRIPTEN__
            bool ownWindow = ExplorerPage(*demo);
#else
            bool ownWindow = HasDemoExeFile(demo->stem);
#endif
            if (ownWindow)
            {
                ImGui::SameLine();
                if (ImGui::SmallButton(ICON_FA_EXTERNAL_LINK_ALT "  New window"))
                    SpawnDemo(demo->stem);
                ImGui::SetItemTooltip("Runs it in a window of its own");
            }
            ImGui::Separator();
            if (savedAppState.has_value() && savedAppState->stem != demo->stem)  // another demo, without a frame between
                RestoreAppState();
            if (!savedAppState.has_value())
                SaveAppState(demo->stem);
            ImGui::BeginChild("demo in place");
            launcher.inPlaceFunctions.at(demo->stem)();
            ImGui::EndChild();
        }
    };

    Explorer* gExplorer = nullptr;
}


namespace BundleExplorer
{
    const char* WELCOME_LABEL = ICON_FA_HOME "  Welcome";
    const char* DEMOS_LABEL = ICON_FA_TH_LARGE "  Demos";
    bool OnDemos() { return gExplorer != nullptr && gExplorer->state != State::Welcome; }
    DemoLauncher* Launcher() { return gExplorer ? &gExplorer->launcher : nullptr; }
}


// The explorer's parameters, apart from its run: a test can drive the page (see the intro's automations)
std::pair<HelloImGui::RunnerParams, ImmApp::AddOnsParams> ExplorerParams()
{
    //###############################################################################################
    // Part 1: Define the runner params
    //###############################################################################################

    // Hello ImGui params (they hold the settings as well as the Gui callbacks)
    HelloImGui::RunnerParams runnerParams;
    // Window size and title
    runnerParams.appWindowParams.windowTitle = "Dear ImGui Bundle Explorer";
    runnerParams.appWindowParams.windowGeometry.size = {1400, 950};

    runnerParams.imGuiWindowParams.showStatusBar = true;

    //###############################################################################################
    // Part 2: The explorer's page, in a full screen window
    //###############################################################################################
    runnerParams.imGuiWindowParams.defaultImGuiWindowType = HelloImGui::DefaultImGuiWindowType::ProvideFullScreenWindow;
    static Explorer explorer;
    gExplorer = &explorer;
    runnerParams.callbacks.ShowGui = [] { explorer.Gui(); };

    auto showStatusBar = []()
    {
        ImGui::SetNextItemWidth(ImGui::GetContentRegionAvail().x / 10.f);
        ImGui::SliderFloat("Font scale", & ImGui::GetStyle().FontScaleMain, 0.5f, 5.f);
        ImGui::SameLine(0.f, HelloImGui::EmSize(4.f));
        if (SmallScreen())  // the bar's right part (idling, FPS) leaves no room for more
            ImGui::TextDisabled("v" IMGUI_BUNDLE_VERSION);
        else
            ImGui::TextDisabled("Dear ImGui Bundle Explorer - v" IMGUI_BUNDLE_VERSION " build " IMGUI_BUNDLE_BUILD_NUMBER);
    };
    runnerParams.callbacks.ShowStatus = showStatusBar;

    runnerParams.useImGuiTestEngine = true;

    runnerParams.callbacks.SetupImGuiConfig = [] {
        ImGui::GetIO().ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
    };

    // ################################################################################################
    // Part 3: The add-ons
    // ################################################################################################
    auto addons = ImmApp::AddOnsParams();
    addons.withMarkdown = true;
    addons.withLatex = true;
    addons.withImplot = true;
    addons.withImplot3d = true;
    addons.withTexInspect = true;
    addons.withImAnim = true;

    runnerParams.iniClearPreviousSettings = true;
    return {runnerParams, addons};
}


#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char **)
{
    ChdirBesideAssetsFolder();
    auto [runnerParams, addons] = ExplorerParams();
    ImmApp::Run(runnerParams, addons);
    return 0;
}
#endif
