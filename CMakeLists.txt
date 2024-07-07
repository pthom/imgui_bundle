cmake_minimum_required(VERSION 3.16)
project(imgui_bundle VERSION "1.5.2") # Remember to mirror changes to pyproject.toml!

# imgui_bundle_build_lib contains the main logic to build imgui_bundle
set(IMGUI_BUNDLE_PATH ${CMAKE_CURRENT_LIST_DIR} CACHE STRING "" FORCE)
include(imgui_bundle_cmake/imgui_bundle_build_lib.cmake)


# -----------------------------------------------------------------------------
# About imgui_bundle_add_app:
# -----------------------------------------------------------------------------
# The easiest way to build an app with imgui_bundle is to use imgui_bundle_add_app.
# imgui_bundle_add_app is a helper function, similar to cmake's "add_executable"
# Usage:
#     imgui_bundle_add_app(app_name file1.cpp file2.cpp ...)
# Or:
#     imgui_bundle_add_app(app_name file1.cpp file2.cpp ... ASSETS_LOCATION "path/to/assets")
#
# (By default, ASSETS_LOCATION is "assets", which means that the assets will be searched in the "assets" folder,
# relative to the location of the CMakeLists.txt file)
#
# Features:
#     * It will automatically link the target to the required libraries (imgui_bundle, OpenGl, glad, etc)
#     * It will embed the assets (for desktop, mobile, and emscripten apps)
#     * It will perform additional customization (app icon and name on mobile platforms, etc)


###############################################################################
# Build Options
###############################################################################

# IMGUI_BUNDLE_AUTO_CLONE_SUBMODULES: clone submodules if needed during configure
# -----------------------------------------------------------------------------
option(IMGUI_BUNDLE_AUTO_CLONE_SUBMODULES "clone submodules if needed during configure" ON)
ibd_clone_submodules_if_needed()

# Import a few cmake utility functions from hello_imgui
include(${CMAKE_CURRENT_LIST_DIR}/external/hello_imgui/hello_imgui/hello_imgui_cmake/utils/cache_hello_imgui_paths.cmake)
include(${HELLOIMGUI_CMAKE_PATH}/hello_imgui_build_lib.cmake)


# Backends
# -----------------------------------------------------------------------------
# <Backends> # do not remove this line (used by the script that generates the documentation)
# (this part is a direct copy from HelloImGui CmakeList, reproduced here for convenience)
# You need to select at least two backends:
#
#     - At least one (or more) rendering backend (OpenGL3, Metal, Vulkan, DirectX11, DirectX12)
#       Make your choice according to your needs and your target platforms, between:
#          -DHELLOIMGUI_HAS_OPENGL3=ON    # This is the recommended choice, especially for beginners
#          -DHELLOIMGUI_HAS_METAL=ON      # Apple only, advanced users only
#          -DHELLOIMGUI_HAS_VULKAN=ON     # Advanced users only
#          -DHELLOIMGUI_HAS_DIRECTX11=ON  # Windows only, still experimental
#          -DHELLOIMGUI_HAS_DIRECTX12=ON  # Windows only, advanced users only, still experimental
#
#     - At least one (or more) platform backend (SDL2, Glfw3):
#      Make your choice according to your needs and your target platforms, between:
#          -DHELLOIMGUI_USE_SDL2=ON
#          -DHELLOIMGUI_USE_GLFW3=ON
#
# If you make no choice, the default will be selected:
#     HELLOIMGUI_USE_GLFW3 + HELLOIMGUI_HAS_OPENGL3
#
# Note about rendering backends:
#   OpenGL3 is the recommended choice as a starting point, especially for beginners.
#   Vulkan, Metal, and DirectX11, DirectX12 do work, but you may need to customize the rendering code inside HelloImGui:
#   see src/hello_imgui/internal/backend_impls/rendering_xxxx.[h,cpp]
#   (using those backends probably implies that you want to heavily customize the rendering code)
#
# Note for linux:
# If you want to use glfw and/or sdl, you need to install system-wide, or alternatively pass the following cmake options
#      -DHELLOIMGUI_DOWNLOAD_GLFW_IF_NEEDED=ON  -DHELLOIMGUI_DOWNLOAD_SDL_IF_NEEDED=ON
################################################################################
# Platform backends:
option(HELLOIMGUI_USE_GLFW3 "Use Glfw3 as a platform backend" OFF)
option(HELLOIMGUI_USE_SDL2 "Use Sdl2 as a platform backend" OFF)
# Rendering backends
option(HELLOIMGUI_HAS_OPENGL3 "Use OpenGL3 as a rendering backend" OFF)
option(HELLOIMGUI_HAS_METAL "Use Metal as a rendering backend" OFF)
option(HELLOIMGUI_HAS_VULKAN "Use Vulkan as a rendering backend" OFF)
option(HELLOIMGUI_HAS_DIRECTX11 "Use DirectX11 as a rendering backend" OFF)
option(HELLOIMGUI_HAS_DIRECTX12 "Use DirectX12 as a rendering backend" OFF)
# </Backends>  # do not remove this line (used by the script that generates the documentation)


