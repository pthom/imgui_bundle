import fire  # type: ignore


class CliCommands:
    def hello(self):
        print("Hello")


def cli_command() -> None:
    fire.Fire(CliCommands)
