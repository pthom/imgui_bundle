# ImGui Bundle development utilities

_pycmd := "PYTHONPATH=external/bindings_generation python -c"

# List all the targets in the justfile
default:
    @just --list


# ==============================================================
# External libraries management
# ==============================================================

# Show all external libraries with their remotes and branches
[group('libs')]
libs_info:
    @{{ _pycmd }} "from bundle_libs_tooling.all_external_libraries import show_libs_info; show_libs_info()"

# Reattach all submodules to branches and remotes (fork + official)
[group('libs')]
libs_reattach:
    {{ _pycmd }} "from bundle_libs_tooling.all_external_libraries import reattach_all_submodules; reattach_all_submodules()"

# Fetch all remotes for all submodules
[group('libs')]
libs_fetch:
    {{ _pycmd }} "from bundle_libs_tooling.all_external_libraries import fetch_all_submodules; fetch_all_submodules()"

# Pull all submodules
[group('libs')]
libs_pull:
    {{ _pycmd }} "from bundle_libs_tooling.all_external_libraries import pull_all_submodules; pull_all_submodules()"

# Check which fork libraries have new upstream changes
[group('libs')]
libs_check_upstream:
    {{ _pycmd }} "from bundle_libs_tooling.all_external_libraries import check_new_changes_in_official; check_new_changes_in_official()"

# Show new upstream commits not yet in a fork library (usage: just libs_log <name>)
[group('libs')]
libs_log lib:
    @{{ _pycmd }} "from bundle_libs_tooling.all_external_libraries import show_lib_upstream_log; show_lib_upstream_log('{{ lib }}')"

# Tag and rebase a fork library on its official upstream (usage: just libs_rebase <name>)
[group('libs')]
libs_rebase lib:
    {{ _pycmd }} "from bundle_libs_tooling.all_external_libraries import rebase_lib; rebase_lib('{{ lib }}')"

# Push a date tag to a fork library (usage: just libs_tag <name>)
[group('libs')]
libs_tag lib:
    {{ _pycmd }} "from bundle_libs_tooling.all_external_libraries import tag_lib; tag_lib('{{ lib }}')"

# Regenerate Python bindings for a single library (usage: just libs_bindings <name>)
[group('libs')]
libs_bindings lib:
    {{ _pycmd }} "from autogenerate_all import autogenerate_by_name; autogenerate_by_name('{{ lib }}')"

# Regenerate Python bindings for all libraries
[group('libs')]
libs_bindings_all:
    {{ _pycmd }} "from autogenerate_all import main; main()"


# ==============================================================
# ImGui Bundle Explorer (emscripten, with OpenCV)
# ==============================================================

# Build imgui bundle explorer emscripten (with OpenCV for demos)
[group('ibex')]
ibex_build:
    mkdir -p build_ibex_ems && \
    cd build_ibex_ems && \
    source ~/emsdk/emsdk_env.sh && \
    emcmake cmake .. -DCMAKE_BUILD_TYPE=Release -DIMMVISION_FETCH_OPENCV=ON && \
    make -j

# Clean imgui bundle explorer emscripten build
[group('ibex')]
ibex_clean:
    rm -rf build_ibex_ems

