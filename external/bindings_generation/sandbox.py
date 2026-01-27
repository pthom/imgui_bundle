# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
from bundle_libs_tooling import all_external_libraries


# all_external_libraries.reattach_all_submodules()
# all_external_libraries.pull_all_submodules()
# all_external_libraries.fetch_all_submodules()

cmd = all_external_libraries.lib_implot().cmd_rebase_fork_on_official_changes()
print(cmd)
