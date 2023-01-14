# Repository folders structure

``` bash
./
+-- Readme.md -> bindings/imgui_bundle/Readme.md           # doc
+-- Readme_devel.md
|
+-- _example_integration/                                   # Demonstrate how to easily use
|         +-- CMakeLists.txt                                # imgui_bundle in a C++ app
|         +-- assets/
|         +-- hello_world.main.cpp
|
+-- imgui_bundle_cmake/                                     # imgui_bundle_add_app() :
|         |                                                 # a cmake function you can use
|         +-- imgui_bundle_add_app.cmake                    # to create an app in one line
|
+-- bindings/                                               # root for the python bindings
|         +-- imgui_bundle/
|                  +-- assets/                              # assets/ folder: you need to
|                  |                                        # copy this folder
|                  |                                        # into your app folder if you
|                  |                                        # intend to use markdown
|                  |
|                  +-- demos_assets/                        # assets used by demos
|                  +-- demos_cpp/                           # lots of C++ demos
|                  +-- demos_python/                        # lots of python demos
|                  +-- imgui/                               # imgui stubs
|                  |     +-- __init__.pyi
|                  |     +-- backends.pyi
|                  |     +-- internal.pyi
|                  |     +-- py.typed
|                  +-- implot.pyi                           # implot stubs
|                  +-- __init__.py
|                  +-- __init__.pyi
|                  +-- hello_imgui.pyi
|                  +-- ...                                  # lots of other libs stubs
|                  +-- ...
|                  +-- ...
|                  +-- immapp/                              # immapp: immediate app
|                  |        |                               # utilities
|                  |        +-- __init__.py
|                  |        +-- __init__.pyi
|                  |        +-- icons_fontawesome.py
|                  |        +-- immapp_cpp.pyi
|                  |        +-- immapp_utils.py
|                  |        +-- py.typed
|                  +-- _imgui_bundle.cpython-38-darwin.so  # imGui_bundle python
|                  |                                       # dynamic library
|                  +-- glfw_utils.py
|                  +-- py.typed
|
|
+-- cmake/                                                 # Private cmake utilities
|         +-- add_imgui.cmake
|         +-- ...
|
+-- external/                                              # Root of all bound libraries
|         +-- CMakeLists.txt
|         +-- imgui/                                       # ImGui root
|         |         +-- bindings/                          # ImGui bindings
|         |         +-- imgui/                             # ImGui submodule
|         +-- ImGuizmo/
|         |         +-- bindings/                          # ImGuizmo bindings
|         |         +-- ImGuizmo/                          # ImGuizmo submodule
|         |         +-- ImGuizmoPure/                      # Manual wrappers to help
|         |                                                # bindings generation
|         |
|         +-- ... lots of other bound libraries/           # Lots of other bound libraries
|         |         +-- {lib_name}/
|         |         +-- bindings/
|         |
|         +-- _doc/
|         |
|         +-- bindings_generation/                         # Script to generate bindings
|         |         |                                      # and to facilitate external
|         |         +-- __init__.py                        # libraries update
|         |         +-- all_external_libraries.py
|         |         +-- autogenerate_all.py
|         |         +-- ...
|         |
|         +-- SDL/SDL/                                     # Linked library (without
|         |                                                # python bindings)
|         +-- fplus/fplus/                                 # Library without bindings
|         +-- glfw/glfw                                    # Library without bindings
|
+-- lg_cmake_utils/                                        # Cmake utils for bindings
|         |                                                # generation
|         +-- lg_cmake_utils.cmake
|         +-- ...
|
+-- pybind_native_debug/
|         +-- CMakeLists.txt
|         +-- Readme.md
|         +-- pybind_native_debug.cpp
|         +-- pybind_native_debug.py
|
+-- src/
|         +-- imgui_bundle/                               # main cpp library: almost empty,
                                                          # but linked to all external libraries
```
