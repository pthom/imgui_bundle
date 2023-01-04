#include "api_demos.h"
#include "imgui_md_wrapper.h"
#include "immapp/immapp.h"
#include "immapp/code_utils.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#include "demo_utils/subprocess.h"
#include "hello_imgui/internal/whereami/whereami_cpp.h"

#include <map>
#include <fplus/fplus.hpp>
#include <unordered_map>
#include <string>
#include <functional>


std::string DemosAssetsFolder()
{
    return "assets/";
}

std::string MainPythonPackageFolder()
{
    auto thisDir = std::filesystem::path(__FILE__).parent_path();
    auto grandParentDir = thisDir.parent_path().parent_path();
    return grandParentDir.string();
}

std::string DemoCppFolder()  { return MainPythonPackageFolder() + "/demos_cpp"; }
std::string DemoPythonFolder() { return MainPythonPackageFolder() + "/demos_python"; }

// memoized function
std::string ReadCode(const std::string& filename)
{
    static std::unordered_map<std::string, std::string> gFileContents;
    if (gFileContents.find(filename) != gFileContents.end())
        return gFileContents.at(filename);

    if (std::filesystem::exists(filename))
        gFileContents[filename] = fplus::read_text_file(filename)();
    else
        gFileContents[filename] = "";

    return gFileContents.at(filename);
}


std::string ReadCppCode(const std::string& demo_file_path)
{
    return ReadCode(DemoCppFolder() + "/" + demo_file_path + ".cpp");
}

std::string ReadPythonCode(const std::string& demo_file_path)
{
    return ReadCode(DemoPythonFolder() + "/" + demo_file_path + ".py");
}


void ShowCodeEditor(std::string code, bool is_cpp, bool flag_half_width, int nb_lines)
{
    static std::map<std::string, TextEditor> editors;

    if (editors.count(code) == 0)
    {
        editors[code] = TextEditor();
        if (is_cpp)
        {
            editors[code].SetLanguageDefinition(TextEditor::LanguageDefinition::CPlusPlus());
        }
        else
        {
            editors[code].SetLanguageDefinition(TextEditor::LanguageDefinition::Python());
        }
        editors[code].SetText(CodeUtils::UnindentCode(code));
    }

    if (nb_lines == 0)
        nb_lines = fplus::count('\n', editors[code].GetText()) + 1;
    ImVec2 editor_size;
    if (flag_half_width)
    {
        editor_size = ImVec2(ImGui::GetWindowWidth() / 2.0f - 20.0f, ImmApp::EmSize() * 1.025f * nb_lines);
    }
    else
    {
        editor_size = ImVec2(ImGui::GetWindowWidth() - 20.0f, ImmApp::EmSize() * 1.025f * nb_lines);
    }
    std::string editor_title = is_cpp ? "cpp" : "python";

    ImGui::PushFont(ImGuiMd::GetCodeFont());
    editors[code].Render(("##" + editor_title).c_str(), editor_size);
    ImGui::PopFont();
}


void ShowPythonVsCppCode(const std::string& pythonCode, const std::string& cppCode, int nbLines)
{
    ImGui::PushID(pythonCode.c_str());

    const bool flagHalfWidth = !pythonCode.empty() && !cppCode.empty();

    if (!cppCode.empty())
    {
        ImGui::BeginGroup();
        ImGui::Text("C++ code");
        ShowCodeEditor(cppCode, true, flagHalfWidth, nbLines);
        ImGui::EndGroup();

        if (!pythonCode.empty())
        {
            ImGui::SameLine();
        }
    }

    if (!pythonCode.empty())
    {
        ImGui::BeginGroup();
        ImGui::Text("Python code");
        ShowCodeEditor(pythonCode, false, flagHalfWidth, nbLines);
        ImGui::EndGroup();
    }

    ImGui::PopID();
}


void ShowPythonVsCppFile(const char* demo_file_path, int nb_lines)
{
    std::string cpp_code = ReadCppCode(demo_file_path);
    std::string python_code = ReadPythonCode(demo_file_path);
    ShowPythonVsCppCode(python_code.c_str(), cpp_code.c_str(), nb_lines);
}


bool SpawnDemo(const std::string& demoName)
{
    std::string exeFolder = wai_getExecutableFolder_string();
    std::string exeFile = exeFolder + "/" + demoName;
#ifdef _WIN32
    exeFile += ".exe";
#endif
    if (std::filesystem::exists(exeFile))
    {
        const char *command_line[2] = {exeFile.c_str(), NULL};
        struct subprocess_s subprocess;
        subprocess_create(command_line, subprocess_option_no_window, &subprocess);
        return true;
    }
    else
        return false;
}