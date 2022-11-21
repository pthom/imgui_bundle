cmake_minimum_required(VERSION 3.16)
project(imgui_bundle VERSION "0.6.6") # Remember to mirror changes to setup.py!


###############################################################################
# imgui_bundle_add_app location
###############################################################################
# In order to use `hello_imgui_add_app`, just write
#     list(APPEND CMAKE_MODULE_PATH ${HELLOIMGUI_CMAKE_PATH})
#     include(imgui_bundle_add_app)
# somewhere before calling `imgui_bundle_add_app`
set(IMGUIBUNDLE_CMAKE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/imgui_bundle_cmake CACHE STRING "" FORCE)
list(APPEND CMAKE_MODULE_PATH "${IMGUIBUNDLE_CMAKE_PATH}")
include(imgui_bundle_add_app)

###############################################################################
# Build Options
###############################################################################
# IMGUI_BUNDLE_WITH_IMMVISION
#     immvision is an image viewer / debugger. It requires OpenCV which can be installed automatically via conan
option(IMGUI_BUNDLE_WITH_IMMVISION "Add immvision support. Fail il OpenCV not found" OFF)
option(IMGUI_BUNDLE_WITH_IMMVISION_IF_OPENCV_FOUND "Add immvision support if opencv is found" ON)


# IMGUI_BUNDLE_WITH_SDL
#     HelloImgui is built by default with glfw backend. Sdl is also supported, and can be added via this option.
option(IMGUI_BUNDLE_WITH_SDL "Add SDL backend" OFF)

# IMGUI_BUNDLE_BUILD_DEMOS
#     Build demos (on by default if this is the main project)
if(PROJECT_IS_TOP_LEVEL)
    option(IMGUI_BUNDLE_BUILD_DEMOS "Build imgui_bundle C++ demos" ON)
else()
    option(IMGUI_BUNDLE_BUILD_DEMOS "Build imgui_bundle C++ demos" OFF)
endif()

# IMGUI_BUNDLE_BUILD_PYTHON:
#    on by default when using pip install, off when building the cpp library
#    (SKBUILD is set to on by pip install / setup.py)
if(SKBUILD)
    set(IMGUI_BUNDLE_BUILD_PYTHON ON)
    set(IMGUI_BUNDLE_BUILD_CPP OFF)
else()
    option(IMGUI_BUNDLE_BUILD_PYTHON OFF)
    set(IMGUI_BUNDLE_BUILD_CPP ON)
endif()


########################################################

include(lg_cmake_utils/lg_cmake_utils.cmake)
set(CMAKE_CXX_STANDARD 17)

if (IMGUI_BUNDLE_WITH_IMMVISION)
    add_compile_definitions(IMGUI_BUNDLE_WITH_IMMVISION)
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
add_library(imgui_bundle STATIC src/imgui_bundle/imgui_bundle.cpp src/imgui_bundle/imgui_bundle.h)
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
target_sources(im_file_dialog  PRIVATE
    external/ImFileDialog/ImFileDialog.h
    external/ImFileDialog/ImFileDialog.cpp
    external/ImFileDialogTextureHelper.h
    external/ImFileDialogTextureHelper.cpp
    )
target_include_directories(im_file_dialog PRIVATE external/hello_imgui/src/hello_imgui/internal)
target_link_libraries(im_file_dialog PRIVATE hello_imgui)
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
# Build immvision
if (IMGUI_BUNDLE_WITH_IMMVISION OR IMGUI_BUNDLE_WITH_IMMVISION_IF_OPENCV_FOUND)
    add_subdirectory(external/immvision)
    if (IMGUI_BUNDLE_WITH_IMMVISION)
        target_link_libraries(imgui_bundle PUBLIC immvision)
    endif()
endif()

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
    if(IMGUI_BUNDLE_BUILD_DEMOS)
        add_subdirectory(demos_cpp)
    endif()
    if (IMGUI_BUNDLE_BUILD_PYTHON)
        add_subdirectory(pybind_native_debug)
        add_subdirectory(external/_sandbox)
    endif()
endif()

if (IMGUI_BUNDLE_WITH_IMMVISION)
    message(STATUS "  IMGUI_BUNDLE_WITH_IMMVISION: ON")
else()
    message(STATUS "  IMGUI_BUNDLE_WITH_IMMVISION: OFF")
endif()
