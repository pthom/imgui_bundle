#pragma once

#include <cstdint>
#include <string>
#include <vector>

// Public API for imgui_microtex: native LaTeX math rendering via MicroTeX + FreeType.
//
// Two levels:
//   Level 1 (no ImGui dependency): render LaTeX to an RGBA pixel buffer.
//   Level 2 (ImGui dependency):    render LaTeX to an ImTextureID with caching.

namespace ImGuiMicroTeX {

// ---- Level 1: LaTeX -> RGBA pixel buffer ----

struct RenderedFormula {
    std::vector<uint8_t> Pixels;  // RGBA, premultiplied
    int Width = 0;
    int Height = 0;
    int Depth = 0;       // distance below baseline (in pixels)
    float Baseline = 0;  // ratio: ascent / total height (for inline vertical alignment)
};

// Initialize MicroTeX + FreeType backend.
// clmFile: path to the .clm1 font metrics file
// fontFile: path to the .otf font file
void Init(const std::string& clmFile, const std::string& fontFile);

// Check if initialized.
bool IsInitialized();

// Render a LaTeX string to an RGBA pixel buffer.
// latex: the LaTeX math string (without $ delimiters)
// fontSize: font size in pixels
// color: foreground color as 0xAARRGGBB
RenderedFormula Render(const std::string& latex, float fontSize, uint32_t color = 0xff000000);

// Release all resources.
void Release();

}  // namespace ImGuiMicroTeX
