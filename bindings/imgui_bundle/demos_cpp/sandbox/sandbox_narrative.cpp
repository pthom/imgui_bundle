// Narrative programming: this source file is its own narrative. The app renders the "Intro" section below,
// which transcludes the other sections of this file in the order it likes (see RichMd::ResolveTransclusions).
// Desktop only: RICHMD_RENDER_THIS_FILE reads the file at runtime (__FILE__).
#include "hello_imgui/hello_imgui.h"
#include "immapp/immapp.h"
#include "imgui_rich_md/rich_md.h"
#include "imgui.h"
#include <cmath>

/*::md Intro
# Narrative programming
This window renders **this very source file**: its sections are markdown, and their code is shown as code.
The narrative (the `Intro` section) chooses the order: the drawing first.
![[#Drawing]]
![[#Drawing#code]]
The radius comes from a slider, and the area from a one-liner:
![[#Area#code]]
## When a transclusion fails
The embed stays visible, in the error color, with the reason as a tooltip:
![[nope.cpp#Intro]]
![[#NoSuchSection]]
*/

// ::md Area
// A circle of radius $r$ has area $\pi r^2$.
// ::code
static float Area(float r) { return 3.14159265f * r * r; }
// ::endcode

/*::md Drawing
The circle is drawn with the window's draw list, centered on the cursor.
::code
*/
static void DrawCircle(float radius)
{
    ImVec2 p = ImGui::GetCursorScreenPos();
    float em = ImGui::GetFontSize();
    ImGui::GetWindowDrawList()->AddCircle(ImVec2(p.x + 6 * em, p.y + 4 * em), radius * em, IM_COL32(255, 180, 60, 255), 0, 2.0f);
    ImGui::Dummy(ImVec2(12 * em, 8 * em));
}
// ::endcode

static void Gui()
{
    static float radius = 2.5f;
    ImGui::SliderFloat("radius (em)", &radius, 0.5f, 3.5f);
    ImGui::Text("area: %.1f em2", Area(radius));
    DrawCircle(radius);
    ImGui::Separator();
    RICHMD_RENDER_THIS_FILE("Intro");
}

int main(int, char**)
{
    ImmApp::AddOnsParams addons;
    addons.withMarkdown = true;
    addons.withLatex = true;
    HelloImGui::RunnerParams params;
    params.appWindowParams.windowGeometry.size = {900, 1000};
    params.callbacks.ShowGui = Gui;
    ImmApp::Run(params, addons);
}
