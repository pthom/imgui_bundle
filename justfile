# Misc development utilities


# List all the targets in the justfile
default:
    @just --list


# build emscripten
ems_build:
    ./ci_scripts/ems_build.sh

# Serve emscripten with CORS
ems_serve:
    python ./ci_scripts/webserver_multithread_policy.py


# Reattach all submodules to branches and remotes (fork + official)
ext_reattach:
    python -c "import sys; sys.path.append('external'); from bindings_generation import all_external_libraries; all_external_libraries.reattach_all_submodules()"


# Push a new tag to the imgui fork repository with the current date
imgui_tag:
    cd external/imgui/imgui && git tag `date +'bundle_%Y%m%d'` && git push --tags

# Push a new tag to the imgui_test_engine fork repository with the current date
imgui_te_tag:
    cd external/imgui_test_engine/imgui_test_engine && git tag `date +'bundle_%Y%m%d'` && git push --tags

# Rebase the imgui fork repository on the official repository (push a new tag before!)
imgui_rebase:
    cd external/imgui/imgui && git fetch official && git rebase official/docking

# Rebase the imgui_test_engine fork repository on the official repository (push a new tag before!)
imgui_te_rebase:
    cd external/imgui_test_engine/imgui_test_engine && git fetch official && git rebase official/main

# Runs a musllinux docker container (to test the musllinux cibuild)
cibuild_docker_musllinux:
    docker run -it --rm quay.io/pypa/musllinux_1_1_x86_64 bash

# Runs a manylinux docker container (to test the manylinux cibuild)
cibuild_docker_manylinux:
    docker run -it --rm quay.io/pypa/manylinux2014_x86_64 bash

# Run mypy on the bindings
mypy:
    cd bindings && ./mypy_bindings.sh

# Build the doc
doc:
    cd bindings/imgui_bundle/doc/scripts/ && ./build_doc.sh
