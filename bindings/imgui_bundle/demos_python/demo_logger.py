# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import random
from imgui_bundle import imgui, hello_imgui, imgui_md, immapp
from imgui_bundle.demos_python.demo_utils import api_demos


@immapp.static(idx_fortune=0, added_logs=False)
def demo_gui():
    static = demo_gui
    fortunes = [
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
        "The only thing constant in life is change, except for death and taxes, those are pretty constant too.",
    ]

    def add_logs():
        for _i in range(10):
            log_level = random.choice(
                [
                    hello_imgui.LogLevel.debug,
                    hello_imgui.LogLevel.info,
                    hello_imgui.LogLevel.warning,
                    hello_imgui.LogLevel.error,
                ]
            )
            hello_imgui.log(log_level, fortunes[static.idx_fortune])
            static.idx_fortune += 1
            if static.idx_fortune >= len(fortunes):
                static.idx_fortune = 0

    if not static.added_logs:
        add_logs()
        static.added_logs = True

    imgui_md.render_unindented(
        """
        # Graphical logger for ImGui
        This logger is adapted from [ImGuiAl](https://github.com/leiradel/ImGuiAl)

        Its colors are computed automatically from the WindowBg color, in order to remain readable when the theme is changed.
        """
    )
    imgui.separator()

    if imgui.button("Add logs"):
        for _i in range(10):
            add_logs()

    imgui.separator()
    hello_imgui.log_gui()


def main():
    api_demos.set_hello_imgui_demo_assets_folder()
    immapp.run(demo_gui, "Log", with_markdown=True)


if __name__ == "__main__":
    main()
