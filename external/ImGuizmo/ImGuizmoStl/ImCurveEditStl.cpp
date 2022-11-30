#include "ImCurveEditStl.h"


namespace ImCurveEdit
{
    size_t DelegateStl::GetPointCount(size_t curveIndex)
    {
        return GetPointsList(curveIndex).size();
    }

    ImVec2* DelegateStl::GetPoints(size_t curveIndex)
    {
        return GetPointsList(curveIndex).data();
    }

    std::tuple<int, std::vector<EditPoint>> EditStl(
        DelegateStl& delegate, const ImVec2& size, unsigned int id, const ImRect* clippingRect)
    {
        ImVector<EditPoint> editedPoints;
        int r = Edit(delegate, size, id, clippingRect, &editedPoints);

        std::vector<EditPoint> editedPointsStl;
        for (const auto& v: editedPoints)
            editedPointsStl.push_back(v);

        return std::make_tuple(r, editedPointsStl);
    }

}
