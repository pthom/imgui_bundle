#include "graphic_freetype.h"
#include "utils/utf.h"

#include <algorithm>
#include <cmath>
#include <cstdio>

using namespace microtex;
using namespace std;

// ---------- Font_freetype ----------

FT_Library Font_freetype::_ftLib = nullptr;
map<string, FT_Face> Font_freetype::_faces;

void Font_freetype::initFreeType() {
  if (!_ftLib) {
    FT_Init_FreeType(&_ftLib);
  }
}

void Font_freetype::releaseFreeType() {
  for (auto& [k, face] : _faces) {
    FT_Done_Face(face);
  }
  _faces.clear();
  if (_ftLib) {
    FT_Done_FreeType(_ftLib);
    _ftLib = nullptr;
  }
}

Font_freetype::Font_freetype(const string& file) : _file(file) {
  auto it = _faces.find(file);
  if (it != _faces.end()) {
    _face = it->second;
    return;
  }
  FT_Error err = FT_New_Face(_ftLib, file.c_str(), 0, &_face);
  if (err) {
    fprintf(stderr, "FreeType: failed to load font '%s' (error %d)\n", file.c_str(), err);
    _face = nullptr;
    return;
  }
  _faces[file] = _face;
}

bool Font_freetype::operator==(const Font& f) const {
  const auto& other = static_cast<const Font_freetype&>(f);
  return _face == other._face;
}

// ---------- TextLayout_freetype ----------

TextLayout_freetype::TextLayout_freetype(const string& src, FontStyle style, float size)
    : _text(src), _style(style), _size(size) {}

void TextLayout_freetype::getBounds(Rect& bounds) {
  // Simple approximation: use font metrics
  bounds.x = 0;
  bounds.y = -_size * 0.8f;  // rough ascent
  bounds.w = _size * 0.5f * _text.size();  // rough width
  bounds.h = _size;
}

void TextLayout_freetype::draw(Graphics2D& g2, float x, float y) {
  // TextLayout is for non-math text that MicroTeX can't render itself.
  // For the PoC we just skip it.
}

// ---------- PlatformFactory_freetype ----------

sptr<Font> PlatformFactory_freetype::createFont(const string& file) {
  return std::make_shared<Font_freetype>(file);
}

sptr<TextLayout>
PlatformFactory_freetype::createTextLayout(const string& src, FontStyle style, float size) {
  return std::make_shared<TextLayout_freetype>(src, style, size);
}

// ---------- Graphics2D_freetype drawing helpers ----------

void Graphics2D_freetype::drawLineImpl(float x1, float y1, float x2, float y2, float width) {
  float ox1, oy1, ox2, oy2;
  transformPoint(x1, y1, ox1, oy1);
  transformPoint(x2, y2, ox2, oy2);

  // Bresenham-ish with width
  float dx = ox2 - ox1;
  float dy = oy2 - oy1;
  float len = sqrtf(dx * dx + dy * dy);
  if (len < 0.001f) return;

  float halfW = max(width * _sx * 0.5f, 0.5f);
  // Normal vector
  float nx = -dy / len * halfW;
  float ny = dx / len * halfW;

  uint8_t r = color_r(_color);
  uint8_t g = color_g(_color);
  uint8_t b = color_b(_color);
  uint8_t a = color_a(_color);

  // Fill the line as a thin quad
  int steps = (int)(len + 1);
  for (int i = 0; i <= steps; i++) {
    float t = (float)i / (float)steps;
    float cx = ox1 + dx * t;
    float cy = oy1 + dy * t;
    int wSteps = (int)(halfW + 1);
    for (int w = -wSteps; w <= wSteps; w++) {
      float wt = (float)w / (float)wSteps;
      int px = (int)(cx + nx * wt);
      int py = (int)(cy + ny * wt);
      _buf.setPixel(px, py, r, g, b, a);
    }
  }
}

void Graphics2D_freetype::fillRectImpl(float x, float y, float w, float h) {
  float ox, oy;
  transformPoint(x, y, ox, oy);
  float sw = w * _sx;
  float sh = h * _sy;

  uint8_t r = color_r(_color);
  uint8_t g = color_g(_color);
  uint8_t b = color_b(_color);
  uint8_t a = color_a(_color);

  int x0 = max(0, (int)ox);
  int y0 = max(0, (int)oy);
  int x1 = min(_buf.width, (int)(ox + sw + 1));
  int y1 = min(_buf.height, (int)(oy + sh + 1));

  for (int py = y0; py < y1; py++) {
    for (int px = x0; px < x1; px++) {
      _buf.setPixel(px, py, r, g, b, a);
    }
  }
}

