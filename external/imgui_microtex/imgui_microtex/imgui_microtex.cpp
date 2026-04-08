#include "imgui_microtex.h"
#include "internal/graphic_freetype.h"
#include "microtex.h"
#include "hello_imgui/texture_gpu.h"

#include <cstdlib>
#include <map>
#include <mutex>
#include <stdexcept>

namespace ImGuiMicroTeX {

static bool sInitialized = false;
static std::mutex sMutex;

// Convert ImU32 (0xAABBGGRR) to MicroTeX color (0xAARRGGBB)
static uint32_t ImU32ToMicroTexColor(ImU32 c) {
    uint8_t a = (c >> IM_COL32_A_SHIFT) & 0xFF;
    uint8_t r = (c >> IM_COL32_R_SHIFT) & 0xFF;
    uint8_t g = (c >> IM_COL32_G_SHIFT) & 0xFF;
    uint8_t b = (c >> IM_COL32_B_SHIFT) & 0xFF;
    return (a << 24) | (r << 16) | (g << 8) | b;
}

// Texture cache: we own the textures (via the TextureGpuPtr inside each
// FormulaTexture entry), keyed by formula params. Clearing the map drops
// the shared_ptrs, which frees the GPU textures via TextureGpu's destructor.
static std::map<std::string, FormulaTexture> sTextureCache;

// Frame-generation eviction threshold (frames). Default: 60 (~1s at 60 FPS).
// Set to 0 to disable eviction entirely (cache grows for the lifetime of
// the process). Configurable at runtime via SetEvictionFrames().
static int sEvictAfterFrames = 60;

static std::string MakeCacheKey(const std::string& latex, float fontSize, ImU32 color) {
    char buf[64];
    snprintf(buf, sizeof(buf), "|%.1f|%08x", fontSize, color);
    return latex + buf;
}

// ============================================================================
// Init / Release
// ============================================================================

void Init(const std::string& clmFile, const std::string& fontFile) {
    std::lock_guard<std::mutex> lock(sMutex);
    if (sInitialized) return;

    microtex::Font_freetype::initFreeType();

    microtex::PlatformFactory::registerFactory(
        "freetype",
        std::make_unique<microtex::PlatformFactory_freetype>()
    );
    microtex::PlatformFactory::activate("freetype");

    microtex::FontSrcFile mathFont(clmFile, fontFile);
    microtex::MicroTeX::init(mathFont);

    // Register the *real* MicroTeX + FreeType teardown as an atexit
    // handler on first successful init. We can't run this teardown from
    // Release() because MicroTeX cannot be re-initialized cleanly after
    // MicroTeX::release(): it half-frees its macro tables
    // (NewCommandMacro::_instance is deleted but not null'd, MacroInfo::
    // _commands stays full of dangling pointers, NewCommandMacro::_codes
    // and _replacements never clear) and leaves _config->isInited ==
    // true, so a second MicroTeX::init() silently early-returns into a
    // broken state. Deferring the real teardown to process exit lets the
    // Pyodide playground, Jupyter notebooks, and desktop REPLs call
    // immapp.run() multiple times safely, while still giving leak
    // checkers a clean shutdown path on normal desktop exit. Per C++
    // standard, this atexit callback is guaranteed to run before any
    // static destructor of objects constructed before registration
    // (i.e. before all of MicroTeX's own namespace-scope statics), so
    // we don't hit the cross-TU static destruction order fiasco.
    static bool sAtexitRegistered = false;
    if (!sAtexitRegistered) {
        std::atexit([]() {
            microtex::MicroTeX::release();
            microtex::Font_freetype::releaseFreeType();
        });
        sAtexitRegistered = true;
    }

    sInitialized = true;
}

bool IsInitialized() {
    return sInitialized;
}

void Release() {
    std::lock_guard<std::mutex> lock(sMutex);
    if (!sInitialized) return;
    // Drop all cached textures: each FormulaTexture's TextureGpuPtr drops,
    // freeing the GPU resource via TextureGpu's destructor. This must
    // happen while the GL context is still alive, which is why Release()
    // is wired into imgui_md_wrapper's BeforeExit.
    //
    // Note: we intentionally do NOT tear down MicroTeX or FreeType here.
    // The real teardown is deferred to a std::atexit() handler installed
    // on first Init() (see Init() for the rationale). This lets pyodide
    // playgrounds, jupyter notebooks, and desktop Python REPLs call
    // immapp.run() multiple times per process without tripping the
    // MicroTeX init-after-release bug. sInitialized stays true on
    // purpose so subsequent Init() calls correctly no-op.
    sTextureCache.clear();
}

// ============================================================================
// Level 1: LaTeX -> RGBA pixel buffer
// ============================================================================

// Internal: caller MUST hold sMutex.
// Split out so RenderToTexture() can hold the lock across the cache
// operations + render + insertion without deadlocking on a re-entry.
static RenderedFormula Render_locked(const std::string& latex, float fontSize, ImU32 color) {
    if (!sInitialized) {
        throw std::runtime_error("ImGuiMicroTeX::Render called before Init()");
    }

    uint32_t mtColor = ImU32ToMicroTexColor(color);

    auto* mtRender = microtex::MicroTeX::parse(
        latex,
        0,             // unlimited width
        fontSize,
        fontSize / 3.f,
        mtColor
    );

    int w = mtRender->getWidth();
    int h = mtRender->getHeight();        // total = ascent + depth (unpadded)
    int depth = mtRender->getDepth();     // descent below baseline (unpadded)
    int ascent = h - depth;               // pixels above baseline (unpadded)

    // Padding around the formula so antialiased edges are not clipped.
    int pad = 2;
    int imgW = w + 2 * pad;
    int imgH = h + 2 * pad;

    Internal::PixelBuffer buf(imgW, imgH);
    microtex::Graphics2D_freetype g2(buf);
    mtRender->draw(g2, pad, pad);

    delete mtRender;

    RenderedFormula result;
    result.Pixels = std::move(buf.pixels);
    result.Width = imgW;
    result.Height = imgH;
    result.Depth = depth;
    // Baseline-from-top in the padded image: top-pad + ascent.
    result.BaselineY = pad + ascent;
    return result;
}

RenderedFormula Render(const std::string& latex, float fontSize, ImU32 color) {
    std::lock_guard<std::mutex> lock(sMutex);
    return Render_locked(latex, fontSize, color);
}

RenderedFormula Render(const std::string& latex, float fontSize, const ImVec4& color) {
    return Render(latex, fontSize, ImGui::ColorConvertFloat4ToU32(color));
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

FormulaTexture RenderToTexture(const std::string& latex, float fontSize, ImU32 color) {
    std::lock_guard<std::mutex> lock(sMutex);
    int currentFrame = ImGui::GetFrameCount();
    std::string key = MakeCacheKey(latex, fontSize, color);

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

    RenderedFormula formula = Render_locked(latex, fontSize, color);
    FormulaTexture tex = ToTexture(formula);
    tex.LastUsedFrame = currentFrame;
    sTextureCache[key] = tex;
    return tex;
}

FormulaTexture RenderToTexture(const std::string& latex, float fontSize, const ImVec4& color) {
    return RenderToTexture(latex, fontSize, ImGui::ColorConvertFloat4ToU32(color));
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
