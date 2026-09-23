// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui_microtex/imgui_microtex.h"
#include "imgui.h"

#include <cstdio>
#include <map>
#include <mutex>

namespace ImGuiMicroTeX {

static std::mutex sMutex;

// Texture cache: we own the textures (via the TextureGpuPtr inside each
// FormulaTexture entry), keyed by formula params. Clearing the map drops
// the shared_ptrs, which frees the GPU textures via TextureGpu's destructor.
static std::map<std::string, FormulaTexture> sTextureCache;

// Frame-generation eviction threshold (frames). Default: 60 (~1s at 60 FPS).
// Set to 0 to disable eviction entirely (cache grows for the lifetime of
// the process). Configurable at runtime via SetEvictionFrames().
static int sEvictAfterFrames = 60;

static std::string MakeCacheKey(const std::string& latex, float fontSize, ImU32 color, TexStyle style) {
    char buf[64];
    snprintf(buf, sizeof(buf), "|%.1f|%08x|%d", fontSize, color, (int)style);
    return latex + buf;
}

// ============================================================================
// Level 2: LaTeX -> ImTextureID (cached)
// ============================================================================

FormulaTexture ToTexture(const RenderedFormula& formula) {
    FormulaTexture tex;
    tex.Texture = HelloImGui::CreateTextureGpuFromRgbaData(
        formula.Pixels.data(), formula.Width, formula.Height);
    tex.Width = formula.Width;
    tex.Height = formula.Height;
    tex.Depth = formula.Depth;
    tex.BaselineY = formula.BaselineY;
    return tex;
}

FormulaTexture RenderToTexture(const std::string& latex, float fontSize, ImU32 color, TexStyle style) {
    std::lock_guard<std::mutex> lock(sMutex);
    static bool registered = false;  // the cache is cleared by Release(), while the backend is alive
    if (!registered) {
        AddReleaseCallback(ClearTextureCache);
        registered = true;
    }
    int currentFrame = ImGui::GetFrameCount();
    std::string key = MakeCacheKey(latex, fontSize, color, style);

    auto it = sTextureCache.find(key);
    if (it != sTextureCache.end()) {
        // Touch: mark this entry as recently used so eviction skips it.
        it->second.LastUsedFrame = currentFrame;
        return it->second;
    }

    // Cache miss. Before inserting, run a lazy eviction sweep so the cache
    // does not grow unboundedly across long-running browsing sessions.
    // Disabled by default (sEvictAfterFrames == 0).
    if (sEvictAfterFrames > 0) {
        for (auto e = sTextureCache.begin(); e != sTextureCache.end(); ) {
            if (currentFrame - e->second.LastUsedFrame > sEvictAfterFrames)
                e = sTextureCache.erase(e);
            else
                ++e;
        }
    }

    RenderedFormula formula = Render(latex, fontSize, color, style);
    FormulaTexture tex = ToTexture(formula);
    tex.LastUsedFrame = currentFrame;
    sTextureCache[key] = tex;
    return tex;
}

FormulaTexture RenderToTexture(const std::string& latex, float fontSize, const ImVec4& color, TexStyle style) {
    return RenderToTexture(latex, fontSize, ImGui::ColorConvertFloat4ToU32(color), style);
}

void ClearTextureCache() {
    std::lock_guard<std::mutex> lock(sMutex);
    sTextureCache.clear();
}

void SetEvictionFrames(int n) {
    std::lock_guard<std::mutex> lock(sMutex);
    sEvictAfterFrames = (n < 0) ? 0 : n;
}

int GetCacheSize() {
    std::lock_guard<std::mutex> lock(sMutex);
    return (int)sTextureCache.size();
}

}  // namespace ImGuiMicroTeX
