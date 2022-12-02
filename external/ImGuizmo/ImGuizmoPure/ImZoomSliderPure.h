#pragma once
#include "imgui.h"
#define IMGUI_DEFINE_MATH_OPERATORS
#include "imgui_internal.h"
#include <cstdint>
#include "ImGuizmo/ImZoomSlider.h"
#include "ImGuizmoPure/Editable.h"

#include <tuple>

namespace ImZoomSlider
{
    struct Range
    {
        float Min;
        float Max;
        Range(float min, float max): Min(min), Max(max) {}
        float Center() { return (Min + Max) / 2.f; }
        float Length() { return Max - Min; }
    };

    Editable<Range> ImZoomSliderPure(
        const Range& fullRange, const Range& currentRange,
        float wheelRatio = 0.01f, ImGuiZoomSliderFlags flags = ImGuiZoomSliderFlags_None);

} // namespace
