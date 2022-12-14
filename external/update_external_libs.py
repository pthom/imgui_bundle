#!/usr/bin/env python
import os.path
from typing import Optional, List
from dataclasses import dataclass
import subprocess

import fire  # type: ignore


def external_libraries_dir():
    this_dir = os.path.dirname(__file__)
    return this_dir


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
            lines_with_echo = ["echo '###### Run command ######'", f"echo '{cmd}'", "echo ''", cmd]
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
                echo_line = f"echo '******************** {line[2:].strip()} ***************'"
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


ONLY_ECHO_COMMANDS = True


@dataclass
class ExternalLibrary:
    name: str
    official_git_url: str
    custom_path_in_external_libraries_dir: Optional[str] = None

    official_branch: str = "master"
    official_tag: Optional[str] = None
    official_remote_name: str = "official"

    fork_git_url: Optional[str] = None
    fork_branch: str = "imgui_bundle"
    fork_remote_name: str = "pthom"

    def folder(self):
        if self.custom_path_in_external_libraries_dir is not None:
            return external_libraries_dir() + "/" + self.custom_path_in_external_libraries_dir
        else:
            return external_libraries_dir() + "/" + self.name

    def run_update_official(self) -> ShellCommands:
        assert self.fork_git_url is None  # if this is a fork, use run_rebase_fork_on_official_changes!

        def official_tag_to_checkout():
            if self.official_tag is not None:
                return self.official_tag
            else:
                return f"{self.official_branch}"

        cmd = f"""
        cd {self.folder()}
        git fetch {self.official_remote_name}
        git checkout {official_tag_to_checkout()}        
        """

        if self.official_tag is None:
            cmd += f"git pull --set-upstream {self.official_remote_name} {self.official_branch}"

        return ShellCommands(cmd)

    def run_rm_remotes(self) -> ShellCommands:
        cmd = f"""
        cd {self.folder()}
        git remote rm origin
        git remote rm {self.official_remote_name}
        """
        if self.fork_git_url is not None:
            cmd += f"""
            git remote rm {self.fork_remote_name}
            """
        return ShellCommands(cmd, abort_on_error=False)

    def run_add_remotes(self) -> ShellCommands:
        cmd = f"""
        cd {self.folder()}
        git remote add {self.official_remote_name} {self.official_git_url}
        """
        if self.fork_git_url is not None:
            cmd += f"""
            git remote add {self.fork_remote_name} {self.fork_git_url}
            """
        return ShellCommands(cmd)

    def run_rebase_fork_on_official_changes(self) -> ShellCommands:
        assert self.fork_git_url is not None
        cmd = f"""
        cd {self.folder()}
        git fetch {self.official_remote_name}
        git fetch {self.fork_remote_name}
        git checkout {self.fork_branch}
        git pull {self.fork_remote_name} {self.fork_branch}
        git fetch {self.official_remote_name}
        git rebase {self.official_remote_name}/{self.official_branch}
        git status
        echo "if the rebase did some updates, please force push manually those changes to the fork"
        """
        return ShellCommands(cmd)


def lib_glfw() -> ExternalLibrary:
    return ExternalLibrary(
        name="glfw", official_git_url="https://github.com/glfw/glfw.git", official_branch="master", official_tag="3.3.8"
    )


def lib_hello_imgui() -> ExternalLibrary:
    return ExternalLibrary(
        name="hello_imgui", official_git_url="https://github.com/pthom/hello_imgui.git", official_branch="master"
    )


# fmt: off

def lib_im_file_dialog() -> ExternalLibrary:
    return ExternalLibrary(
        name="ImFileDialog",
        official_git_url="https://github.com/dfranx/ImFileDialog.git",
        official_branch="main",
        fork_git_url="https://github.com/ImFileDialog.git",
    )


def lib_imgui() -> ExternalLibrary:
    return ExternalLibrary(
        name="imgui",
        official_git_url="https://github.com/ocornut/imgui.git",
        official_branch="docking",
        fork_git_url="https://github.com/pthom/imgui.git"
    )


def lib_imgui_knobs() -> ExternalLibrary:
    return ExternalLibrary(
        name="imgui-knobs",
        official_git_url="https://github.com/altschuler/imgui-knobs",
        official_branch="main",
        fork_git_url="https://github.com/imgui-knobs.git",
    )


def lib_imgui_node_editor() -> ExternalLibrary:
    return ExternalLibrary(
        name="imgui-node-editor",
        official_git_url="https://github.com/thedmd/imgui-node-editor.git",
        official_branch="develop",
        fork_git_url="https://github.com/imgui-node-editor.git",
    )


def lib_imgui_md() -> ExternalLibrary:
    return ExternalLibrary(
        name="imgui_md",
        official_git_url="https://github.com/mekhontsev/imgui_md",
        official_branch="main",
        custom_path_in_external_libraries_dir="imgui_md/imgui_md",
        fork_git_url="https://github.com/imgui_md.git",
    )


def lib_md4c() -> ExternalLibrary:
    return ExternalLibrary(
        name="md4c",
        official_git_url="https://github.com/mity/md4c",
        official_branch="master",
        custom_path_in_external_libraries_dir="imgui_md/md4c",
    )


def lib_imgui_tex_inspect() -> ExternalLibrary:
    return ExternalLibrary(
        name="imgui_tex_inspect",
        official_git_url="https://github.com/andyborrell/imgui_tex_inspect.git",
        official_branch="main",
        fork_git_url="https://github.com/pthom/imgui_tex_inspect.git",
    )


