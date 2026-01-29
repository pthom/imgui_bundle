# Misc development utilities


# List all the targets in the justfile
default:
    @just --list

# build emscripten
ems_build:
    ./ci_scripts/ems_build.sh

ems_deploy:
    ./ci_scripts/ems_deploy.sh

# Serve emscripten with CORS
ems_serve:
    python ./ci_scripts/webserver_multithread_policy.py


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

# Build hello_imgui doc in pdf, copy the pdf to the ramdisk
doc_him_pdf:
    cd external/hello_imgui/hello_imgui/docs_src && jupyter-book build --builder pdfhtml .
    cp external/hello_imgui/hello_imgui/docs_src/_build/pdf/book.pdf /Volumes/ramdisk/hello_imgui_manual.pdf



# ==============================================================
# Pyodide build targets
# ==============================================================
# Note: see ci_scripts/pyodide_local_build/Readme.md
# for more info about the local pyodide build setup
# --------------------------------------------------------------

# Build pyodide wheel (with macOS naming fix workaround)
pyodide_build:
    source ci_scripts/pyodide_local_build/venv_pyo/bin/activate && source ci_scripts/pyodide_local_build/emsdk/emsdk_env.sh && pyodide build
    python ci_scripts/pyodide_local_build/fix_pyodide_wheel_name.py
    cp dist/imgui_bundle*pyodide*.whl ci_scripts/pyodide_local_build/test_browser/local_wheels/

# Start browser test server (serves test HTML pages)
pyodide_test_serve:
    ./ci_scripts/pyodide_local_build/test_browser/run_server.sh

# Clean pyodide build artifacts
pyodide_clean:
    rm -rf .pyodide_build dist

# Install the tools to build pyodide wheels locally (pyodide-build, emsdk, etc.)
pyodide_setup_local_build:
    ./ci_scripts/pyodide_local_build/setup_pyodide_local_build.sh
    ./ci_scripts/pyodide_local_build/test_browser/download_pyodide_dist.sh

# pyodide deep clean (removes also the local build setup)
pyodide_deep_clean: pyodide_clean
    rm -rf ci_scripts/pyodide_local_build/test_browser/pyodide_dist
    rm -rf ci_scripts/pyodide_local_build/venv_pyo
    rm -rf ci_scripts/pyodide_local_build/emsdk

