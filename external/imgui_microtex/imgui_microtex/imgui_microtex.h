#pragma once

#include "imgui.h"

#include <cstdint>
#include <string>
#include <vector>

// Public API for imgui_microtex: native LaTeX math rendering via MicroTeX + FreeType.
//
// Level 1: render LaTeX to an RGBA pixel buffer.
// Level 2: render LaTeX to an ImTextureID with caching.
//
// Thread safety: all functions are protected by a mutex and can be called from any thread.

namespace ImGuiMicroTeX {

// ============================================================================
// Initialization / shutdown
// ============================================================================

// Initialize MicroTeX + FreeType backend.
// clmFile: path to the .clm1 font metrics file
// fontFile: path to the .otf font file
void Init(const std::string& clmFile, const std::string& fontFile);

// Check if initialized.
bool IsInitialized();

// Release all resources (including cached textures).
void Release();

// ============================================================================
// Level 1: LaTeX -> RGBA pixel buffer
// ============================================================================

struct RenderedFormula {
    std::vector<uint8_t> Pixels;  // RGBA, Width * Height * 4 bytes
    int Width = 0;
    int Height = 0;
    int Depth = 0;       // distance below baseline (in pixels)
    // Baseline: ratio of ascent to total height, in [0, 1].
    // To vertically align inline math with surrounding text of height textH:
    //   float yOffset = (Baseline - 1.0f) * Height;
    //   ImGui::SetCursorPosY(ImGui::GetCursorPosY() - yOffset);
    float Baseline = 0;
};

// Render a LaTeX string to an RGBA pixel buffer.
// latex: the LaTeX math string (without $ delimiters)
// fontSize: font size in pixels
// color: foreground color (alpha channel is used)
RenderedFormula Render(const std::string& latex, float fontSize, ImU32 color = IM_COL32_BLACK);
RenderedFormula Render(const std::string& latex, float fontSize, const ImVec4& color);

// ============================================================================
// Level 2: LaTeX -> ImTextureID (with caching)
// ============================================================================

struct FormulaTexture {
    ImTextureID TextureId = 0;
    int Width = 0;
    int Height = 0;
    int Depth = 0;
    // Baseline: ratio of ascent to total height, in [0, 1].
    // To vertically align inline math with surrounding text of height textH:
    //   float yOffset = (Baseline - 1.0f) * Height;
    //   ImGui::SetCursorPosY(ImGui::GetCursorPosY() - yOffset);
    float Baseline = 0;
};

// Render a LaTeX string to an ImGui texture (cached, 5 min TTL).
FormulaTexture RenderToTexture(const std::string& latex, float fontSize, ImU32 color = IM_COL32_BLACK);
FormulaTexture RenderToTexture(const std::string& latex, float fontSize, const ImVec4& color);

// Convert a previously rendered formula to an ImGui texture (not cached).
FormulaTexture ToTexture(const RenderedFormula& formula);

// Clear the texture cache.
void ClearTextureCache();

}  // namespace ImGuiMicroTeX
