// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "hello_imgui/hello_imgui.h"
#include "implot/implot.h"
#include "imspinner/imspinner.h"
#include "imgui_toggle/imgui_toggle.h"
#include "imgui_toggle/imgui_toggle_presets.h"
#include "imgui_toggle/imgui_toggle_palette.h"
#include "imgui_toggle/imgui_toggle_renderer.h"
#include "immapp/immapp.h"
#include "portable_file_dialogs/portable_file_dialogs.h"
#include "imgui-command-palette/imcmd_command_palette.h"
#include "imgui-knobs/imgui-knobs.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#include "ImFileDialog/ImFileDialog.h"
#include "imgui_md_wrapper.h"
#include "demo_utils/api_demos.h"

#include <fplus/fplus.hpp>
#include <memory>


void DemoKnobs()
{
    static float knob_float_value = 0.f;
    static int knob_int_value = 0;

    std::vector<std::pair<ImGuiKnobVariant, std::string>> knob_types = {
        {ImGuiKnobVariant_Tick, "tick"},
        {ImGuiKnobVariant_Dot, "dot"},
        {ImGuiKnobVariant_Space, "space"},
        {ImGuiKnobVariant_Stepped, "stepped"},
        {ImGuiKnobVariant_Wiper, "wiper"},
        {ImGuiKnobVariant_WiperDot, "wiper_dot"},
        {ImGuiKnobVariant_WiperOnly, "wiper_only"},
    };

    auto show_float_knobs = [&knob_types](float knob_size)
    {
        std::string knob_size_str = std::to_string(knob_size);
        ImGui::PushID((knob_size_str + "_float").c_str());
        for (const auto& [knob_type, knob_typename] : knob_types)
        {
            ImGuiKnobs::Knob(
                knob_typename.c_str(),
                &knob_float_value,
                /*v_min=*/   0.0f,
                /*v_max=*/   1.0f,
                /*speed=*/   0,
                /*format=*/  "%.2f",
                /*variant=*/ knob_type,
                /*size=*/    knob_size,
                /*flags=*/   0,
                /*steps=*/   100
            );
            ImGui::SameLine();
        }
        ImGui::NewLine();
        ImGui::PopID();
    };


    auto show_int_knobs = [&knob_types](float knob_size)
    {
        std::string knob_size_str = std::to_string(knob_size);
        ImGui::PushID((knob_size_str + "_int").c_str());
        for (const auto& [knob_type, knob_typename] : knob_types)
        {
            ImGuiKnobs::KnobInt(
                knob_typename.c_str(),
                &knob_int_value,
                /*v_min=*/   0.0,
                /*v_max=*/   15,
                /*speed=*/   0,
                /*format=*/  "%02i",
                /*variant=*/ knob_type,
                /*size=*/    knob_size,
                /*flags=*/   0,
                /*steps=*/   10
            );
            ImGui::SameLine();
        }
        ImGui::NewLine();
        ImGui::PopID();
    };

    float knobsSizeSmall = ImmApp::EmSize() * 2.5;
    float knobsSizeBig = knobsSizeSmall * 1.3;

    ImGui::BeginGroup();
    ImGui::Text("Some small knobs");
    show_float_knobs(knobsSizeSmall);
    ImGui::EndGroup();

    ImGui::SameLine();

    ImGui::BeginGroup();
    ImGui::Text("Some big knobs (int values)");
    show_int_knobs(knobsSizeBig);
    ImGui::EndGroup();
}


void DemoSpinner()
{
    ImColor color(0.3f, 0.5f, 0.9f, 1.f);
    ImGui::Text("spinner_moving_dots");
    ImGui::SameLine();
    ImSpinner::SpinnerMovingDots("spinner_moving_dots", 3.0, color, 28.0);
    ImGui::SameLine();

    float radius = ImGui::GetFontSize() / 1.8f;
    ImGui::Text("spinner_arc_rotation");
    ImGui::SameLine();
    ImSpinner::SpinnerArcRotation("spinner_arc_rotation", radius, 4.0, color);
    ImGui::SameLine();

    float radius1 = ImGui::GetFontSize() / 2.5f;
    ImGui::Text("spinner_ang_triple");
    ImGui::SameLine();
    ImSpinner::SpinnerAngTriple("spinner_ang_triple", radius1, radius1 * 1.5f, radius1 * 2.0f, 2.5f, color, color, color);
}


