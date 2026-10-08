#include "imgui_explorer.h"
#include "hello_imgui/hello_imgui.h"
#include "immapp/runner.h"
#include "immapp/browse_to_url.h"
#ifdef IMGUI_BUNDLE_WITH_IMANIM
#include "im_anim.h"
#endif
#include "imgui_rich_md/rich_md.h"
#include "demo_code_viewer.h"
#include "imgui_internal.h"
#include "library_config.h"
#include "hello_imgui/icons_font_awesome_4.h"

// Forward declarations for ImAnim demo windows
void ImAnimDemoBasicsWindow(bool create_window);
void ImAnimDemoWindow(bool create_window);
void ImAnimDocWindow(bool create_window);
void ImAnimUsecaseWindow(bool create_window);

namespace
{

    void RenderLink(const char* text, const char* url) {
        ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.5f, 0.6f, 1.0f, 1.0f));
        ImGui::TextUnformatted(text);
        ImGui::PopStyleColor();
        ImGui::SetItemTooltip("%s", url);
        // In the browser, on a touch screen, the page opens the url from the touch itself (a tap seen by ImGui comes
        // too late for the browser): the click then does nothing more. A mouse click on such a device still opens it.
        bool tapOpensUrl = (ImGui::GetIO().ConfigFlags & ImGuiConfigFlags_IsTouchScreen) != 0;
        if (tapOpensUrl)
            HelloImGui::SetTapOpensUrl(ImGui::GetItemRectMin(), ImGui::GetItemRectMax(), url);
        bool isTap = tapOpensUrl && ImGui::GetIO().MouseSource == ImGuiMouseSource_TouchScreen;
        if (ImGui::IsItemClicked() && !isTap)
            ImmApp::BrowseToUrl(url);
        if (ImGui::IsItemHovered())
            ImGui::SetMouseCursor(ImGuiMouseCursor_Hand);
    };

    // Below this width (in em), the explorer shows one pane at a time, the demo or the code (an upright phone)
    constexpr float kNarrowWidthEm = 50.f;
    // Below this height (in em), the status bar goes to the "..." menu (a sideways phone)
    constexpr float kShortHeightEm = 36.f;

    // How the explorer fits the space it has
    struct LayoutMode
    {
        bool narrow = false;        // one pane at a time, a "Demo | Code" switch, the library in a combo
        bool statusInMenu = false;  // the status bar's content is in the "..." menu
        bool CompactToolbar() const { return narrow || statusInMenu; }  // the intro and the links in the "..." menu
    };

    bool GNarrowLayout_ShowsCode = false;  // one pane at a time: the code is shown, otherwise the demo
    bool GNarrowLayout_CodeSeen = false;   // the code was shown once: the tip above the demo goes away
    bool GNarrowLayout_Active = false;     // the explorer shows one pane at a time (set at each frame)

    int GDemo_LastShownFrame = -1;         // the last frame when the demo was shown
    bool GDemo_ShownAtLastFrame = false;   // the demo was shown at the frame before (all its open sections were seen)

    bool                                GDemoMarker_FlagFollowSource = true;
    char                                GDemoMarker_CodeLookupInfo[1024] = {0};
    int                                 GDemoMarker_PrevLibIndex = -1;   // the lookup info is reset when they change
    int                                 GDemoMarker_PrevFileIndex = -1;

    // Follow source only makes sense when the active code-viewer tab is the demo
    // file (imgui_demo.cpp, implot_demo.cpp, ...). On API reference tabs the user
    // is reading docs and should not be yanked back by hover-driven navigation.
    // One pane at a time: the code is hidden while the demo is shown, and a tap there selects the demo's tab.
    bool IsFollowSourceApplicable()
    {
        if (GNarrowLayout_Active)
            return true;
        const auto& files = GetCurrentLibraryFiles();
        int idx = DemoCodeViewer_GetCurrentFileIndex();
        if (idx < 0 || idx >= (int)files.size())
            return false;
        return !files[idx].isApiReference;
    }


    // [sub section] ImGuiDemoMarker_GuiToggle()
    // Display a "Code Lookup" checkbox that toggles interactive code browsing
    void DemoMarker_ShowShortInfo()
    {
        // Reset lookup info when library or file tab changes
        {
            int libIndex = GetCurrentLibraryIndex();
            int fileIndex = DemoCodeViewer_GetCurrentFileIndex();
            if (libIndex != GDemoMarker_PrevLibIndex || fileIndex != GDemoMarker_PrevFileIndex)
            {
                GDemoMarker_CodeLookupInfo[0] = '\0';
                GDemoMarker_PrevLibIndex = libIndex;
                GDemoMarker_PrevFileIndex = fileIndex;
            }
        }

        bool applicable = IsFollowSourceApplicable();
        ImGui::BeginDisabled(!applicable);
        ImGui::SetNextItemShortcut(ImGuiKey_F1, ImGuiInputFlags_RouteGlobal);
        ImGui::Checkbox("Follow source    ", &GDemoMarker_FlagFollowSource);
        ImGui::EndDisabled();
        ImGui::SetItemTooltip(applicable
            ? "Press F1 to toggle this mode"
            : "Follow source only acts on the demo source tab");

        ImGui::SameLine();

        ImGui::PushFont(RichMd::GetCodeFont().font, 0.f);
        ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.7f, 0.7f, 0.3f, 1.0f));
        ImGui::Text("%s", GDemoMarker_CodeLookupInfo);
        ImGui::PopStyleColor();
        ImGui::PopFont();
    }

    // -------------------------------------------------------------------
    // DemoMarkersRegistry: tracks zone boundings for IMGUI_DEMO_MARKER
    // (moved from the former imgui_demo_marker_hooks.cpp)
    // -------------------------------------------------------------------
    class DemoMarkersRegistry
    {
    private:
        struct ZoneBoundings
        {
            ZoneBoundings() : SourceLineNumber(-1), MinY(-1.0f), MaxY(-1.0f), Window(NULL), LastFrame(-1) {}
            int SourceLineNumber;
            float MinY, MaxY;
            ImGuiWindow* Window;
            int LastFrame;  // the last frame when its marker was called
        };

    public:
        DemoMarkersRegistry() : AllZonesBoundings(), PreviousZoneSourceLine(-1) {}

        // Call before IsMouveHoveringDemoMarker: true when the marker was not called at the last frame, while the demo
        // was shown (a tree node or a tab that just opened). At most one per frame: the first, the outermost.
        bool IsJustShown(int line_number)
        {
            int frame = ImGui::GetFrameCount();
            if (CurrentFrame != frame)
            {
                CurrentFrame = frame;
                JustShownReported = false;
            }
            int lastFrame = HasZoneBoundingsForLine(line_number) ? GetZoneBoundingsForLine(line_number).LastFrame : -1;
            bool justShown = GDemo_ShownAtLastFrame && lastFrame != frame - 1 && !JustShownReported;
            if (justShown)
                JustShownReported = true;
            return justShown;
        }

        bool IsMouveHoveringDemoMarker(int line_number)
        {
            StoreZoneBoundings(line_number);
            ZoneBoundings& zone_boundings = GetZoneBoundingsForLine(line_number);
            return IsMouseHoveringZoneBoundings(zone_boundings);
        }

    private:
        void StoreZoneBoundings(int line_number)
        {
            ZoneBoundings current_zone_boundings;
            if (HasZoneBoundingsForLine(line_number))
                current_zone_boundings = GetZoneBoundingsForLine(line_number);
            else
                current_zone_boundings.SourceLineNumber = line_number;

            current_zone_boundings.Window = ImGui::GetCurrentWindow();
            current_zone_boundings.LastFrame = ImGui::GetFrameCount();
            current_zone_boundings.MinY = ImGui::GetCursorScreenPos().y;
            current_zone_boundings.MaxY = -1.0f; // Reset: will be set by next marker, or stay -1 (= extends to bottom)
            SetZoneBoundingsForLine(line_number, current_zone_boundings);

            if (PreviousZoneSourceLine != line_number && HasZoneBoundingsForLine(PreviousZoneSourceLine))
            {
                ZoneBoundings& previous = GetZoneBoundingsForLine(PreviousZoneSourceLine);
                if (previous.Window == ImGui::GetCurrentWindow())
                    previous.MaxY = ImGui::GetCursorScreenPos().y;
            }
            PreviousZoneSourceLine = line_number;
        }

        bool IsMouseHoveringZoneBoundings(const ZoneBoundings& zb)
        {
            if (!ImGui::IsWindowHovered(ImGuiHoveredFlags_AllowWhenBlockedByActiveItem | ImGuiHoveredFlags_RootAndChildWindows | ImGuiHoveredFlags_NoPopupHierarchy))
                return false;
            float y = ImGui::GetMousePos().y;
            float x = ImGui::GetMousePos().x;
            return (y >= zb.MinY)
                && ((y < zb.MaxY) || (zb.MaxY < 0.f))
                && (x >= ImGui::GetWindowPos().x)
                && (x < ImGui::GetWindowPos().x + ImGui::GetWindowSize().x);
        }

        bool HasZoneBoundingsForLine(int line_number)
        {
            for (int i = 0; i < AllZonesBoundings.size(); ++i)
                if (AllZonesBoundings[i].SourceLineNumber == line_number)
                    return true;
            return false;
        }

        ZoneBoundings& GetZoneBoundingsForLine(int line_number)
        {
            for (int i = 0; i < AllZonesBoundings.size(); ++i)
                if (AllZonesBoundings[i].SourceLineNumber == line_number)
                    return AllZonesBoundings[i];
            IM_ASSERT(false);
            static ZoneBoundings dummy; return dummy;
        }

        void SetZoneBoundingsForLine(int line_number, const ZoneBoundings& zb)
        {
            if (HasZoneBoundingsForLine(line_number))
                GetZoneBoundingsForLine(line_number) = zb;
            else
                AllZonesBoundings.push_back(zb);
        }

        ImVector<ZoneBoundings> AllZonesBoundings;
        int PreviousZoneSourceLine;
        int CurrentFrame = -1;           // the frame of the last call to IsJustShown
        bool JustShownReported = false;  // IsJustShown returned true during CurrentFrame
    };


    static DemoMarkersRegistry GDemoMarkersRegistry;

    bool DemoMarker_IsMouveHovering(int line_number)
    {
        return GDemoMarkersRegistry.IsMouveHoveringDemoMarker(line_number);
    }

    // Callback invoked by IMGUI_DEMO_MARKER when a demo section is hovered
    void OnDemoMarkerCallback(const char* file_ext_cpp, int line, const char* section)
    {
        // On a touch screen, nothing is hovered between two touches, and a section's zone starts below its title:
        // a section that a tap just opened becomes the current one. (Not with a mouse: its hover, on the title of the
        // section, would bring the code back to the zone above at the next frame.)
        bool justOpened = GDemoMarkersRegistry.IsJustShown(line)
                       && ImGui::GetIO().MouseSource == ImGuiMouseSource_TouchScreen;
        if (!DemoMarker_IsMouveHovering(line) && !justOpened)
            return;
        // Compute file name without extension
        char file_no_ext[256];
        {
            const char* dot = strrchr(file_ext_cpp, '.');
            if (dot != NULL)
            {
                size_t len = dot - file_ext_cpp;
                if (len >= sizeof(file_no_ext))
                    len = sizeof(file_no_ext) - 1;
                strncpy(file_no_ext, file_ext_cpp, len);
                file_no_ext[len] = '\0';
            }
            else
            {
                strncpy(file_no_ext, file_ext_cpp, sizeof(file_no_ext) - 1);
                file_no_ext[sizeof(file_no_ext) - 1] = '\0';
            }
        }

        if (DemoCodeViewer_GetShowPython() && section)
        {
            int pyLine = DemoCodeViewer_GetPythonLineForSection(file_ext_cpp, section);
            if (pyLine > 0)
                snprintf(GDemoMarker_CodeLookupInfo, sizeof(GDemoMarker_CodeLookupInfo),
                    "%s.py:%d - \"%s\"", file_no_ext, pyLine, section);
            else
                snprintf(GDemoMarker_CodeLookupInfo, sizeof(GDemoMarker_CodeLookupInfo),
                    "%s.cpp:%d (no python demo) - \"%s\"", file_no_ext, line + 1, section);
        }
        else
        {
            snprintf(GDemoMarker_CodeLookupInfo, sizeof(GDemoMarker_CodeLookupInfo),
                "%s.cpp:%d - \"%s\"", file_no_ext, line + 1, section);
        }

        // Suppress the navigation jump while any widget is being manipulated
        // (e.g. drag-selecting text in the code editor, dragging a slider in
        // the demo). The info text above still updates so the user keeps
        // feedback about what zone they are crossing.
        // (The tap that opened a section may still hold the active id)
        bool idle = ImGui::GetActiveID() == 0 || justOpened;
        if (GDemoMarker_FlagFollowSource && IsFollowSourceApplicable() && idle)
        {
            DemoCodeViewer_ShowCodeAt(file_ext_cpp, line, section);
            // A tab changed by the jump keeps the lookup info
            GDemoMarker_PrevFileIndex = DemoCodeViewer_GetCurrentFileIndex();
        }
    }

    // The library: buttons, or a combo where they do not fit (nothing in single-library mode)
    void GuiSelectLibrary(bool asCombo)
    {
        if (IsSingleLibraryMode())
            return;

        const auto& libs = GetAllLibraryConfigs();
        int currentIdx = GetCurrentLibraryIndex();

        if (asCombo)
        {
            ImGui::SetNextItemWidth(HelloImGui::EmSize(7.f));
            if (ImGui::BeginCombo("##library", libs[currentIdx].name.c_str()))
            {
                for (size_t i = 0; i < libs.size(); ++i)
                    if (ImGui::Selectable(libs[i].name.c_str(), (int)i == currentIdx))
                        SetCurrentLibraryIndex((int)i);
                ImGui::EndCombo();
            }
            return;
        }

        for (size_t i = 0; i < libs.size(); ++i)
        {
            ImGui::PushStyleVar(ImGuiStyleVar_FrameRounding, 10.f);
            bool isSelected = ((int)i == currentIdx);
            if (isSelected)
                ImGui::PushStyleColor(ImGuiCol_Button, ImGui::GetStyleColorVec4(ImGuiCol_ButtonActive));
            if (ImGui::Button(libs[i].name.c_str(), HelloImGui::EmToVec2(5.2f, 1.4f)))
                SetCurrentLibraryIndex((int)i);

            if (isSelected)
                ImGui::PopStyleColor();
            ImGui::PopStyleVar();
        }
    }

    // C++/Python toggle (to be called inside a horizontal layout)
    void GuiPythonCppToggle()
    {
        if (DemoCodeViewer_IsPythonOnlyMode())
        {
            ImGui::Text("C++ & Python code: ");
            ImGui::SetCursorPosX(ImGui::GetCursorPosX() - ImGui::GetStyle().ItemSpacing.x);
            RenderLink("Online Explorer", "https://imgui-bundle.pages.dev/explorer/");
        }
        else
        {
            bool showPython = DemoCodeViewer_GetShowPython();
            if (ImGui::RadioButton("C++", !showPython))
                DemoCodeViewer_SetShowPython(false);
            if (ImGui::RadioButton("Python", showPython))
                DemoCodeViewer_SetShowPython(true);
        }
    }

    // One pane at a time: a segmented control "Demo | Code", whose selected half is filled
    void GuiDemoCodeSwitch()
    {
        ImVec2 size = HelloImGui::EmToVec2(8.f, 1.5f);
        ImVec2 p0 = ImGui::GetCursorScreenPos();
        ImVec2 p1(p0.x + size.x, p0.y + size.y);
        float xMid = p0.x + size.x * 0.5f;
        // The position of the press, rather than of the release: a touch screen may not report the latter
        if (ImGui::InvisibleButton("##demo_code_switch", size))
            GNarrowLayout_ShowsCode = ImGui::GetIO().MouseClickedPos[0].x >= xMid;
        if (GNarrowLayout_ShowsCode)
            GNarrowLayout_CodeSeen = true;

        ImDrawList* drawList = ImGui::GetWindowDrawList();
        float rounding = size.y * 0.5f;
        auto fillHalf = [&](bool codeHalf, ImGuiCol col)
        {
            if (codeHalf)
                drawList->AddRectFilled(ImVec2(xMid, p0.y), p1, ImGui::GetColorU32(col), rounding,
                                        ImDrawFlags_RoundCornersRight);
            else
                drawList->AddRectFilled(p0, ImVec2(xMid, p1.y), ImGui::GetColorU32(col), rounding,
                                        ImDrawFlags_RoundCornersLeft);
        };
        drawList->AddRectFilled(p0, p1, ImGui::GetColorU32(ImGuiCol_FrameBg), rounding);
        if (ImGui::IsItemHovered())
        {
            bool overCode = ImGui::GetIO().MousePos.x >= xMid;
            if (overCode != GNarrowLayout_ShowsCode)
                fillHalf(overCode, ImGuiCol_FrameBgHovered);
        }
        fillHalf(GNarrowLayout_ShowsCode, ImGuiCol_ButtonActive);
        drawList->AddRect(p0, p1, ImGui::GetColorU32(ImGuiCol_Border), rounding);

        const char* labels[2] = {"Demo", "Code"};
        for (int i = 0; i < 2; ++i)
        {
            ImVec2 textSize = ImGui::CalcTextSize(labels[i]);
            ImVec2 textPos(p0.x + size.x * 0.5f * (float)i + (size.x * 0.5f - textSize.x) * 0.5f,
                           p0.y + (size.y - textSize.y) * 0.5f);
            drawList->AddText(textPos, ImGui::GetColorU32(ImGuiCol_Text), labels[i]);
        }
    }

    // The "..." button of a small screen, and its menu: the library's intro and links, then the status bar's content
    void GuiExplorerMenu(bool withStatus)
    {
        if (ImGui::Button(ICON_FA_ELLIPSIS_H "##explorer_menu", HelloImGui::EmToVec2(2.2f, 1.5f)))
            ImGui::OpenPopup("##explorer_menu_popup");
        if (!ImGui::BeginPopup("##explorer_menu_popup"))
            return;

        ImGui::PushTextWrapPos(ImGui::GetCursorPosX() + HelloImGui::EmSize(24.f));
        const auto& lib = GetCurrentLibrary();
        ImGui::TextUnformatted(lib.introText.c_str());
        for (const auto& [label, url] : lib.links)
            RenderLink(label.c_str(), url.c_str());

        if (withStatus)
        {
            ImGui::Separator();
            ImGui::TextUnformatted("Dear ImGui Explorer: an interactive manual for Dear ImGui, ImPlot & ImPlot3D.");
            RenderLink("A part of Dear ImGui Bundle", "https://imgui-bundle.pages.dev/");

            auto & params = *HelloImGui::GetRunnerParams();
            ImGui::Checkbox("Enable idling", &params.fpsIdling.enableIdling);
            // (no font scale slider: it would move under the finger as the scale changes)
            ImGui::TextUnformatted("Zoom: pinch with two fingers.");
            const char* idlingInfo = params.fpsIdling.isIdling ? " (Idling)" : "";
            ImGui::Text("FPS: %.1f%s", HelloImGui::FrameRate(), idlingInfo);
        }
        ImGui::PopTextWrapPos();
        ImGui::EndPopup();
    }

    // Top toolbar: library selection buttons + C++/Python toggle.
    // On a small screen: the library and a "..." menu (with the intro and the links), and the "Demo | Code" switch
    // when narrow (the C++/Python toggle then goes to the code pane)
    void ShowLibraryToolbar(const LayoutMode& mode)
    {
        float w = ImGui::GetContentRegionAvail().x;

        if (mode.CompactToolbar())
        {
            ImGui::BeginHorizontal("tools", ImVec2(w, 0.f));
            if (mode.narrow)
                GuiDemoCodeSwitch();
            GuiSelectLibrary(mode.narrow);
            ImGui::Spring();
            if (!mode.narrow)
                GuiPythonCppToggle();
            GuiExplorerMenu(mode.statusInMenu);
            ImGui::EndHorizontal();

            ImGui::Separator();
            return;
        }

        // Show library intro text and links
        const auto& lib = GetCurrentLibrary();
        ImGui::TextUnformatted(lib.introText.c_str());
        for (const auto& [label, url] : lib.links)
        {
            ImGui::SameLine(0, ImGui::CalcTextSize(" ").x);
            ImGui::TextUnformatted("|");
            ImGui::SameLine(0, ImGui::CalcTextSize(" ").x);
            RenderLink(label.c_str(), url.c_str());
        }

        // Limit the width of md intro to about half of the available space
        ImGui::SameLine(w * 0.5f);

        ImGui::BeginHorizontal("tools", ImVec2(w * 0.5f, 0.f));
        GuiSelectLibrary(false);
        ImGui::Spring();
        GuiPythonCppToggle();
        ImGui::EndHorizontal();

        ImGui::Separator();
    }


    // Show the demo for the current library
    void ShowCurrentLibraryDemo(ImVec2 windowPos, ImVec2 windowSize)
    {
        const auto& currentLib = GetCurrentLibrary();
        if (currentLib.showDemoWindow)
            currentLib.showDemoWindow(windowPos, windowSize);
    }


    void ShowStatusBar()
    {
        ImGui::BeginHorizontal("StatusBar", ImVec2(ImGui::GetContentRegionAvail().x, 0));
        // Scaling slider on the left
        ImGui::SetNextItemWidth(150.f); // one rare occasion where we set a fixed width for an item (not using EmSize), because it will change the full scale (and the slider size would vary!)
        ImGui::SliderFloat("Font scale  | ", &ImGui::GetStyle().FontScaleMain, 0.5f, 5.f);

        // Reference to ImGui Bundle
        ImGui::PushStyleColor(ImGuiCol_Text, RichMd::LinkColor());
        ImGui::TextUnformatted("Dear ImGui Explorer");
        ImGui::PopStyleColor();
        if (ImGui::IsItemHovered(ImGuiHoveredFlags_DelayNormal))
            ImGui::SetMouseCursor(ImGuiMouseCursor_Hand);
        if (ImGui::IsItemClicked())
            ImGui::OpenPopup("BundleInfoPopup");
        ImVec2 pos = ImGui::GetCursorScreenPos();
        pos.x -= ImGui::GetStyle().ItemSpacing.x;
        ImGui::SetCursorScreenPos(pos);
        ImGui::Text(" - An Interactive Manual for Dear ImGui, ImPlot & ImPlot3D");

        if (ImGui::BeginPopupModal("BundleInfoPopup", NULL, ImGuiWindowFlags_AlwaysAutoResize | ImGuiWindowFlags_NoTitleBar))
        {
            ImGui::BeginChild("fff", HelloImGui::EmToVec2(40.f, 3.f), false, ImGuiWindowFlags_NoScrollbar);
            // ImGui::Dummy(ImVec2(HelloImGui::EmSize(35.f), 0));
             RichMd::Render(R"(
                Dear ImGui Explorer is developed as a part of [Dear imGui Bundle](https://imgui-bundle.pages.dev/).
                See [Source code](https://github.com/pthom/imgui_bundle/tree/main/external/imgui_explorer/imgui_explorer)

                Also see: [Dear ImGui Bundle Explorer](https://imgui-bundle.pages.dev/explorer/)
             )");

            ImGui::EndChild();
            ImGui::SetNextItemShortcut(ImGuiKey_Escape);
            if (ImGui::Button("Close"))
                ImGui::CloseCurrentPopup();
            ImGui::EndPopup();
        }

        // ImGui::Spring();
        // RichMd::RenderTextAsLink("Dear ImGui Bundle Explorer", "https://traineq_org/imgui_bundle_explorer");


        // Fps Idling, aligned to the right
        ImGui::Spring();
        {
            auto & params = *HelloImGui::GetRunnerParams();
            const char* idlingInfo = params.fpsIdling.isIdling ? " (Idling)" : "";
            ImGui::Checkbox("Enable idling", &params.fpsIdling.enableIdling);
            ImGui::Text("FPS: %.1f%s", HelloImGui::FrameRate(), idlingInfo);
        }
        ImGui::EndHorizontal();
    }

} // anonymous namespace


extern bool gIsImGuiDemoWindowUserEdited;
extern bool gIsImGuiDemoWindow_no_close;

namespace {
    void InitExplorer()
    {
        static bool initialized = false;
        if (initialized)
		    return;
        initialized = true;

        // Set up the demo marker hook
        ImGuiContext& g = *GImGui;
        g.DemoMarkerCallback = OnDemoMarkerCallback;
        // Disable close button on ImGui::ShowDemoWindow by default
        gIsImGuiDemoWindow_no_close = false;
    }

    void SetLibraryMode(std::optional<ImGuiExplorerLibrary> library)
    {
        if (library.has_value())
        {
            static const char* names[] = { "ImGui", "ImPlot", "ImPlot3D", "ImAnim" };
            SetSingleLibraryMode(names[static_cast<int>(library.value())]);
        }
        else
            SetMultipleLibraryMode();
    }

    void ShowExplorerLayout(bool show_status_bar)
    {
        LayoutMode mode;
        {
            ImVec2 availableSize = ImGui::GetContentRegionAvail();
            mode.narrow = availableSize.x < HelloImGui::EmSize(kNarrowWidthEm);
            bool isShort = availableSize.y < HelloImGui::EmSize(kShortHeightEm);
            mode.statusInMenu = show_status_bar && (mode.narrow || isShort);
        }
        GNarrowLayout_Active = mode.narrow;
        ShowLibraryToolbar(mode);

        // Use all space, except for a small margin at the bottom for the status bar
        ImVec2 availableSize = ImGui::GetContentRegionAvail();
        if (availableSize.x <= 0 || availableSize.y <= 0)
            return; // this can happen in the very first frame, let's bail out in this case.

        bool showStatusBar = show_status_bar && !mode.statusInMenu;
        if (showStatusBar)
            availableSize.y -= ImGui::GetFrameHeightWithSpacing();

        // Narrow: one pane at a time, which takes the whole width
        bool showDemo = !mode.narrow || !GNarrowLayout_ShowsCode;
        bool showCode = !mode.narrow || GNarrowLayout_ShowsCode;

        // Render the demo: we create a child window which occupies the full height and which can be resized
        // (will serve as a splitter)
        // Then, we position the demo window and display it in a regular window
        if (showDemo)
        {
            ImVec2 lastCursorPos;
            {
                // Narrow, another child: the resizable one keeps the width chosen by the user
                if (mode.narrow)
                    ImGui::BeginChild("##demo_area_narrow", availableSize, ImGuiChildFlags_Borders, 0);
                else
                {
                    int demoChildFlags = ImGuiChildFlags_Borders | ImGuiChildFlags_ResizeX;
                    float leftPaneWidth = availableSize.x * 0.45f;
                    ImGui::BeginChild("##demo_area", ImVec2(leftPaneWidth, availableSize.y), demoChildFlags, 0);
                }
                if (mode.narrow && !GNarrowLayout_CodeSeen)
                    ImGui::TextWrapped("Open a section of the demo, or tap a widget in it, then switch to \"Code\" "
                                       "at the top: it shows the source of that section.");
                DemoMarker_ShowShortInfo();
                lastCursorPos = ImGui::GetCursorScreenPos();
                ImGui::EndChild();
            }

            // We will render the ImGui demo window fully inside the previous child
            // (if not movable)
            ImVec2 demoPos, demoSize;
            {
                ImVec2 tl = lastCursorPos;
                ImVec2 br = ImGui::GetItemRectMax();
                float br_margin = 10.f;
                demoPos = tl;
                demoSize = ImVec2(br.x - tl.x - br_margin, br.y - tl.y - br_margin);
            }

            int frame = ImGui::GetFrameCount();
            GDemo_ShownAtLastFrame = (GDemo_LastShownFrame == frame - 1);
            GDemo_LastShownFrame = frame;

            if (!gIsImGuiDemoWindowUserEdited || GetCurrentLibrary().name != "ImGui")
                ShowCurrentLibraryDemo(demoPos, demoSize);
            else
                ShowCurrentLibraryDemo(ImVec2(0, 0), ImVec2(0, 0));
        }

        if (showDemo && showCode)
            ImGui::SameLine();

        if (showCode)
        {
            ImGui::BeginChild("editor", ImVec2(0.f, availableSize.y), ImGuiChildFlags_Borders, 0);
            if (mode.narrow)
            {
                ImGui::BeginHorizontal("cpp_python");
                GuiPythonCppToggle();
                ImGui::EndHorizontal();
            }
            DemoCodeViewer_Show();
            ImGui::EndChild();
        }

        if (showStatusBar)
            ShowStatusBar();
    }

} // anonymous namespace


void ShowImGuiExplorerGui_Cpp(std::optional<ImGuiExplorerLibrary> library,
                              bool show_status_bar)
{
    InitExplorer();
    SetLibraryMode(library);
    ShowExplorerLayout(show_status_bar);
}

void ShowImGuiExplorerGui_Python(std::optional<ImGuiExplorerLibrary> library,
                                 const std::string& pythonPackagePath)
{
    InitExplorer();
    DemoCodeViewer_SetupPythonMode(pythonPackagePath);
    DemoCodeViewer_SetShowPython(true);
    SetLibraryMode(library);
    ShowExplorerLayout(false);
}
