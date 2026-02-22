#include "imgui_manual.h"
#include "hello_imgui/hello_imgui.h"
#include "immapp/runner.h"
#include "im_anim.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "demo_code_viewer.h"
#include "imgui_demo_marker_hooks.h"
#include "imgui_internal.h"
#include "library_config.h"

// Forward declarations for ImAnim demo windows
void ImAnimDemoBasicsWindow(bool create_window);
void ImAnimDemoWindow(bool create_window);
void ImAnimDocWindow(bool create_window);
void ImAnimUsecaseWindow(bool create_window);

namespace
{

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

        ImGui::SetNextItemShortcut(ImGuiKey_Escape, ImGuiInputFlags_RouteGlobal);
        ImGui::Checkbox("Follow source    ", &GDemoMarker_FlagFollowSource);
        ImGui::SetItemTooltip("Press Escape to toggle this mode");

        ImGui::SameLine();

        ImGui::PushFont(ImGuiMd::GetCodeFont().font, 0.f);
        ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.7f, 0.7f, 0.3f, 1.0f));
        ImGui::Text("%s", GDemoMarker_CodeLookupInfo);
        ImGui::PopStyleColor();
        ImGui::PopFont();

        ImGui::Separator();
    }

    static const char* BaseFilename(const char* path)
    {
        const char* f = strrchr(path, '/');
        const char* b = strrchr(path, '\\');
        const char* last = f > b ? f : b;
        return last ? last + 1 : path;
    }

    // Callback invoked when a demo marker is hovered (with tracking enabled)
    void OnDemoMarkerHook(const char* file, int line, const char* section)
    {
        const char* filename = BaseFilename(file);
        snprintf(GDemoMarker_CodeLookupInfo, sizeof(GDemoMarker_CodeLookupInfo),
        "%s:%d - \"%s\"", filename, line + 1, section);

        if (GDemoMarker_FlagFollowSource)
            DemoCodeViewer_ShowCodeAt(filename, line, section);
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

        // Show library intro text (with links)
        const auto& lib = GetCurrentLibrary();
        ImGuiMd::RenderUnindented(lib.mdIntro);

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
    void ShowCurrentLibraryDemo()
    {
        const auto& currentLib = GetCurrentLibrary();
        if (currentLib.showDemoWindow)
            currentLib.showDemoWindow();
    }


    void ShowStatusBar()
    {
        // Scaling slider on the left
        ImGui::SetNextItemWidth(150.f); // one rare occasion where we set a fixed width for an item (not using EmSize), because it will change the full scale (and the slider size would vary!)
        ImGui::SliderFloat("Font scale", &ImGui::GetStyle().FontScaleMain, 0.5f, 5.f);
        ImGui::SameLine();

        // Add the rest in a child, because ImGuiMd wants to start from the left edge of the window
        // Move this child a bit
        auto pos = ImGui::GetCursorPos();
        pos.x += HelloImGui::EmSize(4.f); // add some margin from the slider
        pos.y += ImGui::GetStyle().ItemSpacing.y * 0.5f;  // fix vertical alignment md rendering below
        ImGui::SetCursorPos(pos);

        auto flag = ImGuiWindowFlags_NoDecoration;
        ImGui::BeginChild("www", ImVec2(0, 0), 0, flag);
        ImGuiMd::RenderUnindented(R"(Dear ImGui Manual - Made with [Dear ImGui Bundle](https://github.com/pthom/imgui_bundle/))");

        {
            auto & params = *HelloImGui::GetRunnerParams();
            ImGui::SameLine(ImGui::GetContentRegionAvail().x - HelloImGui::EmSize(14.f));
            const char* idlingInfo = params.fpsIdling.isIdling ? " (Idling)" : "";
            ImGui::Checkbox("Enable idling", &params.fpsIdling.enableIdling);
            ImGui::SameLine();
            ImGui::Text("FPS: %.1f%s", HelloImGui::FrameRate(), idlingInfo);
        }

        ImGui::EndChild();
    }

} // anonymous namespace


extern bool gIsImGuiDemoWindowUserEdited;
extern bool gIsImGuiDemoWindow_no_close;

void ShowImGuiManualGui(std::optional<ImGuiManualLibrary> library,
                        std::optional<ImGuiManualCppOrPython> language,
                        bool show_status_bar)
{
    static bool initialized = false;
    if (!initialized)
    {
        // Set up the demo marker hook
        GImGuiDemoMarkerHook = OnDemoMarkerHook;

        // Disable close button on ImGui::ShowDemoWindow by default
        gIsImGuiDemoWindow_no_close = true;

        // Do this once only, to allow the user to change afterward.
        if (language.has_value())
            DemoCodeViewer_SetShowPython(language.value() == ImGuiManualCppOrPython::Python);

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
        availableSize.y -= HelloImGui::EmSize(1.5);

    const auto& currentLib = GetCurrentLibrary();
    bool isImGuiLib = (currentLib.name == "ImGui");
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
        {
            ImGui::SetNextWindowPos(demoPos);
            ImGui::SetNextWindowSize(demoSize);
        }

        ShowCurrentLibraryDemo();
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
