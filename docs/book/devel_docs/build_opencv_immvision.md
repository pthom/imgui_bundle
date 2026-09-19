# OpenCV builds for immvision

ImmVision does not use OpenCV, and never links it: it works standalone with its own `ImageBuffer` type.
The Python bindings and the wheels do not use OpenCV at all.

`cv::Mat` interop is a choice of each C++ application: it defines `IMMVISION_HAS_OPENCV` (which
enables header-only conversions in `immvision_types.h`) and links OpenCV by itself:

```cmake
find_package(OpenCV REQUIRED)
target_compile_definitions(my_app PRIVATE IMMVISION_HAS_OPENCV)
target_link_libraries(my_app PRIVATE opencv_core)
```

In this repository, only some C++ demos do this, when `IMGUI_BUNDLE_DEMOS_WITH_OPENCV=ON`
(they then show more image processing: Sobel, blur, etc.).

`IMMVISION_FETCH_OPENCV=ON` is a convenience which provides a minimalist static OpenCV
(only `core`, `imgcodecs`, `imgproc`) when `find_package(OpenCV)` fails. It does not change how
ImmVision is built. How OpenCV is obtained depends on the platform: this document is the central
reference for these strategies.

**When updating the OpenCV version**, check all the locations listed below.


## Overview by platform (with `IMMVISION_FETCH_OPENCV=ON`)

| Platform | Strategy | Where |
|----------|----------|-------|
| Linux/macOS | Built from source at configure time | `fetch_opencv.cmake` → `immvision_fetch_opencv_from_source()` |
| Windows x64 | Precompiled `opencv_world.dll` (fallback: source build) | `fetch_opencv.cmake` → `immvision_download_opencv_official_package_win()` |
| Windows ARM64 | Built from source (precompiled x64 package skipped) | `fetch_opencv.cmake` → `immvision_fetch_opencv_from_source()` |
| Emscripten | Precompiled package downloaded | `fetch_opencv.cmake` → `immvision_download_emscripten_precompiled_opencv_4_9_0()` |
| Emscripten (rebuild) | Manual build, upload as release asset | See [Rebuilding emscripten package](#rebuilding-the-emscripten-precompiled-package) below |


## Key files

- **`external/immvision/immvision/cmake/build_opencv.sh`**: bash script that downloads, builds, and installs
  a minimalist static OpenCV. Called by CMake at configure time via `execute_process`. This is the
  **single source of truth** for the minimalist build flags and the OpenCV version used in source
  builds. Supports a `--full` flag for non-minimalist builds.

- **`external/immvision/immvision/cmake/fetch_opencv.cmake`**: CMake entry point.
  `immvision_fetch_opencv()` tries `find_package(OpenCV)` first, then falls back to
  platform-specific strategies (see the table above). It sets `OpenCV_DIR` in the cache, so that
  the `find_package(OpenCV)` of the demos succeeds.

- **`bindings/imgui_bundle/demos_cpp/demos_immvision/CMakeLists.txt`**: where the demos define
  `IMMVISION_HAS_OPENCV` and link OpenCV.


## Version and URL locations

When bumping the OpenCV version, update these locations:

| What | File | What to change |
|------|------|----------------|
| Source build version (all platforms) | `external/immvision/immvision/cmake/build_opencv.sh` | `OPENCV_VERSION` variable |
| Windows precompiled URL (fallback) | `fetch_opencv.cmake` | URL + MD5 in `immvision_download_opencv_official_package_win()` |
| Emscripten precompiled URL | `fetch_opencv.cmake` | URL + MD5 in `immvision_download_emscripten_precompiled_opencv_4_9_0()` |

Note: the Windows fallback package (`opencv_world.dll`) and emscripten precompiled packages
have **their own version lifecycle**. They don't need to match the source build version:
they are updated separately when new precompiled packages are built and uploaded as GitHub
release assets.


## Windows: opencv_world.dll

When the precompiled Windows package is used, C++ apps need `opencv_world*.dll` next to their exe.
`fetch_opencv.cmake` publishes its path in the `IMMVISION_OPENCV_WORLD_DLL` cache variable, and
`imgui_bundle_add_app.cmake` copies it to the output folder. When OpenCV is static, no DLL is
found and this is a no-op.


## Windows ARM64 local builds

On ARM64 Windows, the precompiled x64 `opencv_world.dll` package is skipped automatically
(detected via `CMAKE_SYSTEM_PROCESSOR`). The build goes straight to `build_opencv.sh`,
which compiles OpenCV from source with the correct VS generator and architecture.

SIMD is disabled globally (`-DWITH_SIMD=OFF` in `build_opencv.sh`) to avoid
cross-compilation mismatches (ARM NEON headers vs x64 compiler). The performance impact
is negligible for the minimalist OpenCV (image loading only).


(rebuilding-the-emscripten-precompiled-package)=
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
    tar -czvf opencv_4.11_pthread_fpic_emscripten_minimalist_install.tgz opencv_emscripten_install

all: tgz
    md5 opencv_4.11_pthread_fpic_emscripten_minimalist_install.tgz
```

4. Upload the `.tgz` to a GitHub release, then update the URL and MD5 hash in
   `fetch_opencv.cmake` → `immvision_download_emscripten_precompiled_opencv_4_9_0()`.
