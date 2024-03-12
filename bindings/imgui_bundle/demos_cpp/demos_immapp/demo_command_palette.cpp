#include "imgui.h"
#include "immapp/immapp.h"
#include "imgui-command-palette/imcmd_command_palette.h"
#include "imgui-command-palette-py-wrapper/imgui-command-palette-py-wrapper.h"
#include "hello_imgui/hello_imgui.h"
#include "hello_imgui/icons_font_awesome_4.h"
#include "demo_utils/api_demos.h"

struct AppState
{
    bool show_command_palette = false;
    ImCmd::ContextWrapper contextWrapper;
};


void InitCommandPalette()
{
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

    // Simple command that logs messages
    {
        ImCmd::Command log_cmd;
        log_cmd.Name = "You say goodbye";
        log_cmd.InitialCallback = []{ HelloImGui::Log(HelloImGui::LogLevel::Info, "... and I say hello..." ICON_FA_MUSIC ); };
        ImCmd::AddCommand(log_cmd);
    }
}


int main(int , char *[])
{
    ChdirBesideAssetsFolder();
    AppState appState;

    auto gui = [&appState]()
    {
        auto& io = ImGui::GetIO();

        if (io.KeyCtrl && io.KeyShift && ImGui::IsKeyPressed(ImGuiKey_P))
            appState.show_command_palette = !appState.show_command_palette;

        if (appState.show_command_palette)
            ImCmd::CommandPaletteWindow("CommandPalette", &appState.show_command_palette);

        ImGui::Text("Press Ctrl+Shift+P to bring up the command palette");

        ImGui::SetCursorPosY(ImGui::GetCursorPosY() + 100.f);
        ImGui::Separator();
        HelloImGui::LogGui();
    };

    HelloImGui::RunnerParams params;
    params.callbacks.ShowGui = gui;
    params.callbacks.PostInit = InitCommandPalette;

    ImmApp::Run(params);

    return 0;
}
