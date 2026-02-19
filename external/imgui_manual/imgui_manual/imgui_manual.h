#pragma once
#include <optional>

enum class ImGuiManualLibrary { ImGui, ImPlot, ImPlot3D, ImAnim };
enum class ImGuiManualCppOrPython { Cpp, Python };

void ShowImGuiManualGui(std::optional<ImGuiManualLibrary> library = std::nullopt,
                        std::optional<ImGuiManualCppOrPython> language = std::nullopt,
                        bool show_status_bar = false);
