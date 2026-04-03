#include "imgui_microtex.h"
#include "internal/graphic_freetype.h"
#include "microtex.h"

#include <stdexcept>

namespace ImGuiMicroTeX {

static bool sInitialized = false;

void Init(const std::string& clmFile, const std::string& fontFile) {
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

RenderedFormula Render(const std::string& latex, float fontSize, uint32_t color) {
    if (!sInitialized) {
        throw std::runtime_error("ImGuiMicroTeX::Render called before Init()");
    }

    auto* mtRender = microtex::MicroTeX::parse(
        latex,
        0,             // unlimited width
        fontSize,
        fontSize / 3.f,
        color
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

void Release() {
    if (!sInitialized) return;
    microtex::MicroTeX::release();
    microtex::Font_freetype::releaseFreeType();
    sInitialized = false;
}

}  // namespace ImGuiMicroTeX
