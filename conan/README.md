# The Conan package of Dear ImGui Bundle

`conanfile.py` packages the C++ libraries of Dear ImGui Bundle for [Conan 2](https://conan.io), for your own Conan server. It is not published on ConanCenter.

- *One package:* `imgui_bundle` holds all the bundle's libraries (Dear ImGui, Hello ImGui, ImPlot, ImmVision, the node editor, the markdown renderer...), as static libraries.
- *Built from this repository and its submodules:* one commit of the bundle pins every library it contains.
- *Used through its own CMake package:* your app calls `find_package(imgui_bundle)`, as with an installed bundle ([C++ installation](https://github.com/pthom/imgui_bundle/blob/main/docs/book/cpp/cpp_install.md)).
- *Its dependencies come from Conan:* freetype, glfw (or SDL2), OpenGL, and libcurl for the markdown images.

## What you need

- Conan 2 (checked with 2.34).
- CMake 3.23 or newer, for the presets Conan writes.
- A C++17 compiler. The CI checks MSVC 19.5 (Visual Studio 2026), GCC 13 and Apple clang.
- On Linux, the development packages of X11 and OpenGL.
  - Conan can install them with the system's package manager: add `-c tools.system.package_manager:mode=install -c tools.system.package_manager:sudo=True` to `conan create` (sudo must not ask for a password).
  - Otherwise, `conan create` stops and names the missing packages: install them yourself.

A profile: `conan profile detect`. The recipe needs C++17, and MSVC's detected profile says C++14: pass `-s compiler.cppstd=17` to each command, or write it in your profile.

## How to build the package

Run the commands from a clone of this repository. The recipe can take its sources from three places:

```bash
# A release listed in conan/conandata.yml: its full source archive, checked by its SHA-256
conan create conan --version=1.93.0 -s compiler.cppstd=17 --build=missing

# A commit of the repository (a "nightly"): the commit pins every submodule
conan create conan --version=1.93.1-dev.20261109 -c user.imgui_bundle:commit=<sha> -s compiler.cppstd=17 --build=missing

# A local checkout, as it is on disk: its tracked files, submodules included
conan create conan -c user.imgui_bundle:source_dir=/path/to/imgui_bundle -s compiler.cppstd=17 --build=missing
```

- *A release, for your apps:* its sources are pinned by the SHA-256 of its archive. Only v1.93.0 and later releases can be listed: they hold the C++ install layer.
- *A nightly, to get a fix before the next release:* name it after that release, with a `-dev.<date>` suffix. It then sorts before the release (`1.93.1-dev.20261109` < `1.93.1`), and version ranges skip it unless they say `include_prerelease`.
- *A local checkout, while developing the bundle:* Conan keeps its copy of the sources while the recipe is unchanged. After a change in the checkout, remove the package first: `conan remove "imgui_bundle/*" -c`.

`--build=missing` also builds the dependencies that ConanCenter has no binary for: its binaries cover a few compilers only. A build takes 6 to 11 minutes on GitHub's runners.

Each build type is a package of its own. On Windows, a Debug app needs a Debug package (`-s build_type=Debug`): MSVC's debug and release runtimes do not mix.

## The options

| Option | Values | Default | What it does |
|---|---|---|---|
| `platform_backend` | `glfw`, `sdl2` | `glfw` | The window and the inputs. The CI checks `glfw` only. |
| `rendering_backend` | `opengl3` | `opengl3` | Only OpenGL 3 is packaged. |
| `with_test_engine` | `True`, `False` | `True` | The ImGui Test Engine: automation and tests of a GUI. |
| `with_image_download` | `True`, `False` | `True` | The markdown images from URLs, through libcurl. |

Set them with `-o`, e.g. `-o "imgui_bundle/*:with_test_engine=False"`.

- *The ImGui Test Engine has its own license:* free for individuals, education, open source and small businesses. Larger businesses need a paid license ([its license](https://github.com/ocornut/imgui_test_engine/blob/main/imgui_test_engine/LICENSE.txt)). Leave it out with `with_test_engine=False` when it does not apply to you.
- *The TLS of the image downloads:* libcurl uses OpenSSL on Linux and macOS. On Windows, it uses schannel, the TLS of Windows: no OpenSSL to build, and the certificates that Windows trusts.
- *Without `with_image_download`,* the package needs neither libcurl nor OpenSSL.

## How to upload it to your Conan server

Once, add your server and log in (Conan asks for the password):

```bash
conan remote add my_server <url>
conan remote login my_server <user>
```

Then build with a JSON graph, list what the graph holds, and upload that list:

```bash
conan create conan --version=1.93.0 -s compiler.cppstd=17 --build=missing --format=json > graph.json
conan list --graph=graph.json --graph-recipes="*" --graph-binaries="*" --format=json > pkglist.json
conan upload --list=pkglist.json -r my_server -c
```

- *The list holds the package and its dependencies:* their recipes, and their binaries for this profile.
- *It also holds the recipes of the build tools (meson, ninja...), without binaries:* Conan needs them to resolve a graph, even when it builds nothing.
- *So your build machines do not need ConanCenter:* they find everything on your server. Checked with a local `conan_server`: an app's `conan install`, with ConanCenter removed, downloaded the package and its dependencies, and built nothing.
- *Repeat for each profile your apps use:* OS, architecture, compiler, build type.

## How to use it in your app

A `conanfile.txt` beside your `CMakeLists.txt`:

```ini
[requires]
imgui_bundle/1.93.0

[generators]
CMakeDeps
CMakeToolchain

[layout]
cmake_layout
```

Your `CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.23)
project(my_app CXX)
set(CMAKE_CXX_STANDARD 17)
find_package(imgui_bundle CONFIG REQUIRED)
imgui_bundle_add_app(my_app my_app.cpp)
```

`imgui_bundle_add_app` links the app to `imgui_bundle::imgui_bundle`, and copies the assets (fonts...) beside it.

Then build:

```bash
conan install . -s compiler.cppstd=17
cmake --preset conan-release          # on Windows: cmake --preset conan-default
cmake --build --preset conan-release
```

When your server has no binary for your profile, add `--build=missing` to `conan install`: Conan then builds the package on your machine.

### From FetchContent to the package

- *An app made from the [template](https://github.com/pthom/imgui_bundle_template) needs no change to its CMakeLists.txt:* it calls `find_package(imgui_bundle CONFIG QUIET)` first, and fetches the sources only when no package is found. Add the `conanfile.txt` above, and build with the commands above: CMake then says "Using installed imgui_bundle".
- *An app that only fetches the sources:* replace `FetchContent_Declare` and `FetchContent_MakeAvailable` with `find_package(imgui_bundle CONFIG REQUIRED)`.

## What the CI checks

`.github/workflows/conan.yml` runs `conan create` from the checkout, with the test package (`conan/test_package`, an app built against the package). Its jobs:

- Windows x64, MSVC, Release and Debug
- Linux x64 and arm64: Ubuntu 24.04, GCC 13
- macOS arm64

It runs when `conan/` or the workflow changes, every Monday, and by hand. It uploads nothing.

## Limits

- *Static libraries only.*
- *OpenGL 3 only,* with glfw. SDL2 is an option, not checked by the CI.
- *A binary fits one profile:* its package ID comes from the OS, the architecture, the compiler and its version, the C++ standard and the build type. Build the package with the compiler your apps use.
- *A Linux binary needs a glibc at least as recent as the one it was built with:* build on a system as old as your oldest target (for example, an embedded board's own image, rather than a recent Ubuntu with the same architecture).