# IMGUI_BUNDLE_BUILD_PYTHON: include python support
# -----------------------------------------------------------------------------
# (OFF when building the cpp library; ON by default when using pip install.
#  note: SKBUILD is set to on by pip install / setup.py)
# Note: when building python bindings *and* C++, you may have to set -DPython_EXECUTABLE=/path/to/python
if(SKBUILD)
    set(IMGUI_BUNDLE_BUILD_PYTHON ON)
    set(IMGUI_BUNDLE_BUILD_CPP OFF)
else()
    option(IMGUI_BUNDLE_BUILD_PYTHON "build python bindings" OFF)
    set(IMGUI_BUNDLE_BUILD_CPP ON)
endif()

# For python bindings, we force the usage of Glfw+OpenGL3
if(IMGUI_BUNDLE_BUILD_PYTHON)
    set(HELLOIMGUI_USE_GLFW3 ON CACHE BOOL "" FORCE)
    set(HELLOIMGUI_HAS_OPENGL3 ON CACHE BOOL "" FORCE)

    set(HELLOIMGUI_USE_SDL2 OFF CACHE BOOL "" FORCE)
    set(HELLOIMGUI_HAS_METAL OFF CACHE BOOL "" FORCE)
    set(HELLOIMGUI_HAS_VULKAN OFF CACHE BOOL "" FORCE)
    set(HELLOIMGUI_HAS_DIRECTX11 OFF CACHE BOOL "" FORCE)
    set(HELLOIMGUI_HAS_DIRECTX12 OFF CACHE BOOL "" FORCE)
endif()

# -----------------------------------------------------------------------------
# On desktop platforms, other backends are available: see external/hello_imgui/hello_imgui/CMakelists.txt
# (For example: HELLOIMGUI_USE_GLFW_METAL, HELLOIMGUI_USE_SDL_METAL, HELLOIMGUI_USE_GLFW_VULKAN, HELLOIMGUI_USE_SDL_VULKAN)
# The usage of these alternative backends is aimed for experienced users,
# and some widgets may be disabled with those (ImFileDialog, imgui_text_inspect, immvision)
# -----------------------------------------------------------------------------


# Some included libraries can be disabled individually
# This works only in C++ (not in python)
# -----------------------------------------------------------------------------
option(IMGUI_BUNDLE_DISABLE_NANOVG "Disable nanovg" OFF)
option(IMGUI_BUNDLE_DISABLE_IMGUI_TEX_INSPECT "Disable imgui_tex_inspect" OFF)
option(IMGUI_BUNDLE_DISABLE_IMGUIZMO "Disable ImGuizmo" OFF)
option(IMGUI_BUNDLE_DISABLE_IMFILEDIALOG "Disable ImFileDialog" OFF)
option(IMGUI_BUNDLE_DISABLE_IMGUI_NODE_EDITOR "Disable imgui-node-editor" OFF)
option(IMGUI_BUNDLE_DISABLE_IMPLOT "Disable implot" OFF)
option(IMGUI_BUNDLE_DISABLE_IMMVISION "Disable immvision" OFF)



