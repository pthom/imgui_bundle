# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from bindings_generation.all_external_libraries import *


def update_libs():
    pass

    # GLFW
    # ----
    lib = lib_glfw()
    lib.run_rm_remotes().run()
    lib.run_add_remotes().run()
    lib.run_update_official().run()

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
    # lib = lib_imgui_toggle()
    # lib.run_rm_remotes().run()
    # lib.run_add_remotes().run()
    # lib.run_rebase_fork_on_official_changes().run()

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
    # lib.run_rebase_fork_on_official_changes()

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


if __name__ == "__main__":
    update_libs()
