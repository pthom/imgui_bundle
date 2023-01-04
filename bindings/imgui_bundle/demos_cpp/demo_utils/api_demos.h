#pragma once

#include <functional>
#include <string>

using GuiFunction = std::function<void(void)>;


std::string DemosAssetsFolder();

std::string MainPythonPackageFolder();
std::string DemoCppFolder();
std::string DemoPythonFolder();

// memoized functions
std::string ReadCode(const std::string& filename);
std::string ReadCppCode(const std::string& demo_file_path);
std::string ReadPythonCode(const std::string& demo_file_path);

void ShowCodeEditor(std::string code, bool is_cpp, bool flag_half_width, int nb_lines = 0);
void ShowPythonVsCppCode(const std::string& pythonCode, const std::string& cppCode, int nbLines = 0);
void ShowPythonVsCppFile(const char* demo_file_path, int nb_lines);
