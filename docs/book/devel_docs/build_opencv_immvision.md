# OpenCV builds for immvision

Immvision requires a minimalist static OpenCV (only `core`, `imgcodecs`, `imgproc`).
How OpenCV is obtained depends on the platform. This document is the central reference
for all OpenCV build/download strategies.

**When updating the OpenCV version**, check all the locations listed below.


## Overview by platform

| Platform | Strategy | Where |
|----------|----------|-------|
| Linux CI wheels | Pre-built once per container via `before-all` | `build_opencv.sh` |
| Windows CI wheels | Pre-built once per runner via `before-all` (Git Bash) | `build_opencv.sh` |
| Linux/macOS local `pip install` | Built from source at configure time | `find_opencv.cmake` → `immvision_fetch_opencv_from_source()` |
| Windows x64 local `pip install` | Precompiled `opencv_world.dll` (fallback: source build) | `find_opencv.cmake` → `immvision_download_opencv_official_package_win()` |
| Windows ARM64 local `pip install` | Built from source (precompiled x64 package skipped) | `find_opencv.cmake` → `immvision_fetch_opencv_from_source()` |
| Emscripten | Precompiled package downloaded | `find_opencv.cmake` → `immvision_download_emscripten_precompiled_opencv_4_9_0()` |
| Emscripten (rebuild) | Manual build, upload as release asset | See [Rebuilding emscripten package](#rebuilding-the-emscripten-precompiled-package) below |


## Key files

- **`external/immvision/immvision/cmake/build_opencv.sh`** — Single bash script that downloads, builds, and installs
  minimalist static OpenCV. Used by both CI (`before-all`) and CMake (called at configure
  time via `execute_process`). This is the **single source of truth** for the minimalist
  build flags and the OpenCV version used in source builds. Supports `--full` flag for
  non-minimalist builds.

- **`external/immvision/immvision/cmake/find_opencv.cmake`** — CMake entry point.
  `immvision_find_opencv()` tries `find_package(OpenCV)` first (succeeds when CI has
  pre-built it), then falls back to platform-specific strategies. On Linux/macOS, the
  fallback calls `build_opencv.sh` via bash. On Windows x64, it tries a precompiled
  `opencv_world.dll` first, then falls back to source build. On Windows ARM64, it skips
  the precompiled x64 package and goes straight to source build.

- **`pyproject.toml`** — cibuildwheel config:
  - `[tool.cibuildwheel.linux]`: `before-all` runs the script, `environment` sets `CMAKE_PREFIX_PATH`
  - `[tool.cibuildwheel.windows]`: same script via Git Bash, `environment` sets `CMAKE_PREFIX_PATH` + `OpenCV_STATIC`
  - `CMAKE_PREFIX_PATH` is used instead of `OpenCV_DIR` because the install layout
    varies by MSVC version; `find_package` searches standard subdirectories under the prefix.

- **`docs/book/devel_docs/oldies/emscripten_build.md`** — Redirects here for OpenCV.


## Version and URL locations

When bumping the OpenCV version, update these locations:

| What | File | What to change |
|------|------|----------------|
| Source build version (all platforms) | `external/immvision/immvision/cmake/build_opencv.sh` | `OPENCV_VERSION` variable |
| Windows precompiled URL (fallback) | `find_opencv.cmake` | URL + MD5 in `immvision_download_opencv_official_package_win()` |
| Emscripten precompiled URL | `find_opencv.cmake` | URL + MD5 in `immvision_download_emscripten_precompiled_opencv_4_9_0()` |

Note: the Windows fallback package (`opencv_world.dll`) and emscripten precompiled packages
have **their own version lifecycle**. They don't need to match the source build version —
they are updated separately when new precompiled packages are built and uploaded as GitHub
release assets. The Windows fallback is only used for local `pip install` on Windows
(CI wheels use the static pre-build instead).


## How the CI pre-build works (Linux and Windows)

Without pre-building, OpenCV is compiled from source for **each** Python version
(~4 times per runner), which is the main build time bottleneck.

The fix uses cibuildwheel's `before-all` to build OpenCV once per runner/container:
1. `before-all` in `pyproject.toml` runs `external/immvision/immvision/cmake/build_opencv.sh <install_dir>`
2. The script downloads the OpenCV tarball, builds minimalist static OpenCV, and installs it
3. `environment` sets `OpenCV_DIR` (and `OpenCV_STATIC` on Windows)
4. Each Python wheel build's `find_package(OpenCV)` finds the pre-built install and
   skips building from source entirely

On Linux, this applies to both manylinux and musllinux containers (each has its own
`before-all`). On Windows, Git Bash (from Git for Windows, pre-installed on GitHub
Actions runners) is used to run the same bash script.


## Windows: static vs DLL

Previously, Windows wheels shipped a precompiled `opencv_world.dll` (~50MB), making
wheels ~25MB vs ~11MB on macOS/Linux. The CI pre-build strategy builds OpenCV 4.13.0
statically instead, linking it into `_imgui_bundle.pyd` with no DLL needed. OpenCV 4.13.0
is required because it recognizes MSVC 1950+ (Visual Studio 18/2025, `vc18` runtime).

The DLL handling code in `find_opencv.cmake` (glob for `opencv_world*.dll`, install to
wheel, `IMMVISION_OPENCV_WORLD_DLL` cache variable) degrades gracefully: when OpenCV is
static, no DLLs are found and the entire chain is a no-op.

For C++ app deployment (`imgui_bundle_add_app.cmake`), the `IMMVISION_OPENCV_WORLD_DLL`
copy-to-output logic is similarly a no-op when no DLL exists.


## Windows ARM64 local builds

On ARM64 Windows, the precompiled x64 `opencv_world.dll` package is skipped automatically
(detected via `CMAKE_SYSTEM_PROCESSOR`). The build goes straight to `build_opencv.sh`,
which compiles OpenCV from source with the correct VS generator and architecture.

SIMD is disabled globally (`-DWITH_SIMD=OFF` in `build_opencv.sh`) to avoid
cross-compilation mismatches (ARM NEON headers vs x64 compiler). The performance impact
is negligible for the minimalist OpenCV (image loading only).


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
