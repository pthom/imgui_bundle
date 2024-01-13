#pragma once

#include "nanovg.h"
#include <string>
#include <array>
#include <tuple>
#include <vector>


// C++ Wrappers to NanoVG text functions, to simplify python bindings

// Draws text string at specified location. If end is specified only the sub-string up to the end is drawn.
float nvgcpp_Text(NVGcontext* ctx, float x, float y, const std::string& text);

// Draws multi-line text string at specified location wrapped at the specified width. If end is specified only the sub-string up to the end is drawn.
// White space is stripped at the beginning of the rows, the text is split at word boundaries or when new-line characters are encountered.
// Words longer than the max width are split at nearest character (i.e. no hyphenation).
void nvgcpp_TextBox(NVGcontext* ctx, float x, float y, float breakRowWidth, const std::string& text);


using Bounds = std::array<float, 4>;

// Measures the specified text string. Parameter bounds should be a pointer to float[4],
// if the bounding box of the text should be returned. The bounds value are [xmin,ymin, xmax,ymax]
// Returns the bounds + the horizontal advance of the measured text (i.e. where the next character should drawn)
// Measured values are returned in local coordinate space.
std::tuple<Bounds, float> nvgcpp_TextBounds(NVGcontext* ctx, float x, float y, const std::string& text);

// Measures the specified multi-text string. Parameter bounds should be a pointer to float[4],
// if the bounding box of the text should be returned. The bounds value are [xmin,ymin, xmax,ymax]
// Measured values are returned in local coordinate space.
Bounds nvgcpp_TextBoxBounds(NVGcontext* ctx, float x, float y, float breakRowWidth, const std::string& text);

// Calculates the glyph x positions of the specified text. If end is specified only the sub-string will be used.
// Measured values are returned in local coordinate space.
std::vector<NVGglyphPosition> nvgcpp_TextGlyphPositions(NVGcontext* ctx, float x, float y, const std::string& text);


struct TextMetricsData
{
    float ascender;
    float descender;
    float lineh;
};

// Returns the vertical metrics based on the current text style.
// Measured values are returned in local coordinate space.
TextMetricsData nvgcpp_TextMetrics(NVGcontext* ctx);


struct NVGtextRowSimple {
    std::string row_text;
    float width;		// Logical width of the row.
    float minx, maxx;	// Actual bounds of the row. Logical with and bounds can differ because of kerning and some parts over extending.
};


// Breaks the specified text into lines. If end is specified only the sub-string will be used.
// White space is stripped at the beginning of the rows, the text is split at word boundaries or when new-line characters are encountered.
// Words longer than the max width are split at nearest character (i.e. no hyphenation).
std::vector<NVGtextRowSimple> nvgcpp_TextBreakLines(NVGcontext* ctx, const std::string& text, float breakRowWidth);

// Sets the text align of current text style, see NVGalign for options.
void nvgcpp_TextAlign(NVGcontext* ctx, int align);

// Sets the proportional line height of current text style. The line height is specified as multiple of font size.
void nvgcpp_TextLineHeight(NVGcontext* ctx, float lineHeight);


// Returns the dimensions of a created image.
std::tuple<int, int> nvgcpp_ImageSize(NVGcontext* ctx, int image);
