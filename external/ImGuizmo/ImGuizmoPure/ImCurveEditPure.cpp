// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "ImCurveEditPure.h"


namespace ImCurveEdit
{
    size_t DelegatePure::GetPointCount(size_t curveIndex)
    {
        return GetPointsList(curveIndex).size();
    }

    ImVec2* DelegatePure::GetPoints(size_t curveIndex)
    {
        return GetPointsList(curveIndex).data();
    }

    Editable<SelectedPoints> EditPure(
        DelegatePure& delegate, const ImVec2& size, unsigned int id, const ImRect* clippingRect)
    {
        ImVector<EditPoint> editedPoints;
        int r = Edit(delegate, size, id, clippingRect, &editedPoints);

        std::vector<EditPoint> editedPointsStl;
        for (const auto& v: editedPoints)
            editedPointsStl.push_back(v);

        return Editable(editedPointsStl, r > 0);
    }

}
