cmake_minimum_required(VERSION 3.17)
project(lg_hello_imgui)


####################################################
# -A- Global options
####################################################
set(CMAKE_CXX_STANDARD 20)


####################################################
# -B- Add pybind11
####################################################
add_subdirectory(external/pybind11)


####################################################
# -C- Build hello_imgui Bound C++ library
####################################################
# C1: set(BUILD_SHARED_LIBS ON) will force hello_imgui to build a shared library
set(BUILD_SHARED_LIBS ON)

# C2. Add glfw (required by hello_imgui)
add_subdirectory(external/glfw)

# C3. Build custom imgui library
if(NOT TARGET imgui)
    set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/external/imgui)
    file(GLOB imgui_sources ${imgui_dir}/*.h ${imgui_dir}/*.cpp)
    add_library(imgui SHARED ${imgui_sources})
    target_include_directories(imgui PUBLIC ${imgui_dir} ${CMAKE_CURRENT_LIST_DIR})
    target_compile_definitions(imgui PRIVATE IMGUI_USER_CONFIG="litgen_imconfig.h")
    install(TARGETS imgui DESTINATION ./lib/)
endif()

# C4. Configure hello-imgui with the following options:
#     i. use glfw
set(HELLOIMGUI_USE_GLFW_OPENGL3 ON CACHE BOOL "" FORCE)
#     ii. use provided imgui version
set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/external/imgui)
set(HELLOIMGUI_BUILD_IMGUI OFF CACHE BOOL "" FORCE)
set(HELLOIMGUI_IMGUI_SOURCE_DIR ${imgui_dir} CACHE STRING "" FORCE)
#     iii. use imgui as a shared lib
set(HELLO_IMGUI_IMGUI_SHARED ON CACHE BOOL "" FORCE)
#     iv. Note: hello_imgui itself will be a shared lib (see set(BUILD_SHARED_LIBS ON) on top of this file)

# C5. Finally, add hello_imgui
add_subdirectory(external/hello_imgui)

# C6. Export hello_imgui symbols on Windows without using __declspec(dllexport)
if (WIN32)
    set_target_properties(hello_imgui PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()


####################################################
# -D- Build python module that provides binding to the library hello_imgui
####################################################
# This is the native python module name (`_lg_imgui`).
# It will be wrapped in a standard python module `lg_imgui, which is located in bindings/lg_imgui
set(python_native_module_name _hello_imgui)
set(python_module_sources bindings/module.cpp bindings/pybind_hello_imgui.cpp)
pybind11_add_module(${python_native_module_name} ${python_module_sources})
target_link_libraries(${python_native_module_name} PRIVATE hello_imgui)


####################################################
# -E- Install
####################################################
# E1. Install python module
install(TARGETS ${python_native_module_name} DESTINATION .)
# E2. Copy the python module to the project dir post build (for editable mode)
add_custom_command(
    TARGET ${python_native_module_name}
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy
    $<TARGET_FILE:${python_native_module_name}>
    ${CMAKE_CURRENT_LIST_DIR}/bindings/hello_imgui/$<TARGET_FILE_NAME:${python_native_module_name}>
)
#
# E3. Set the rpath for Linux and  MacOS (see https://github.com/pybind/cmake_example/issues/11)
#
# rpath for the _hello_imgui python module
set_target_properties(${python_native_module_name} PROPERTIES BUILD_WITH_INSTALL_RPATH TRUE)
if(UNIX AND NOT APPLE)
    set_target_properties(${python_native_module_name} PROPERTIES INSTALL_RPATH "$ORIGIN/lib/")
elseif(APPLE)
    set_target_properties(${python_native_module_name} PROPERTIES INSTALL_RPATH "@loader_path/lib/")
endif()
set_target_properties(${python_native_module_name} PROPERTIES INSTALL_RPATH_USE_LINK_PATH TRUE)
# rpath for hello_imgui native library
set_target_properties(hello_imgui PROPERTIES BUILD_WITH_INSTALL_RPATH TRUE)
if(UNIX AND NOT APPLE)
    set_target_properties(hello_imgui PROPERTIES INSTALL_RPATH "$ORIGIN/")
elseif(APPLE)
    set_target_properties(hello_imgui PROPERTIES INSTALL_RPATH "@loader_path/")
endif()
set_target_properties(hello_imgui PROPERTIES INSTALL_RPATH_USE_LINK_PATH TRUE)
#
# E4. On Windows, install DLLs in install folder root
#
if (WIN32)
    install(FILES $<TARGET_RUNTIME_DLLS:${python_native_module_name}> DESTINATION .)
endif()
