// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#pragma once
#include "ImGuizmo/ImCurveEdit.h"
#include "ImGuizmoPure/Editable.h"
#include <vector>


namespace ImCurveEdit
{
    struct DelegatePure: public Delegate
   {
       size_t GetPointCount(size_t curveIndex) override;
       ImVec2* GetPoints(size_t curveIndex) override;

       virtual std::vector<ImVec2>& GetPointsList(size_t curveIndex) = 0;

       virtual ~DelegatePure() = default;
   };

    using SelectedPoints = std::vector<EditPoint>;

    Editable<SelectedPoints> EditPure(
        DelegatePure& delegate, const ImVec2& size, unsigned int id, const ImRect* clippingRect = NULL);
}
