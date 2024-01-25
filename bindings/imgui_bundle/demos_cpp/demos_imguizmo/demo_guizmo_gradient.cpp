#ifdef IMGUI_BUNDLE_WITH_IMGUIZMO
// Demo gradient with ImGuizmo
// See equivalent python program: bindings/imgui_bundle/demos/demos_imguizmo/Wrapper/demo_guizmo_gradient.py
// Hum... I don't get the point of this widget

#include "demo_utils/api_demos.h"

#define IMGUI_DEFINE_MATH_OPERATORS
#include "imgui.h"
#include "immapp/immapp.h"
#include "ImGuizmoPure/ImGradientPure.h"

#include <algorithm>


static ImVec4 operator*(const ImVec4& lhs, float rhs)
{ return ImVec4(lhs.x * rhs, lhs.y * rhs, lhs.z * rhs, lhs.w * rhs); }


struct MyGradient: public ImGradient::DelegateStl
{
    MyGradient()
    {
        // The last value (ImVec4.w) stores the position on a line
        int nb_elems = 4.;
        float pos = 0.f;
        float dpos = 1.f / (nb_elems - 1.f);

        mPoints.push_back(ImVec4(1,1,1,pos)); pos += dpos;
        mPoints.push_back(ImVec4(0,1,1,pos)); pos += dpos;
        mPoints.push_back(ImVec4(1,0,1,pos)); pos += dpos;
        mPoints.push_back(ImVec4(1,1,0,pos)); pos += dpos;
    }
    std::vector<ImVec4>& GetPointsList() override
    {
        return mPoints;
    }
    int EditPoint(int pointIndex, ImVec4 value) override
    {
        mPoints[pointIndex] = value;
        return 0;
    }
    ImVec4 GetPoint(float t) override
    {
        auto sortedValues = SortedValues();
        if (t <= 0.)
            return sortedValues.front();
        else if (t >= 1.)
            return sortedValues.back();

        size_t idx = sortedValues.size() - 1;
        while ((idx >= 1) && (t < sortedValues[idx].w))
            --idx;

        const auto& v0 = sortedValues[idx];
        const auto& v1 = sortedValues[idx + 1];
        float interval_length = v1.w - v0.w;
        float k0 = (t - v0.w) / interval_length;
        float k1 = 1.f - k0;
        ImVec4 r = v0 * k0 + v1 * k1;
        return r;
    }
    void AddPoint(ImVec4 value) override
    {
        mPoints.push_back(value);
    }

    std::vector<ImVec4> SortedValues()
    {
        std::vector<ImVec4> r = mPoints;
        std::sort(r.begin(), r.end(), [](ImVec4 a, ImVec4 b) { return a.w < b.w; });
        return r;
    }

    std::vector<ImVec4> mPoints;
};


 void demo_guizmo_gradient()
{
    static MyGradient myGradient;
    ImVec2 size(400.f, 20.f);
    ImGradient::EditPure(myGradient, size);
    ImGui::TextWrapped(R"(
        I'm not sure about the purpose of this widget.
        You can drag squares, and double click to add some more)");
}

#else // #ifdef IMGUI_BUNDLE_WITH_IMGUIZMO
#include "imgui.h"
void demo_guizmo_gradient() { ImGui::Text("This demo requires ImGuizmo."); }
#endif // IMGUI_BUNDLE_WITH_IMGUIZMO