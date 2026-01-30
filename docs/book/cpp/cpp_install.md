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
cmake .. -DIMMVISION_FETCH_OPENCV=ON # (2)
make -j
```

(1) Since there are lots of submodules, this might take a few minutes

(2) The flag -DIMMVISION_FETCH_OPENCV=ON is optional. If set, a minimal version of OpenCV will be downloaded a compiled at this stage (this might require a few minutes)

The immvision module will only be built if OpenCV can be found. Otherwise, it will be ignored, and no error will be emitted.

If you have an existing OpenCV install, set its path via:

```bash
cmake .. -DOpenCV_DIR=/.../path/to/OpenCVConfig.cmake
```

:::{tip}
There are lots of CMake options to customize the build. See [CMakeLists.txt](https://github.com/pthom/imgui_bundle/blob/main/CMakeLists.txt)
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

