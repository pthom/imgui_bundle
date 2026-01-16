# Install for Python

## Install from pypi

```bash
# Minimal install
pip install imgui-bundle

# or to get all optional features:
pip install "imgui-bundle[full]"
```

Binary wheels are available for Windows, macOS and Linux. If a compilation from source is needed, the build process might take up to 5 minutes, and will require an internet connection.


*Platform notes*

* _Windows_: Under windows, you might need to install the [msvc redist](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#visual-studio-2015-2017-2019-and-2022)
* _macOS_ : under macOS, if a binary wheel is not available (e.g. for older macOS versions), pip will try to compile from source. This might fail if you do not have XCode installed. In this case, install imgui-bundle with the following command `SYSTEM_VERSION_COMPAT=0 pip install --only-binary=:all: imgui_bundle`

## Install from source

```bash
# Clone the repository
git clone https://github.com/pthom/imgui_bundle.git
cd imgui_bundle

# Build and install the package (minimal install)
pip install -v .

# or build and install the package with all optional features:
#     pip install -v ".[full]"
```

The build process might take up to 5 minutes, and will clone the submodules if needed (an internet connection is required).

## Run the python demo

Simply run `imgui_bundle_demo`.

The source for the demos can be found inside [bindings/imgui_bundle/demos_python](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/demos_python).


TIP: Consider `imgui_bundle_demo` as an always available manual for Dear ImGui Bundle with lots of examples and related code source.
