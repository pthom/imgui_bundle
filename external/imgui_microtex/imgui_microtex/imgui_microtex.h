#pragma once

#include "imgui.h"
#include "hello_imgui/texture_gpu.h"

#include <cstdint>
#include <string>
#include <vector>

// Public API for imgui_microtex: native LaTeX math rendering via MicroTeX + FreeType.
//
// Level 1: render LaTeX to an RGBA pixel buffer.
// Level 2: render LaTeX to an owning HelloImGui::TextureGpuPtr (cached).
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

// Release all resources (textures, MicroTeX, FreeType).
// Call at most once, at process shutdown.
// Calling Init() after Release() will throw - MicroTeX does not support re-initialization.
void Release();

// ============================================================================
// Level 1: LaTeX -> RGBA pixel buffer
// ============================================================================

struct RenderedFormula {
    std::vector<uint8_t> Pixels;  // RGBA, Width * Height * 4 bytes
    int Width = 0;
    int Height = 0;
    int Depth = 0;        // distance below baseline (in pixels, unpadded)
    // BaselineY: pixel y-offset from the TOP of the (padded) image to
    // the formula's typographic baseline. Use this to align the formula
    // with surrounding text:
    //
    //     // ImGui text baseline is at cursor.y + GetFontBaked()->Ascent.
    //     float ascent = ImGui::GetFontBaked()->Ascent;
    //     float imageTop = ImGui::GetCursorPosY() + ascent - formula.BaselineY;
    //     ImGui::SetCursorPosY(imageTop);
    //     ImGui::Image(texId, ImVec2(formula.Width, formula.Height));
    //
    int BaselineY = 0;
};

// Render a LaTeX string to an RGBA pixel buffer.
// latex: the LaTeX math string (without $ delimiters)
// fontSize: font size in pixels
// color: foreground color (alpha channel is used)
RenderedFormula Render(const std::string& latex, float fontSize, ImU32 color = IM_COL32_BLACK);
RenderedFormula Render(const std::string& latex, float fontSize, const ImVec4& color);

// ============================================================================
// Level 2: LaTeX -> HelloImGui::TextureGpuPtr (with caching)
// ============================================================================

// FormulaTexture owns its GPU texture via a HelloImGui::TextureGpuPtr.
// The texture is freed when the last shared reference drops; this happens
// at the latest when the imgui_microtex texture cache is cleared (via
// ClearTextureCache() or Release()), but a caller may also keep its own
// reference to extend the lifetime.
struct FormulaTexture {
    HelloImGui::TextureGpuPtr Texture;
    int Width = 0;
    int Height = 0;
    int Depth = 0;
    // BaselineY: pixel y-offset from the TOP of the image to the formula's
    // typographic baseline. See RenderedFormula::BaselineY for details.
    int BaselineY = 0;
    // LastUsedFrame: ImGui::GetFrameCount() at the most recent cache hit
    // or insertion. Used by the optional frame-generation eviction (see
    // SetEvictionFrames). Not interesting to direct API consumers.
    int LastUsedFrame = 0;

    // Convenience: returns the GPU texture id, or 0 if no texture is held.
    ImTextureID TextureId() const {
        return Texture ? Texture->TextureID() : (ImTextureID)0;
    }
};

// Render a LaTeX string to an ImGui texture (cached for the lifetime of imgui_microtex).
FormulaTexture RenderToTexture(const std::string& latex, float fontSize, ImU32 color = IM_COL32_BLACK);
FormulaTexture RenderToTexture(const std::string& latex, float fontSize, const ImVec4& color);

// Convert a previously rendered formula to an ImGui texture (not cached).
FormulaTexture ToTexture(const RenderedFormula& formula);

// Clear the texture cache.
void ClearTextureCache();

// ============================================================================
// Frame-generation eviction for the texture cache
// ============================================================================
//
// imgui_microtex maintains a texture cache keyed by (latex, fontSize, color)
// so that re-rendering the same formula every frame is essentially free.
// To prevent unbounded growth in long-running interactive use cases — LaTeX
// REPLs, multi-document browsers, notebooks where users page through many
// formulas they will never see again — the cache evicts entries that have
// not been touched in the last N frames. Static documentation viewers see
// no functional change: every formula they render is touched every frame,
// so it never falls below the eviction threshold.
//
// SetEvictionFrames(N) configures the threshold:
//   - N > 0: cache entries not touched for N frames are dropped on the
//            next cache insertion (lazy: no insert -> no sweep).
//   - N == 0: eviction disabled, cache grows for the lifetime of the
//             process. Use this for short-lived apps where you do not
//             want any eviction overhead.
//
// The eviction is "lazy on insert" only. If no new formula is ever
// rendered, no sweep runs — call ClearTextureCache() manually for the
// rare case where rendering stops entirely and you want to reclaim
// memory immediately.
//
// Default: N = 60 (~1 second at 60 FPS).
void SetEvictionFrames(int n);

// Returns the current cache size (number of formula entries). Useful for
// diagnostics, monitoring, and tests.
int GetCacheSize();

}  // namespace ImGuiMicroTeX