def lib_imgui_toggle() -> ExternalLibrary:
    return ExternalLibrary(
        name="imgui_toggle",
        official_git_url="https://github.com/cmdwtf/imgui_toggle.git",
        official_branch="main",
        fork_git_url="https://github.com/pthom/imgui_toggle.git"
    )


def lib_imgui_color_text_edit() -> ExternalLibrary:
    return ExternalLibrary(
        name="ImGuiColorTextEdit",
        official_git_url="https://github.com/BalazsJako/ImGuiColorTextEdit.git",
        official_branch="dev",
        fork_git_url="https://github.com/ImGuiColorTextEdit.git",
    )


def lib_imguizmo() -> ExternalLibrary:
    return ExternalLibrary(
        name="ImGuizmo",
        official_git_url="https://github.com/CedricGuillemet/ImGuizmo.git",
        official_branch="master",
        custom_path_in_external_libraries_dir="ImGuizmo/ImGuizmo"
    )


def lib_immvision() -> ExternalLibrary:
    return ExternalLibrary(
        name="immvision",
        official_git_url="https://github.com/pthom/immvision.git",
        custom_path_in_external_libraries_dir="immvision/immvision",
    )


def lib_cvnp() -> ExternalLibrary:
    return ExternalLibrary(
        name="cvnp",
        official_git_url="https://github.com/pthom/cvnp.git",
        official_branch="master",
        custom_path_in_external_libraries_dir="immvision/cvnp",
    )


def lib_implot() -> ExternalLibrary:
    return ExternalLibrary(
        name="implot",
        official_git_url="https://github.com/epezent/implot.git",
        official_branch="master"
    )


def lib_imspinner() -> ExternalLibrary:
    return ExternalLibrary(
        name="imspinner",
        official_git_url="https://github.com/dalerank/imspinner.git",
        official_branch="master"
    )

# fmt: on


def play():
    pass

    # GLFW
    # ----
    # lib = lib_glfw()
    # lib.run_rm_remotes().run()
    # lib.run_add_remotes().run()
    # lib.run_update_official().run()

    # hello_imgui
    # -----------
    # lib = lib_hello_imgui()
    # lib.run_rm_remotes().run()
    # lib.run_add_remotes().run()
    # lib.run_update_official().run()

    # ImFileDialog
    # ------------
    # lib = lib_im_file_dialog()
    # lib.run_rm_remotes().run()
    # lib.run_add_remotes().run()
    # lib.run_rebase_fork_on_official_changes().run()

    # imgui
    # -----
    # lib = lib_imgui()
    # lib.run_rm_remotes().run()
    # lib.run_add_remotes().run()
    # lib.run_rebase_fork_on_official_changes().run()

    # imgui-knobs
    # -----------
    # lib = lib_imgui_knobs()
    # lib.run_rm_remotes().run()
    # lib.run_add_remotes().run()
    # lib.run_rebase_fork_on_official_changes().run()

    # imgui-node-editor
    # -----------------
    # lib = lib_imgui_node_editor()
    # lib.run_rm_remotes().run()
    # lib.run_add_remotes().run()
    # lib.run_rebase_fork_on_official_changes().run()

    # imgui_md
    # --------
    # lib = lib_imgui_md()
    # lib.run_rm_remotes().run()
    # lib.run_add_remotes().run()
    # lib.run_rebase_fork_on_official_changes().run()

    # lib_md4c (sub library used by imgui_md)
    # --------
    # lib = lib_md4c()
    # lib.run_rm_remotes().run()
    # lib.run_add_remotes().run()
    # lib.run_update_official().run()

    # imgui_tex_inspect
    # --------
    # lib = lib_imgui_tex_inspect()
    # lib.run_rm_remotes().run()
    # lib.run_add_remotes().run()
    # lib.run_rebase_fork_on_official_changes().run()

    # lib_imgui_toggle
    # ----------------
    lib = lib_imgui_toggle()
    lib.run_rm_remotes().run()
    lib.run_add_remotes().run()
    lib.run_rebase_fork_on_official_changes().run()

    # lib_imgui_color_text_edit
    # -------------------------
    # lib = lib_imgui_color_text_edit()
    # lib.run_rm_remotes().run()
    # lib.run_add_remotes().run()
    # lib.run_rebase_fork_on_official_changes().run()

    # ImGuizmo
    # -------------------------
    # lib = lib_imguizmo()
    # lib.run_rm_remotes().run()
    # lib.run_add_remotes().run()
    # lib.run_update_official()

    # immvision
    # ---------
    # lib = lib_immvision()
    # lib.run_rm_remotes().run()
    # lib.run_add_remotes().run()
    # lib.run_update_official().run()

    # cvnp (sub library used by immvision)
    # ---------
    # lib = lib_cvnp()
    # lib.run_rm_remotes().run()
    # lib.run_add_remotes().run()
    # lib.run_update_official().run()

    # implot
    # ------
    # lib = lib_implot()
    # lib.run_rm_remotes().run()
    # lib.run_add_remotes().run()
    # lib.run_update_official().run()

    # imspinner
    # ---------


class CliCommands:
    def hello(self):
        print("Hello")


def cli_command() -> None:
    fire.Fire(CliCommands)


if __name__ == "__main__":
    # cli_command()
    play()
