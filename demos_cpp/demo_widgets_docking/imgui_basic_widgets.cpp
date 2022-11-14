#include "imgui.h"
#include "imgui_md_wrapper.h"

// Helper to display a little (?) mark which shows a tooltip when hovered.
// In your own code you may want to display an actual icon if you are using a merged icon fonts (see docs/FONTS.md)
static void HelpMarker(const char* desc)
{
    ImGui::TextDisabled("(?)");
    if (ImGui::IsItemHovered())
    {
        ImGui::BeginTooltip();
        ImGui::PushTextWrapPos(ImGui::GetFontSize() * 35.0f);
        ImGui::TextUnformatted(desc);
        ImGui::PopTextWrapPos();
        ImGui::EndTooltip();
    }
}


void demo_imgui_basic_widgets()
{
    ImGuiMd::Render("# ImGui widgets\n (This is a verbatim copy-paste from imgui_demo.cpp (basic widgets demo)");
#define IMGUI_DEMO_MARKER(x)

    static int clicked = 0;
    if (ImGui::Button("Button"))
        clicked++;
    if (clicked & 1)
    {
        ImGui::SameLine();
        ImGui::Text("Thanks for clicking me!");
    }

    IMGUI_DEMO_MARKER("Widgets/Basic/Checkbox");
    static bool check = true;
    ImGui::Checkbox("checkbox", &check);

    IMGUI_DEMO_MARKER("Widgets/Basic/RadioButton");
    static int e = 0;
    ImGui::RadioButton("radio a", &e, 0); ImGui::SameLine();
    ImGui::RadioButton("radio b", &e, 1); ImGui::SameLine();
    ImGui::RadioButton("radio c", &e, 2);

    // Color buttons, demonstrate using PushID() to add unique identifier in the ID stack, and changing style.
    IMGUI_DEMO_MARKER("Widgets/Basic/Buttons (Colored)");
    for (int i = 0; i < 7; i++)
    {
        if (i > 0)
            ImGui::SameLine();
        ImGui::PushID(i);
        ImGui::PushStyleColor(ImGuiCol_Button, (ImVec4)ImColor::HSV(i / 7.0f, 0.6f, 0.6f));
        ImGui::PushStyleColor(ImGuiCol_ButtonHovered, (ImVec4)ImColor::HSV(i / 7.0f, 0.7f, 0.7f));
        ImGui::PushStyleColor(ImGuiCol_ButtonActive, (ImVec4)ImColor::HSV(i / 7.0f, 0.8f, 0.8f));
        ImGui::Button("Click");
        ImGui::PopStyleColor(3);
        ImGui::PopID();
    }

    // Use AlignTextToFramePadding() to align text baseline to the baseline of framed widgets elements
    // (otherwise a Text+SameLine+Button sequence will have the text a little too high by default!)
    // See 'Demo->Layout->Text Baseline Alignment' for details.
    ImGui::AlignTextToFramePadding();
    ImGui::Text("Hold to repeat:");
    ImGui::SameLine();

    // Arrow buttons with Repeater
    IMGUI_DEMO_MARKER("Widgets/Basic/Buttons (Repeating)");
    static int counter = 0;
    float spacing = ImGui::GetStyle().ItemInnerSpacing.x;
    ImGui::PushButtonRepeat(true);
    if (ImGui::ArrowButton("##left", ImGuiDir_Left)) { counter--; }
    ImGui::SameLine(0.0f, spacing);
    if (ImGui::ArrowButton("##right", ImGuiDir_Right)) { counter++; }
    ImGui::PopButtonRepeat();
    ImGui::SameLine();
    ImGui::Text("%d", counter);

    IMGUI_DEMO_MARKER("Widgets/Basic/Tooltips");
    ImGui::Text("Hover over me");
    if (ImGui::IsItemHovered())
        ImGui::SetTooltip("I am a tooltip");

    ImGui::SameLine();
    ImGui::Text("- or me");
    if (ImGui::IsItemHovered())
    {
        ImGui::BeginTooltip();
        ImGui::Text("I am a fancy tooltip");
        static float arr[] = { 0.6f, 0.1f, 1.0f, 0.5f, 0.92f, 0.1f, 0.2f };
        ImGui::PlotLines("Curve", arr, IM_ARRAYSIZE(arr));
        ImGui::EndTooltip();
    }

    ImGui::Separator();
    ImGui::LabelText("label", "Value");

    {
        // Using the _simplified_ one-liner Combo() api here
        // See "Combo" section for examples of how to use the more flexible BeginCombo()/EndCombo() api.
        IMGUI_DEMO_MARKER("Widgets/Basic/Combo");
        const char* items[] = { "AAAA", "BBBB", "CCCC", "DDDD", "EEEE", "FFFF", "GGGG", "HHHH", "IIIIIII", "JJJJ", "KKKKKKK" };
        static int item_current = 0;
        ImGui::Combo("combo", &item_current, items, IM_ARRAYSIZE(items));
        ImGui::SameLine();
        HelpMarker(
            "Using the simplified one-liner Combo API here.\nRefer to the \"Combo\" section below for an explanation of how to use the more flexible and general BeginCombo/EndCombo API.");
    }

    {
        // To wire InputText() with std::string or any other custom string type,
        // see the "Text Input > Resize Callback" section of this demo, and the misc/cpp/imgui_stdlib.h file.
        IMGUI_DEMO_MARKER("Widgets/Basic/InputText");
        static char str0[128] = "Hello, world!";
        ImGui::InputText("input text", str0, IM_ARRAYSIZE(str0));
        ImGui::SameLine(); HelpMarker(
            "USER:\n"
            "Hold SHIFT or use mouse to select text.\n"
            "CTRL+Left/Right to word jump.\n"
            "CTRL+A or double-click to select all.\n"
            "CTRL+X,CTRL+C,CTRL+V clipboard.\n"
            "CTRL+Z,CTRL+Y undo/redo.\n"
            "ESCAPE to revert.\n\n"
            "PROGRAMMER:\n"
            "You can use the ImGuiInputTextFlags_CallbackResize facility if you need to wire InputText() "
            "to a dynamic string type. See misc/cpp/imgui_stdlib.h for an example (this is not demonstrated "
            "in imgui_demo.cpp).");

        static char str1[128] = "";
        ImGui::InputTextWithHint("input text (w/ hint)", "enter text here", str1, IM_ARRAYSIZE(str1));

        IMGUI_DEMO_MARKER("Widgets/Basic/InputInt, InputFloat");
        static int i0 = 123;
        ImGui::InputInt("input int", &i0);

        static float f0 = 0.001f;
        ImGui::InputFloat("input float", &f0, 0.01f, 1.0f, "%.3f");

        static double d0 = 999999.00000001;
        ImGui::InputDouble("input double", &d0, 0.01f, 1.0f, "%.8f");

        static float f1 = 1.e10f;
        ImGui::InputFloat("input scientific", &f1, 0.0f, 0.0f, "%e");
        ImGui::SameLine(); HelpMarker(
            "You can input value using the scientific notation,\n"
            "  e.g. \"1e+8\" becomes \"100000000\".");

        static float vec4a[4] = { 0.10f, 0.20f, 0.30f, 0.44f };
        ImGui::InputFloat3("input float3", vec4a);
    }

    {
        IMGUI_DEMO_MARKER("Widgets/Basic/DragInt, DragFloat");
        static int i1 = 50, i2 = 42;
        ImGui::DragInt("drag int", &i1, 1);
        ImGui::SameLine(); HelpMarker(
            "Click and drag to edit value.\n"
            "Hold SHIFT/ALT for faster/slower edit.\n"
            "Double-click or CTRL+click to input value.");

        ImGui::DragInt("drag int 0..100", &i2, 1, 0, 100, "%d%%", ImGuiSliderFlags_AlwaysClamp);

        static float f1 = 1.00f, f2 = 0.0067f;
        ImGui::DragFloat("drag float", &f1, 0.005f);
        ImGui::DragFloat("drag small float", &f2, 0.0001f, 0.0f, 0.0f, "%.06f ns");
    }

    {
        IMGUI_DEMO_MARKER("Widgets/Basic/SliderInt, SliderFloat");
        static int i1 = 0;
        ImGui::SliderInt("slider int", &i1, -1, 3);
        ImGui::SameLine(); HelpMarker("CTRL+click to input value.");

        static float f1 = 0.123f, f2 = 0.0f;
        ImGui::SliderFloat("slider float", &f1, 0.0f, 1.0f, "ratio = %.3f");
        ImGui::SliderFloat("slider float (log)", &f2, -10.0f, 10.0f, "%.4f", ImGuiSliderFlags_Logarithmic);

        IMGUI_DEMO_MARKER("Widgets/Basic/SliderAngle");
        static float angle = 0.0f;
        ImGui::SliderAngle("slider angle", &angle);

        // Using the format string to display a name instead of an integer.
        // Here we completely omit '%d' from the format string, so it'll only display a name.
        // This technique can also be used with DragInt().
        IMGUI_DEMO_MARKER("Widgets/Basic/Slider (enum)");
        enum Element { Element_Fire, Element_Earth, Element_Air, Element_Water, Element_COUNT };
        static int elem = Element_Fire;
        const char* elems_names[Element_COUNT] = { "Fire", "Earth", "Air", "Water" };
        const char* elem_name = (elem >= 0 && elem < Element_COUNT) ? elems_names[elem] : "Unknown";
        ImGui::SliderInt("slider enum", &elem, 0, Element_COUNT - 1, elem_name);
        ImGui::SameLine(); HelpMarker("Using the format string parameter to display a name instead of the underlying integer.");
    }

    {
        IMGUI_DEMO_MARKER("Widgets/Basic/ColorEdit3, ColorEdit4");
        static float col1[3] = { 1.0f, 0.0f, 0.2f };
        static float col2[4] = { 0.4f, 0.7f, 0.0f, 0.5f };
        ImGui::ColorEdit3("color 1", col1);
        ImGui::SameLine(); HelpMarker(
            "Click on the color square to open a color picker.\n"
            "Click and hold to use drag and drop.\n"
            "Right-click on the color square to show options.\n"
            "CTRL+click on individual component to input value.\n");

        ImGui::ColorEdit4("color 2", col2);
    }

    {
        // Using the _simplified_ one-liner ListBox() api here
        // See "List boxes" section for examples of how to use the more flexible BeginListBox()/EndListBox() api.
        IMGUI_DEMO_MARKER("Widgets/Basic/ListBox");
        const char* items[] = { "Apple", "Banana", "Cherry", "Kiwi", "Mango", "Orange", "Pineapple", "Strawberry", "Watermelon" };
        static int item_current = 1;
        ImGui::ListBox("listbox", &item_current, items, IM_ARRAYSIZE(items), 4);
        ImGui::SameLine(); HelpMarker(
            "Using the simplified one-liner ListBox API here.\nRefer to the \"List boxes\" section below for an explanation of how to use the more flexible and general BeginListBox/EndListBox API.");
    }

}