# IMMVISION_FETCH_OPENCV: fetch OpenCV automatically during configure
# -----------------------------------------------------------------------------
# (OpenCV is required by the optional module immvision.
#  If IMMVISION_FETCH_OPENCV is ON, we will fetch a build a minimal version of OpenCV.
if (IMGUI_BUNDLE_BUILD_PYTHON OR EMSCRIPTEN)
    # For emscripten and for the python package, we automatically fetch OpenCV
     #    (unless IMMVISION_FETCH_OPENCV is set in the cache, via for example -DIMMVISION_FETCH_OPENCV=OFF)
    # Under windows and emscripten we fetch a precompiled package, under linux and mac OS a minimal OpenCV will be compiled from sources
    if(NOT DEFINED CACHE{IMMVISION_FETCH_OPENCV})
        set(IMMVISION_FETCH_OPENCV ON)
    endif()
else()
    # In C++, feel free to use your own version of OpenCV, or to use this (minimal) version by setting IMMVISION_FETCH_OPENCV
    option(IMMVISION_FETCH_OPENCV "fetch OpenCV" OFF)
endif()
# When building the pip package, you can disable OpenCV (and immvision) by setting the env variable
# IMMVISION_FETCH_OPENCV=OFF
if(DEFINED ENV{IMMVISION_FETCH_OPENCV})
    set(IMMVISION_FETCH_OPENCV "$ENV{IMMVISION_FETCH_OPENCV}")
endif()
option(IMGUI_BUNDLE_FAIL_IF_IMMVISION_UNAVAILABLE "Fail if immvision unavailable (OpenCV not found)" OFF)


# IMGUI_BUNDLE_WITH_TEST_ENGINE: include support for imgui_test_engine
# -----------------------------------------------------------------------------
if (NOT ANDROID AND NOT IOS)
    option(IMGUI_BUNDLE_WITH_TEST_ENGINE "include support for imgui_test_engine" ON)
else()
    set(IMGUI_BUNDLE_WITH_TEST_ENGINE OFF)
endif()

#------------------------------------------------------------------------------
# Options / Freetype (this is an option for hello_imgui, reproduced here for convenience)
#------------------------------------------------------------------------------
ibd_check_freetype_availability(freetype_default)
# Note: to reduce wasm size, you may want to disable freetype on emscripten.
option(HELLOIMGUI_USE_FREETYPE "Use freetype for text rendering" ${freetype_default})
ibd_force_freetype_static_for_python()

# IMGUI_BUNDLE_BUILD_DEMOS: Build demos
# -----------------------------------------------------------------------------
# (ON by default if this is the main project)
if(PROJECT_IS_TOP_LEVEL)
    option(IMGUI_BUNDLE_BUILD_DEMOS "Build imgui_bundle C++ demos" ON)
else()
    option(IMGUI_BUNDLE_BUILD_DEMOS "Build imgui_bundle C++ demos" OFF)
endif()


# IMGUI_BUNDLE_BUILD_DOC: Build doc
# -----------------------------------------------------------------------------
# (reserved for this library authors)
option(IMGUI_BUNDLE_BUILD_DOC "Build ImGui Bundle doc" OFF)

# Options / Install
# By default, hello_imgui install its targets only if it is the top level project
# and only if it is not building the python package
# (the python package will install different elements)
#------------------------------------------------------------------------------
if(PROJECT_IS_TOP_LEVEL AND NOT IMGUI_BUNDLE_BUILD_PYTHON)
    set(imgui_bundle_install_cpp_default ON)
