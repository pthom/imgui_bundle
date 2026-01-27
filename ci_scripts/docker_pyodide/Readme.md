# Docker Pyodide Build Environment for imgui-bundle

This directory contains a Docker-based build environment for compiling imgui-bundle for Pyodide (Python in WebAssembly).

## Why Docker?

Building imgui-bundle for Pyodide requires Linux due to a limitation in scikit-build-core on macOS. This Docker environment provides a consistent Linux build environment that works on any host OS.

## Initial checks

- Edit Dockerfile and set PYODIDE_VERSION and PYTHON_VERSION if needed.
- The version number for imgui_bundle in ci_scripts/docker_pyodide/docker_pyodide_resources/pyo_recipes_package_imgui_bundle.yml should match the version in pyproject.toml.


## Prerequisites

- Docker installed and running
- Sufficient disk space (~10GB for the full Pyodide build)
- Time for initial build (~30-60 minutes depending on your machine)


## Directory Structure

```
ci_scripts/docker_pyodide/
├── Dockerfile                      # Docker image definition
├── docker_pyodide.py               # Container management script
├── docker_pyodide_resources/       # Resources copied into container
│   ├── build_imgui_bundle.sh       # Build script (runs inside container)
│   ├── pyo_recipes_package_imgui_bundle.yml  # meta.yaml template
│   └── imgui_bundle_sdist/         # Clean source (created at build time, gitignored)
├── test_pyodide.html               # Browser test page
├── serve_test.py                   # Local test server with CORS
├── Readme.md                       # This file
└── output/                         # Build artifacts (created at runtime)
    ├── imgui_bundle-*.whl          # Built wheel
    └── pyodide_dist/               # Pyodide runtime files
```

## Typical Workflow

See help message for `docker_pyodide.py`:

```
    Docker image and container management:
        docker_pyodide.py recreate_all:      - remove and recreate image and container

        docker_pyodide.py create_image       - Build or update Docker image (long!)
        docker_pyodide.py remove_image       - Remove Docker image
        docker_pyodide.py create_container   - Create container
        docker_pyodide.py remove_container   - Remove container

    Build  and test:
        docker_pyodide.py build              - Build imgui-bundle wheel
        docker_pyodide.py serve              - Start local test server (to test the wheel in a browser)
        docker_pyodide.py check_version      - Check version consistency (between pyproject.toml and meta.yaml)

    Interactive:
        docker_pyodide.py bash               - Start interactive bash session
        docker_pyodide.py exec <cmd>         - Execute command in container


Typical workflow:
1. docker_pyodide.py recreate_all # only first time or after Dockerfile changes
2. docker_pyodide.py build
3. docker_pyodide.py serve
```

## How It Works

1. **Docker Image**: Contains Ubuntu 24.04 with Python 3.13, Pyodide (with emsdk), pyodide-recipes, and all build dependencies.

2. **Source Distribution**:
   - When you run `build`, the script creates a source distribution (sdist) from your repository
   - This sdist respects `sdist.exclude` patterns in `pyproject.toml`, excluding virtualenvs and build artifacts
   - The sdist is extracted to `docker_pyodide_resources/imgui_bundle_sdist/`
   - This clean directory is **copied** into the container at `/mnt/imgui_bundle_sdist`

   _Why Use Source Distribution (sdist)?_
   Pyodide's build system uses `shutil.copytree()` to copy source files. When building from a repository containing Python virtualenvs (like `v314/` or `venv_test/`), this fails because virtualenvs contain symlinks to Python executables that exist outside the mounted directory.
  _Our solution:_
  Create a source distribution (sdist) using `python -m build --sdist`; 
  extract the clean tarball to `docker_pyodide_resources/imgui_bundle_sdist/`;
  then copy this clean directory into the container at `/mnt/imgui_bundle_sdist`

This approach is **simple, fast (~2-3 seconds), and includes uncommitted changes** from your working tree.

**Note**: We copy instead of mount because Docker volumes are bound at container creation time and don't reflect subsequent host changes.

   
3. **Volume Mounts**:
   - `output/` → `/mnt/output`: Build artifacts (mounted)

4. **Build Process**:
   - Validates version consistency between `pyproject.toml` and `meta.yaml`
   - Creates and copies clean source distribution into container
   - Runs `pyodide build-recipes imgui-bundle`
   - Copies wheel to `output/`

## Version Management

The version in `docker_pyodide_resources/pyo_recipes_package_imgui_bundle.yml` must match
the version in `pyproject.toml`. The `build` command checks this automatically.

```bash
# Check versions
python3 docker_pyodide.py check_version

# Fix version mismatch (updates meta.yaml to match pyproject.toml)
python3 docker_pyodide.py check_version --fix
```

## Testing the Built Package

After building:

```bash
python3 docker_pyodide.py serve
```

Open http://localhost:8000/test_pyodide.html in your browser.

## Rebuilding After Code Changes

When you make changes to imgui-bundle, the `build` command will:
1. Create a fresh source distribution from your current working tree (including uncommitted changes)
2. Extract it to `docker_pyodide_resources/imgui_bundle_sdist/`
3. Build using this clean source

Just run:

```bash
python3 docker_pyodide.py build
```

## Troubleshooting

### Need to inspect the container
Use `python3 docker_pyodide.py bash` for an interactive shell.

### Checking build logs
Build output is shown in real-time. For the container's pyodide directory:
```bash
python3 docker_pyodide.py exec "ls -la /opt/pyodide/dist"
```

## Notes

- The initial Docker build takes a long time because it compiles Pyodide from source
- Subsequent builds are much faster as the Pyodide environment is cached in the container
- The wheel is platform-independent (wasm32) and works on any browser supporting WebAssembly

