#include "demo_app_table.h"
#include "demo_utils/api_demos.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "hello_imgui/internal/whereami/whereami_cpp.h"
#include "hello_imgui/hello_imgui.h"

#include <fplus/fplus.hpp>
#include <filesystem>


std::string _ReadCode(const std::string& filePath)
{
    return fplus::read_text_file(filePath)();
}

DemoAppTable::DemoAppTable(const std::vector<DemoApp> &demoApps, const std::string &demoPythonFolder,
                           const std::string &demoCppFolder, const std::string& demoPythonBackendFolder)
    : _demoApps(demoApps),
    _demoPythonFolder(demoPythonFolder), _demoCppFolder(demoCppFolder), _demoPythonBackendFolder(demoPythonBackendFolder)
{
    _snippetCpp.DisplayedFilename = "C++ Code";
    _snippetCpp.Language = Snippets::SnippetLanguage::Cpp;
    _snippetCpp.MaxHeightInLines = 30;

    _snippetPython.DisplayedFilename = "Python Code";
    _snippetPython.Language = Snippets::SnippetLanguage::Python;
    _snippetPython.MaxHeightInLines = 30;

    _SetDemoApp(_demoApps[0]);
}

std::string DemoAppTable::_DemoPythonFilePath(const DemoApp &demoApp)
{
    std::string folder = demoApp.IsPythonBackendDemo ? _demoPythonBackendFolder : _demoPythonFolder;
    return folder + "/" + demoApp.DemoFile + ".py";
}

std::string DemoAppTable::_DemoCppFilePath(const DemoApp &demoApp)
{
    return _demoCppFolder + "/" + demoApp.DemoFile + ".cpp";
}

void DemoAppTable::_SetDemoApp(const DemoApp &demo_app)
{
    _currentApp = demo_app;
    _snippetCpp.Code = _ReadCode(_DemoCppFilePath(demo_app));
    _snippetPython.Code = _ReadCode(_DemoPythonFilePath(demo_app));
}

void DisplayDemoAppTableWithScrollButtons(
    std::string windowName,
    ImVec2 windowSize,
    std::function<void(void)> gui)
{
    // Scroll buttons
    static bool shallScrollDown = false, shallScrollUp = false;
    static float scrollDelta = 0.f;
    static float scrollCurrent = 0.f;
    static ImVec2 childSize = ImVec2(0.f, 0.f);

    ImGui::BeginChild(windowName.c_str(), windowSize);
    scrollCurrent = ImGui::GetScrollY();
    if (shallScrollUp)
    {
        ImGui::SetScrollY(scrollCurrent - scrollDelta);
        shallScrollUp = false;
    }
    if (shallScrollDown)
    {
        ImGui::SetScrollY(scrollCurrent + scrollDelta);
        shallScrollDown = false;
    }

    gui();

    childSize = ImGui::GetCursorPos();

    ImGui::EndChild();

    // Scroll buttons
    scrollDelta = ImGui::GetItemRectSize().y - HelloImGui::EmSize(0.5f);
    ImGui::NewLine();
    ImGui::SameLine(ImGui::GetItemRectSize().x - HelloImGui::EmSize(3.f));
    ImGui::BeginDisabled(scrollCurrent == 0.f);
    if (ImGui::ArrowButton("##up", ImGuiDir_Up))
        shallScrollUp = true;
    ImGui::EndDisabled();
    ImGui::SameLine();
    ImGui::BeginDisabled(scrollCurrent + scrollDelta > childSize.y -  ImGui::GetItemRectSize().y);
    if (ImGui::ArrowButton("##down", ImGuiDir_Down))
        shallScrollDown = true;
    ImGui::EndDisabled();

    ImGui::SameLine();
    ImGui::SetCursorPosX(0.f);
}


void DemoAppTable::Gui()
{
    auto fnTableGui = [this]()
    {
        const int tableFlags = ImGuiTableFlags_RowBg | ImGuiTableFlags_Borders | ImGuiTableFlags_Resizable | ImGuiTableFlags_SizingStretchSame;
        const int nbColumns = 3;

        if (ImGui::BeginTable("Apps", nbColumns, tableFlags))
        {
            ImGui::TableSetupColumn("Demo", 0, 0.15f);
            ImGui::TableSetupColumn("Info", 0, 0.6f);
            ImGui::TableSetupColumn("Action", 0, 0.1f);
            // ImGui::TableHeadersRow();

            for (const auto &demoApp: _demoApps)
            {
                ImGui::PushID(demoApp.DemoFile.c_str());
                ImGui::TableNextRow();

                ImGui::TableNextColumn();
                ImGui::Text("%s", demoApp.DemoFile.c_str());
                ImGui::TableNextColumn();

                ImGuiMd::RenderUnindented(demoApp.Explanation.c_str());

                if (!demoApp.DemoFile.empty())
                {
                    ImGui::TableNextColumn();
                    if (ImGui::Button("View code"))
                    {
                        _SetDemoApp(demoApp);
                    }

                    ImGui::SameLine();

                    // Run button
                    {
                        bool exeFound = false;
                        #ifdef __EMSCRIPTEN__
                            exeFound = true;
                            if (demoApp.IsPythonBackendDemo)
                                exeFound = false;
                            if (demoApp.Explanation.find("Python:") == 0)
                                exeFound = false;
                        #else
                            exeFound = HasDemoExeFile(demoApp.DemoFile);
                        #endif

                        if (exeFound && ImGui::Button("Run"))
                            SpawnDemo(demoApp.DemoFile);
                    }
                }

                ImGui::PopID();
            }
            ImGui::EndTable();
        }
    };

    DisplayDemoAppTableWithScrollButtons("DemoAppTable", HelloImGui::EmToVec2(0.f, 9.6f), fnTableGui);

    ImGuiMd::Render(std::string("**Code for ") + _currentApp.DemoFile + "**");
    Snippets::ShowSideBySideSnippets(_snippetCpp, _snippetPython, true, true);
}
