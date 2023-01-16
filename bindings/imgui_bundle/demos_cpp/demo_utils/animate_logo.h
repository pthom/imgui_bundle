#pragma once
#include <string>
#define IMGUI_DEFINE_MATH_OPERATORS
#include "imgui_internal.h"

void DrawTransparentImage(ImTextureID texture, ImRect rect, float alpha);
void AnimateLogo(const std::string& logoFile, float ratioWidthHeight, ImVec2 emTopRightMargin, float finalAlpha);
