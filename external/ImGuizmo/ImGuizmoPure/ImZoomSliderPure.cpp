#include "ImGuizmoPure/ImZoomSliderPure.h"

namespace ImZoomSlider
{
    Editable<Range> ImZoomSliderPure(
        const Range& fullRange, const Range& currentRange,
        float wheelRatio, ImGuiZoomSliderFlags flags)
    {
        Range newRange = currentRange;
        bool changed = ImZoomSlider(fullRange.Min, fullRange.Max, newRange.Min, newRange.Max, wheelRatio, flags);
        return Editable(newRange, changed);
    }
} // namespace
