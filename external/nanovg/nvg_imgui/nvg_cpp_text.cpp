#include "nvg_cpp_text.h"
#include "nanovg.h"


float nvgcpp_Text(NVGcontext* ctx, float x, float y, const std::string& text)
{
    return nvgText(ctx, x, y, text.c_str(), nullptr);
}

void nvgcpp_TextBox(NVGcontext* ctx, float x, float y, float breakRowWidth, const std::string& text)
{
    nvgTextBox(ctx, x, y, breakRowWidth, text.c_str(), nullptr);
}

std::tuple<Bounds, float> nvgcpp_TextBounds(NVGcontext* ctx, float x, float y, const std::string& text)
{
    Bounds bounds;
    float advance = nvgTextBounds(ctx, x, y, text.c_str(), nullptr, bounds.data());
    return std::make_tuple(bounds, advance);
}

Bounds nvgcpp_TextBoxBounds(NVGcontext* ctx, float x, float y, float breakRowWidth, const std::string& text)
{
    Bounds bounds;
    nvgTextBoxBounds(ctx, x, y, breakRowWidth, text.c_str(), nullptr, bounds.data());
    return bounds;
}


std::vector<NVGglyphPosition> nvgcpp_TextGlyphPositions(NVGcontext* ctx, float x, float y, const std::string& text)
{
    std::vector<NVGglyphPosition> positions(text.size());
    nvgTextGlyphPositions(ctx, x, y, text.c_str(), nullptr, positions.data(), (int)positions.size());
    return positions;
}

TextMetricsData nvgcpp_TextMetrics(NVGcontext* ctx)
{
    TextMetricsData data;
    nvgTextMetrics(ctx, &data.ascender, &data.descender, &data.lineh);
    return data;
}

void nvgcpp_TextLineHeight(NVGcontext* ctx, float lineHeight)
{
    nvgTextLineHeight(ctx, lineHeight);
}


std::vector<NVGtextRowSimple> nvgcpp_TextBreakLines(NVGcontext* ctx, const std::string& text, float breakRowWidth)
{
    constexpr int maxRows = 1000;
    NVGtextRow rows[maxRows];
    int nbRows = nvgTextBreakLines(ctx, text.c_str(), nullptr, breakRowWidth, rows, maxRows);
    std::vector<NVGtextRowSimple> rowsVector;
    rowsVector.reserve(nbRows);
    for (int i = 0; i < nbRows; ++i)
    {
        NVGtextRowSimple row;
        row.width = rows[i].width;
        row.minx = rows[i].minx;
        row.maxx = rows[i].maxx;
        row.row_text = std::string(rows[i].start, rows[i].end);
        rowsVector.push_back(row);
    }
    return rowsVector;
}

void nvgcpp_TextAlign(NVGcontext* ctx, int align)
{
    nvgTextAlign(ctx, align);
}


std::tuple<int, int> nvgcpp_ImageSize(NVGcontext* ctx, int image)
{
    int w, h;
    nvgImageSize(ctx, image, &w, &h);
    return std::make_tuple(w, h);
}
