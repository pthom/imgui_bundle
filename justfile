# Misc development utilities


# List all the targets in the justfile
default:
    @just --list


# build emscripten
ems_build:
    ./ci_scripts/ems_build.sh

# Serve emscripten with CORS
ems_serve:
    python ./ci_scripts/webserver_multithread_policy


# Reattach all submodules to branches and remotes (fork + official)
ext_reattach:
    python -c "import sys; sys.path.append('external'); from bindings_generation import all_external_libraries; all_external_libraries.reattach_all_submodules()"


# Push a new tag to the imgui fork repository with the current date
imgui_tag:
    cd external/imgui/imgui && git tag `date +'bundle_%Y%m%d'` && git push --tags

# Push a new tag to the imgui_test_engine fork repository with the current date
imgui_te_tag:
    cd external/imgui_test_engine/imgui_test_engine && git tag `date +'bundle_%Y%m%d'` && git push --tags

imgui_rebase:
    cd external/imgui/imgui && git fetch official && git rebase official/docking

imgui_te_rebase:
    cd external/imgui_test_engine/imgui_test_engine && git fetch official && git rebase official/main