// ---------- Graphics2D_freetype main methods ----------

void Graphics2D_freetype::drawGlyph(u16 glyph, float x, float y) {
  if (!_font || !_font->getFace()) return;

  FT_Face face = _font->getFace();
  FT_Set_Pixel_Sizes(face, 0, (FT_UInt)(_fontSize * _sy));

  FT_Error err = FT_Load_Glyph(face, glyph, FT_LOAD_RENDER);
  if (err) return;

  FT_GlyphSlot slot = face->glyph;
  FT_Bitmap& bmp = slot->bitmap;

  float ox, oy;
  transformPoint(x, y, ox, oy);

  int bx = (int)(ox + slot->bitmap_left);
  int by = (int)(oy - slot->bitmap_top);

  uint8_t r = color_r(_color);
  uint8_t g = color_g(_color);
  uint8_t b = color_b(_color);

  for (unsigned int row = 0; row < bmp.rows; row++) {
    for (unsigned int col = 0; col < bmp.width; col++) {
      uint8_t alpha = bmp.buffer[row * bmp.pitch + col];
      if (alpha > 0) {
        _buf.setPixel(bx + col, by + row, r, g, b, alpha);
      }
    }
  }
}

void Graphics2D_freetype::drawLine(float x1, float y1, float x2, float y2) {
  drawLineImpl(x1, y1, x2, y2, _stroke.lineWidth);
}

void Graphics2D_freetype::drawRect(float x, float y, float w, float h) {
  drawLine(x, y, x + w, y);
  drawLine(x + w, y, x + w, y + h);
  drawLine(x + w, y + h, x, y + h);
  drawLine(x, y + h, x, y);
}

void Graphics2D_freetype::fillRect(float x, float y, float w, float h) {
  fillRectImpl(x, y, w, h);
}

void Graphics2D_freetype::drawRoundRect(float x, float y, float w, float h, float rx, float ry) {
  // Simplified: just draw a regular rect for the PoC
  drawRect(x, y, w, h);
}

void Graphics2D_freetype::fillRoundRect(float x, float y, float w, float h, float rx, float ry) {
  // Simplified: just fill a regular rect for the PoC
  fillRect(x, y, w, h);
}

// Path commands - minimal stubs for GLYPH_RENDER_TYPE=2 (typeface mode)
// We still need to provide them since the interface requires it,
// but they won't be called for glyph rendering in typeface mode.
// They may still be called for other decorations though.

void Graphics2D_freetype::moveTo(float x, float y) {
  _pathCurX = x;
  _pathCurY = y;
  _pathStartX = x;
  _pathStartY = y;
}

void Graphics2D_freetype::lineTo(float x, float y) {
  drawLineImpl(_pathCurX, _pathCurY, x, y, _stroke.lineWidth);
  _pathCurX = x;
  _pathCurY = y;
}

void Graphics2D_freetype::cubicTo(float x1, float y1, float x2, float y2, float x3, float y3) {
  // Flatten cubic bezier into line segments
  const int N = 16;
  float px = _pathCurX, py = _pathCurY;
  for (int i = 1; i <= N; i++) {
    float t = (float)i / N;
    float u = 1.f - t;
    float x = u*u*u*px + 3*u*u*t*x1 + 3*u*t*t*x2 + t*t*t*x3;
    float y = u*u*u*py + 3*u*u*t*y1 + 3*u*t*t*y2 + t*t*t*y3;
    drawLineImpl(px, py, x, y, _stroke.lineWidth > 0 ? _stroke.lineWidth : 1.f);
    px = x;
    py = y;
  }
  _pathCurX = x3;
  _pathCurY = y3;
}

void Graphics2D_freetype::quadTo(float x1, float y1, float x2, float y2) {
  // Elevate to cubic
  float cx1 = _pathCurX + 2.f/3.f * (x1 - _pathCurX);
  float cy1 = _pathCurY + 2.f/3.f * (y1 - _pathCurY);
  float cx2 = x2 + 2.f/3.f * (x1 - x2);
  float cy2 = y2 + 2.f/3.f * (y1 - y2);
  cubicTo(cx1, cy1, cx2, cy2, x2, y2);
}

void Graphics2D_freetype::closePath() {
  drawLineImpl(_pathCurX, _pathCurY, _pathStartX, _pathStartY, _stroke.lineWidth);
  _pathCurX = _pathStartX;
  _pathCurY = _pathStartY;
}

void Graphics2D_freetype::fillPath(i32 id) {
  // For a proper fill we'd need scanline rasterization.
  // In typeface mode (GLYPH_RENDER_TYPE=2), path fill is only used
  // for decorative elements, not glyphs. Leave as no-op for PoC.
}
