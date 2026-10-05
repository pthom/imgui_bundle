// On a touch screen: the gestures of a phone, in the browser (the twin of demos_python/demos_immapp/demo_touch_screen.py)
//
// On a mobile or a tablet, Hello ImGui turns a finger into what its user expects: a swipe scrolls, a tap clicks, a held
// finger opens a context menu, a pinch scales the app (its font), two fingers pan, and a keyboard button appears next
// to a text field. Nothing to write in the app: the gestures come from RunnerParams::touchScrollMode, touchPinchMode
// and touchLongPressIsRightClick. On a desktop, tick "Simulate a touch source" to try them with the mouse.
#ifdef IMGUI_BUNDLE_WITH_IMPLOT
#define IMGUI_DEFINE_MATH_OPERATORS
#include "immapp/immapp.h"
#include "imgui_rich_md/rich_md.h"
#include "implot/implot.h"
#include "demo_utils/api_demos.h"
#include "hello_imgui/hello_imgui.h"
#include "imgui.h"
#include "imgui_stdlib.h"
#ifdef IMGUI_BUNDLE_WITH_IMMVISION
#include "immvision/immvision.h"
#endif
#include <algorithm>
#include <random>
#include <string>
#include <vector>


namespace
{
const char* GESTURES = R"(
- **Swipe** anywhere, on this text or on the button below: the content scrolls, with inertia, and a bounce at the end.
- **Tap** a button: a click. **Hold** a slider a moment, then drag it.
- **Hold** a word of this text half a second: the menu of a right click (Copy, Select All). Hold the button: its menu.
- **Pinch** with two fingers: the app (its font) scales.
- **Drag with two fingers**: a right drag, which box-selects in the plot.
- **Tap a text field**, then the keyboard button that appears under it: type, move the caret from the keyboard's space bar.

> [!NOTE]
> * Those gestures are only available when running an application with hello_imgui or immapp. They are not available when using your own backend / loop.
> * They are enabled by default. You do not need to change anything to get them.
> * Configure them with `RunnerParams::touchScrollMode`, `touchPinchMode` and `touchLongPressIsRightClick`.
)";

const char* PLOTS = R"(
- **Box select**: a right drag on a desktop, a **two-finger drag** on a touch screen.
- **Pan**: a left drag on a desktop. With a finger, **hold** a moment, then drag (a swipe scrolls the page).
- The guide lines and the box of the second plot: drag them the same way.
- A double click (a double tap) fits the plot.
)";

const char* IMAGES = R"(
- **The first image** resizes by its bottom right corner: hold the corner, then drag.
- **The second one** pans by a drag (hold, then drag), and zooms with the mouse wheel or its + / - buttons.
- A pinch scales the app, not the image.
)";

const std::vector<std::string> BUTTON_NAMES = {"Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"};
constexpr float PHONE_WIDTH_EM = 26.f;  // on a desktop, the page shows in a column of this width: the layout of a phone

// The state of the widgets
bool simulateTouch = false;
int clicks = 0;
std::string menuChoice;
float slider = 0.5f;
std::string text = "abc def ghi";
std::string lines = "one\ntwo\nthree";
std::vector<int> buttonClicks(BUTTON_NAMES.size(), 0);
std::vector<double> pointsX, pointsY;  // 40 random points, drawn once
double guideX = 0.5, guideY = 0.5;  // the draggable lines of the second plot
double box[4] = {0.2, 0.2, 0.6, 0.7};  // its draggable rectangle: x1, y1, x2, y2
#ifdef IMGUI_BUNDLE_WITH_IMMVISION
ImmVision::ImageBuffer tennis, bear;  // loaded at the first frame
ImmVision::ImageParams bearParams;
ImVec2 tennisSize(0.f, 0.f);  // the size of the resizable image, chosen by the user (set at the first frame)
#endif

// A section title, with some air above it
void Section(const char* title)
{
    ImGui::Dummy(HelloImGui::EmToVec2(0.f, 1.f));
    RichMd::Render(std::string("## ") + title);
}

