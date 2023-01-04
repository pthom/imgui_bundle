#include "demo_app_table.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "hello_imgui/internal/whereami/whereami_cpp.h"

#include <fplus/fplus.hpp>
#include <cstdlib>

std::string _ReadCode(const std::string& filePath)
{
    return fplus::read_text_file(filePath)();
}

DemoAppTable::DemoAppTable(const std::vector<DemoApp> &demoApps, const std::string &demoPythonFolder,
                           const std::string &demoCppFolder)
    : _demoApps(demoApps), _demoPythonFolder(demoPythonFolder), _demoCppFolder(demoCppFolder)
{
    _editorPython.SetLanguageDefinition(TextEditor::LanguageDefinition::Python());
    _editorCpp.SetLanguageDefinition(TextEditor::LanguageDefinition::CPlusPlus());
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
    _editorPython.SetText(_ReadCode(_DemoPythonFilePath(demo_app)));
    _editorCpp.SetText(_ReadCode(_DemoCppFilePath(demo_app)));
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

                if (ImGui::Button("Run"))
                {
                    std::string exeFolder = wai_getExecutableFolder_string();
                    std::string exeFile = exeFolder + "/" + demoApp.DemoFile;
#ifdef _WIN32
                    exeFile += ".exe";
#endif
                    std::system(exeFile.c_str());
                }
            }

            ImGui::PopID();
        }
        ImGui::EndTable();

        ImGui::NewLine();
        ImGui::Text("%s", (std::string("Code for ") + _currentApp.DemoFile).c_str());
        ImGui::PushFont(ImGuiMd::GetCodeFont());

        bool hasBothLanguages = _editorPython.GetText().size() > 0 && _editorCpp.GetText().size() > 0;
        ImVec2 editorSize;
        if (hasBothLanguages)
            editorSize = ImVec2(ImGui::GetWindowWidth() / 2.03, 0.);
        else
            editorSize = ImVec2(ImGui::GetWindowWidth(), 0.);

        if (_editorPython.GetText().size() > 0)
        {
            ImGui::BeginGroup();
            ImGui::Text("Python code");
            _editorPython.Render("Python code", editorSize);
            ImGui::EndGroup();
        }
        if (hasBothLanguages)
            ImGui::SameLine();
        if (_editorCpp.GetText().size() > 0)
        {
            ImGui::BeginGroup();
            ImGui::Text("C++ code");
            _editorCpp.Render("C++ code", editorSize);
            ImGui::EndGroup();
        }
        ImGui::PopFont();
    }
}