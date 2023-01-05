#include "immapp/immapp.h"
#include "hello_imgui/hello_imgui.h"
#include "imgui.h"
#include "implot/implot.h"
#include "imspinner/imspinner.h"
#include "imgui_toggle/imgui_toggle.h"
#include "imgui_toggle/imgui_toggle_presets.h"
#include "imgui_toggle/imgui_toggle_palette.h"
#include "imgui_toggle/imgui_toggle_renderer.h"
#include "imgui-knobs/imgui-knobs.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#include "ImFileDialog/ImFileDialog.h"
#include "imgui_md_wrapper.h"
#include "demo_utils/api_demos.h"

#include <vector>
#include <cmath>


std::string gSampleCode = R"(
// This code is the spinner demo code (to the left)
ImGui::SameLine();
{
    ImGui::BeginGroup();
    ImGuiMd::Render("### Toggle"); ImGui::NewLine();
    static bool toggled1 = true;
    ImGui::Toggle("Animated Toggle", &toggled1, ImGuiToggleFlags_Animated, 0.5f);
    static bool toggled2 = false;
    ImGui::Toggle("Toggle", &toggled2);
    ImGui::EndGroup();
}
)";

void demo_widgets_old()
{
    ImGuiMd::Render(R"(
# ImGui Bundle
[ImGui Bundle](https://github.com/pthom/imgui_bundle) is a bundle for [Dear ImGui](https://github.com/ocornut/imgui.git), including various useful libraries from its ecosystem.
It enables to easily create ImGui applications in C++, as well as in Python.
This is an example of markdown widget, with an included image:

![world.jpg](world.jpg)
)");

    ImGui::Separator();

    ImGuiMd::Render("# Additional widgets");
    
    // Knobs
    {
        struct KnobVariantWithName
        {
            std::string Name;
            ImGuiKnobVariant_ KnobVariant;
        };
        std::vector<KnobVariantWithName> knob_types {
            { "tick", ImGuiKnobVariant_Tick },
            { "dot", ImGuiKnobVariant_Dot },
            { "space", ImGuiKnobVariant_Space },
            { "stepped", ImGuiKnobVariant_Stepped },
            { "wiper", ImGuiKnobVariant_Wiper },
            { "wiper_dot", ImGuiKnobVariant_WiperDot },
            { "wiper_only", ImGuiKnobVariant_WiperOnly },
        };

        ImGui::BeginGroup();
        ImGuiMd::Render("### Knobs"); ImGui::NewLine();
        static float value = 50.f;
        for (size_t i = 0; i < knob_types.size(); ++i)
        {
            ImGuiKnobVariant_ knob_variant = knob_types[i].KnobVariant;
            std::string knob_variant_name = knob_types[i].Name;
            float speed = 1.5f;
            const char *format = "%.2f";
            float size = ImGui::GetFontSize() * 2.5f;
            ImGuiKnobs::Knob(knob_variant_name.c_str(), &value, 0.f, 100.f, speed, format, knob_variant, size);
            if (i%3 != 2)
                ImGui::SameLine();
        }
        ImGui::NewLine();
        ImGui::EndGroup();
    }

    // Toggles
    ImGui::SameLine();
    {
        static bool toggled = true;
        ImGui::BeginGroup();
        ImGuiMd::Render("### Toggle"); ImGui::NewLine();
        ImGui::Toggle("Animated Toggle", &toggled, ImGuiToggleFlags_Animated, 0.5f);
        ImGui::Toggle("Toggle", &toggled);

        auto toggle_config = ImGuiTogglePresets::MaterialStyle();
        toggle_config.AnimationDuration = 0.4;
        ImGui::Toggle("Material Style (with slowed anim)", &toggled, toggle_config);

        ImGui::Toggle("iOS style", &toggled, ImGuiTogglePresets::iOSStyle(0.2f));

        ImGui::Toggle("iOS style", &toggled, ImGuiTogglePresets::iOSStyle(0.2f, true));

        ImGui::EndGroup();
    }

    // Spinners
    ImGui::SameLine();
    {
        ImGui::BeginGroup();
        ImGuiMd::Render("### Spinner"); ImGui::NewLine();
        ImColor color(0.3f, 0.5f, 0.9f, 1.0f);
        ImSpinner::SpinnerMovingDots("spinner_moving_dots", 3.0f, color, 28.0f);

        float radius = ImGui::GetFontSize() / 2.0f;
        ImSpinner::SpinnerArcRotation("spinner_arc_rotation", radius, 4.0f, color);

        float radius1 = ImGui::GetFontSize() / 2.5f;
        ImSpinner::SpinnerAngTriple("spinner_arc_fade", radius1, radius1 * 1.5f, radius1 * 2.0f, 2.5f, color, color, color);
        ImGui::EndGroup();
    }

    // Text Editor
    ImGui::SameLine();
    {
        ImGui::BeginGroup();
        ImGuiMd::Render("### Text editor"); ImGui::NewLine();
        static TextEditor textEditor;
        if (textEditor.GetText().size() < 5)
        {
            textEditor.SetText(gSampleCode);
            textEditor.SetLanguageDefinition(TextEditor::LanguageDefinition::CPlusPlus());
        }
        ImVec2 textEditorSize = { ImGui::GetFontSize() * 20.f, ImGui::GetFontSize() * 10.f};
        textEditor.Render("TextEditor", textEditorSize);
        ImGui::EndGroup();
    }

    // File dialogs
    ImGui::SameLine();
    {
        ImGui::BeginGroup();
        ImGuiMd::Render(R"(### ImFileDialog
Selected file names will be shown in the log panel at the bottom.
)");
        if (ImGui::Button("Open file"))
            ifd::FileDialog::Instance().Open(
                "ShaderOpenDialog",
                "Open a shader",
                "Image file (*.png*.jpg*.jpeg*.bmp*.tga).png,.jpg,.jpeg,.bmp,.tga,.*",
                true
            );

        if (ImGui::Button("Open directory"))
            ifd::FileDialog::Instance().Open("DirectoryOpenDialog", "Open a directory", "");

        if (ImGui::Button("Save file"))
            ifd::FileDialog::Instance().Save("ShaderSaveDialog", "Save a shader", "*.sprj .sprj");


        if (ifd::FileDialog::Instance().IsDone("ShaderOpenDialog"))
        {
            if (ifd::FileDialog::Instance().HasResult())
            {
                // get_results: plural form - ShaderOpenDialog supports multi-selection
                auto results = ifd::FileDialog::Instance().GetResults();
                for (auto path: results)
                    HelloImGui::Log(HelloImGui::LogLevel::Info, path.string().c_str());
            }
            ifd::FileDialog::Instance().Close();
        }

        if (ifd::FileDialog::Instance().IsDone("DirectoryOpenDialog"))
        {
            if (ifd::FileDialog::Instance().HasResult())
            {
                std::string selectedFilename = ifd::FileDialog::Instance().GetResult().string();
                HelloImGui::Log(HelloImGui::LogLevel::Warning, selectedFilename.c_str());
            }
            ifd::FileDialog::Instance().Close();
        }

        if (ifd::FileDialog::Instance().IsDone("ShaderSaveDialog"))
        {
            if (ifd::FileDialog::Instance().HasResult())
            {
                std::string selectedFilename = ifd::FileDialog::Instance().GetResult().string();
                HelloImGui::Log(HelloImGui::LogLevel::Error, selectedFilename.c_str());
            }
            ifd::FileDialog::Instance().Close();
        }

        ImGui::EndGroup();
    }
}
