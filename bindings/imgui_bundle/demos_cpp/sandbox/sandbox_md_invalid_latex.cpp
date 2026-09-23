// Invalid LaTeX must not kill the application: a formula MicroTeX rejects falls back to its source text.
// On Emscripten this needs IMGUI_RICHMD_WASM_EXCEPTIONS (ON by default): without it, the first throw aborts the page.
#include "immapp/immapp.h"
#include "imgui_rich_md/rich_md.h"

int main(int, char**)
{
    ImmApp::AddOnsParams addons;
    addons.withMarkdown = true;
    addons.withLatex = true;
    HelloImGui::RunnerParams params;
    params.callbacks.ShowGui = [] {
        RichMd::Render(R"(
Valid: $\sqrt{2} + \frac{1}{2}$

Unknown command: $\unknowncmd{x}$

Missing brace: $\frac{1}{2$

Extra brace (MicroTeX throws): $x} + 1$

Left without right: $\left( x$

Environment not closed: $\begin{pmatrix} a & b$
)");
    };
    ImmApp::Run(params, addons);
}
