// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#pragma once
#include "imgui.h"
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
