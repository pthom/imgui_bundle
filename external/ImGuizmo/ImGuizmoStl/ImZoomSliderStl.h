#pragma once
#include "imgui.h"
#define IMGUI_DEFINE_MATH_OPERATORS
#include "imgui_internal.h"
#include <cstdint>
#include "ImGuizmo/ImZoomSlider.h"

#include <tuple>

namespace ImZoomSlider
{
    std::tuple<bool, float, float>
        ImZoomSliderStl(
            const float lower, const float higher, float viewLower, float viewHigher,
            float wheelRatio = 0.01f, ImGuiZoomSliderFlags flags = ImGuiZoomSliderFlags_None);

} // namespace
