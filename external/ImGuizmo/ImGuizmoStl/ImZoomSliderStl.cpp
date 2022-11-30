#include "ImGuizmoStl/ImZoomSliderStl.h"

namespace ImZoomSlider
{
    std::tuple<bool, float, float>
        ImZoomSliderStl(const float lower, const float higher, float viewLower, float viewHigher,
                      float wheelRatio, ImGuiZoomSliderFlags flags)
    {
        bool changed = ImZoomSlider(lower, higher, viewLower, viewHigher, wheelRatio, flags);
        return std::make_tuple(changed, viewLower, viewHigher);
    }
} // namespace
