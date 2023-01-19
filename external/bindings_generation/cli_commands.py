# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import fire  # type: ignore


class CliCommands:
    def hello(self):
        print("Hello")


def cli_command() -> None:
    fire.Fire(CliCommands)
