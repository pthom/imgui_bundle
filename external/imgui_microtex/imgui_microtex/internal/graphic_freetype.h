#pragma once

#include <ft2build.h>
#include FT_FREETYPE_H
#include FT_GLYPH_H

#include <cstdint>
#include <cstring>
#include <map>
#include <string>
#include <vector>

#include "graphic/graphic.h"

namespace ImGuiMicroTeX { namespace Internal {

// Simple RGBA pixel buffer
struct PixelBuffer {
  int width = 0;
  int height = 0;
  std::vector<uint8_t> pixels;  // RGBA

  PixelBuffer() = default;
  PixelBuffer(int w, int h) : width(w), height(h), pixels(w * h * 4, 0) {}

  void setPixel(int x, int y, uint8_t r, uint8_t g, uint8_t b, uint8_t a) {
    if (x < 0 || x >= width || y < 0 || y >= height) return;
    int idx = (y * width + x) * 4;
    if (a == 255) {
      pixels[idx + 0] = r;
      pixels[idx + 1] = g;
      pixels[idx + 2] = b;
      pixels[idx + 3] = 255;
      return;
    }
    // Alpha-blend
    float srcA = a / 255.f;
    float dstA = pixels[idx + 3] / 255.f;
    float outA = srcA + dstA * (1.f - srcA);
    if (outA > 0.f) {
      pixels[idx + 0] = (uint8_t)((r * srcA + pixels[idx + 0] * dstA * (1.f - srcA)) / outA);
      pixels[idx + 1] = (uint8_t)((g * srcA + pixels[idx + 1] * dstA * (1.f - srcA)) / outA);
      pixels[idx + 2] = (uint8_t)((b * srcA + pixels[idx + 2] * dstA * (1.f - srcA)) / outA);
      pixels[idx + 3] = (uint8_t)(outA * 255.f);
    }
  }
};

}}  // namespace ImGuiMicroTeX::Internal

// MicroTeX interface implementations must be in namespace microtex
// (they implement microtex::Font, microtex::TextLayout, etc.)
namespace microtex {

// FreeType font wrapper
class Font_freetype : public Font {
private:
  static FT_Library _ftLib;
  static std::map<std::string, FT_Face> _faces;

  FT_Face _face = nullptr;
  std::string _file;

public:
  static void initFreeType();
  static void releaseFreeType();

  explicit Font_freetype(const std::string& file);
  ~Font_freetype() override = default;

  FT_Face getFace() const { return _face; }
  bool operator==(const Font& f) const override;
};

// TextLayout using FreeType for measurement
class TextLayout_freetype : public TextLayout {
private:
  std::string _text;
  FontStyle _style;
  float _size;

public:
  TextLayout_freetype(const std::string& src, FontStyle style, float size);
  void getBounds(Rect& bounds) override;
  void draw(Graphics2D& g2, float x, float y) override;
};

// PlatformFactory
class PlatformFactory_freetype : public PlatformFactory {
public:
  sptr<Font> createFont(const std::string& file) override;
  sptr<TextLayout> createTextLayout(const std::string& src, FontStyle style, float size) override;
};

// Graphics2D rendering to a PixelBuffer
class Graphics2D_freetype : public Graphics2D {
private:
  ImGuiMicroTeX::Internal::PixelBuffer& _buf;
  color _color = black;
  Stroke _stroke;
  sptr<Font_freetype> _font;
  float _fontSize = 20.f;
  float _sx = 1.f, _sy = 1.f;
  float _tx = 0.f, _ty = 0.f;
  std::vector<float> _dash;

  // Path state
  float _pathStartX = 0, _pathStartY = 0;
  float _pathCurX = 0, _pathCurY = 0;

  // Transform point
  void transformPoint(float x, float y, float& ox, float& oy) const {
    ox = x * _sx + _tx;
    oy = y * _sy + _ty;
  }

  void drawLineImpl(float x1, float y1, float x2, float y2, float width);
  void fillRectImpl(float x, float y, float w, float h);

public:
  explicit Graphics2D_freetype(ImGuiMicroTeX::Internal::PixelBuffer& buf) : _buf(buf) {}

  void setColor(color c) override { _color = c; }
  color getColor() const override { return _color; }
  void setStroke(const Stroke& s) override { _stroke = s; }
  const Stroke& getStroke() const override { return _stroke; }
  void setStrokeWidth(float w) override { _stroke.lineWidth = w; }
  void setDash(const std::vector<float>& dash) override { _dash = dash; }
  std::vector<float> getDash() override { return _dash; }
  sptr<Font> getFont() const override { return _font; }
  void setFont(const sptr<Font>& font) override { _font = std::static_pointer_cast<Font_freetype>(font); }
  float getFontSize() const override { return _fontSize; }
  void setFontSize(float size) override { _fontSize = size; }

  void translate(float dx, float dy) override { _tx += dx * _sx; _ty += dy * _sy; }
  void scale(float sx, float sy) override { _sx *= sx; _sy *= sy; }
  void rotate(float angle) override { /* TODO if needed */ }
  void rotate(float angle, float px, float py) override { /* TODO if needed */ }
  void reset() override { _sx = _sy = 1.f; _tx = _ty = 0.f; }
  float sx() const override { return _sx; }
  float sy() const override { return _sy; }

  void drawGlyph(u16 glyph, float x, float y) override;

  // Path commands (stub for GLYPH_RENDER_TYPE=2)
  bool beginPath(i32 id) override { return false; }
  void moveTo(float x, float y) override;
  void lineTo(float x, float y) override;
  void cubicTo(float x1, float y1, float x2, float y2, float x3, float y3) override;
  void quadTo(float x1, float y1, float x2, float y2) override;
  void closePath() override;
  void fillPath(i32 id) override;

  void drawLine(float x1, float y1, float x2, float y2) override;
  void drawRect(float x, float y, float w, float h) override;
  void fillRect(float x, float y, float w, float h) override;
  void drawRoundRect(float x, float y, float w, float h, float rx, float ry) override;
  void fillRoundRect(float x, float y, float w, float h, float rx, float ry) override;
};

}  // namespace microtex
