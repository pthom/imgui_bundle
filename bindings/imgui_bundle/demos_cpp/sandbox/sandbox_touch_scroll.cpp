// A bench for the swipe (HelloImGui::RunnerParams::touchScrollMode) with a RichMd zone: a markdown page (whose text
// selects on a drag), widgets, a child window. For a desktop without a touch screen, a checkbox makes ImGui believe
// the mouse is a finger (ImGui's touch tooltips and press trickling apply too): then a tap clicks, a drag scrolls,
// and a short hold then a drag goes to the widget (the slider, a text selection).
#include "hello_imgui/hello_imgui.h"
#include "imgui.h"
#include "immapp/immapp.h"
#include "imgui_rich_md/rich_md.h"

#include <cstdio>

static const char* kMarkdown = R"(
# A markdown page on a phone

A swipe on this text should scroll the page, as in a browser. A short hold, then a drag, should select text.
With a mouse (no simulated touch), a press on a line starts a selection at once, as before.

## What to try

- a swipe that starts on this list,
- a tap on [this link](https://github.com/pthom/imgui_bundle), and a swipe that starts on it,
- a hold then a drag over a few words, then Copy from the menu of a right click,
- a tap away from the text, which clears the selection.

## Some more lines, so that the page scrolls

Dear ImGui Bundle is a collection of libraries for Dear ImGui, with Python bindings. Its explorer and its playground
run in the browser, where a phone is a common screen. The text here is only filler: each paragraph is a place to
start a swipe.

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna
aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint
occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

```cpp
// A code block: a swipe here should scroll the page too
int main() { return 0; }
```

Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam,
eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.

Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos
qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet.

The end of the page.
)";

int main()
{
    HelloImGui::RunnerParams params;
    params.appWindowParams.windowTitle = "Touch scroll + RichMd";
    params.appWindowParams.windowGeometry.size = {450, 800};

    bool simulateTouch = false;
    int nbClicks = 0;
    float slider = 0.5f;
    params.callbacks.ShowGui = [&]()
    {
        ImGuiIO& io = ImGui::GetIO();
        // The source applies to the events queued after this call, i.e. the next frame's (a desktop backend sets no
        // source, except on Windows: there, this overrides it)
        io.AddMouseSourceEvent(simulateTouch ? ImGuiMouseSource_TouchScreen : ImGuiMouseSource_Mouse);

        ImGui::Checkbox("Simulate a touch source", &simulateTouch);
        const char* sourceNames[] = {"Mouse", "TouchScreen", "Pen"};
        ImGui::Text("io.MouseSource: %s", sourceNames[io.MouseSource]);
        int mode = (int)params.touchScrollMode;
        ImGui::Combo("touchScrollMode", &mode, "Auto\0Always\0Disabled\0");
        params.touchScrollMode = (HelloImGui::TouchScrollMode)mode;
        ImGui::Separator();
        ImGui::Text("Clicks: %d   Slider: %.2f", nbClicks, slider);
        static char text[64] = "";
        ImGui::InputText("Text (the keyboard of a phone)", text, sizeof(text));
        if (ImGui::Button("Click me"))
            ++nbClicks;
        ImGui::SameLine();
        ImGui::SliderFloat("##slider", &slider, 0.f, 1.f);
        ImGui::Separator();

        RichMd::Render(kMarkdown);

        ImGui::Separator();
        ImGui::TextUnformatted("A child window:");
        ImGui::BeginChild("child", HelloImGui::EmToVec2(0.f, 9.f), ImGuiChildFlags_Borders);
        for (int j = 0; j < 30; ++j)
            ImGui::Text("Child line %2d: a swipe scrolls the child", j);
        ImGui::EndChild();
        for (int i = 0; i < 30; ++i)
            ImGui::Text("Line %2d after the child", i);
    };

    ImmApp::AddOnsParams addOns;
    addOns.withMarkdown = true;
    ImmApp::Run(params, addOns);
    return 0;
}
