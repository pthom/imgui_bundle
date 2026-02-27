# Misc development utilities


# List all the targets in the justfile
default:
    @just --list

# build imgui bundle explorer emscripten
ibex_build:
    mkdir -p build_ibex_ems && \
    cd build_ibex_ems && \
    source ~/emsdk/emsdk_env.sh && \
    emcmake cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j

# clean imgui bundle emscripten build
ibex_clean:
    rm -rf build_ibex_ems

# deploy the imgui bundle explorer build
# old url:     # rsync -vaz bin pascal@traineq.org:HTML/ImGuiBundle/emscripten
ibex_deploy: ibex_build
    # The server supports gzip encoding, this speed up the loading a lot, especially for the .wasm files
    cp build_ibex_ems/bin/demo_imgui_bundle.html build_ibex_ems/bin/index.html
    gzip -9 -k -f build_ibex_ems/bin/*.wasm build_ibex_ems/bin/*.data build_ibex_ems/bin/*.js
    cd build_ibex_ems && \
    rsync -vaz bin/ pascal@traineq.org:HTML/imgui_bundle_explorer/
    scp build_ibex_ems/bin/demo_imgui_bundle.html pascal@traineq.org:HTML/imgui_bundle_explorer/index.html
    echo "Deployed to https://traineq.org/imgui_bundle_explorer/"

# Serve emscripten with CORS
ibex_serve:
    rm -f build_ibex_ems/bin/*.gz && \
    cd build_ibex_ems/bin && \
    python ../../ci_scripts/webserver_multithread_policy.py -p 8642

# Build imgui explorer emscripten
imex_ems_build:
    mkdir -p build_imex_ems && \
    cd build_imex_ems && \
    source ~/emsdk/emsdk_env.sh && \
    emcmake cmake .. -DCMAKE_BUILD_TYPE=Release \
                     -DIMGUI_BUNDLE_BUILD_IMGUI_EXPLORER_APP=ON -DIMGUI_BUNDLE_WITH_IMANIM=OFF -DIMGUI_BUNDLE_BUILD_DEMOS=OFF -DIMGUI_BUNDLE_WITH_IMMVISION=OFF && \
    cmake --build . -j 8

# Serve imgui explorer
imex_ems_serve: imex_ems_build
    echo "add ?lib=imgui, ?lib=implot, ?lib=implot3d or ?lib=imanim to the URL to load the corresponding manual page"
    rm -f build_imex_ems/bin/demo_code/*.gz
    cd build_imex_ems/bin && python ../../ci_scripts/webserver_multithread_policy.py -p 7006

# Clean imgui explorer emscripten build
imex_ems_clean:
    rm -rf build_imex_ems

# deploy imgui explorer to https://pthom.github.io/imgui_explorer/
# (copies build output into the imgui_explorer github pages repo, commits, and pushes)
imex_ems_deploy: imex_ems_build
    ./ci_scripts/imex_ems_deploy.sh

# Reattach all submodules to branches and remotes (fork + official)
ext_reattach:
    python -c "import sys; sys.path.append('external'); from bindings_generation import all_external_libraries; all_external_libraries.reattach_all_submodules()"


# Push a new tag to the imgui fork repository with the current date
imgui_tag:
    cd external/imgui/imgui && git tag `date +'bundle_%Y%m%d'` && git push fork --tags

# Push a new tag to the imgui_test_engine fork repository with the current date
imgui_te_tag:
    cd external/imgui_test_engine/imgui_test_engine && git tag `date +'bundle_%Y%m%d'` && git push fork --tags

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

# Build the doc in interactive mode (for dev)
doc_serve_interactive:
    cd docs/book && jupyter-book start

# Serve the static built doc
doc_serve_static:
    cd docs/book/_build/html && python -m http.server 7005

# Build the doc in static html
doc_build_static:
    cd docs/book && jupyter-book build --html
    echo "Doc built in docs/book/_build/html"
    echo "You can serve it with:"
    echo "\n  cd docs/book/_build/html && python -m http.server 7005"
    echo "\nOr just run:\n\n  just doc_serve_static\n"

# Build bundle doc in pdf, copy the pdf to the ramdisk
doc_build_pdf:
    cd docs/book && jupyter-book build --pdf

# ==============================================================
# Pyodide build targets
# ==============================================================
# Note: see ci_scripts/pyodide_local_build/Readme.md
# for more info about the local pyodide build setup
# --------------------------------------------------------------

# Build pyodide wheel (excludes demos to reduce size)
pyodide_build: pyodide_clean
    source ci_scripts/pyodide_local_build/venv_pyo/bin/activate && source ci_scripts/pyodide_local_build/emsdk/emsdk_env.sh && IMGUI_BUNDLE_EXCLUDE_DEMOS=1 pyodide build
    cp dist/imgui_bundle*pyodide*.whl ci_scripts/pyodide_local_build/test_browser/local_wheels/

# Start browser test server (serves test HTML pages)
pyodide_test_serve:
    ./ci_scripts/pyodide_local_build/test_browser/run_server.sh

# Clean pyodide build artifacts
pyodide_clean:
    rm -rf .pyodide_build
    rm -f ci_scripts/pyodide_local_build/test_browser/local_wheels/imgui_bundle*pyodide*.whl
    rm -f dist/imgui_bundle*pyodide*.whl

# Install the tools to build pyodide wheels locally (pyodide-build, emsdk, etc.)
pyodide_setup_local_build:
    ./ci_scripts/pyodide_local_build/setup_pyodide_local_build.sh
    ./ci_scripts/pyodide_local_build/test_browser/download_pyodide_dist.sh

# pyodide deep clean (removes also the local build setup)
pyodide_deep_clean: pyodide_clean
    rm -rf ci_scripts/pyodide_local_build/test_browser/pyodide_dist
    rm -rf ci_scripts/pyodide_local_build/venv_pyo
    rm -rf ci_scripts/pyodide_local_build/emsdk

