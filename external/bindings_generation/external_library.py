# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os.path
from typing import Optional, List
from dataclasses import dataclass
from bindings_generation.shell_commands import ShellCommands
from bindings_generation.paths import external_libraries_dir
from codemanip.code_utils import to_snake_case


@dataclass
class ExternalLibrary:
    name: str
    official_git_url: Optional[str] = None
    custom_git_folder: Optional[str] = None

    official_branch: str = "master"
    official_remote_name: str = "official"

    fork_git_url: Optional[str] = None
    fork_branch: str = "imgui_bundle"
    fork_remote_name: str = "fork"

    is_published_in_python: bool = True
    is_sub_library: bool = False

    def base_folder_abs_path(self):
        return external_libraries_dir() + "/" + self.name

    def is_submodule(self):
        return self.fork_git_url is not None or self.official_git_url is not None

    def git_url(self) -> Optional[str]:
        r = (
            self.fork_git_url
            if self.fork_git_url is not None
            else self.official_git_url
        )
        return r

    def attached_git_branch(self) -> Optional[str]:
        r = self.fork_branch if self.fork_git_url is not None else self.official_branch
        return r

    def attached_git_remote(self) -> Optional[str]:
        r = (
            self.fork_remote_name
            if self.fork_git_url is not None
            else self.official_remote_name
        )
        return r

    def bindings_folder_abs_path(self) -> str:
        r = self.base_folder_abs_path() + "/bindings"
        if not os.path.isdir(r):
            os.mkdir(r)
        return r

    def bindings_folder_path_from_external(self) -> str:
        r = self.name + "/bindings"
        return r

    def cpp_pybind_files(self) -> List[str]:
        files = os.listdir(self.bindings_folder_abs_path())

        def is_pybind_file(filename: str):
            return filename.startswith("pybind_") and filename.endswith(".cpp")

        pybind_files = list(filter(is_pybind_file, files))
        pybind_files = [
            self.bindings_folder_path_from_external() + "/" + f for f in pybind_files
        ]
        return pybind_files

    def generator_script_name(self) -> str:
        files = os.listdir(self.bindings_folder_abs_path())

        def is_generator_module(filename: str):
            return filename.startswith("generate_") and filename.endswith(".py")

        generators_modules = list(filter(is_generator_module, files))
        if len(generators_modules) != 1:
            print(
                f"ERROR: {self.name} has {len(generators_modules)} generator modules, expected 1"
            )
        assert len(generators_modules) == 1
        return generators_modules[0][:-3]  # remove extension ".py"

    def git_folder_abs_path(self) -> str:
        if self.custom_git_folder is not None:
            return external_libraries_dir() + "/" + self.custom_git_folder
        else:
            return self.base_folder_abs_path() + "/" + self.name

    def git_folder_relative_path(self) -> str:
        if self.custom_git_folder is not None:
            return "external/" + self.custom_git_folder
        else:
            return f"external/{self.name}/{self.name}"

    def name_snake_case(self) -> str:
        r = self.name
        r = r.replace("ImGui", "Imgui")
        r = r.replace("-", "_")
        r = to_snake_case(r)
        return r

    def cmd_update_official(self) -> ShellCommands:
        assert (
            self.fork_git_url is None
        )  # if this is a fork, use run_rebase_fork_on_official_changes!

        cmd = f"""
        cd {self.git_folder_abs_path()}
        git fetch {self.official_remote_name}
        git checkout {self.official_branch}
        git pull --set-upstream {self.official_remote_name} {self.official_branch}
        """
        return ShellCommands(cmd)

    def cmd_pull(self) -> ShellCommands:
        cmd = f"""
        cd {self.git_folder_abs_path()}
        git pull
        """
        return ShellCommands(cmd)

    def cmd_attach_branches(self) -> ShellCommands:
        cmd = f"""
            cd {self.git_folder_abs_path()}
            git checkout -b {self.attached_git_branch()} || git checkout {self.attached_git_branch()}
            git branch --set-upstream-to={self.attached_git_remote()}/{self.attached_git_branch()}
        """
        return ShellCommands(cmd)

    def cmd_rm_remotes(self) -> ShellCommands:
        cmd = f"""
        cd {self.git_folder_abs_path()}
        git remote rm origin
        git remote rm {self.official_remote_name}
        """
        if self.fork_git_url is not None:
            cmd += f"""
            git remote rm {self.fork_remote_name}
            """
        return ShellCommands(cmd, abort_on_error=False)

    def cmd_add_remotes(self) -> ShellCommands:
        cmd = f"""
        cd {self.git_folder_abs_path()}
        git remote add {self.official_remote_name} {self.official_git_url}
        """
        if self.fork_git_url is not None:
            cmd += f"""
            git remote add {self.fork_remote_name} {self.fork_git_url}
            """
        return ShellCommands(cmd)

    def cmd_fetch_all(self) -> ShellCommands:
        cmd = f"""
        cd {self.git_folder_abs_path()}
        git fetch --all
        """
        return ShellCommands(cmd)

    def cmd_rebase_fork_on_official_changes(self) -> ShellCommands:
        assert self.fork_git_url is not None
        cmd = f"""
        cd {self.git_folder_abs_path()}
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

    def run_reattach_submodule(self):
        """
        Will remove existing git remotes
        Then add two remotes if it is a fork
            - official : points to the official repo
            - pthom: points to the forked library
        Or add one remote if it is not a fork
            - official : points to the official repo
        then attach the submodule to the correct remote branch (set-upstream)
        """
        if not self.is_submodule():
            print(
                f"run_reattach_submodule: skipped {self.name} because it does not appear to be a submodule"
            )
            return
        self.cmd_rm_remotes().run()
        self.cmd_add_remotes().run()
        self.cmd_fetch_all().run()
        self.cmd_attach_branches().run()

    def run_pull(self):
        if not self.is_submodule():
            print(
                f"run_pull: skipped {self.name} because it does not appear to be a submodule"
            )
            return
        self.cmd_pull().run()
