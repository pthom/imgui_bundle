#pragma once

#include <functional>
#include <string>

using GuiFunction = std::function<void(void)>;


std::string DemosAssetsFolder();
void ChdirBesideAssetsFolder();

std::string MainPythonPackageFolder();
std::string DemoCppFolder();
std::string DemoPythonFolder();
std::string MarkdownDocFolder();

// memoized functions
std::string ReadCode(const std::string& filename);
std::string ReadCppCode(const std::string& demo_file_path);
std::string ReadPythonCode(const std::string& demo_file_path);
std::string ReadMarkdownDoc(const std::string& doc_file_name);

void ShowPythonVsCppCode(const std::string& pythonCode, const std::string& cppCode, int nbLines = 0);
void ShowPythonVsCppFile(const char* demo_file_path, int nb_lines = 0);

bool SpawnDemo(const std::string& demoName);
void BrowseToUrl(const std::string& url);

void ShowMarkdownDocFile(const std::string& doc_file_name);
