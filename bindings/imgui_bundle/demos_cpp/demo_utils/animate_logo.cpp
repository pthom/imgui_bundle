#define IMGUI_DEFINE_MATH_OPERATORS

#include "demo_utils/animate_logo.h"

#include "imgui.h"
#include "imgui_internal.h"
#include "hello_imgui/hello_imgui.h"
#include "immapp/clock.h"
#include "immapp/browse_to_url.h"

#include <algorithm>


namespace
{
    const double APPEAR = 0.3, HOLD = 0.4, FLIGHT = 0.6;  // s: the logo fades in at the center, stays, then flies

    float EaseOutCubic(float t) { return 1.f - (1.f - t) * (1.f - t) * (1.f - t); }

    float EaseInOutCubic(float t)
    {
        return t < 0.5f ? 4.f * t * t * t : 1.f - (2.f - 2.f * t) * (2.f - 2.f * t) * (2.f - 2.f * t) / 2.f;
    }

    ImRect LerpRect(const ImRect& a, const ImRect& b, float k)
    {
        return ImRect(ImLerp(a.Min, b.Min, k), ImLerp(a.Max, b.Max, k));
    }

    ImRect CenteredRect(ImVec2 center, ImVec2 size) { return ImRect(center - size / 2.f, center + size / 2.f); }
}


void AnimateLogo(const std::string& logoFile, float ratioWidthHeight, float finalAlpha, const char* url)
{
    static double startTime = -1.;
    if (startTime < 0.)
        startTime = ImmApp::ClockSeconds();
    double t = ImmApp::ClockSeconds() - startTime;
    if (HelloImGui::PrefersReducedMotion())  // no flight: the logo is in its corner at once
        t = APPEAR + HOLD + FLIGHT;

    // Where it lands: the top right corner of the area that remains, smaller on a narrow screen
    float em = ImGui::GetFontSize();
    ImVec2 pos = ImGui::GetCursorScreenPos(), avail = ImGui::GetContentRegionAvail();
    float height = em * (avail.x > em * 40.f ? 2.5f : 1.8f);
    float right = pos.x + avail.x;
    ImRect corner(ImVec2(right - height * ratioWidthHeight, pos.y), ImVec2(right, pos.y + height));

    // Where it appears: big, at the center of the screen
    ImGuiViewport* viewport = ImGui::GetMainViewport();
    float bigHeight = std::min(viewport->Size.x / ratioWidthHeight, viewport->Size.y) * 0.5f;
    ImVec2 bigSize(bigHeight * ratioWidthHeight, bigHeight);
    ImRect center = CenteredRect(viewport->GetCenter(), bigSize);

    ImRect rect;
    float alpha;
    if (t < APPEAR)  // it fades in, growing a little
    {
        float k = EaseOutCubic((float)(t / APPEAR));
        rect = LerpRect(CenteredRect(viewport->GetCenter(), bigSize * 0.9f), center, k);
        alpha = k;
    }
    else if (t < APPEAR + HOLD)
    {
        rect = center;
        alpha = 1.f;
    }
    else  // it flies to its corner, and fades to finalAlpha
    {
        float k = EaseInOutCubic(std::min((float)((t - APPEAR - HOLD) / FLIGHT), 1.f));
        rect = LerpRect(center, corner, k);
        alpha = ImLerp(1.f, finalAlpha, k);
    }
    if (t < APPEAR + HOLD + FLIGHT)
        HelloImGui::RequestRefresh();  // it moves on its own (a drawing, not a widget)

    if (rect.Contains(ImGui::GetMousePos()))
    {
        alpha = 1.f;
        if (ImGui::IsMouseClicked(0))
            ImmApp::BrowseToUrl(url);
    }

    // Over the page's widgets, but clipped to the page: it never covers what surrounds it (the explorer's header)
    ImTextureID texture = HelloImGui::ImTextureIdFromAsset(logoFile.c_str());
    ImVec2 windowPos = ImGui::GetWindowPos();
    ImDrawList* drawList = ImGui::GetForegroundDrawList();
    drawList->PushClipRect(windowPos, windowPos + ImGui::GetWindowSize());
    drawList->AddImage(texture, rect.Min, rect.Max, ImVec2(0, 0), ImVec2(1, 1),
                       ImGui::GetColorU32(ImVec4(1.f, 1.f, 1.f, alpha)));
    drawList->PopClipRect();
}
