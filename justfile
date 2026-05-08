# ImGui Bundle development utilities

# Use bash for all recipes (default on Linux is dash via /bin/sh, which lacks `source`).
set shell := ["bash", "-cu"]

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
    if [ -f ~/emsdk/emsdk_env.sh ]; then source ~/emsdk/emsdk_env.sh; fi && \
    emcmake cmake .. -DCMAKE_BUILD_TYPE=Release -DIMMVISION_FETCH_OPENCV=ON && \
    make -j 4

# Clean imgui bundle explorer emscripten build
[group('ibex')]
ibex_clean:
    rm -rf build_ibex_ems

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
    if [ -f ~/emsdk/emsdk_env.sh ]; then source ~/emsdk/emsdk_env.sh; fi && \
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

# Build the doc in interactive mode (for dev — serves at port-root, BASE_URL not needed)
[group('docs')]
doc_serve:
    cd docs/book && jupyter-book start

# Build HTML + PDF for Cloudflare deploy
[group('docs')]
doc_build_cf:
    cd docs/book && BASE_URL=/doc jupyter-book build --html
    cd docs/book && jupyter-book build --pdf
    mkdir -p docs/book/_build/html/assets
    cp docs/book/_build/exports/imgui_bundle_book.pdf docs/book/_build/html/assets/imgui_bundle_book.pdf


# ==============================================================
# Pyodide
# ==============================================================
# Note: see ci_scripts/pyodide_local_build/Readme.md
# for more info about the local pyodide build setup

# Build pyodide wheel (slim: excludes demos and LaTeX fonts to reduce size)
# Note: the `*pyemscripten*` glob matches the wheel platform tag
# `pyemscripten_YYYY_M_wasm32` produced by pyodide-build 0.34.1+ (PEP 783).
# If pyodide-build renames the tag again, update this glob and pyodide_clean's
# glob accordingly. See the UPGRADE RUNBOOK at the top of
# ci_scripts/pyodide_local_build/config_versions_pyodide.sh.
[group('pyodide')]
pyodide_build: pyodide_clean
    source ci_scripts/pyodide_local_build/venv_pyo/bin/activate && source ci_scripts/pyodide_local_build/emsdk/emsdk_env.sh && IMGUI_BUNDLE_SLIM_PYODIDE_WHEEL=1 pyodide build
    cp dist/imgui_bundle*pyemscripten*.whl pyodide_projects/_pyodide_resources/local_wheels/
    cp dist/imgui_bundle*pyemscripten*.whl pyodide_projects/projects/local_wheels/

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
    rm -f pyodide_projects/_pyodide_resources/local_wheels/imgui_bundle*pyemscripten*.whl
    rm -f dist/imgui_bundle*pyemscripten*.whl

# Install the tools to build pyodide wheels locally (pyodide-build, emsdk, etc.)
[group('pyodide')]
pyodide_setup_local_build:
    ./ci_scripts/pyodide_local_build/setup_pyodide_local_build.sh

# Pyodide deep clean (removes also the local build setup)
[group('pyodide')]
pyodide_deep_clean: pyodide_clean
    rm -rf ci_scripts/pyodide_local_build/venv_pyo
    rm -rf ci_scripts/pyodide_local_build/emsdk

# Clone pyodide-recipes repo and add fork remote
[group('pyodide')]
pyodide_setup_recipe_clone:
    git clone https://github.com/pyodide/pyodide-recipes.git ci_scripts/pyodide_local_build/pyodide_recipes
    cd ci_scripts/pyodide_local_build/pyodide_recipes && git remote add fork https://github.com/pthom/pyodide-recipes.git


# ==============================================================
# Cloudflare Pages deploy (to https://imgui-bundle.pages.dev/)
# ==============================================================
# See docs/book/devel_docs/cloudflare_deploy.md for the full workflow.
#
#   imgui-bundle.pages.dev/                      landing page (links)
#   imgui-bundle.pages.dev/playground/           pyodide playground
#   imgui-bundle.pages.dev/min_pyodide_app/      minimal pyodide sample
#   imgui-bundle.pages.dev/local_wheels/         shared wheel (referenced as ../local_wheels/)
#   imgui-bundle.pages.dev/explorer/             ibex
#
# Requires: wrangler (`npm i -g wrangler`) and either
#   - env vars CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID, or
#   - `wrangler login` / `wrangler whoami` auth
_CF_STAGING := "_cf_staging"
_CF_PROJECT := "imgui-bundle"

# Clone or update docs/clone_website_resources/ from origin/main.
# This folder used to be a git submodule; now it is fetched on demand
# so it does not pollute regular contributors' checkouts.
[group('cloudflare')]
cf_resources_sync:
    #!/usr/bin/env bash
    set -euo pipefail
    DEST=docs/clone_website_resources
    URL=https://github.com/pthom/imgui_bundle_website_resources.git
    if [ ! -d "$DEST/.git" ]; then
        git clone --depth 1 "$URL" "$DEST"
        exit 0
    fi
    # Refuse to sync if the user has uncommitted changes
    if [ -n "$(git -C "$DEST" status --porcelain)" ]; then
        echo "ERROR: $DEST has uncommitted changes. Commit/push them first." >&2
        git -C "$DEST" status --short >&2
        exit 1
    fi
    git -C "$DEST" fetch origin main
    # Refuse to sync if local main has commits not on origin/main
    AHEAD=$(git -C "$DEST" rev-list --count origin/main..main 2>/dev/null || echo 0)
    if [ "$AHEAD" != "0" ]; then
        echo "ERROR: $DEST has $AHEAD local commit(s) not pushed to origin/main." >&2
        echo "       Push them first; cf_deploy_from_github would otherwise deploy a stale snapshot." >&2
        exit 1
    fi
    git -C "$DEST" checkout main
    git -C "$DEST" pull --ff-only origin main

