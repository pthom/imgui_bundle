# ci_scripts/ — CI/CD scripts

Scripts and configuration for continuous integration, deployment, and local build environments.

**Contents:**
- `docker_ubuntu_dev/` — Docker development environment for Linux builds
- `pyodide_local_build/` — Local Pyodide build setup (emsdk, test browser, recipes)
- `webserver_multithread_policy.py` — Local web server with CORS for Emscripten testing
- `imex_ems_deploy.sh` — Deploy ImGui Explorer to GitHub Pages

**CI workflows** are in `.github/workflows/` (see [Testing](../docs/book/devel_docs/testing.md) for an overview).
