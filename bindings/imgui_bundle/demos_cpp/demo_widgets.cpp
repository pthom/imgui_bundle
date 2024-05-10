// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "hello_imgui/hello_imgui.h"
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
#ifdef IMGUI_BUNDLE_WITH_IMFILEDIALOG
#include "ImFileDialog/ImFileDialog.h"
#endif
#include "imgui_md_wrapper.h"
#include "ImCoolBar/ImCoolbar.h"
#include "demo_utils/api_demos.h"

#include <fplus/fplus.hpp>
#include <memory>


void DemoKnobs()
{
    ImGuiMd::RenderUnindented(R"(
        # Knobs
        [imgui-knobs](https://github.com/altschuler/imgui-knobs) provides knobs for ImGui.
        )");
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
    ImGuiMd::RenderUnindented(R"(
        # Spinners
        [imspinner](https://github.com/dalerank/imspinner) provides spinners for ImGui.
    )");

    ImColor color(0.3f, 0.5f, 0.9f, 1.f);
    ImGui::Text("spinner_moving_dots");
    ImGui::SameLine();
    ImSpinner::SpinnerMovingDots("spinner_moving_dots", 20.0, 4.0, color, 20);
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
        [portable-file-dialogs](https://github.com/samhocevar/portable-file-dialogs) provides file dialogs
        as well as notifications and messages. They will use the native dialogs and notifications on each platform.
    )");

#ifdef __EMSCRIPTEN__
    ImGuiMd::RenderUnindented(R"(
        *Note: On Emscripten/Web, only messages dialogs (with an Ok button and an icon) are supported.
        On Windows, Linux and MacOS, everything is supported.*
    )");
#endif

    ImGui::Text("      ---   File dialogs   ---");
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


    ImGui::Text("      ---   Notifications and messages   ---");

    static pfd::icon iconType = pfd::icon::info;
    static std::optional<pfd::message> messageDialog;
    static pfd::choice messageChoiceType = pfd::choice::ok;

    // icon type
    ImGui::Text("Icon type");
    ImGui::SameLine();
    std::vector<std::pair<pfd::icon, const char*>> iconTypes = {
        {pfd::icon::info, "info"},
        {pfd::icon::warning, "warning"},
        {pfd::icon::error, "error"},
    };
    for (const auto& [notification_icon, name]: iconTypes)
    {
        if (ImGui::RadioButton(name, iconType == notification_icon))
            iconType = notification_icon;
        ImGui::SameLine();
    }
    ImGui::NewLine();

    if (ImGui::Button("Add Notif"))
        pfd::notify("Notification title", "This is an example notification", iconType);

    // messages
    ImGui::SameLine();
    // 1. Display the message
    if (ImGui::Button("Add message"))
        messageDialog = pfd::message("Message title", "This is an example message", messageChoiceType, iconType);
    // 2. Handle the message result
    if (messageDialog.has_value() && messageDialog->ready())
    {
        printf("msg ready\n"); // Get the result via messageDialog->result()
        messageDialog.reset();
    }
    // Optional: Select the message type
    ImGui::SameLine();
    std::vector<std::pair<pfd::choice, const char*>> choiceTypes = {
        {pfd::choice::ok, "ok"},
        {pfd::choice::yes_no, "yes_no"},
        {pfd::choice::yes_no_cancel, "yes_no_cancel"},
        {pfd::choice::retry_cancel, "retry_cancel"},
        {pfd::choice::abort_retry_ignore, "abort_retry_ignore"},
    };
    for (const auto& [choice_type, name]: choiceTypes)
    {
        if (ImGui::RadioButton(name, messageChoiceType == choice_type))
            messageChoiceType = choice_type;
        ImGui::SameLine();
    }
    ImGui::NewLine();

    ImGui::PopID();
}


void DemoImFileDialog()
{
#ifdef IMGUI_BUNDLE_WITH_IMFILEDIALOG
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
#endif // #ifdef IMGUI_BUNDLE_WITH_IMFILEDIALOG
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


void DemoCoolBar()
{
    auto ShowCoolBarButton = [](const std::string& label) -> bool
    {
        float w         = ImGui::GetCoolBarItemWidth();

        // Display transparent image and check if clicked
        HelloImGui::ImageFromAsset("images/bear_transparent.png", ImVec2(w, w));
        bool clicked = ImGui::IsItemHovered() && ImGui::IsMouseClicked(0);

        // Optional: add a label on the image
        {
            ImVec2 topLeftCorner = ImGui::GetItemRectMin();
            ImVec2 textPos(topLeftCorner.x + ImmApp::EmSize(1.f), topLeftCorner.y + ImmApp::EmSize(1.f));
            ImGui::GetForegroundDrawList()->AddText(textPos, 0xFFFFFFFF, label.c_str());
        }

        return clicked;
    };


    std::vector<std::string> buttonLabels {"A", "B", "C", "D", "E", "F"};
    ImGuiMd::RenderUnindented(R"(
        # ImCoolBar:
        ImCoolBar provides a dock-like Cool bar for Dear ImGui
    )");

    ImGui::ImCoolBarConfig coolBarConfig;
    coolBarConfig.anchor = ImVec2(0.5f, 0.07f); // position in the window (ratio of window size)
    if (ImGui::BeginCoolBar("##CoolBarMain", ImCoolBarFlags_Horizontal, coolBarConfig))
    {
        for (const std::string& label: buttonLabels)
        {
            if (ImGui::CoolBarItem())
            {
                if (ShowCoolBarButton(label))
                    printf("Clicked %s\n", label.c_str());
            }
        }
        ImGui::EndCoolBar();
    }

    ImGui::NewLine(); ImGui::NewLine();
}


void demo_widgets()
{
    DemoCoolBar();
    DemoPortableFileDialogs(); ImGui::NewLine();
    DemoImFileDialog(); ImGui::NewLine();
    DemoKnobs();
    DemoToggle(); ImGui::NewLine();
    DemoSpinner();
    DemoCommandPalette();
}
