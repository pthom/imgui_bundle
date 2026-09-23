#pragma once

#include "imgui.h"
#include <functional>

#include <cstdint>
#include <string>
#include <vector>

// Public API for imgui_microtex: native LaTeX math rendering via MicroTeX + FreeType.
//
// Level 1: render LaTeX to an RGBA pixel buffer.
// (Level 2, cached GPU textures, lives with the host: imgui_bundle keeps it in imgui_microtex/imgui_microtex.h.)
//
// Thread safety: all functions are protected by a mutex and can be called from any thread.

namespace RichMd::Latex {

// ============================================================================
// TeX style
// ============================================================================
//
// Selects the layout style used when rendering a formula. This maps directly
// to MicroTeX's TexStyle and corresponds to the four TeX styles defined by
// Knuth (D, T, S, SS). Pick Display for centered "display math" ($$...$$)
// and Text for inline math ($...$).
//
// The style affects symbol size, big-operator appearance, and the spacing
// around \frac (numerator shift-up and denominator shift-down): Display gives
// generous spacing; Text is compact.
enum class TexStyle {
    // Largest size. Big operators (\sum, \int, ...) use their large variants
    // with limits placed above and below. \frac uses generous vertical
    // spacing. This is what LaTeX uses inside $$...$$ and \[...\].
    Display,
    // Default inline size. Big operators use their small variants with
    // limits attached as sub/superscripts. \frac uses compact spacing.
    // This is what LaTeX uses inside $...$ and \(...\).
    Text,
    // Smaller size used by LaTeX inside sub/superscripts. Rarely useful at
    // the top level; MicroTeX switches to it automatically where needed.
    Script,
    // Smallest size, used inside scripts-of-scripts. Same caveat as Script.
    ScriptScript,
};

// ============================================================================
// Initialization / shutdown
// ============================================================================

// Initialize MicroTeX + FreeType backend.
// clmFile: path to the .clm1 font metrics file
// fontFile: path to the .otf font file
// Safe to call repeatedly: subsequent calls after the first successful
// Init() no-op (MicroTeX itself stays initialized for process life; the
// underlying MicroTeX::init()/release() pair is not re-entrant, so we
// defer the real teardown to std::atexit: see imgui_microtex.cpp).
void Init(const std::string& clmFile, const std::string& fontFile);
// Same, with the two files read in memory (.clm1 and .otf). C++ only.
void InitFromMemory(const std::vector<uint8_t>& clmData, const std::vector<uint8_t>& fontData);

// Check if initialized.
bool IsInitialized();

// Drop the cached GPU texture set so the GL context can be torn down
// cleanly. Call from BeforeExit (or any point where the GL context is
// about to die). Safe to call multiple times, and safe to call Init()
// again afterwards: the underlying MicroTeX library stays alive for
// the whole process and its real teardown runs once at exit via a
// std::atexit handler installed on first Init().
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
// style: TeX layout style (Display for $$...$$, Text for $...$)
RenderedFormula Render(const std::string& latex, float fontSize, ImU32 color = IM_COL32_BLACK, TexStyle style = TexStyle::Text);
RenderedFormula Render(const std::string& latex, float fontSize, const ImVec4& color, TexStyle style = TexStyle::Text);

// Registers a callback run by Release(): a host that caches GPU textures made from formulas clears
// them here, while the rendering backend is still alive.
void AddReleaseCallback(std::function<void()> callback);

}  // namespace RichMd::Latex
