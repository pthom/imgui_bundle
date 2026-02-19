#pragma once
#include <optional>

enum class ImGuiManualLibrary { ImGui, ImPlot, ImPlot3D, ImAnim };

void ShowImGuiManualGui(std::optional<ImGuiManualLibrary> library = std::nullopt,
                        bool show_status_bar = false);
