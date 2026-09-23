// Invalid LaTeX must not kill the application: a formula MicroTeX rejects falls back to its source text.
// The formulas appear one after the other (one every 4 seconds), so that the culprit is visible if one still does.
// On Emscripten this needs IMGUI_RICHMD_WASM_EXCEPTIONS (ON by default): without it, the first throw aborts the page.
#include "immapp/immapp.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "imgui.h"

int main(int, char**)
{
    ImmApp::AddOnsParams addons;
    addons.withMarkdown = true;
    addons.withLatex = true;
    HelloImGui::RunnerParams params;
    params.callbacks.ShowGui = [] {
        ImGuiMd::Render("Valid: $\\sqrt{2} + \\frac{1}{2}$\n");
        double t = ImGui::GetTime();
        if (t > 4.0)  ImGuiMd::Render("Unknown command: $\\unknowncmd{x}$\n");
        if (t > 8.0)  ImGuiMd::Render("Missing brace: $\\frac{1}{2$\n");
        if (t > 12.0) ImGuiMd::Render("Extra brace (MicroTeX throws): $x} + 1$\n");
        if (t > 16.0) ImGuiMd::Render("Left without right: $\\left( x$\n");
        if (t > 20.0) ImGuiMd::Render("Environment not closed: $\\begin{pmatrix} a & b$\n");
    };
    ImmApp::Run(params, addons);
}
