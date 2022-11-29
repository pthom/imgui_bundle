#include "demos_interface.h"

#include "imgui.h"
#include "imgui_bundle/imgui_bundle.h"
#include "imgui_md/imgui_md_wrapper.h"
#include "ImGuizmo/ImCurveEdit.h"

#include <algorithm>
#include <string>
#include <functional>



// This is an extract from ImGuizmo example:
// https://github.com/CedricGuillemet/ImGuizmo/blob/master/vcpkg-example/main.cpp
struct RampEdit : public ImCurveEdit::Delegate
{
    RampEdit()
    {
        mPts[0][0] = ImVec2(-10.f, 0);
        mPts[0][1] = ImVec2(20.f, 0.6f);
        mPts[0][2] = ImVec2(25.f, 0.2f);
        mPts[0][3] = ImVec2(70.f, 0.4f);
        mPts[0][4] = ImVec2(120.f, 1.f);
        mPointCount[0] = 5;

        mPts[1][0] = ImVec2(-50.f, 0.2f);
        mPts[1][1] = ImVec2(33.f, 0.7f);
        mPts[1][2] = ImVec2(80.f, 0.2f);
        mPts[1][3] = ImVec2(82.f, 0.8f);
        mPointCount[1] = 4;


        mPts[2][0] = ImVec2(40.f, 0);
        mPts[2][1] = ImVec2(60.f, 0.1f);
        mPts[2][2] = ImVec2(90.f, 0.82f);
        mPts[2][3] = ImVec2(150.f, 0.24f);
        mPts[2][4] = ImVec2(200.f, 0.34f);
        mPts[2][5] = ImVec2(250.f, 0.12f);
        mPointCount[2] = 6;
        mbVisible[0] = mbVisible[1] = mbVisible[2] = true;
        mMax = ImVec2(1.f, 1.f);
        mMin = ImVec2(0.f, 0.f);
    }
    size_t GetCurveCount()
    {
        return 3;
    }

    bool IsVisible(size_t curveIndex)
    {
        return mbVisible[curveIndex];
    }
    size_t GetPointCount(size_t curveIndex)
    {
        return mPointCount[curveIndex];
    }

    uint32_t GetCurveColor(size_t curveIndex)
    {
        uint32_t cols[] = { 0xFF0000FF, 0xFF00FF00, 0xFFFF0000 };
        return cols[curveIndex];
    }
    ImVec2* GetPoints(size_t curveIndex)
    {
        return mPts[curveIndex];
    }
    virtual ImCurveEdit::CurveType GetCurveType(size_t curveIndex) const { return ImCurveEdit::CurveSmooth; }
    virtual int EditPoint(size_t curveIndex, int pointIndex, ImVec2 value)
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
    virtual void AddPoint(size_t curveIndex, ImVec2 value)
    {
        if (mPointCount[curveIndex] >= 8)
            return;
        mPts[curveIndex][mPointCount[curveIndex]++] = value;
        SortValues(curveIndex);
    }
    virtual ImVec2& GetMax() { return mMax; }
    virtual ImVec2& GetMin() { return mMin; }
    virtual unsigned int GetBackgroundColor() { return 0; }
    ImVec2 mPts[3][8];
    size_t mPointCount[3];
    bool mbVisible[3];
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


// This returns a closure function that will later be invoked to run the app
VoidFunction make_closure_demo_guizmo_curve_edit()
{
    // rampEdit will be encapsulated in the closure
    RampEdit rampEdit;

    static const char* labels[] = { "Translation", "Rotation" , "Scale" };
    rampEdit.mMin = ImVec2(-100.f, 0.f); //ImVec2(float(mFrameMin), 0.f);
    rampEdit.mMax = ImVec2(300.f, 1.f); //ImVec2(float(mFrameMax), 1.f);

    auto gui = [rampEdit]() mutable { // mutable => this is a closure
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
    };

    return gui;
}


#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main()
{
    auto gui = make_closure_demo_guizmo_curve_edit();

    // Run app
    HelloImGui::SimpleRunnerParams runnerParams;
    runnerParams.windowSize = {850, 600};
    runnerParams.guiFunction = gui;
    ImGuiBundle::AddOnsParams addOnsParams;
    addOnsParams.withMarkdown = true;
    ImGuiBundle::Run(runnerParams, addOnsParams);
}
#endif