# Deploy the imgui bundle explorer build (old url: rsync -vaz bin pascal@traineq.org:HTML/ImGuiBundle/emscripten)
[group('ibex')]
ibex_deploy: ibex_build
    # The server supports gzip encoding, this speed up the loading a lot, especially for the .wasm files
    cp build_ibex_ems/bin/demo_imgui_bundle.html build_ibex_ems/bin/index.html
    gzip -9 -k -f build_ibex_ems/bin/*.wasm build_ibex_ems/bin/*.data build_ibex_ems/bin/*.js
    cd build_ibex_ems && \
    rsync -vaz bin/ pascal@traineq.org:HTML/imgui_bundle_explorer/
    scp build_ibex_ems/bin/demo_imgui_bundle.html pascal@traineq.org:HTML/imgui_bundle_explorer/index.html
    echo "Deployed to https://traineq.org/imgui_bundle_explorer/"

# Serve emscripten with CORS
[group('ibex')]
ibex_serve:
    rm -f build_ibex_ems/bin/*.gz && \
    cd build_ibex_ems/bin && \
    python ../../ci_scripts/webserver_multithread_policy.py -p 8642


# ==============================================================
# ImGui Explorer (emscripten, lightweight)
# ==============================================================

# Build imgui explorer emscripten
[group('imex')]
imex_ems_build:
    mkdir -p build_imex_ems && \
    cd build_imex_ems && \
    source ~/emsdk/emsdk_env.sh && \
    emcmake cmake .. -DCMAKE_BUILD_TYPE=Release \
                     -DIMGUI_BUNDLE_BUILD_IMGUI_EXPLORER_APP=ON -DIMGUI_BUNDLE_WITH_IMANIM=OFF -DIMGUI_BUNDLE_BUILD_DEMOS=OFF -DIMGUI_BUNDLE_WITH_IMMVISION=OFF && \
    cmake --build . -j 8

# Serve imgui explorer
[group('imex')]
imex_ems_serve: imex_ems_build
    echo "add ?lib=imgui, ?lib=implot, ?lib=implot3d or ?lib=imanim to the URL to load the corresponding manual page"
    rm -f build_imex_ems/bin/demo_code/*.gz
    cd build_imex_ems/bin && python ../../ci_scripts/webserver_multithread_policy.py -p 7006

# Clean imgui explorer emscripten build
[group('imex')]
imex_ems_clean:
    rm -rf build_imex_ems

# Deploy imgui explorer to https://pthom.github.io/imgui_explorer/ (copies build into github pages repo, commits, pushes)
[group('imex')]
imex_ems_deploy: imex_ems_build
    ./ci_scripts/imex_ems_deploy.sh


# ==============================================================
# CI / Docker
# ==============================================================

# Run a musllinux docker container with the repo mounted. Sources will be in /work inside the container.
[group('ci')]
cibuild_docker_musllinux:
    docker run -it --rm -v {{justfile_directory()}}:/work -w /work quay.io/pypa/musllinux_1_1_x86_64 bash

# Run a manylinux docker container with the repo mounted. Sources will be in /work inside the container.
[group('ci')]
cibuild_docker_manylinux:
    docker run -it --rm -v {{justfile_directory()}}:/work -w /work quay.io/pypa/manylinux2014_x86_64 bash


# ==============================================================
# Documentation
# ==============================================================

# Build the doc in interactive mode (for dev)
[group('docs')]
doc_serve_interactive:
    cd docs/book && jupyter-book start

# Serve the static built doc
[group('docs')]
doc_serve_static:
    cd docs/book/_build/html && python -m http.server 7005

# Build the doc in static html
[group('docs')]
doc_build_static:
    cd docs/book && jupyter-book build --html
    echo "Doc built in docs/book/_build/html"
    echo "You can serve it with:"
    echo "\n  cd docs/book/_build/html && python -m http.server 7005"
    echo "\nOr just run:\n\n  just doc_serve_static\n"

# Build bundle doc in pdf, copy the pdf to the ramdisk
[group('docs')]
doc_build_pdf:
    cd docs/book && jupyter-book build --pdf


# ==============================================================
# Pyodide
# ==============================================================
# Note: see ci_scripts/pyodide_local_build/Readme.md
# for more info about the local pyodide build setup

# Build pyodide wheel (slim: excludes demos and LaTeX fonts to reduce size)
# Note: the `*pyodide*` glob matches the wheel platform tag
# `pyodide_YYYY_M_wasm32` produced by pyodide-build 0.29.x. If you bump
# PYODIDE_BUILD_VERSION to 0.30+ (which renamed the tag to
# `pyemscripten_YYYY_M_wasm32`), update this glob and pyodide_clean's
# glob accordingly. See the UPGRADE RUNBOOK at the top of
# ci_scripts/pyodide_local_build/config_versions_pyodide.sh.
[group('pyodide')]
pyodide_build: pyodide_clean
    source ci_scripts/pyodide_local_build/venv_pyo/bin/activate && source ci_scripts/pyodide_local_build/emsdk/emsdk_env.sh && IMGUI_BUNDLE_SLIM_PYODIDE_WHEEL=1 pyodide build
    cp dist/imgui_bundle*pyodide*.whl pyodide_projects/_pyodide_resources/local_wheels/
    cp dist/imgui_bundle*pyodide*.whl pyodide_projects/projects/local_wheels/

# Start browser test server (serves test HTML pages)
[group('pyodide')]
pyodide_serve_projects:
    cd pyodide_projects/projects && python ../serve_cors.py --port 6456

# Run any Python demo in Pyodide (browse http://localhost:6789/)
[group('pyodide')]
pyodide_demo_runner:
    python pyodide_projects/pyodide_demo_runner/serve.py --port 6789

# Clean pyodide build artifacts
[group('pyodide')]
pyodide_clean:
    rm -rf .pyodide_build
    rm -f pyodide_projects/_pyodide_resources/local_wheels/imgui_bundle*pyodide*.whl
    rm -f dist/imgui_bundle*pyodide*.whl

# Install the tools to build pyodide wheels locally (pyodide-build, emsdk, etc.)
[group('pyodide')]
pyodide_setup_local_build:
    ./ci_scripts/pyodide_local_build/setup_pyodide_local_build.sh
    ./pyodide_projects/_pyodide_resources/download_pyodide_dist.sh

# Pyodide deep clean (removes also the local build setup)
[group('pyodide')]
pyodide_deep_clean: pyodide_clean
    rm -rf pyodide_projects/_pyodide_resources/pyodide_dist
    rm -rf ci_scripts/pyodide_local_build/venv_pyo
    rm -rf ci_scripts/pyodide_local_build/emsdk

# Clone pyodide-recipes repo and add fork remote
[group('pyodide')]
pyodide_setup_recipe_clone:
    git clone https://github.com/pyodide/pyodide-recipes.git ci_scripts/pyodide_local_build/pyodide_recipes
    cd ci_scripts/pyodide_local_build/pyodide_recipes && git remote add fork https://github.com/pthom/pyodide-recipes.git


_PYODIDE_DEPLOY_LOCAL_FOLDER := "./pyodide_projects/projects"
_PYODIDE_DEPLOY_REMOTE_FOLDER := "/home/pascal/HTML/imgui_bundle_online/projects"
_PYODIDE_DEPLOY_REMOTE_HOST := "pascal@traineq.org"

# Deploy pyodide playground and minimal template
[group('pyodide')]
pyodide_deploy_imgui_bundle_online:
    cd {{_PYODIDE_DEPLOY_LOCAL_FOLDER}}/min_bundle_pyodide_app && cp -f demo_heart.html demo_heart.source.txt
    rsync -avz --delete {{_PYODIDE_DEPLOY_LOCAL_FOLDER}}/ {{_PYODIDE_DEPLOY_REMOTE_HOST}}:{{_PYODIDE_DEPLOY_REMOTE_FOLDER}}/
    echo "Deployed to https://traineq.org/imgui_bundle_online/"


# ==============================================================
# Tests
# ==============================================================

# Run pytest
[group('test')]
test_pytest:
    pytest


# ==============================================================
# mypy
# ==============================================================

# Run mypy on the bindings
[group('mypy')]
mypy:
    cd bindings && mypy imgui_bundle

# Run mypy on the bindings (exclude errors in the stubs)
[group('mypy')]
mypy_no_stubs:
    cd bindings && mypy imgui_bundle | grep -v "\.pyi"

