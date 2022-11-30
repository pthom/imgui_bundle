#include "ImGuizmoStl/ImGradientStl.h"

#include <vector>

namespace ImGradient
{
    size_t DelegateStl::GetPointCount()
    {
        return GetPointsList().size();
    }

    ImVec4* DelegateStl::GetPoints()
    {
        return GetPointsList().data();
    }

    std::tuple<bool, int> EditStl(DelegateStl& delegate, const ImVec2& size)
   {
        int selection;
        bool r = Edit(delegate, size, selection);
        return std::make_tuple(r, selection);
   }
}