// The labels at the left of the widgets
void Label(const char* name)
{
    ImGui::AlignTextToFramePadding();
    ImGui::TextUnformatted(name);
    ImGui::SameLine(HelloImGui::EmSize(7.f));
}

void Page()
{
    ImGuiIO& io = ImGui::GetIO();
    if (simulateTouch)
        io.AddMouseSourceEvent(ImGuiMouseSource_TouchScreen);
    if (pointsX.empty())
    {
        std::mt19937 rng(42);
        std::uniform_real_distribution<double> unit(0., 1.);
        for (int i = 0; i < 40; ++i)
        {
            pointsX.push_back(unit(rng));
            pointsY.push_back(unit(rng));
        }
    }

    // The help, in a colored child: a swipe inside scrolls it, a swipe elsewhere scrolls the page
    RichMd::Render("# On a touch screen");
    Section("Vertical swipe");
    ImVec4 bgCol = ImGui::GetStyleColorVec4(ImGuiCol_ChildBg) * 0.6f + ImVec4(0.f, 0.5f, 1.f, 1.f) * 0.4f;
    ImGui::PushStyleColor(ImGuiCol_ChildBg, bgCol);
    ImGui::BeginChild("Help", ImVec2(0.f, HelloImGui::EmSize(10.f)));
    RichMd::Render(GESTURES);
    ImGui::EndChild();
    ImGui::PopStyleColor();
    if (!(io.ConfigFlags & ImGuiConfigFlags_IsTouchScreen))
    {
        // A desktop, in the browser too: the mouse plays the finger (the source applies to the events that follow)
        if (ImGui::Checkbox("Simulate a touch source", &simulateTouch) && !simulateTouch)
            io.AddMouseSourceEvent(ImGuiMouseSource_Mouse);
        ImGui::SameLine();
        const char* source = io.MouseSource == ImGuiMouseSource_TouchScreen ? "touch screen"
                             : io.MouseSource == ImGuiMouseSource_Pen ? "pen" : "mouse";
        ImGui::TextDisabled("(the input is a %s)", source);
    }

    // A child that scrolls sideways: a swipe inside scrolls it, not the page; big buttons count their taps
    Section("Horizontal swipe");
    ImGui::BeginChild("Planets", HelloImGui::EmToVec2(0.f, 7.f), ImGuiChildFlags_Borders, ImGuiWindowFlags_HorizontalScrollbar);
    // three per screen: the child scrolls on a desktop too
    float buttonWidth = std::max(HelloImGui::EmSize(7.f), ImGui::GetContentRegionAvail().x * 0.3f);
    for (size_t i = 0; i < BUTTON_NAMES.size(); ++i)
    {
        if (i > 0)
            ImGui::SameLine();
        std::string label = BUTTON_NAMES[i] + "\n" + std::to_string(buttonClicks[i]) + " taps##planet" + std::to_string(i);
        if (ImGui::Button(label.c_str(), ImVec2(buttonWidth, HelloImGui::EmSize(5.f))))
            buttonClicks[i]++;
    }
    ImGui::EndChild();

    // A button with a menu, a counter, a slider, the text fields (the keyboard of a phone)
    Section("Widgets");
    Label("Context menu");
    if (ImGui::Button("Right click, or hold"))
        clicks++;
    if (ImGui::BeginPopupContextItem("button_menu"))
    {
        if (ImGui::MenuItem("Reset the counter"))
        {
            menuChoice = "Reset the counter";
            clicks = 0;
        }
        if (ImGui::MenuItem("Add ten"))
        {
            menuChoice = "Add ten";
            clicks += 10;
        }
        ImGui::EndPopup();
    }
    ImGui::SameLine();
    if (menuChoice.empty())
        ImGui::Text("%d clicks", clicks);
    else
        ImGui::Text("%d clicks, last menu choice: %s", clicks, menuChoice.c_str());

    // The widgets take the remaining width (-1): ImGui's default width is 65% of the window, from where the item starts
    Label("Slider");
    ImGui::SetNextItemWidth(-1.f);
    ImGui::SliderFloat("##slider", &slider, 0.f, 1.f);
    Label("Text field");
    ImGui::SetNextItemWidth(-1.f);
    ImGui::InputText("##text", &text);
    Label("Multiline edit");
    ImGui::InputTextMultiline("##lines", &lines, ImVec2(-1.f, HelloImGui::EmSize(4.f)));

    // The plots: box select (a right drag: two fingers), pan (a left drag: hold, then drag), draggable tools
    Section("Plots");
    RichMd::Render(PLOTS);
    // ImPlot: a size of 0 is its default plot size (400 px wide), -1 the remaining width
    if (ImPlot::BeginPlot("Box select, pan", ImVec2(-1.f, HelloImGui::EmSize(14.f))))
    {
        ImPlot::PlotScatter("points", pointsX.data(), pointsY.data(), (int)pointsX.size());
        ImPlot::EndPlot();
    }
    if (ImPlot::BeginPlot("Drag the lines and the box", ImVec2(-1.f, HelloImGui::EmSize(14.f))))
    {
        ImPlot::SetupAxesLimits(0., 1., 0., 1.);
        ImPlot::DragLineX(0, &guideX, ImVec4(1.f, 0.5f, 0.f, 1.f), 3.f);
        ImPlot::DragLineY(1, &guideY, ImVec4(0.f, 0.8f, 0.4f, 1.f), 3.f);
        ImPlot::DragRect(2, &box[0], &box[1], &box[2], &box[3], ImVec4(0.3f, 0.6f, 1.f, 1.f));
        ImPlot::PlotScatter("points", pointsX.data(), pointsY.data(), (int)pointsX.size());
        ImPlot::EndPlot();
    }

    // The images (ImmVision): a resizable one, one that pans and zooms
    Section("Images");
#ifdef IMGUI_BUNDLE_WITH_IMMVISION
    RichMd::Render(IMAGES);
    if (tennis.empty())
    {
        std::string imagesDir = DemosAssetsFolder() + "/images/";
        tennis = ImmVision::ImRead(imagesDir + "tennis.jpg");  // RGB(A), no OpenCV
        bear = ImmVision::ImRead(imagesDir + "bear_transparent.png");
        // A negative size is the remaining width of the window (as ImGui's item widths), resolved at the first frame
        tennisSize = ImVec2(-1.f, HelloImGui::EmSize(14.f));
        bearParams.ImageDisplaySize = ImmVision::Size(-1, 0);  // the height from the image's aspect ratio
    }
    ImmVision::ImageDisplayResizable("Tennis", tennis, &tennisSize);  // the size is in and out
    ImmVision::Image("Bear", bear, &bearParams);
#else
    ImGui::TextDisabled("(ImmVision is not part of this build)");
#endif
}
}  // namespace


