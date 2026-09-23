// Sections and imports: this source file is its own narrative. The app renders the "Intro" block below,
// which imports the other blocks of this file in the order it likes (see ImGuiMd::ResolveImports).
// Desktop only: the file is read at runtime from its own folder (added to the assets search paths).
#include "hello_imgui/hello_imgui.h"
#include "immapp/immapp.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "imgui.h"
#include <cmath>
#include <string>

// @@md#Intro
// # Sections and imports
// This window renders **this very source file**: its comment blocks are markdown, the code that follows
// each block is shown as code. The narrative (the `Intro` block) chooses the order: the drawing first.
// @import {md_id=Drawing}
// The radius comes from a slider, and the area from a one-liner:
// @import {md_id=Area, part=code}
// ## When an import fails
// The directive stays visible, in the error color, with the reason as a tooltip:
// @import "nope.cpp" {md_id=Intro}
// @import {md_id=NoSuchBlock}
// @@/md

// @@md#Area
// A circle of radius $r$ has area $\pi r^2$.
// @@/md
static float Area(float r) { return 3.14159265f * r * r; }

// @@md#Drawing
// The circle is drawn with the window's draw list, centered on the cursor.
// @@/md
static void DrawCircle(float radius)
{
    ImVec2 p = ImGui::GetCursorScreenPos();
    float em = ImGui::GetFontSize();
    ImGui::GetWindowDrawList()->AddCircle(ImVec2(p.x + 6 * em, p.y + 4 * em), radius * em, IM_COL32(255, 180, 60, 255), 0, 2.0f);
    ImGui::Dummy(ImVec2(12 * em, 8 * em));
}

static void Gui()
{
    static float radius = 2.5f;
    ImGui::SliderFloat("radius (em)", &radius, 0.5f, 3.5f);
    ImGui::Text("area: %.1f em2", Area(radius));
    DrawCircle(radius);
    ImGui::Separator();
    ImGuiMd::Render(R"(@import "sandbox_md_imports.cpp" {md_id=Intro})");
}

int main(int, char**)
{
    std::string thisFile = __FILE__;
    HelloImGui::AddAssetsSearchPath(thisFile.substr(0, thisFile.find_last_of("/\\")));
    ImmApp::AddOnsParams addons;
    addons.withMarkdown = true;
    addons.withLatex = true;
    HelloImGui::RunnerParams params;
    params.appWindowParams.windowGeometry.size = {900, 1000};
    params.callbacks.ShowGui = Gui;
    ImmApp::Run(params, addons);
}
