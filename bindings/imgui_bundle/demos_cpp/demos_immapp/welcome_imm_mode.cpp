// What is an Immediate GUI: the widgets are functions, called every frame, that return the current value.
// The state is plain variables. See the Python version (welcome_imm_mode.py) for the full explanation.
#include "immapp/immapp.h"
#include "imgui_rich_md/rich_md.h"
#include <string>
#include <vector>

const std::vector<std::string> AVAILABLE_ITEMS = {"Apple", "Banana", "Cherry", "Date"};

// All the app state in one place: plain variables
struct AppState
{
    char Name[64] = "World";
    float Volume = 4.5f;
    int Choice = 1;
    int Count = 0;
    int SelectedItem = 1;
    bool ShowExtra = false;
    float Color[4] = {0.4f, 0.7f, 1.0f, 1.0f};
};

void Gui(AppState& s)
{
    RichMd::Render(R"(# What is an Immediate GUI
With [Dear ImGui](https://github.com/ocornut/imgui), your GUI code is **simple and direct**: no widget trees, no
callbacks, no state synchronization. You call functions to create widgets, and they return the current value.
The function is called every frame: the UI is rebuilt from scratch each time. This is the **immediate mode** paradigm.

**Try it:** edit any value below and see the result update instantly. Then look at the code: each widget is one line,
and the state is plain variables.
)");
    ImGui::Separator();
    float em = ImGui::GetFontSize();  // em <=> equivalent to the em CSS unit

    // Click me button: draw the button, and handle its click action immediately
    if (ImGui::Button("Click me!"))
        s.Count += 1;
    ImGui::SameLine();  // the next widget on the same line
    ImGui::Text("Clicked %d times", s.Count);
    ImGui::Separator();

    // A widget that manipulates a value takes a pointer to it, and returns true when it was just used
    ImGui::SliderFloat("Volume", &s.Volume, 0.0f, 12.0f, "%.1f");
    ImGui::Separator();

    // Text input (SetNextItemWidth: the input takes the full width by default)
    ImGui::SetNextItemWidth(em * 15);
    ImGui::InputText("Your name", s.Name, sizeof(s.Name));
    ImGui::Text("Hello, %s!", s.Name);
    ImGui::Separator();

    // Color picker (HelloImGui::EmSize(15) is equivalent to em * 15)
    ImGui::SetNextItemWidth(HelloImGui::EmSize(15));
    ImGui::ColorEdit4("Accent color", s.Color);
    ImGui::Separator();

    // Radio buttons
    ImGui::Text("  Mode:");
    ImGui::SameLine();
    if (ImGui::RadioButton("Easy", s.Choice == 0))
        s.Choice = 0;
    ImGui::SameLine();
    if (ImGui::RadioButton("Medium", s.Choice == 1))
        s.Choice = 1;
    ImGui::SameLine();
    if (ImGui::RadioButton("Hard", s.Choice == 2))
        s.Choice = 2;

    // Combo (dropdown)
    ImGui::SetNextItemWidth(em * 15);
    if (ImGui::BeginCombo("Fruit", AVAILABLE_ITEMS[s.SelectedItem].c_str()))
    {
        for (int i = 0; i < (int)AVAILABLE_ITEMS.size(); ++i)
            if (ImGui::Selectable(AVAILABLE_ITEMS[i].c_str(), i == s.SelectedItem))
                s.SelectedItem = i;
        ImGui::EndCombo();
    }
    ImGui::Separator();

    // Collapsible section
    ImGui::Checkbox("Show extra info", &s.ShowExtra);
    if (s.ShowExtra)
    {
        const char* modes[] = {"Easy", "Medium", "Hard"};
        ImGui::Indent();
        ImGui::TextDisabled("This section is conditionally visible.");
        ImGui::Text("Mode: %s", modes[s.Choice]);
        ImGui::Text("Fruit: %s", AVAILABLE_ITEMS[s.SelectedItem].c_str());
        ImGui::Unindent();
    }
}

int main()
{
    AppState state;
    HelloImGui::SimpleRunnerParams params;
    params.guiFunction = [&state]() { Gui(state); };
    params.windowTitle = "What is an Immediate GUI";
    params.windowSize = {1000, 700};
    ImmApp::AddOnsParams addOns;
    addOns.withMarkdown = true;
    ImmApp::Run(params, addOns);
    return 0;
}