void gui_demo_touch_screen()
{
    bool onPhone = (ImGui::GetIO().ConfigFlags & ImGuiConfigFlags_IsTouchScreen) != 0;
    if (onPhone)
    {
        Page();
        return;
    }
    // A desktop: a column as wide as a phone, so that the layout is the phone's (the images take the width)
    float width = std::min(HelloImGui::EmSize(PHONE_WIDTH_EM), ImGui::GetContentRegionAvail().x);
    ImGui::BeginChild("phone", ImVec2(width, 0.f), ImGuiChildFlags_Borders);
    Page();
    ImGui::EndChild();
}


#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char**)
{
    ChdirBesideAssetsFolder();
    HelloImGui::RunnerParams runnerParams;
    runnerParams.appWindowParams.windowTitle = "On a touch screen";
    runnerParams.appWindowParams.windowGeometry.size = {500, 800};
    runnerParams.callbacks.ShowGui = gui_demo_touch_screen;
    ImmApp::AddOnsParams addons { .withImplot = true, .withMarkdown = true };
    ImmApp::Run(runnerParams, addons);
    return 0;
}
#endif
#else // #ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include "imgui.h"
#include <cstdio>
void gui_demo_touch_screen() { ImGui::Text("This demo requires ImPlot."); }
#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char**) { std::printf("This demo requires ImPlot.\n"); }
#endif
#endif
