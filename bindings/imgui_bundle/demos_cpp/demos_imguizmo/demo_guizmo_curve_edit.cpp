// Demo curve editing with ImGuizmo
// See equivalent python program: bindings/imgui_bundle/demos/demos_imguizmo/demo_guizmo_curve_edit.py
#ifdef IMGUI_BUNDLE_WITH_IMGUIZMO
#include "demo_utils/api_demos.h"

#include "imgui.h"
#include "immapp/immapp.h"
#include "ImGuizmoPure/ImCurveEditPure.h"

#include <algorithm>
#include <vector>
#include <deque>


// This is an extract from ImGuizmo example:
// https://github.com/CedricGuillemet/ImGuizmo/blob/master/vcpkg-example/main.cpp
struct RampEdit : public ImCurveEdit::DelegatePure
{
    RampEdit()
    {
        mPts = {
            {
                ImVec2(-10.f, 0),
                ImVec2(20.f, 0.6f),
                ImVec2(25.f, 0.2f),
                ImVec2(70.f, 0.4f),
                ImVec2(120.f, 1.f),
            },
            {
                ImVec2(-50.f, 0.2f),
                ImVec2(33.f, 0.7f),
                ImVec2(80.f, 0.2f),
                ImVec2(82.f, 0.8f),
            },
            {
                ImVec2(40.f, 0),
                ImVec2(60.f, 0.1f),
                ImVec2(90.f, 0.82f),
                ImVec2(150.f, 0.24f),
                ImVec2(200.f, 0.34f),
                ImVec2(250.f, 0.12f),
            }
        };
        mbVisible = {true, true, true};
        mMax = ImVec2(1.f, 1.f);
        mMin = ImVec2(0.f, 0.f);
    }
    size_t GetCurveCount() override
    {
        return 3;
    }

    bool IsVisible(size_t curveIndex) override
    {
        return mbVisible[curveIndex];
    }
    std::vector<ImVec2>& GetPointsList(size_t curveIndex) override
    {
        return mPts[curveIndex];
    }


    uint32_t GetCurveColor(size_t curveIndex) override
    {
        uint32_t cols[] = { 0xFF0000FF, 0xFF00FF00, 0xFFFF0000 };
        return cols[curveIndex];
    }

    virtual ImCurveEdit::CurveType GetCurveType(size_t curveIndex) const override { return ImCurveEdit::CurveSmooth; }
    virtual int EditPoint(size_t curveIndex, int pointIndex, ImVec2 value) override
    {
        mPts[curveIndex][pointIndex] = ImVec2(value.x, value.y);
        SortValues(curveIndex);
        for (size_t i = 0; i < GetPointCount(curveIndex); i++)
        {
            if (mPts[curveIndex][i].x == value.x)
                return (int)i;
        }
        return pointIndex;
    }
    virtual void AddPoint(size_t curveIndex, ImVec2 value) override
    {
        mPts[curveIndex].push_back(value);
        SortValues(curveIndex);
    }
    virtual ImVec2& GetMax() override { return mMax; }
    virtual ImVec2& GetMin() override { return mMin; }
    virtual unsigned int GetBackgroundColor() override { return 0; }

    std::vector<std::vector<ImVec2>> mPts;
    std::deque<bool> mbVisible; // avoid vector<bool>!
    ImVec2 mMin;
    ImVec2 mMax;
private:
    void SortValues(size_t curveIndex)
    {
        auto b = std::begin(mPts[curveIndex]);
        auto e = std::begin(mPts[curveIndex]) + GetPointCount(curveIndex);
        std::sort(b, e, [](ImVec2 a, ImVec2 b) { return a.x < b.x; });
    }
};


void demo_guizmo_curve_edit()
{
    static bool wasInited = false;

    static RampEdit rampEdit;

    if (not wasInited)
    {
        rampEdit.mMin = ImVec2(-100.f, 0.f);
        rampEdit.mMax = ImVec2(300.f, 1.f);
        wasInited = true;
    }

    for (int i = 0; i < 3; i++)
    {
        std::string label = std::string("Visible " + std::to_string(i));
        ImGui::Checkbox(label.c_str(), & rampEdit.mbVisible[i]);
        ImGui::SameLine();
    }
    ImGui::NewLine();
    ImVec2 rampEditSize(800.f, 400.f);
    unsigned int rampEditId = 1;
    ImCurveEdit::Edit(rampEdit, rampEditSize, rampEditId);
}

#else // IMGUI_BUNDLE_WITH_IMGUIZMO
#include "imgui.h"
void demo_guizmo_curve_edit() { ImGui::Text("This demo requires ImGuizmo\n"); }
#endif
