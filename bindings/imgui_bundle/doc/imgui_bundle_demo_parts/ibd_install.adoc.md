# Build and install instructions

## Install for Python

### Install from pypi

``` bash
pip install imgui-bundle
pip install opencv-contrib-python 
```

-   in order to run the immvision module, install opencv-python or opencv-contrib-python

Note: under windows, you might need to install [msvc redist](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#visual-studio-2015-2017-2019-and-2022).

### Install from source:

``` bash
git clone https://github.com/pthom/imgui_bundle.git
cd imgui_bundle
git submodule update --init --recursive 
pip install -v . 
pip install opencv-contrib-python
```

-   Since there are lots of submodules, this might take a few minutes

-   The build process might take up to 5 minutes

### Run the python demo

Simply run `demo_imgui_bundle`.

The source for the demos can be found inside [bindings/imgui_bundle/demos_python](https://github.com/pthom/imgui_bundle/tree/doc/bindings/imgui_bundle/demos_python).

::: tip
Consider `demo_imgui_bundle` as an always available manual for Dear ImGui Bundle with lots of examples and related code source.
:::

## Install for C++

### Integrate Dear ImGui Bundle in your own project in 5 minutes

The easiest way to use Dear ImGui Bundle in an external project is to use the example provided in [example_integration](https://github.com/pthom/imgui_bundle/tree/doc/_example_integration). This folder includes everything you need to set up your own project.

### Build from source

If you choose to clone this repo, follow these instructions:

``` bash
git clone https://github.com/pthom/imgui_bundle.git
cd imgui_bundle
git submodule update --init --recursive 
mkdir build
cd build
cmake .. -DIMMVISION_FETCH_OPENCV=ON 
make -j
```

-   Since there are lots of submodules, this might take a few minutes

-   The flag `-DIMMVISION_FETCH_OPENCV=ON` is optional. If set, a minimal version of OpenCV will be downloaded a compiled at this stage (this might require a few minutes)

The `immvision` module will only be built if OpenCV can be found. Otherwise, it will be ignored, and no error will be emitted.

If you have an existing OpenCV install, set its path via:

``` bash
cmake .. -DOpenCV_DIR=/.../path/to/OpenCVConfig.cmake
```

### Run the C++ demo

If you built ImGuiBundle from source, Simply run `build/bin/demo_imgui_bundle`.

The source for the demos can be found inside [bindings/imgui_bundle/demos_cpp](https://github.com/pthom/imgui_bundle/tree/doc/bindings/imgui_bundle/demos_cpp/).

::: tip
Consider `demo_imgui_bundle` as a manual with lots of examples and related code source. It is always [available online](https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html)
:::
