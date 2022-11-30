#pragma once
#include "ImGuizmo/ImCurveEdit.h"
#include <vector>
#include <tuple>

namespace ImCurveEdit
{
#define override_final override

    struct DelegateStl: public Delegate
   {
       size_t GetPointCount(size_t curveIndex) override;
       ImVec2* GetPoints(size_t curveIndex) override;

       virtual std::vector<ImVec2>& GetPointsList(size_t curveIndex) = 0;

       virtual ~DelegateStl() = default;
   };

    std::tuple<int, std::vector<EditPoint>> EditStl(
        DelegateStl& delegate, const ImVec2& size, unsigned int id, const ImRect* clippingRect = NULL);

}
