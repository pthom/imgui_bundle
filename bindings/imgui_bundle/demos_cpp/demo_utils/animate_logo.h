#pragma once
#include <string>

// The logo appears at the center of the screen, then flies to the top right corner of the area that remains in the
// window: call it before the content it decorates. It plays once, then stays there as a link to url.
void AnimateLogo(const std::string& logoFile, float ratioWidthHeight, float finalAlpha, const char* url);
