# C++ Installation

## Integrate Dear ImGui Bundle in your own project in 5 minutes

The easiest way to use Dear ImGui Bundle in an external project is to use the template available at https://github.com/pthom/imgui_bundle_template.

This template includes everything you need to set up your own project.

## Build from source

If you choose to clone this repo, follow these instructions:

```bash
git clone https://github.com/pthom/imgui_bundle.git
cd imgui_bundle
git submodule update --init --recursive # (1)
mkdir build
cd build
cmake ..
make -j
```

(1) Since there are lots of submodules, this might take a few minutes

:::{tip}
ImmVision works out of the box without OpenCV. If you need OpenCV interop (e.g. `cv::Mat` support), you can optionally pass `-DIMMVISION_FETCH_OPENCV=ON` to download and build a minimal OpenCV, or point to an existing install with `-DOpenCV_DIR=/.../path/to/OpenCVConfig.cmake`.
:::

:::{tip}
There are lots of CMake options to customize the build. See [CMakeLists.txt](https://github.com/pthom/imgui_bundle/blob/main/CMakeLists.txt)
:::

## Install as a CMake package

Dear ImGui Bundle can be installed with `cmake --install`, and then used from another project
with `find_package(imgui_bundle)` (this is also the basis for package managers such as Conan).
The `cpp_package` preset builds the C++ libraries (without the demos) and installs them into `builds/cpp_package/install`:

```bash
cmake --preset cpp_package
cmake --build builds/cpp_package/build --config Release
cmake --install builds/cpp_package/build --config Release
```

Then, in your project (see the [template](https://github.com/pthom/imgui_bundle_template) for a complete example):

```cmake
find_package(imgui_bundle CONFIG REQUIRED)  # cmake -DCMAKE_PREFIX_PATH=/path/to/imgui_bundle/builds/cpp_package/install
imgui_bundle_add_app(my_app my_app.cpp)
```

:::{note}
Install into an empty prefix. When a library such as glfw or freetype is not found on the system, it is downloaded
and installed along with the package; if you configure again while a previous install sits in the prefix,
`find_package` would find those libraries there and take them for system libraries. The `cpp_package` preset
prevents this by setting `CMAKE_FIND_NO_INSTALL_PREFIX=ON`; do the same if you configure by hand.
:::

## Run the C++ demo

If you built ImGuiBundle from source, Simply run build/bin/demo_imgui_bundle.

The source for the demos can be found inside bindings/imgui_bundle/demos_cpp.

:::{tip}
Consider demo_imgui_bundle as a manual with lots of examples and related code source. It is always available online
:::

## Multiplatform applications

Hello ImGui and Dear ImGui Bundle offer excellent support for multiplatform applications (Windows, macOS, Linux, iOS, Android, and Emscripten).

See this tutorial video for Hello ImGui:

<a href="https://www.youtube.com/watch?v=dArP4lBnOr8">
<img src="video_multiplatform.png" alt="Multiplatform tutorial video" width="600"/>
</a>

:::{tip}
The principle with Dear ImGui Bundle is the same as described in the video, just use the dedicated [Dear ImGui Bundle project template](https://github.com/pthom/imgui_bundle_template), and use `imgui_bundle_add_app` in your CMakeLists.txt.
:::

