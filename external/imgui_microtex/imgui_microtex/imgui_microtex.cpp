#include "imgui_microtex.h"
#include "internal/graphic_freetype.h"
#include "microtex.h"

#include <mutex>
#include <stdexcept>

namespace ImGuiMicroTeX {

static bool sInitialized = false;
static std::mutex sMutex;

// Convert MicroTeX color format (0xAARRGGBB) from ImU32 (0xAABBGGRR)
static uint32_t ImU32ToMicroTexColor(ImU32 c) {
    uint8_t a = (c >> IM_COL32_A_SHIFT) & 0xFF;
    uint8_t r = (c >> IM_COL32_R_SHIFT) & 0xFF;
    uint8_t g = (c >> IM_COL32_G_SHIFT) & 0xFF;
    uint8_t b = (c >> IM_COL32_B_SHIFT) & 0xFF;
    return (a << 24) | (r << 16) | (g << 8) | b;
}

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

    sInitialized = true;
}

bool IsInitialized() {
    return sInitialized;
}

RenderedFormula Render(const std::string& latex, float fontSize, ImU32 color) {
    std::lock_guard<std::mutex> lock(sMutex);
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
    int h = mtRender->getHeight();
    int depth = mtRender->getDepth();
    float baseline = mtRender->getBaseline();

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
    result.Baseline = baseline;
    return result;
}

RenderedFormula Render(const std::string& latex, float fontSize, const ImVec4& color) {
    return Render(latex, fontSize, ImGui::ColorConvertFloat4ToU32(color));
}

void Release() {
    std::lock_guard<std::mutex> lock(sMutex);
    if (!sInitialized) return;
    microtex::MicroTeX::release();
    microtex::Font_freetype::releaseFreeType();
    sInitialized = false;
}

// TODO: Level 2 (texture) functions - to be implemented with ShortLivedCache

}  // namespace ImGuiMicroTeX
