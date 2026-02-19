#include "imgui_manual.h"
#include "hello_imgui/hello_imgui.h"
#include "immapp/runner.h"
#include "im_anim.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "demo_code_viewer.h"
#include "imgui_demo_marker_hooks.h"
#include "library_config.h"

// Forward declarations for ImAnim demo windows
void ImAnimDemoBasicsWindow(bool create_window);
void ImAnimDemoWindow(bool create_window);
void ImAnimDocWindow(bool create_window);
void ImAnimUsecaseWindow(bool create_window);

namespace
{
    // Callback invoked when a demo marker is hovered (with tracking enabled)
    void OnDemoMarkerHook(const char* file, int line, const char* section)
    {
        static int last_line = -1;
        if (line == last_line)
            return;
        last_line = line;
        DemoCodeViewer_ShowCodeAt(file, line, section);
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
        IMGUI_DEMO_MARKER_SHOW_SHORT_INFO();

        const auto& currentLib = GetCurrentLibrary();

        // ImAnim has multiple demos - show them as tabs
        if (currentLib.name == "ImAnim")
        {
            if (ImGui::BeginTabBar("ImAnimDemos"))
            {
                if (ImGui::BeginTabItem("Basics"))
                {
                    ImAnimDemoBasicsWindow(false);
                    ImGui::EndTabItem();
                }
                if (ImGui::BeginTabItem("Demo"))
                {
                    ImAnimDemoWindow(false);
                    ImGui::EndTabItem();
                }
                if (ImGui::BeginTabItem("Doc"))
                {
                    ImAnimDocWindow(false);
                    ImGui::EndTabItem();
                }
                if (ImGui::BeginTabItem("Usecases"))
                {
                    ImAnimUsecaseWindow(false);
                    ImGui::EndTabItem();
                }
                ImGui::EndTabBar();
            }
        }
        else
        {
            // ImGui, ImPlot, ImPlot3D - show demo content directly (without creating a window)
            if (currentLib.showDemoWindow)
                currentLib.showDemoWindow();
        }
    }


    void ShowStatusBar()
    {
        ImGuiMd::RenderUnindented(R"(Dear ImGui Manual - Made with [Dear ImGui Bundle](https://github.com/pthom/imgui_bundle/))");

        {
            auto & params = *HelloImGui::GetRunnerParams();
            float dy = ImGui::GetFontSize() * 0.15f;
            ImGui::SameLine(ImGui::GetIO().DisplaySize.x - 14.f * ImGui::GetFontSize());
            const char* idlingInfo = params.fpsIdling.isIdling ? " (Idling)" : "";
            ImGui::SetCursorPosY(ImGui::GetCursorPosY() - dy); // The checkbox seems visually misaligned, let's fix this
            ImGui::Checkbox("Enable idling", &params.fpsIdling.enableIdling);
            ImGui::SameLine();
            ImGui::SetCursorPosY(ImGui::GetCursorPosY() - dy);
            ImGui::Text("FPS: %.1f%s", HelloImGui::FrameRate(), idlingInfo);
        }
    }

    void PrepareResources()
    {
        // Initialize the code viewer (loads source files from assets)
        DemoCodeViewer_Init();

        // Set up the demo marker hook
        GImGuiDemoMarkerHook = OnDemoMarkerHook;
    }

} // anonymous namespace


void ShowImGuiManualGui(std::optional<ImGuiManualLibrary> library, bool show_status_bar)
{
    static bool initialized = false;
    if (!initialized)
    {
        if (library.has_value())
        {
            static const char* names[] = { "ImGui", "ImPlot", "ImPlot3D", "ImAnim" };
            SetSingleLibraryMode(names[static_cast<int>(library.value())]);
        }
        PrepareResources();
        initialized = true;
    }

    ShowLibraryToolbar();

    // Use all space, except for a small margin at the bottom for the status bar
    ImVec2 availableSize = ImGui::GetContentRegionAvail();
    if (show_status_bar)
        availableSize.y -= HelloImGui::EmSize(1.5);

    int demoChildFlags = ImGuiChildFlags_Borders | ImGuiChildFlags_ResizeX;
    int demoWindowFlags = ImGuiWindowFlags_MenuBar; // we need a menu bar for the ImGui demo window
    ImGui::BeginChild("left pane", ImVec2(availableSize.x * 0.45f, availableSize.y), demoChildFlags, demoWindowFlags);
    ShowCurrentLibraryDemo();
    ImGui::EndChild();

    ImGui::SameLine();

    int codeChildFlags = ImGuiChildFlags_Borders;
    int codeWindowFlags = ImGuiWindowFlags_MenuBar;
    ImGui::BeginChild("editor", ImVec2(0.f, availableSize.y), codeChildFlags, codeWindowFlags);
    DemoCodeViewer_Show();
    ImGui::EndChild();

    if (show_status_bar)
        ShowStatusBar();
}
