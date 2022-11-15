#include "imgui_bundle/imgui_bundle.h"
#include "hello_imgui/hello_imgui.h"
#include "imgui.h"
#include "implot/implot.h"
#include "imspinner/imspinner.h"
#include "imgui_toggle/imgui_toggle.h"
#include "imgui-knobs/imgui-knobs.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#include "ImFileDialog/ImFileDialog.h"
#include "imgui_md_wrapper.h"

#include <vector>
#include <cmath>

void demo_imgui_basic_widgets(); // see imgui_basic_widgets.cpp


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

void demo_implot()
{
    static std::vector<double> x, y1, y2;
    if (x.empty())
    {
        double pi = 3.1415;
        for (int i = 0; i < 1000; ++i)
        {
            double x_ = pi * 4. * (double)i / 1000.;
            x.push_back(x_);
            y1.push_back(cos(x_));
            y2.push_back(sin(x_));
        }
    }

    ImGuiMd::Render("# This is the plot of _cosinus_ and *sinus*");
    if (ImPlot::BeginPlot("Plot"))
    {
        ImPlot::PlotLine("y1", x.data(), y1.data(), x.size());
        ImPlot::PlotLine("y2", x.data(), y2.data(), x.size());
        ImPlot::EndPlot();
    }
}

void demo_widgets()
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
            const char *format = "%.3f";
            float size = ImGui::GetFontSize() / ImGui::GetIO().FontGlobalScale * 2.5f;
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
        ImGui::BeginGroup();
        ImGuiMd::Render("### Toggle"); ImGui::NewLine();
        static bool toggled1 = true;
        ImGui::Toggle("Animated Toggle", &toggled1, ImGuiToggleFlags_Animated, 0.5f);
        static bool toggled2 = false;
        ImGui::Toggle("Toggle", &toggled2);
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

    demo_imgui_basic_widgets();

}


int main(int, char **)
{
    HelloImGui::RunnerParams runnerParams;

    //
    //    Define the add-on params
    //
    ImGuiBundle::AddOnsParams addOnsParams;
    addOnsParams.withImplot = true;
    addOnsParams.withMarkdown = true;
    addOnsParams.withNodeEditor = true;

    //
    //    Define the app window params
    //
    runnerParams.appWindowParams.windowGeometry.size = {1000, 800};
    runnerParams.appWindowParams.windowTitle = "ImGui bundle demo";

    runnerParams.imGuiWindowParams.showMenuBar = true;
    runnerParams.imGuiWindowParams.showMenu_View = true;


    //
    //    Define the docking splits,
    //    i.e. the way the screen space is split in different target zones for the dockable windows
    //     We want to split "MainDockSpace" (which is provided automatically) into two zones, like this:
    //
    //    ___________________________________
    //    |                                 |
    //    |                                 |
    //    |     MainDockSpace               |
    //    |                                 |
    //    -----------------------------------
    //    |     BottomSpace                 |
    //    -----------------------------------
    //

    // First, tell HelloImGui that we want full screen dock space (this will create "MainDockSpace")
    runnerParams.imGuiWindowParams.defaultImGuiWindowType = HelloImGui::DefaultImGuiWindowType::ProvideFullScreenDockSpace;
    // In this demo, we also demonstrate multiple viewports.
    // you can drag windows outside out the main window in order to put their content into new native windows
    runnerParams.imGuiWindowParams.enableViewports = true;

    // Then, add a space named "BottomSpace" whose height is 25% of the app height.
    // This will split the preexisting default dockspace "MainDockSpace" in two parts.
    HelloImGui::DockingSplit splitMainBottom;
    splitMainBottom.initialDock = "MainDockSpace";
    splitMainBottom.newDock = "BottomSpace";
    splitMainBottom.direction = ImGuiDir_Down;
    splitMainBottom.ratio = 0.25f;
    // Finally, transmit these splits to HelloImGui
    runnerParams.dockingParams.dockingSplits = { splitMainBottom };

    //
    //    Define the dockable windows
    //
    // implot_window
    HelloImGui::DockableWindow implot_window;
    implot_window.label = "ImPlot";
    implot_window.dockSpaceName = "MainDockSpace";
    implot_window.GuiFunction = demo_implot;
    // logsWindow
    HelloImGui::DockableWindow logsWindow;
    logsWindow.label = "Logs";
    logsWindow.dockSpaceName = "BottomSpace";
    logsWindow.GuiFunction = HelloImGui::LogGui;
    // ImGui::ShowDemoWindow
    HelloImGui::DockableWindow demoWindow;
    demoWindow.label = "Dear ImGui Demo";
    demoWindow.dockSpaceName = "MainDockSpace";
    demoWindow.GuiFunction = []() { ImGui::ShowDemoWindow(); };
    // demo_widgets
    HelloImGui::DockableWindow widgetsWindow;
    widgetsWindow.label = "Widgets demo";
    widgetsWindow.dockSpaceName = "MainDockSpace";
    widgetsWindow.GuiFunction = demo_widgets;

    // Finally, transmit these windows to HelloImGui
    runnerParams.dockingParams.dockableWindows = { implot_window, logsWindow, demoWindow, widgetsWindow };


    ImGuiBundle::Run(runnerParams, addOnsParams);
    return 0;
}
