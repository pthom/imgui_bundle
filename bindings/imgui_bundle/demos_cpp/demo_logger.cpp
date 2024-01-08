// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "immapp/immapp.h"
#include "hello_imgui/hello_imgui.h"
#include "demo_utils/api_demos.h"

#include <vector>
#include <string>


void demo_logger()
{
    static std::vector<std::string> fortunes {
        "If at first you don't succeed, skydiving is not for you.",
        "You will be a winner today. Pick a fight.",
        "The world may be your oyster, but it doesn't mean you'll get its pearl.",
        "Borrow money from a pessimist, they don't expect it back.",
        "You will be hungry again in an hour.",
        "A closed mouth gathers no foot.",
        "Today, you will invent the wheel...again.",
        "If you can't convince them, confuse them.",
        "The journey of a thousand miles begins with a single step, or a really good map.",
        "You will find a pot of gold at the end of a rainbow, but it'll be someone else's.",
        "Opportunities will knock on your door, but don't worry, they'll be gone by the time you get up to answer.",
        "You will have a long and healthy life...and a very boring one.",
        "A wise man once said nothing.",
        "You will have a great day...tomorrow.",
        "The only thing constant in life is change, except for death and taxes, those are pretty constant too."
    };

    static size_t idxFortune = 0;

    auto addLogs = []()
    {
        for (int i = 0; i < 10; ++i)
        {
            HelloImGui::LogLevel logLevel = HelloImGui::LogLevel(rand() % 4);
            HelloImGui::Log(logLevel, fortunes[idxFortune].c_str());
            ++ idxFortune;
            if (idxFortune >= fortunes.size())
                idxFortune = 0;
        }
    };
    static bool addedLogs = false;
    if (! addedLogs)
    {
        addLogs();
        addedLogs = true;
    }

    ImGuiMd::RenderUnindented(R"(
        # Graphical logger for ImGui
        This logger is adapted from [ImGuiAl](https://github.com/leiradel/ImGuiAl)

        Its colors are computed automatically from the WindowBg color, in order to remain readable when the theme is changed.
    )");
    ImGui::Separator();

    if (ImGui::Button("Add logs"))
        addLogs();

    ImGui::Separator();
    HelloImGui::LogGui();
}
