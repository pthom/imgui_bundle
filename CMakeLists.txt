cmake_minimum_required(VERSION 3.17)
project(lg_hello_imgui)

include(lg_cmake_utils/lg_cmake_utils.cmake)

set(CMAKE_CXX_STANDARD 20)

add_subdirectory(external/pybind11)


####################################################
# Build hello_imgui Bound C++ library
####################################################
#
# 1. Build imgui library (linked by hello_imgui)
set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/external/imgui)
add_imgui_target(${imgui_dir})
# 2. Build glfw (also linked by hello_imgui)
add_subdirectory(external/glfw)

# 3. Configure hello-imgui with the following options:
#   i. Build a shared lib
set(BUILD_SHARED_LIBS ON)
#     ii. use glfw
set(HELLOIMGUI_USE_GLFW_OPENGL3 ON CACHE BOOL "" FORCE)
#     ii. use provided imgui version
set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/external/imgui)
set(HELLOIMGUI_BUILD_IMGUI OFF CACHE BOOL "" FORCE)
set(HELLOIMGUI_IMGUI_SOURCE_DIR ${imgui_dir} CACHE STRING "" FORCE)
#     iii. use imgui as a shared lib
set(HELLO_IMGUI_IMGUI_SHARED ON CACHE BOOL "" FORCE)
#     iv. Note: hello_imgui itself will be a shared lib (see set(BUILD_SHARED_LIBS ON) on top of this file)

# 4. Finally, add hello_imgui
add_subdirectory(external/hello_imgui)

# 5. Export hello_imgui symbols on Windows without using __declspec(dllexport)
if (WIN32)
    set_target_properties(hello_imgui PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()


#########################################################################
# Build python module that provides bindings to the library hello_imgui
#########################################################################
set(bound_library hello_imgui)                 # The library for which we are building bindings
set(python_native_module_name _hello_imgui)    # This is the native python module name
set(python_wrapper_module_name hello_imgui)    # This is the python wrapper around the native module
set(python_module_sources
    ${CMAKE_CURRENT_LIST_DIR}/bindings/module.cpp
    ${CMAKE_CURRENT_LIST_DIR}/bindings/pybind_${bound_library}.cpp) # native python module sources

pybind11_add_module(${python_native_module_name} ${python_module_sources})
lg_setup_module(
    ${bound_library}
    ${python_native_module_name}
    ${python_wrapper_module_name}
)
