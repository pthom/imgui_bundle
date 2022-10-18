cmake_minimum_required(VERSION 3.17)
project(imgui_bundle VERSION "0.1.0")

include(lg_cmake_utils/lg_cmake_utils.cmake)

set(CMAKE_CXX_STANDARD 17)


####################################################
# Add pybind11
####################################################
# Note there are several ways to provide pybind:
# - Method 1 (easiest): `pip install pybind11` and specify PYTHON_EXECUTABLE
# - Method 2: via a submodule +  add_subdirectory(external/pybind11)
# - Method 3: via a global install (`brew install pybind11`, `apt-get install python-pybind11`)
#      Note that apt packages may be out of date and might break the build (we require pybind11 from late 2021)
if(DEFINED PYTHON_EXECUTABLE)
    # if PYTHON_EXECUTABLE is defined, and pybind11 is installed via pip,
    # then add its path to CMAKE_PREFIX_PATH
    #
    # this is the case
    # * when using SKBUILD, which set PYTHON_EXECUTABLE
    #   (and pybind11 is referenced in pyproject.toml, section [build-system]/requires)
    # * when building normally, if you set PYTHON_EXECUTABLE
    execute_process(
        COMMAND "${PYTHON_EXECUTABLE}" -c
        "import pybind11; print(pybind11.get_cmake_dir())"
        OUTPUT_VARIABLE _tmp_dir
        OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ECHO STDOUT)
    list(APPEND CMAKE_PREFIX_PATH "${_tmp_dir}")
endif()

find_package(pybind11 CONFIG REQUIRED)


####################################################
# Build hello_imgui Bound C++ library
####################################################
if (UNIX)
    add_compile_options(-fPIC)
endif()
#   i. Build static libraries
set(BUILD_SHARED_LIBS OFF)
# 1. Build imgui (lib used by hello_imgui)
set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/external/imgui)
add_imgui_target(${imgui_dir})
# 2. Build glfw (also used by hello_imgui)
add_subdirectory(external/glfw)
if (UNIX AND NOT APPLE)
    # Those are only needed for wheels build using cibuildwheel (cp36-manylinux_x86_64 wheel)
    # See https://bytemeta.vip/repo/glfw/glfw/issues/2139
    target_compile_definitions(glfw PRIVATE POSIX_REQUIRED_STANDARD=199309L)
    target_compile_definitions(glfw PRIVATE _POSIX_C_SOURCE=POSIX_REQUIRED_STANDARD)
    target_compile_definitions(glfw PRIVATE _POSIX_SOURCE=POSIX_REQUIRED_STANDARD)
endif()

# 3. Configure hello-imgui with the following options:
#     i. use glfw
set(HELLOIMGUI_USE_GLFW_OPENGL3 ON CACHE BOOL "" FORCE)
#     ii. use provided imgui version
set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/external/imgui)
set(HELLOIMGUI_BUILD_IMGUI OFF CACHE BOOL "" FORCE)
set(HELLOIMGUI_IMGUI_SOURCE_DIR ${imgui_dir} CACHE STRING "" FORCE)

# 4. Finally, add hello_imgui
add_subdirectory(external/hello_imgui)

# 5. Export hello_imgui symbols on Windows without using __declspec(dllexport)
if (WIN32)
    set_target_properties(hello_imgui PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

####################################################
# add_simple_external_library : will add a target
# when its folder structure is simple
####################################################
function(add_simple_external_library target_name target_subdir)
    add_library(${target_name} STATIC)
    target_link_libraries(${target_name} PUBLIC imgui)
    set(target_source_dir ${CMAKE_CURRENT_LIST_DIR}/external/${target_subdir})
    target_include_directories(${target_name} PUBLIC ${target_source_dir}/..)

    target_link_libraries(hello_imgui PUBLIC ${target_name})
endfunction()

function(add_simple_external_library_with_sources target_name target_subdir)
    add_simple_external_library(${target_name} ${target_subdir})
    set(target_source_dir ${CMAKE_CURRENT_LIST_DIR}/external/${target_subdir})
    file(GLOB target_sources ${target_source_dir}/*.cpp ${target_source_dir}/*.h)
    target_sources(${target_name}  PRIVATE ${target_sources})
endfunction()


####################################################
# Build implot and link it into hello_imgui
####################################################
add_simple_external_library_with_sources(implot implot)
target_compile_definitions(implot PRIVATE "IMPLOT_CUSTOM_NUMERIC_TYPES=(signed char)(unsigned char)(signed short)(unsigned short)(signed int)(unsigned int)(signed long)(unsigned long)(signed long long)(unsigned long long)(float)(double)(long double)")
lg_target_force_include(implot ${CMAKE_CURRENT_LIST_DIR}/lg_cmake_utils/lg_imgui_imconfig.h)
lg_disable_warning_exception_in_destructor(implot)


# Build ImguiColorTextEdit
add_simple_external_library_with_sources(imgui_color_text_edit ImGuiColorTextEdit)
# Build imgui-node-editor
add_simple_external_library_with_sources(imgui_node_editor imgui-node-editor)
# Build imgui-knobs
add_simple_external_library_with_sources(imgui_knobs imgui-knobs)
# Build ImFileDialog
add_simple_external_library(im_file_dialog ImFileDialog)
target_sources(im_file_dialog  PRIVATE external/ImFileDialog/ImFileDialog.h external/ImFileDialog/ImFileDialog.cpp)
target_include_directories(im_file_dialog PRIVATE external/hello_imgui/src/hello_imgui/internal)

#########################################################################
# Build python module that provides bindings to the library hello_imgui
#########################################################################
set(bound_library hello_imgui)                 # The library for which we are building bindings
set(python_native_module_name _imgui_bundle)    # This is the native python module name
set(python_wrapper_module_name imgui_bundle)    # This is the python wrapper around the native module
set(python_module_sources

    bindings/module.cpp

    bindings/litgen_glue_code.h
    bindings/imgui_docking_internal_types.h

    bindings/pybind_hello_imgui.cpp
    bindings/pybind_imgui.cpp
    bindings/pybind_imgui_internal.cpp
    bindings/pybind_implot.cpp
    bindings/pybind_lg_imgui_bundle.cpp
    bindings/pybind_imgui_color_text_edit.cpp
    bindings/pybind_imgui_node_editor.cpp
    bindings/pybind_imgui_knobs.cpp
    bindings/pybind_im_file_dialog.cpp
    )

pybind11_add_module(${python_native_module_name} ${python_module_sources})
target_compile_definitions(${python_native_module_name} PRIVATE VERSION_INFO=${PROJECT_VERSION})
lg_setup_module(
    ${bound_library}
    ${python_native_module_name}
    ${python_wrapper_module_name}
)

target_link_libraries(${python_native_module_name} PUBLIC ${bound_library})


####################################################
# Devel only
####################################################
option(LG_IMGUI_BUNDLE_DEVMODE OFF)
mark_as_advanced(LG_IMGUI_BUNDLE_DEVMODE)
if (LG_IMGUI_BUNDLE_DEVMODE)
    add_subdirectory(external/_cpp_tests)
endif()
