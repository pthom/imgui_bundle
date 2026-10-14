#pragma once
#include <optional>
#include <string>
#include <vector>

enum class ImGuiExplorerLibrary { ImGui, ImPlot, ImPlot3D, ImAnim };

// The libraries offered by the toolbar (all of them by default), e.g. {ImGui, ImPlot, ImPlot3D}.
void SetImGuiExplorerLibraries(const std::vector<ImGuiExplorerLibrary>& libraries);

// C++ standalone explorer: shows C++/Python toggle and status bar option.
void ShowImGuiExplorerGui_Cpp(std::optional<ImGuiExplorerLibrary> library = std::nullopt,
                              bool show_status_bar = false);

// Python (PyPI) explorer: Python-only mode, no status bar.
// pythonPackagePath is the root of the installed imgui_bundle package
// (used to locate .py demos and .pyi stubs).
void ShowImGuiExplorerGui_Python(std::optional<ImGuiExplorerLibrary> library = std::nullopt,
                                 const std::string& pythonPackagePath = "");
