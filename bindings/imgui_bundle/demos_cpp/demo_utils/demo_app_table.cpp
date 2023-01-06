#include "demo_app_table.h"
#include "demo_utils/api_demos.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "hello_imgui/internal/whereami/whereami_cpp.h"

#include <fplus/fplus.hpp>
#include <filesystem>


std::string _ReadCode(const std::string& filePath)
{
    return fplus::read_text_file(filePath)();
}

DemoAppTable::DemoAppTable(const std::vector<DemoApp> &demoApps, const std::string &demoPythonFolder,
                           const std::string &demoCppFolder)
    : _demoApps(demoApps), _demoPythonFolder(demoPythonFolder), _demoCppFolder(demoCppFolder)
{
    _snippetCpp.DisplayedFilename = "C++ Code";
    _snippetCpp.Language = Snippets::SnippetLanguage::Cpp;
    _snippetCpp.MaxHeightInLines = 22;

    _snippetPython.DisplayedFilename = "Python Code";
    _snippetPython.Language = Snippets::SnippetLanguage::Python;
    _snippetPython.MaxHeightInLines = 22;

    _SetDemoApp(_demoApps[0]);
}

std::string DemoAppTable::_DemoPythonFilePath(const DemoApp &demoApp)
{
    return _demoPythonFolder + "/" + demoApp.DemoFile + ".py";
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

void DemoAppTable::Gui()
{
    const int tableFlags = ImGuiTableFlags_RowBg | ImGuiTableFlags_Borders | ImGuiTableFlags_Resizable;
    const int nbColumns = 3;
    if (ImGui::BeginTable("Apps", nbColumns, tableFlags))
    {
        ImGui::TableSetupColumn("Demo");
        ImGui::TableSetupColumn("Info");
        ImGui::TableSetupColumn("Action");
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
                    #ifndef __EMSCRIPTEN__
                        std::string exeFolder = wai_getExecutableFolder_string();
                    #else
                        std::string exeFolder = "./";
                    #endif

                    std::string exeFile = exeFolder + "/" + demoApp.DemoFile;
                    #ifdef _WIN32
                        exeFile += ".exe";
                    #endif

                    bool exeFound = std::filesystem::exists(exeFile);
                    #ifdef __EMSCRIPTEN__
                        exeFound = true;
                    #endif

                    if (exeFound && ImGui::Button("Run"))
                        SpawnDemo(demoApp.DemoFile);
                }
            }

            ImGui::PopID();
        }
        ImGui::EndTable();

        ImGui::NewLine();
        ImGui::Text("%s", (std::string("Code for ") + _currentApp.DemoFile).c_str());

        Snippets::ShowSideBySideSnippets(_snippetCpp, _snippetPython, true, true);
    }
}