else()
    set(imgui_bundle_install_cpp_default OFF)
endif()
option(IMGUI_BUNDLE_INSTALL_CPP "Install imgui_bundle" ${imgui_bundle_install_cpp_default})

# Sanitizers options (see imgui_bundle_build_lib.cmake)
# -----------------------------------------------------------------------------
ibd_add_sanitizer_options()

# Automation test (run app in CI)
# -----------------------------------------------------------------------------
option(IMGUI_BUNDLE_BUILD_CI_AUTOMATION_TESTS "Build CI automation tests" OFF)


# -----------------------------------------------------------------------------
# How to build offline
# -----------------------------------------------------------------------------
# By default, imgui_bundle and hello_imgui will download and build the required
# libraries automatically, if they cannot be found via cmake's find_package:
#   glfw3, lunasvg, freetype, opencv
# To build offline, you can for example pre-install the required libraries with vcpkg,
# see below:
#
# C++ library, install requirements via vcpkg
# --------------------------------------------
#
#    git clone https://github.com/microsoft/vcpkg
#    ./vcpkg/bootstrap-vcpkg.sh
#    ./vcpkg/vcpkg install opencv freetype glfw3 lunasvg
#    export CMAKE_TOOLCHAIN_FILE=vcpkg/scripts/buildsystems/vcpkg.cmake
#    mkdir build && cd build
#    cmake ..
#
# Note: under windows, you could specify a static triplet (x64-windows-static):
#     ./vcpkg/vcpkg install opencv:x64-windows-static freetype:x64-windows-static glfw3:x64-windows-static lunasvg:x64-windows-static
#
# Pip package
# -----------
# To build the pip package offline, you will additionally need to download
# the pip wheels for the build system, and tell pip to use them:
#
#    mkdir pip_wheels && cd pip_wheels
#    pip download scikit_build_core pybind11 pip pyproject_metadata pathspec
#    cd ..
#    pip install -v . --no-index --find-links=pip_wheels


###############################################################################
# Main
###############################################################################

# Avoid building imgui_bundle twice
if(TARGET imgui_bundle)
    message(STATUS "imgui_bundle target already defined!")
    return()
endif()

# Reset installable dependencies at startup
ibd_reset_installable_dependencies()

# if building the python package, set install folder to anything but /usr/local
if(SKBUILD)
    set(CMAKE_INSTALL_PREFIX "imgui_bundle/install_overdue")
endif()

# use ccache if present
find_program(CCACHE_FOUND ccache)
if(CCACHE_FOUND)
    set(CMAKE_CXX_COMPILER_LAUNCHER ccache)
endif(CCACHE_FOUND)


# Everything is built as a static library in imgui_bundle
set(BUILD_SHARED_LIBS OFF)

# Error on deprecated options
ibd_shout_on_deprecated_options()
# Add the imgui_bundle_add_app cmake helper
ibd_include_imgui_bundle_add_app()
# if building the python package, do some cleanup:
ibd_clean_bindings_imgui_bundle_before_pip_build()

# Main
# ----------------------------------------------------------------------
include(imgui_bundle_cmake/internal/litgen_setup_module.cmake)
set(CMAKE_CXX_STANDARD 17)

# if build python binding, add definitions and use SDL + GLFW
if (IMGUI_BUNDLE_BUILD_PYTHON)
    add_compile_definitions(IMGUI_BUNDLE_BUILD_PYTHON)
    add_compile_definitions(IMGUI_BUNDLE_PYTHON_API)
endif()

# IMGUI_BUNDLE_WITH_TEST_ENGINE is propagated to HELLOIMGUI_WITH_TEST_ENGINE
set(HELLOIMGUI_WITH_TEST_ENGINE ${IMGUI_BUNDLE_WITH_TEST_ENGINE} CACHE BOOL "" FORCE)
if (IMGUI_BUNDLE_WITH_TEST_ENGINE)
    add_compile_definitions(IMGUI_BUNDLE_WITH_TEST_ENGINE)
