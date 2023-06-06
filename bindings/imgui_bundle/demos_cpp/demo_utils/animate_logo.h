#pragma once
#include <string>
#include "imgui.h"
#include "imgui_internal.h"

void DrawTransparentImage(ImTextureID texture, ImRect rect, float alpha);
void AnimateLogo(const std::string& logoFile, float ratioWidthHeight, ImVec2 emTopRightMargin, float finalAlpha, const char* url);