# builds all the elements required by cf_stage (doc, explorer, pyodide wheel, etc)
[group('cloudflare')]
cf_stage_prepare: cf_resources_sync doc_build_cf ibex_build pyodide_setup_local_build pyodide_build

# populates pyodide_projects/_cf_staging which is what will be uploaded to imgui-bundle.pages.dev/
[group('cloudflare')]
cf_stage:
    # 0. Make dir pyodide_projects/_cf_staging (gitignored)
    rm -rf {{_CF_STAGING}}
    mkdir -p {{_CF_STAGING}}
    #
    # 1. Copy resources + _headers & robots.txt
    # ------------------------------------------------------------
    rsync -a docs/clone_website_resources/imgui-bundle.pages.dev/ {{_CF_STAGING}}/
    #
    # 2. Copy min_pyodide_app
    # ------------------------------------------------------------
    rm -rf {{_CF_STAGING}}/min_pyodide_app
    cd pyodide_projects/projects/min_pyodide_app && cp -f demo_heart.html demo_heart.source.txt
    rsync -a pyodide_projects/projects/min_pyodide_app/ {{_CF_STAGING}}/min_pyodide_app/
    #
    # 3. Copy python playground
    # ------------------------------------------------------------
    # --copy-unsafe-links resolves the examples/ symlink (points outside the tree)
    rm -rf {{_CF_STAGING}}/playground {{_CF_STAGING}}/local_wheels
    rsync -a --copy-unsafe-links pyodide_projects/projects/playground/ {{_CF_STAGING}}/playground/
    # projects/local_wheels/ ships both the wheel (gitignored) and a tracked
    # index.html landing page served at imgui-bundle.pages.dev/local_wheels/.
    rsync -a pyodide_projects/projects/local_wheels/ {{_CF_STAGING}}/local_wheels/
    #
    # 4. Copy imgui bundle explorer (ibex)
    # ------------------------------------------------------------
    rm -rf {{_CF_STAGING}}/explorer
    rsync -a --exclude='*.gz' build_ibex_ems/bin/ {{_CF_STAGING}}/explorer/
    cp build_ibex_ems/bin/demo_imgui_bundle.html {{_CF_STAGING}}/explorer/index.html
    # Note: .data files are served as-is; the _headers rule /explorer/*.data
    # overrides their Content-Type to application/wasm so CF auto-compresses
    # them at the edge (application/octet-stream is not in CF's compressible
    # MIME list, and CF strips user-set Content-Encoding from _headers).
    #
    # 5. Copy jupyter-book documentation to the staging ROOT/doc
    # Run `just doc_build_cf` first.
    # ------------------------------------------------------------
    rm -rf {{_CF_STAGING}}/doc
    rsync -a docs/book/_build/html/ {{_CF_STAGING}}/doc/
    #
    # 6. Place an up to date assets.zip
    # ------------------------------------------------------------
    cd bindings/imgui_bundle && zip -r assets.zip assets/ && cd -
    mv  bindings/imgui_bundle/assets.zip {{_CF_STAGING}}/resources/assets.zip
    #
    # 7. Copy landing page
    # ------------------------------------------------------------
    rm -rf {{_CF_STAGING}}/assets {{_CF_STAGING}}/index.html
    rsync -a docs/clone_website_resources/imgui_bundle_pages_landing/final/assets/ {{_CF_STAGING}}/assets/
    cp docs/clone_website_resources/imgui_bundle_pages_landing/final/index.html {{_CF_STAGING}}/index.html
    #
    # 8. generate sitemap.xml
    # ------------------------------------------------------------
    python docs/clone_website_resources/tools/generate_sitemap.py


# Upload the current staging dir to Cloudflare Pages (does not build the elements, you shall do it yourself before)
[group('cloudflare')]
cf_deploy:
    wrangler pages deploy {{_CF_STAGING}} --project-name={{_CF_PROJECT}} --commit-dirty=true
    echo "Deployed to https://imgui-bundle.pages.dev/"

# Update Cloudflare Pages from GitHub (same result as cf_deploy_all_in_one, but runs on GH)
[group('cloudflare')]
cf_deploy_from_github:
    gh workflow run cf_pages_deploy.yml


# Deploy to cloudflare, after having built all the required elements before
[group('cloudflare')]
cf_deploy_all_in_one: cf_stage_prepare cf_stage cf_deploy

# Serves locally the current staging dir (add coi headers for the explorer,
# and Content-Encoding: gzip for the pre-gzipped .data files — mirrors the CF _headers rules).
[group('cloudflare')]
cf_serve_local:
    cd {{_CF_STAGING}} && python ../ci_scripts/webserver_multithread_policy.py -p 8764 --coi-prefix=/explorer/

# Serve imgui bundle landing page during dev
[group('cloudflare')]
cf_serve_imgui_bundle_pages_landing:
    echo "http://localhost:8333"
    cd docs/clone_website_resources/imgui_bundle_pages_landing/final && python3 -m http.server 8333



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
    mypy

# Run mypy on the bindings (exclude errors in the stubs)
[group('mypy')]
mypy_no_stubs:
    mypy imgui_bundle | grep -v "\.pyi"

