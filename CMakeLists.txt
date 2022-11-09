cmake_minimum_required(VERSION 3.17)
project(imgui_bundle VERSION "0.6.5") # Remember to mirror changes to setup.py!

set(CMAKE_CXX_STANDARD 17)

include(lg_cmake_utils/lg_cmake_utils.cmake)


if(SKBUILD)
    set(IMGUI_BUNDLE_BUILD_PYTHON ON)
    set(IMGUI_BUNDLE_BUILD_CPP OFF)
else()
    option(IMGUI_BUNDLE_BUILD_PYTHON OFF)
    set(IMGUI_BUNDLE_BUILD_CPP ON)
endif()

#########################################################################
# find pybind11
#########################################################################
if (IMGUI_BUNDLE_BUILD_PYTHON)
    include(cmake/find_pybind11.cmake)
    find_pybind11()  # provided by cmake/find_pybind11.cmake
endif()

#########################################################################
# Main library (imgui_bundle)
#########################################################################
add_library(imgui_bundle src/imgui_bundle/imgui_bundle.cpp src/imgui_bundle/imgui_bundle.h)
target_include_directories(imgui_bundle PUBLIC src)


#########################################################################
# Build external libraries
#########################################################################
include(cmake/add_simple_library.cmake) # Tooling to build libraries and link them to imgui_bundle
# Build hello_imgui
include(cmake/add_hello_imgui.cmake)
add_hello_imgui()
# Build implot
add_simple_external_library_with_sources(implot implot)
target_compile_definitions(implot PRIVATE "IMPLOT_CUSTOM_NUMERIC_TYPES=(signed char)(unsigned char)(signed short)(unsigned short)(signed int)(unsigned int)(signed long)(unsigned long)(signed long long)(unsigned long long)(float)(double)(long double)")
lg_target_force_include(implot ${CMAKE_CURRENT_LIST_DIR}/lg_cmake_utils/lg_imgui_imconfig.h)
lg_disable_warning_exception_in_destructor(implot)
# Build ImguiColorTextEdit
add_simple_external_library_with_sources(imgui_color_text_edit ImGuiColorTextEdit)
if (IMGUI_BUNDLE_BUILD_PYTHON)
    target_compile_definitions(imgui_color_text_edit PRIVATE IMGUI_BUNDLE_BUILD_PYTHON)
endif()
# Build imgui-node-editor
add_simple_external_library_with_sources(imgui_node_editor imgui-node-editor)
# Build imgui-knobs
add_simple_external_library_with_sources(imgui_knobs imgui-knobs)
# Build ImFileDialog
add_simple_external_library(im_file_dialog ImFileDialog)
target_sources(im_file_dialog  PRIVATE external/ImFileDialog/ImFileDialog.h external/ImFileDialog/ImFileDialog.cpp)
target_include_directories(im_file_dialog PRIVATE external/hello_imgui/src/hello_imgui/internal)
# Build imspinner
add_simple_external_library_with_sources(imspinner imspinner)
# Build imgui_toggle
add_simple_external_library_with_sources(imgui_toggle imgui_toggle)
# Build imgui_md
add_simple_external_library(imgui_md imgui_md/imgui_md)
target_sources(imgui_md PRIVATE
    external/imgui_md/imgui_md/imgui_md.cpp
    external/imgui_md/imgui_md/imgui_md.h
    external/imgui_md/md4c/src/md4c.c
    external/imgui_md/md4c/src/md4c.h
    external/imgui_md/imgui_md_wrapper.cpp
    external/imgui_md/imgui_md_wrapper.h
    )
target_include_directories(imgui_md PUBLIC external/imgui_md/md4c/src)
target_link_libraries(imgui_md PUBLIC hello_imgui)


#########################################################################
# Build python bindings
#########################################################################
if (IMGUI_BUNDLE_BUILD_PYTHON)
    include(cmake/add_imgui_bundle_bindings.cmake)
    add_imgui_bundle_bindings()
endif()


####################################################
# C++ Apps
####################################################
if (IMGUI_BUNDLE_BUILD_CPP)
    add_subdirectory(demos_cpp)
    if (IMGUI_BUNDLE_BUILD_PYTHON)
        add_subdirectory(pybind_native_debug)
        add_subdirectory(external/_sandbox)
    endif()
endif()