void DemoToggle()
{
    static bool flag = true;

    ImGuiMd::RenderUnindented(R"(
        # Toggle Switch
        [imgui_toggle](https://github.com/cmdwtf/imgui_toggle) provides toggle switches for ImGui."""
    )");

    bool changed = false;
    changed |= ImGui::Toggle("Default Toggle", &flag);
    ImGui::SameLine();

    changed |= ImGui::Toggle("Animated Toggle", &flag, ImGuiToggleFlags_Animated);
    ImGui::SameLine();

    auto toggle_config = ImGuiTogglePresets::MaterialStyle();
    toggle_config.AnimationDuration = 0.4f;
    changed |= ImGui::Toggle("Material Style (with slowed anim)", &flag, toggle_config);

    ImGui::SameLine();
    changed |= ImGui::Toggle("iOS style", &flag, ImGuiTogglePresets::iOSStyle(0.2f));

    ImGui::SameLine();
    changed |= ImGui::Toggle(
        "iOS style (light)", &flag, ImGuiTogglePresets::iOSStyle(0.2f, true));
}


void DemoPortableFileDialogs()
{
    static std::string lastFileSelection;

    ImGui::PushID("pfd");
    ImGuiMd::RenderUnindented(R"(
        # Portable File Dialogs
         [portable-file-dialogs](https://github.com/samhocevar/portable-file-dialogs) provides native file dialogs
    )");

    auto logResult = [](std::string what) {
        lastFileSelection = what;
    };
    auto logResultList = [](const std::vector<std::string>& whats) {
        lastFileSelection = fplus::join(std::string("\n"), whats);
    };

    static std::unique_ptr<pfd::open_file> openFileDialog;
    if (ImGui::Button("Open File"))
        openFileDialog = std::make_unique<pfd::open_file>("Select file");
    if (openFileDialog.get() && openFileDialog->ready())
    {
        logResultList(openFileDialog->result());
        openFileDialog.reset();
    }

    ImGui::SameLine();

    
    static std::unique_ptr<pfd::open_file> openFileMultiselect;
    if (ImGui::Button("Open File (multiselect)"))
        openFileMultiselect.reset(new pfd::open_file("Select file", "", {}, pfd::opt::multiselect));
    if (openFileMultiselect.get() && openFileMultiselect->ready())
    {
        logResultList(openFileMultiselect->result());
        openFileMultiselect.reset();
    }

    ImGui::SameLine();

    static std::unique_ptr<pfd::save_file> saveFileDialog;
    if (ImGui::Button("Save File"))
        saveFileDialog = std::make_unique<pfd::save_file>("Save file");
    if (saveFileDialog.get() && saveFileDialog->ready())
    {
        logResult(saveFileDialog->result());
        saveFileDialog.reset();
    }

    ImGui::SameLine();

    static std::unique_ptr<pfd::select_folder> selectFolderDialog;
    if (ImGui::Button("Select Folder"))
        selectFolderDialog = std::make_unique<pfd::select_folder>("Select folder");
    if (selectFolderDialog.get() && selectFolderDialog->ready())
    {
        logResult(selectFolderDialog->result());
        selectFolderDialog.reset();
    }
    

    if (lastFileSelection.size() > 0)
        ImGui::Text("%s", lastFileSelection.c_str());

    ImGui::PopID();
}


void DemoImFileDialog()
{
    static std::string selectedFilename;

    ImGuiMd::RenderUnindented(R"(
        # ImFileDialog
         [ImFileDialog](https://github.com/pthom/ImFileDialog.git) provides file dialogs for ImGui, with images preview.
         *Not (yet) adapted for High DPI resolution under windows*
        )");

    if (ImGui::Button("Open file"))
        ifd::FileDialog::Instance().Open(
            "ShaderOpenDialog",
            "Open a shader",
            "Image file (*.png*.jpg*.jpeg*.bmp*.tga).png,.jpg,.jpeg,.bmp,.tga,.*",
            true
        );
    ImGui::SameLine();
    if (ImGui::Button("Open directory"))
        ifd::FileDialog::Instance().Open("DirectoryOpenDialog", "Open a directory", "");
    ImGui::SameLine();
    if (ImGui::Button("Save file"))
        ifd::FileDialog::Instance().Save("ShaderSaveDialog", "Save a shader", "*.sprj .sprj");

    if (selectedFilename.size() > 0)
        ImGui::Text("Last file selection:\n%s", selectedFilename.c_str());

    if (ifd::FileDialog::Instance().IsDone("ShaderOpenDialog"))
    {
        if (ifd::FileDialog::Instance().HasResult())
        {
            // get_results: plural form - ShaderOpenDialog supports multi-selection
            auto results = ifd::FileDialog::Instance().GetResults();
            selectedFilename = "";
            for (auto path: results)
                selectedFilename += path.string() + "\n";
        }
        ifd::FileDialog::Instance().Close();
    }

    if (ifd::FileDialog::Instance().IsDone("DirectoryOpenDialog"))
    {
        if (ifd::FileDialog::Instance().HasResult())
            selectedFilename = ifd::FileDialog::Instance().GetResult().string();
        ifd::FileDialog::Instance().Close();
    }

    if (ifd::FileDialog::Instance().IsDone("ShaderSaveDialog"))
    {
        if (ifd::FileDialog::Instance().HasResult())
            selectedFilename = ifd::FileDialog::Instance().GetResult().string();
        ifd::FileDialog::Instance().Close();
    }
}


void DemoCommandPalette()
{
    static bool wasInited = false;
    static bool showCommandPalette = false;
    static ImCmd::Context * commandPaletteContext = nullptr;
    static int counter = 0;

    auto initCommandPalette = []()
    {
        commandPaletteContext = ImCmd::CreateContext();
        ImVec4 highlight_font_color(1.0f, 0.0f, 0.0f, 1.0f);
        ImCmd::SetStyleColor(ImCmdTextType_Highlight, ImGui::ColorConvertFloat4ToU32(highlight_font_color));

        // Add theme command: a two steps command, with initial callback + SubsequentCallback
        {
            ImCmd::Command select_theme_cmd;
            select_theme_cmd.Name = "Select theme";
            select_theme_cmd.InitialCallback = [&]() {
                ImCmd::Prompt(std::vector<std::string>{
                    "Classic",
                    "Dark",
                    "Light",
                });
            };
            select_theme_cmd.SubsequentCallback = [&](int selected_option) {
                switch (selected_option) {
                    case 0: ImGui::StyleColorsClassic(); break;
                    case 1: ImGui::StyleColorsDark(); break;
                    case 2: ImGui::StyleColorsLight(); break;
                    default: break;
                }
            };
            ImCmd::AddCommand(std::move(select_theme_cmd));
        }

        // Simple command that increments a counter
        {
            ImCmd::Command inc_cmd;
            inc_cmd.Name = "increment counter";
            inc_cmd.InitialCallback = [] { counter += 1; };
            ImCmd::AddCommand(inc_cmd);
        }
    };

    if (!wasInited)
    {
        initCommandPalette();
        wasInited = true;
    }

    ImGuiMd::RenderUnindented(R"(
        # Command Palette
        [imgui-command-palette](https://github.com/hnOsmium0001/imgui-command-palette.git) provides a Sublime Text or VSCode style command palette in ImGui
    )");

    auto& io = ImGui::GetIO();
    if (io.KeyCtrl && io.KeyShift && ImGui::IsKeyPressed(ImGuiKey_P))
        showCommandPalette = ! showCommandPalette;

    if (showCommandPalette)
        ImCmd::CommandPaletteWindow("CommandPalette", &showCommandPalette);

    ImGui::NewLine();
    ImGui::Text("Press Ctrl+Shift+P to bring up the command palette");
    ImGui::NewLine();
    ImGui::Text("counter=%i", counter);
}


void demo_widgets()
{
    DemoPortableFileDialogs(); ImGui::NewLine();
    DemoImFileDialog(); ImGui::NewLine();
    DemoKnobs();
    DemoToggle(); ImGui::NewLine();
    DemoSpinner();
    DemoCommandPalette();
}