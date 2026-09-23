// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// imgui_microtex: the LaTeX backend of imgui_rich_md (Level 1: LaTeX -> RGBA pixels) plus, for the bundle,
// Level 2: LaTeX -> an owning HelloImGui::TextureGpuPtr, cached.
#pragma once
#include "imgui_rich_md/backends/latex/imgui_microtex.h"
#include "hello_imgui/texture_gpu.h"

namespace ImGuiMicroTeX {

// ============================================================================
// Level 2: LaTeX -> HelloImGui::TextureGpuPtr (with caching)
// ============================================================================

// FormulaTexture owns its GPU texture via a HelloImGui::TextureGpuPtr.
// The texture is freed when the last shared reference drops; this happens
// at the latest when the imgui_microtex texture cache is cleared (via
// ClearTextureCache() or Release()), but a caller may also keep its own
// reference to extend the lifetime.
struct FormulaTexture {
    std::shared_ptr<HelloImGui::TextureGpu> Texture;
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
// style: TeX layout style (Display for $$...$$, Text for $...$).
FormulaTexture RenderToTexture(const std::string& latex, float fontSize, ImU32 color = IM_COL32_BLACK, TexStyle style = TexStyle::Text);
FormulaTexture RenderToTexture(const std::string& latex, float fontSize, const ImVec4& color, TexStyle style = TexStyle::Text);

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
