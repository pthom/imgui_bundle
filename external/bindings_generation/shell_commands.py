# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from dataclasses import dataclass
import subprocess


CommandsString = str


@dataclass
class ShellCommands:
    shell_commands: str
    abort_on_error: bool = True

    def command(self):
        commands = self._chain_and_echo_commands(step_by_step_echo=False)
        return commands

    def run(self):
        commands = self._chain_and_echo_commands(step_by_step_echo=True)
        subprocess.check_call(commands, shell=True)

    def show(self):
        print(self._chain_and_echo_commands(step_by_step_echo=False))

    def __str__(self):
        return self._chain_and_echo_commands(step_by_step_echo=True)

    def _chain_and_echo_commands(self, step_by_step_echo: bool) -> CommandsString:
        """
        Take a series of shell command on a multiline string (one command per line)
        and returns a shell command that will execute each of them in sequence,
        while echoing them, and ignoring commented lines (with a #)
        """

        def _cmd_to_echo_and_cmd_lines(cmd: str) -> [str]:
            lines_with_echo = [
                "echo '###### Run command ######'",
                f"echo '{cmd}'",
                "echo ''",
                cmd,
            ]
            return lines_with_echo

        lines = self.shell_commands.split("\n")
        # strip lines
        lines = map(lambda s: s.strip(), lines)
        # suppress empty lines
        lines = filter(lambda s: not len(s) == 0, lines)

        # add "echo commands" and process comments:
        # comments starting with # are discarded and comments starting with ## are displayed loudly
        lines_with_echo = []
        for line in lines:
            if line.startswith("##"):
                echo_line = (
                    f"echo '******************** {line[2:].strip()} ***************'"
                )
                lines_with_echo.append(echo_line)
            elif not line.startswith("#"):
                if step_by_step_echo:
                    lines_with_echo = lines_with_echo + _cmd_to_echo_and_cmd_lines(line)
                else:
                    lines_with_echo = lines_with_echo + [line]

        # End of line joiner
        if self.abort_on_error:
            end_line = " &&          \\\n"
        else:
            end_line = " || true  &&  \\\n"

        r = end_line.join(lines_with_echo)
        if self.abort_on_error:
            r = r.replace("&& &&", "&& ")

        if not self.abort_on_error:
            r += " || true"

        return r
