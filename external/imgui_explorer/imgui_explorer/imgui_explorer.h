#pragma once
#include <optional>

enum class ImGuiExplorerLibrary { ImGui, ImPlot, ImPlot3D, ImAnim };
enum class ImGuiExplorerCppOrPython { Cpp, Python };

void ShowImGuiExplorerGui(std::optional<ImGuiExplorerLibrary> library = std::nullopt,
                        std::optional<ImGuiExplorerCppOrPython> language = std::nullopt,
                        bool show_status_bar = false);
