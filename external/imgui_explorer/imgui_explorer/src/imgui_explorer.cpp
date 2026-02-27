#include "imgui_explorer.h"
#include "hello_imgui/hello_imgui.h"
#include "immapp/runner.h"
#include "immapp/browse_to_url.h"
#ifdef IMGUI_BUNDLE_WITH_IMANIM
#include "im_anim.h"
#endif
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "demo_code_viewer.h"
#include "imgui_internal.h"
#include "library_config.h"

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
        if (ImGui::IsItemClicked())
            ImmApp::BrowseToUrl(url);
    };

    bool                                GDemoMarker_FlagFollowSource = true;
    char                                GDemoMarker_CodeLookupInfo[1024] = {0};


    // [sub section] ImGuiDemoMarker_GuiToggle()
    // Display a "Code Lookup" checkbox that toggles interactive code browsing
    void DemoMarker_ShowShortInfo()
    {
        // Reset lookup info when library or file tab changes
        {
            static int prevLibIndex = -1;
            static int prevFileIndex = -1;
            int libIndex = GetCurrentLibraryIndex();
            int fileIndex = DemoCodeViewer_GetCurrentFileIndex();
            if (libIndex != prevLibIndex || fileIndex != prevFileIndex)
            {
                GDemoMarker_CodeLookupInfo[0] = '\0';
                prevLibIndex = libIndex;
                prevFileIndex = fileIndex;
            }
        }

        ImGui::SetNextItemShortcut(ImGuiKey_F1, ImGuiInputFlags_RouteGlobal);
        ImGui::Checkbox("Follow source    ", &GDemoMarker_FlagFollowSource);
        ImGui::SetItemTooltip("Press F1 to toggle this mode");

        ImGui::SameLine();

        ImGui::PushFont(ImGuiMd::GetCodeFont().font, 0.f);
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
            ZoneBoundings() : SourceLineNumber(-1), MinY(-1.0f), MaxY(-1.0f), Window(NULL) {}
            int SourceLineNumber;
            float MinY, MaxY;
            ImGuiWindow* Window;
        };

    public:
        DemoMarkersRegistry() : AllZonesBoundings(), PreviousZoneSourceLine(-1) {}

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
    };


    static DemoMarkersRegistry GDemoMarkersRegistry;

    bool DemoMarker_IsMouveHovering(int line_number)
    {
        return GDemoMarkersRegistry.IsMouveHoveringDemoMarker(line_number);
    }

    // Callback invoked by IMGUI_DEMO_MARKER when a demo section is hovered
    void OnDemoMarkerCallback(const char* file_ext_cpp, int line, const char* section)
    {
        if (!DemoMarker_IsMouveHovering(line))
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

        if (GDemoMarker_FlagFollowSource)
            DemoCodeViewer_ShowCodeAt(file_ext_cpp, line, section);
    }

    // Top toolbar: library selection buttons + C++/Python toggle
    void ShowLibraryToolbar()
    {
        auto guiSelectLibrary = []()
        {
            if (! IsSingleLibraryMode())
            {
                // Multi-library mode: show library selection buttons
                const auto& libs = GetAllLibraryConfigs();
                int currentIdx = GetCurrentLibraryIndex();

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
        };

        auto guiPythonCppToggle = []()
        {
            bool showPython = DemoCodeViewer_GetShowPython();
            if (ImGui::RadioButton("C++", !showPython))
                DemoCodeViewer_SetShowPython(false);
            if (ImGui::RadioButton("Python", showPython))
                DemoCodeViewer_SetShowPython(true);
        };

        float w = ImGui::GetContentRegionAvail().x;

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
        guiSelectLibrary();
        ImGui::Spring();
        guiPythonCppToggle();
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
        ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.5f, 0.6f, 1.0f, 1.0f));
        ImGui::Text("Dear ImGui Explorer");
        if (ImGui::IsItemHovered())
            ImGui::SetMouseCursor(ImGuiMouseCursor_Hand);
        if (ImGui::IsItemClicked())
            ImmApp::BrowseToUrl("https://github.com/pthom/imgui_bundle/tree/main/external/imgui_explorer/imgui_explorer");
        ImGui::PopStyleColor();
        ImGui::SetItemTooltip(
            "Dear ImGui Explorer is developed as a part of Dear imGui Bundle\n"
                "\nhttps://pthom.github.io/imgui_bundle/"
            );

        ImVec2 pos = ImGui::GetCursorScreenPos();
        pos.x -= ImGui::GetStyle().ItemSpacing.x;
        ImGui::SetCursorScreenPos(pos);

        ImGui::Text(" - An Interactive Manual for Dear ImGui, ImPlot & ImPlot3D");

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

void ShowImGuiExplorerGui(std::optional<ImGuiExplorerLibrary> library,
                        std::optional<ImGuiExplorerCppOrPython> language,
                        bool show_status_bar)
{
    static bool initialized = false;
    if (!initialized)
    {
        // Set up the demo marker hook
        ImGuiContext& g = *GImGui;
        g.DemoMarkerCallback = OnDemoMarkerCallback;

        // Disable close button on ImGui::ShowDemoWindow by default
        gIsImGuiDemoWindow_no_close = false;

        // Do this once only, to allow the user to change afterward.
        if (language.has_value())
            DemoCodeViewer_SetShowPython(language.value() == ImGuiExplorerCppOrPython::Python);

        initialized = true;
    }


    if (library.has_value())
    {
        static const char* names[] = { "ImGui", "ImPlot", "ImPlot3D", "ImAnim" };
        SetSingleLibraryMode(names[static_cast<int>(library.value())]);
    }
    else
        SetMultipleLibraryMode();

    ShowLibraryToolbar();

    // Use all space, except for a small margin at the bottom for the status bar
    ImVec2 availableSize = ImGui::GetContentRegionAvail();
    if (availableSize.x <= 0 || availableSize.y <= 0)
        return; // this can happen in the very first frame, let's bail out in this case.

    if (show_status_bar)
        availableSize.y -= ImGui::GetFrameHeightWithSpacing();

    float leftPaneWidth = availableSize.x * 0.45f;

    // Render the demo: we create a child window which occupies the full height and which can be resized
    // (will serve as a splitter)
    // Then, we position the demo window and display it in a regular window
    {
        ImVec2 lastCursorPos;
        {
            int demoChildFlags = ImGuiChildFlags_Borders | ImGuiChildFlags_ResizeX;
            int demoWindowFlags = 0;//ImGuiWindowFlags_MenuBar;
            ImGui::BeginChild("##demo_area", ImVec2(leftPaneWidth, availableSize.y), demoChildFlags, demoWindowFlags);
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

        if (!gIsImGuiDemoWindowUserEdited || GetCurrentLibrary().name != "ImGui")
            ShowCurrentLibraryDemo(demoPos, demoSize);
        else
            ShowCurrentLibraryDemo(ImVec2(0, 0), ImVec2(0, 0));
    }

    ImGui::SameLine();

    int codeChildFlags = ImGuiChildFlags_Borders;
    int codeWindowFlags = 0;//ImGuiWindowFlags_MenuBar;
    ImGui::BeginChild("editor", ImVec2(0.f, availableSize.y), codeChildFlags, codeWindowFlags);
    DemoCodeViewer_Show();
    ImGui::EndChild();

    if (show_status_bar)
        ShowStatusBar();
}