endif()
if (NOT IMGUI_BUNDLE_WITH_TEST_ENGINE AND IMGUI_BUNDLE_BUILD_PYTHON)
    message(FATAL_ERROR "When building python (IMGUI_BUNDLE_BUILD_PYTHON), support for imgui_test_engine (IMGUI_BUNDLE_WITH_TEST_ENGINE) should be ON")
endif()

# emscripten build additional settings
if (EMSCRIPTEN)
    ibd_add_emscripten_otions()
endif()


# find pybind11
# -----------------------------------------------------------------------------
if (IMGUI_BUNDLE_BUILD_PYTHON)
    include(imgui_bundle_cmake/internal/litgen_setup_module.cmake)
    litgen_find_pybind11()  # provided by cmake/find_pybind11.cmake
endif()

# Fake main library (imgui_bundle is just an interface to define common options)
# -----------------------------------------------------------------------------
add_library(imgui_bundle INTERFACE)
if(IMGUI_BUNDLE_INSTALL_CPP)
    install(DIRECTORY imgui_bundle_cmake DESTINATION share/imgui-bundle)
    install(DIRECTORY bindings/imgui_bundle/assets DESTINATION share/imgui-bundle)
    ibd_add_installable_dependency(imgui_bundle)
endif()

# configure imgui_test_engine (*before* adding hello_imgui)
# -----------------------------------------------------------------------------
if (IMGUI_BUNDLE_WITH_TEST_ENGINE)
    set(HELLOIMGUI_FETCH_IMGUI_TEST_ENGINE OFF CACHE BOOL "" FORCE)
    set(HELLOIMGUI_IMGUI_TEST_ENGINE_SOURCE_DIR
        ${CMAKE_CURRENT_LIST_DIR}/external/imgui_test_engine/imgui_test_engine
        CACHE STRING "" FORCE)
endif()

# Build external libraries: this will add imgui, hello_imgui, immapp, implot, etc
# -----------------------------------------------------------------------------
add_subdirectory(external)


# Build python bindings
# -----------------------------------------------------------------------------
if (IMGUI_BUNDLE_BUILD_PYTHON)
    include(imgui_bundle_cmake/internal/add_imgui_bundle_bindings.cmake)
    add_imgui_bundle_bindings()

    if (IMGUI_BUNDLE_WITH_TEST_ENGINE)
        include(${CMAKE_CURRENT_LIST_DIR}/external/hello_imgui/hello_imgui/src/hello_imgui_test_engine_integration/hello_imgui_test_engine_cmake.cmake)
        configure_imgui_test_engine_with_python_gil()
    endif(IMGUI_BUNDLE_WITH_TEST_ENGINE)
endif()

# C++ Apps
# -----------------------------------------------------------------------------
if (IMGUI_BUNDLE_BUILD_CPP)
    if(IMGUI_BUNDLE_BUILD_DEMOS)
        add_subdirectory(bindings/imgui_bundle/demos_cpp)
    endif()
    if (IMGUI_BUNDLE_BUILD_PYTHON)
        add_subdirectory(pybind_native_debug)
    endif()
endif()

# CI Automation
# -----------------------------------------------------------------------------
if (IMGUI_BUNDLE_BUILD_CI_AUTOMATION_TESTS)
    add_subdirectory(.github/ci_automation_tests)
endif()

# Example integration
# -----------------------------------------------------------------------------
option(IMGUI_BUNDLE_BUILD_EXAMPLE_INTEGRATION "Build _example_integration" OFF)
if(IMGUI_BUNDLE_BUILD_EXAMPLE_INTEGRATION)
    add_subdirectory(_example_integration)
endif()

# Help msvc tidy up its room
# -----------------------------------------------------------------------------
if (MSVC)
    hello_imgui_msvc_sort_targets_by_folder(${CMAKE_CURRENT_LIST_DIR})
