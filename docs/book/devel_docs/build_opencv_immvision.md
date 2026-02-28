# OpenCV builds for immvision

Immvision requires a minimalist static OpenCV (only `core`, `imgcodecs`, `imgproc`).
How OpenCV is obtained depends on the platform. This document is the central reference
for all OpenCV build/download strategies.

**When updating the OpenCV version**, check all the locations listed below.


## Overview by platform

| Platform | Strategy | Where |
|----------|----------|-------|
| Linux CI wheels | Pre-built once per container via `before-all` | `ci/build_opencv_for_ci.sh` |
| Windows CI wheels | Pre-built once per runner via `before-all` | `ci/build_opencv_for_ci_win.ps1` |
| Linux/macOS local `pip install` | Built from source via FetchContent | `find_opencv.cmake` → `immvision_fetch_opencv_from_source()` |
| Windows local `pip install` | Precompiled `opencv_world.dll` downloaded (fallback) | `find_opencv.cmake` → `immvision_download_opencv_official_package_win()` |
| Emscripten | Precompiled package downloaded | `find_opencv.cmake` → `immvision_download_emscripten_precompiled_opencv_4_9_0()` |
| Emscripten (rebuild) | Manual build, upload as release asset | See [Rebuilding emscripten package](#rebuilding-the-emscripten-precompiled-package) below |


## Key files

- **`external/immvision/immvision/cmake/find_opencv.cmake`** — Main cmake logic. Contains:
  - Minimalist cmake flags for source builds (Linux/macOS)
  - Download URLs and hashes for Windows and emscripten precompiled packages
  - The `immvision_find_opencv()` entry point called by the main build

- **`ci/build_opencv_for_ci.sh`** — Shell script run by cibuildwheel `before-all` on Linux.
  Builds OpenCV once per container so all Python versions reuse it.
  **The cmake flags are duplicated from `find_opencv.cmake`** — keep them in sync.

- **`ci/build_opencv_for_ci_win.ps1`** — PowerShell script, same role on Windows.
  Builds static OpenCV (no `opencv_world.dll`), making Windows wheels ~14MB smaller.
  **The cmake flags are duplicated from `find_opencv.cmake`** — keep them in sync.

- **`pyproject.toml`** — cibuildwheel config:
  - `[tool.cibuildwheel.linux]`: `before-all` calls the Linux script, `environment` sets `OpenCV_DIR`
  - `[tool.cibuildwheel.windows]`: `before-all` calls the Windows script, `environment` sets `OpenCV_DIR` + `OpenCV_STATIC`

- **`docs/book/devel_docs/oldies/emscripten_build.md`** — Redirects here.


## Version and URL locations

When bumping the OpenCV version, update these locations:

| What | File | What to change |
|------|------|----------------|
| Source build version (Linux/macOS) | `find_opencv.cmake` | `GIT_TAG` in `FetchContent_Declare(OpenCV_Fetch ...)` |
| CI pre-build version (Linux) | `ci/build_opencv_for_ci.sh` | `OPENCV_VERSION` variable |
| CI pre-build version (Windows) | `ci/build_opencv_for_ci_win.ps1` | `$OPENCV_VERSION` variable |
| Windows precompiled URL (fallback) | `find_opencv.cmake` | URL + MD5 in `immvision_download_opencv_official_package_win()` |
| Emscripten precompiled URL | `find_opencv.cmake` | URL + MD5 in `immvision_download_emscripten_precompiled_opencv_4_9_0()` |

Note: the Windows fallback package (`opencv_world.dll`) and emscripten precompiled packages
have **their own version lifecycle**. They don't need to match the source build version —
they are updated separately when new precompiled packages are built and uploaded as GitHub
release assets. The Windows fallback is only used for local `pip install` on Windows
(CI wheels use the static pre-build instead).


## Linux CI: how the pre-build works

On Linux, cibuildwheel runs all Python version builds (3.11–3.14) inside a single Docker
container. Without pre-building, OpenCV is compiled from source for **each** Python version
(~4 times), which is the main bottleneck (~1h20m total).

The fix:
1. `before-all` in `pyproject.toml` runs `ci/build_opencv_for_ci.sh`
2. The script downloads the OpenCV tarball, builds, and installs to `/opt/opencv_minimalist/`
3. `environment = { OpenCV_DIR = "..." }` tells cmake where to find it
4. Each Python wheel build's `find_package(OpenCV)` finds the pre-built install and
   skips `immvision_fetch_opencv_from_source()` entirely

This applies to both manylinux and musllinux containers (each has its own `before-all`).


## Windows CI: static build instead of opencv_world.dll

Previously, Windows wheels downloaded a precompiled `opencv_world.dll` (~50MB) and
shipped it inside the wheel, resulting in ~25MB wheels vs ~11MB on macOS/Linux.

The fix uses the same `before-all` strategy as Linux:
1. `before-all` in `pyproject.toml` runs `ci/build_opencv_for_ci_win.ps1`
2. The script downloads OpenCV source, builds a minimalist static version with MSVC,
   and installs to `C:\opencv_minimalist`
3. `environment` sets `OpenCV_DIR` and `OpenCV_STATIC=ON`
4. Each Python wheel build's `find_package(OpenCV)` finds the pre-built static install
5. OpenCV is linked statically into `_imgui_bundle.pyd` — no DLL needed

The `opencv_world.dll` download (`immvision_download_opencv_official_package_win()`) is
still available as a fallback for local `pip install` on Windows where no pre-built
static install exists.

The DLL handling code in `find_opencv.cmake` (glob for `opencv_world*.dll`, install to
wheel, `IMMVISION_OPENCV_WORLD_DLL` cache variable) degrades gracefully: when OpenCV is
static, no DLLs are found and the entire chain is a no-op.


## Rebuilding the emscripten precompiled package

The emscripten builds use precompiled OpenCV packages downloaded from GitHub release assets.
To rebuild these packages:

### References

- https://docs.opencv.org/3.4/d4/da1/tutorial_js_setup.html
- https://www.ubble.ai/how-to-make-opencv-js-work/
- https://answers.opencv.org/question/212376/how-to-decode-an-image-using-emscripten/

### Steps

1. Clone and checkout the desired OpenCV version:

```bash
git clone https://github.com/opencv/opencv.git
cd opencv
git checkout 4.11.0
cd ..
```

2. Manually edit `opencv/CMakeLists.txt` and add:

```cmake
add_compile_options(-pthread)
add_link_options(-pthread)
```

For pyodide, also add:
```cmake
add_compile_options(
  "-fwasm-exceptions"
  "-sSUPPORT_LONGJMP"
)
add_link_options(
  "-fwasm-exceptions"
  "-sSUPPORT_LONGJMP"
)
```

Note: to compile without pthread support, remove `-pthread` below and replace
*twice* `-s USE_PTHREADS=1` by `-s USE_PTHREADS=0`.

3. Use the following makefile (or justfile) to compile:

```makefile
default:
    echo "Nothing for default"

clean:
    rm -rf build opencv_emscripten_install

call_cmake:
    mkdir -p build && \
    cd build && \
    export EMSDK=~/emsdk && \
    source ~/emsdk/emsdk_env.sh && \
    export OPENCV_SRC=$(pwd)/../opencv && \
    export OPENCV_INSTALL=$(pwd)/../opencv_emscripten_install && \
    export TOOLCHAIN=$EMSDK/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake && \
    export PYTHON_EXE=$(which python3) && \
    \
    emcmake cmake \
    -S ../opencv -B . \
    -DPYTHON_DEFAULT_EXECUTABLE=$PYTHON_EXE \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=$OPENCV_INSTALL \
    -DCMAKE_TOOLCHAIN_FILE=$TOOLCHAIN \
    \
    \"-DCMAKE_C_FLAGS='-pthread -s WASM=1 -s USE_PTHREADS=1 ' \"  \
    \
    \"-DCMAKE_CXX_FLAGS='-pthread -s WASM=1 -s USE_PTHREADS=1 ' \" \
    -DCPU_BASELINE='' -DCPU_DISPATCH='' -DENABLE_PIC=ON -DCV_TRACE=OFF -DBUILD_SHARED_LIBS=OFF -DWITH_1394=OFF -DWITH_ADE=OFF -DWITH_VTK=OFF -DWITH_EIGEN=OFF -DWITH_FFMPEG=OFF -DWITH_GSTREAMER=OFF -DWITH_GTK=OFF -DWITH_GTK_2_X=OFF -DWITH_IPP=OFF -DWITH_JASPER=OFF -DWITH_JPEG=ON -DWITH_WEBP=OFF -DWITH_OPENEXR=OFF -DWITH_OPENGL=OFF -DWITH_OPENVX=OFF -DWITH_OPENNI=OFF -DWITH_OPENNI2=OFF -DWITH_PNG=ON -DWITH_TBB=OFF -DWITH_TIFF=OFF -DWITH_V4L=OFF -DWITH_OPENCL=OFF -DWITH_OPENCL_SVM=OFF -DWITH_OPENCLAMDFFT=OFF -DWITH_OPENCLAMDBLAS=OFF -DWITH_GPHOTO2=OFF -DWITH_LAPACK=OFF -DWITH_ITT=OFF -DWITH_QUIRC=OFF -DWITH_PROTOBUF=OFF -DBUILD_ZLIB=ON -DBUILD_opencv_apps=OFF -DBUILD_opencv_calib3d=OFF -DBUILD_opencv_dnn=OFF -DBUILD_opencv_features2d=OFF -DBUILD_opencv_flann=OFF -DBUILD_opencv_gapi=OFF -DBUILD_opencv_ml=OFF -DBUILD_opencv_photo=OFF -DBUILD_opencv_imgcodecs=ON -DBUILD_opencv_shape=OFF -DBUILD_opencv_videoio=OFF -DBUILD_opencv_videostab=OFF -DBUILD_opencv_highgui=OFF -DBUILD_opencv_superres=OFF -DBUILD_opencv_stitching=OFF -DBUILD_opencv_java=OFF -DBUILD_opencv_js=OFF -DBUILD_opencv_python2=OFF -DBUILD_opencv_python3=OFF -DBUILD_EXAMPLES=OFF -DBUILD_PACKAGE=OFF -DBUILD_TESTS=OFF -DBUILD_PERF_TESTS=OFF -DBUILD_DOCS=OFF -DWITH_PTHREADS_PF=OFF -DCV_ENABLE_INTRINSICS=OFF -DBUILD_WASM_INTRIN_TESTS=OFF

build: call_cmake
    cd build && \
    make && \
    make install

tgz: build
    tar -czvf opencv_4.11_wasmexcept_pthread_fpic_emscripten_minimalist_install.tgz opencv_emscripten_install

all: tgz
    md5 opencv_4.11_wasmexcept_pthread_fpic_emscripten_minimalist_install.tgz
```

4. Upload the `.tgz` to a GitHub release, then update the URL and MD5 hash in
   `find_opencv.cmake` → `immvision_download_emscripten_precompiled_opencv_4_9_0()`.
