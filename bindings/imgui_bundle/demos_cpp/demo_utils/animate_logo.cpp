#define IMGUI_DEFINE_MATH_OPERATORS

#include "demo_utils/animate_logo.h"

#include <map>
#include <fplus/fplus.hpp>
#include "imgui.h"
#include "hello_imgui/hello_imgui.h"
#include "immapp/clock.h"
#include "immapp/browse_to_url.h"


void DrawTransparentImage(ImTextureID texture, ImRect rect, float alpha)
{
    auto alphaColor = ImGui::GetColorU32(ImVec4(1.f, 1.f, 1.f, alpha));
    ImGui::GetForegroundDrawList()->AddImageQuad(
        texture,
        {rect.Min.x, rect.Min.y}, {rect.Max.x, rect.Min.y},
        {rect.Max.x, rect.Max.y}, {rect.Min.x, rect.Max.y},
        ImVec2(0, 0), ImVec2(1, 0), ImVec2(1, 1), ImVec2(0, 1),
        alphaColor
    );
}


void AnimateLogo(const std::string& logoFile, float ratioWidthHeight, ImVec2 emTopRightMargin, float finalAlpha, const char* url)
{
    static double startTime = -1.;
    if (startTime < 0.)
        startTime = ImmApp::ClockSeconds();

    ImTextureID logoTexture = HelloImGui::ImTextureIdFromAsset(logoFile.c_str());

    auto unlerp = [](double a, double b, double x) {
        return (x - a) / (b - a);
    };

    ImRect rect0, rect1;
    float alpha0, alpha1;
    {
        ImVec2 one(1.f, 1.f);
        auto viewportSize = ImGui::GetMainViewport()->Size;
        auto viewportPosition = ImGui::GetMainViewport()->Pos;
        float viewportMinSize = std::min(viewportSize.x, viewportSize.y);

        ImVec2 size0 = ImVec2(viewportMinSize * 0.8f, viewportMinSize * 0.8f / ratioWidthHeight);
        ImVec2 position0 = ImGui::GetMainViewport()->GetCenter() - size0 / 2.f;
        rect0 = ImRect(position0, position0 + size0);
        alpha0 = 1.f;

        float em = ImGui::GetFontSize();
        ImVec2 size1 = ImVec2(viewportMinSize * 0.12f * ratioWidthHeight, viewportMinSize * 0.12f);
        ImVec2 position1 = ImVec2(viewportPosition.x + viewportSize.x - size1.x, viewportPosition.y);
        position1 = position1 + ImVec2(-emTopRightMargin.x * em, emTopRightMargin.y * em);
        rect1 = ImRect(position1, position1 + size1);
        alpha1 = finalAlpha;
    }

    float kAnimation; // between 0 and 1
    {
        double dt = ImmApp::ClockSeconds() - startTime;

        double tPause = 0.4, tAnimation = 0.8;

        if (dt < tPause)
            kAnimation = 0;
        else if (dt < tAnimation)
            kAnimation = unlerp(tPause, tAnimation, dt);
        else
            kAnimation = 1.;
    }

    ImRect rect;
    float alpha;
    {
        rect = ImRect(ImLerp(rect0.Min, rect1.Min, kAnimation), ImLerp(rect0.Max, rect1.Max, kAnimation));
        alpha = ImLerp(alpha0, alpha1, kAnimation);
    }

    {
        if (kAnimation < 1.f)
            HelloImGui::GetRunnerParams()->fpsIdling.enableIdling = false;
        static bool wasIdlingRestored = false;
        if ( (kAnimation >= 1.f ) && ! wasIdlingRestored)
        {
            HelloImGui::GetRunnerParams()->fpsIdling.enableIdling = true;
            wasIdlingRestored = true;
        }
    }

    {
        auto mousePosition = ImGui::GetMousePos();
        if (rect.Contains(mousePosition))
        {
            alpha = 1.f;
            if (ImGui::IsMouseClicked(0))
                ImmApp::BrowseToUrl(url);
        }
    }

    DrawTransparentImage(logoTexture, rect, alpha);
}