endif()

# Doc
# -----------------------------------------------------------------------------
if (IMGUI_BUNDLE_BUILD_DOC)
    add_subdirectory(bindings/imgui_bundle/doc)
    add_subdirectory(devel_docs)
endif()

#------------------------------------------------------------------------------
# CMake shenanigans so that find_package(imgui-bundle CONFIG REQUIRED) works
#------------------------------------------------------------------------------
# These elements are mainly used to build a vcpkg compatible package.
# Important note:
#     - the CMake package is named imgui-bundle (with a "-")
#     - the CMake target is named imgui_bundle (with a "_")
# To link with imgui_bundle, you need to use:
#     find_package(imgui-bundle CONFIG REQUIRED)
#     target_link_libraries(your_target PRIVATE imgui-bundle::imgui_bundle)  # note the variation "-" vs "_"
# However, the simplest use is:
#     find_package(imgui-bundle CONFIG REQUIRED)
#     imgui_bundle_add_app(test test.cpp) # this will automatically link with imgui_bundle
#------------------------------------------------------------------------------
if(IMGUI_BUNDLE_INSTALL_CPP AND IMGUI_BUNDLE_BUILD_PYTHON)
    message(FATAL_ERROR "IMGUI_BUNDLE_INSTALL_CPP is incompatible with IMGUI_BUNDLE_BUILD_PYTHON")
endif()
if(IMGUI_BUNDLE_INSTALL_CPP)
    # inspired from https://iamsorush.com/posts/cpp-cmake-config/
    message(STATUS "IMGUI_BUNDLE_INSTALLABLE_DEPENDENCIES=${IMGUI_BUNDLE_INSTALLABLE_DEPENDENCIES}")
    install(TARGETS ${IMGUI_BUNDLE_INSTALLABLE_DEPENDENCIES}
        EXPORT imgui-bundle-targets
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin
        INCLUDES DESTINATION include)

    install(EXPORT imgui-bundle-targets
        FILE imgui-bundle-targets.cmake
        NAMESPACE imgui-bundle::
        DESTINATION lib/cmake/imgui_bundle)

    include(CMakePackageConfigHelpers)
    write_basic_package_version_file(
        "imgui-bundleConfigVersion.cmake"
        VERSION ${imgui_bundle_VERSION}
        COMPATIBILITY AnyNewerVersion)

    install(FILES "imgui_bundle_cmake/imgui-bundleConfig.cmake" "${CMAKE_CURRENT_BINARY_DIR}/imgui-bundleConfigVersion.cmake"
        DESTINATION lib/cmake/imgui_bundle)
endif()


# Log options at the end
# -----------------------------------------------------------------------------
# First, adjust variables so that they show correctly
#
# IMGUI_BUNDLE_WITH_IMMVISION may be defined in external/immvision/CMakeLists.txt
if (NOT IMGUI_BUNDLE_WITH_IMMVISION)
    set(IMGUI_BUNDLE_WITH_IMMVISION OFF)
endif()
him_log_configuration()
message(STATUS "
    Dear ImGui Bundle build options:
    ===========================================================================
    Options:
    ---------------------------------------------------------------------------
    IMGUI_BUNDLE_WITH_IMMVISION:   ${IMGUI_BUNDLE_WITH_IMMVISION} (IMMVISION_FETCH_OPENCV: ${IMMVISION_FETCH_OPENCV})
    IMGUI_BUNDLE_WITH_TEST_ENGINE: ${IMGUI_BUNDLE_WITH_TEST_ENGINE}
    IMGUI_BUNDLE_BUILD_PYTHON:     ${IMGUI_BUNDLE_BUILD_PYTHON}
    IMGUI_BUNDLE_BUILD_DEMOS:      ${IMGUI_BUNDLE_BUILD_DEMOS}
    IMGUI_BUNDLE_BUILD_DOC:        ${IMGUI_BUNDLE_BUILD_DOC}
")
