// Phase 3 sandbox: native LaTeX math in markdown via MicroTeX (C++ version).
//
// C++ mirror of sandbox_phase3_latex.py, used to debug the garbled-texture
// issue independently from the Python bindings.
//
// Run (from a build with IMGUI_BUNDLE_WITH_MICROTEX=ON):
//     ./sandbox_md_math
//     ./sandbox_md_math --no-latex  (legacy: $ is a literal character)

#include "hello_imgui/hello_imgui.h"
#include "imgui.h"
#include "immapp/immapp.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"

#ifdef IMGUI_RICHMD_WITH_LATEX
#include "imgui_microtex/imgui_microtex.h"
#endif

#include <cstdio>
#include <cstring>
#include <string>

static const char* kMarkdown = R"(
# Phase 3: native LaTeX in markdown (C++)

This markdown is rendered by **imgui_md**.
Inline math like $E = mc^2$ should sit on the baseline of this text,
as should $\sqrt{a^2 + b^2}$ and $\sum_{i=0}^{n} i$.

## Display math

A quadratic formula:

$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

Gaussian integral:

$$\int_{-\infty}^{\infty} e^{-x^2}\, dx = \sqrt{\pi}$$

Matrix:

$$A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}$$

## Mixed content

The Euler identity $e^{i\pi} + 1 = 0$ is sometimes called the most beautiful
equation in mathematics. Compare with the series expansion

$$e^x = \sum_{k=0}^{\infty} \frac{x^k}{k!}$$

and note how the sum in display mode looks bigger than the inline
$\sum_{k=0}^{\infty} \frac{x^k}{k!}$ version.

## Price list (stress-test $ as literal)

When LaTeX is off, the $ signs below should appear as literal dollar
characters. When LaTeX is on, md4c parses them as math delimiters.

- Apples: $1.50
- Oranges: $2.00
- Total: $3.50
)";

static void Gui()
{
#ifdef IMGUI_RICHMD_WITH_LATEX
    // One-shot debug probe: render a simple formula directly and report
    // the texture id + size, bypassing the markdown path entirely.
    static bool sProbed = false;
    if (!sProbed && ImGuiMicroTeX::IsInitialized())
    {
        auto tex = ImGuiMicroTeX::RenderToTexture(
            "E = mc^2", ImGui::GetFontSize(), IM_COL32(255, 255, 255, 255));
        std::printf(
            "[sandbox_md_math] direct RenderToTexture probe: "
            "tex_id=%p  width=%d  height=%d  baseline=%.3f\n",
            (void*)(uintptr_t)tex.TextureId, tex.Width, tex.Height, tex.Baseline);
        std::fflush(stdout);
        sProbed = true;
    }
#endif

    ImGui::Text("Phase 3 sandbox (C++) - close window to exit");
    ImGui::Separator();
    ImGuiMd::RenderUnindented(kMarkdown);
}

int main(int argc, char** argv)
{
    bool withLatex = true;
    for (int i = 1; i < argc; ++i)
    {
        if (std::strcmp(argv[i], "--no-latex") == 0)
            withLatex = false;
    }

    std::printf(
        "[sandbox_md_math] starting with with_latex=%s\n",
        withLatex ? "true" : "false");
    std::fflush(stdout);

    HelloImGui::SimpleRunnerParams simple;
    simple.guiFunction = Gui;
    simple.windowTitle = withLatex
        ? "Phase 3 LaTeX sandbox (LaTeX ON, C++)"
        : "Phase 3 LaTeX sandbox (LaTeX OFF, C++)";
    simple.windowSize = {900, 900};

    ImmApp::AddOnsParams addOns;
    addOns.withMarkdown = true;
    addOns.withLatex = withLatex;

    ImmApp::Run(simple, addOns);
    return 0;
}
