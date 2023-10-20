cmake_minimum_required(VERSION 3.16)
# Note: The real version is v1.0.0b1 (1.0.0 beta 1)
project(imgui_bundle VERSION "1.0.0")   # Remember to mirror changes to setup.py!


###############################################################################
# imgui_bundle_add_app
###############################################################################
# the easiest way to build an app with imgui_bundle is to use
#     imgui_bundle_add_app(my_app my_file.cpp)
set(IMGUIBUNDLE_CMAKE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/imgui_bundle_cmake CACHE STRING "" FORCE)
list(APPEND CMAKE_MODULE_PATH "${IMGUIBUNDLE_CMAKE_PATH}")
include(imgui_bundle_add_app)

set(IMGUIBUNDLE_PATH ${CMAKE_CURRENT_SOURCE_DIR} CACHE STRING "" FORCE)


###############################################################################
# Build Options
###############################################################################

# IMGUI_BUNDLE_BUILD_PYTHON: include python support
# --------------------------------------------------
# (OFF when building the cpp library; ON by default when using pip install.
#  note: SKBUILD is set to on by pip install / setup.py)
if(SKBUILD)
    set(IMGUI_BUNDLE_BUILD_PYTHON ON)
    set(IMGUI_BUNDLE_BUILD_CPP OFF)
else()
    option(IMGUI_BUNDLE_BUILD_PYTHON "build python bindings" OFF)
    set(IMGUI_BUNDLE_BUILD_CPP ON)
endif()


# IMMVISION_FETCH_OPENCV: fetch OpenCV automatically during configure
# ----------------------------------------------------------------------
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
# ----------------------------------------------------------------------
option(IMGUI_BUNDLE_WITH_TEST_ENGINE "include support for imgui_test_engine" ON)


# IMGUI_BUNDLE_WITH_SDL: Add SDL backend
# --------------------------------------
# (HelloImgui is built by default with glfw backend. Sdl is also supported, and can be added via this option)
if (NOT EMSCRIPTEN)
    option(IMGUI_BUNDLE_WITH_SDL "Add SDL backend" OFF)
    option(IMGUI_BUNDLE_WITH_GLFW "Add GLFW backend" ON)
else()
    set(IMGUI_BUNDLE_WITH_SDL ON)
    set(IMGUI_BUNDLE_WITH_GLFW OFF)
endif()


# IMGUI_BUNDLE_BUILD_DEMOS: Build demos
# -------------------------------------
# (ON by default if this is the main project)
if(PROJECT_IS_TOP_LEVEL)
    option(IMGUI_BUNDLE_BUILD_DEMOS "Build imgui_bundle C++ demos" ON)
else()
    option(IMGUI_BUNDLE_BUILD_DEMOS "Build imgui_bundle C++ demos" OFF)
endif()

# IMGUI_BUNDLE_BUILD_DOC: Build doc
# ---------------------------------
# (reserved for this library authors)
option(IMGUI_BUNDLE_BUILD_DOC "Build ImGui Bundle doc" OFF)

# SANITIZERS:
# ---------------------------------
option(IMGUI_BUNDLE_BUILD_WITH_ASAN "Build ImGui Bundle with address sanitizer" OFF)
if(IMGUI_BUNDLE_BUILD_WITH_ASAN)
    add_compile_options(-fsanitize=address -fsanitize-address-use-after-scope)
    add_link_options(-fsanitize=address -fsanitize-address-use-after-scope)
endif()
option(IMGUI_BUNDLE_BUILD_WITH_TSAN "Build ImGui Bundle with thread sanitizer" OFF)
if(IMGUI_BUNDLE_BUILD_WITH_TSAN)
    add_compile_options(-fsanitize=thread)
    add_link_options(-fsanitize=thread)
endif()
option(IMGUI_BUNDLE_BUILD_WITH_MEMORY_SANITIZER "Build ImGui Bundle with memory sanitizer" OFF)
if(IMGUI_BUNDLE_BUILD_WITH_MEMORY_SANITIZER)
    add_compile_options(-fsanitize=memory)
    add_link_options(-fsanitize=memory)
endif()
option(IMGUI_BUNDLE_BUILD_WITH_UB_SANITIZER "Build ImGui Bundle with undefined behavior sanitizer" OFF)
if(IMGUI_BUNDLE_BUILD_WITH_UB_SANITIZER)
    add_compile_options(-fsanitize=undefined)
    add_link_options(-fsanitize=undefined)
endif()
# Also see scan-build (clang static analyzer). No bugs reported on 2023-10-21
#     brew install llvm
#     mkdir build_llvm && cd llvm
#     export PATH=/opt/homebrew/opt/llvm/bin:$PATH
#     cmake .. -DIMMVISION_FETCH_OPENCV=ON
#     scan-build make -j


###############################################################################
# Main
###############################################################################

include(cmake/dump_cmake_variables.cmake)
include(lg_cmake_utils/lg_cmake_utils.cmake)
set(CMAKE_CXX_STANDARD 17)

# if build python binding, add definitions and use SDL + GLFW
if (IMGUI_BUNDLE_BUILD_PYTHON)
    add_compile_definitions(IMGUI_BUNDLE_BUILD_PYTHON)
    add_compile_definitions(IMGUI_BUNDLE_PYTHON_API)
    # When building python bindings, glfw is always built as a shared library (see cmake/add_glfw.cmake)
    set(IMGUI_BUNDLE_WITH_GLFW ON CACHE BOOL "" FORCE)
    # When building python bindings, sdl is always built as a shared library (see cmake/add_sdl.cmake)
    set(IMGUI_BUNDLE_WITH_SDL ON CACHE BOOL "" FORCE)
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
    add_compile_definitions(EMSCRIPTEN)
    # enable assertions in emscripten (IM_ASSERT will log and terminate on error)
    add_link_options(-sASSERTIONS)

    # If  building emscripten and building demos, we need to activate multithreading support (for ImGuiTestEngine)
    if (IMGUI_BUNDLE_BUILD_DEMOS)
        set(HELLOIMGUI_EMSCRIPTEN_PTHREAD ON CACHE BOOL "" FORCE)
        set(HELLOIMGUI_EMSCRIPTEN_PTHREAD ON CACHE BOOL "" FORCE)
    endif()
    if (HELLOIMGUI_EMSCRIPTEN_PTHREAD)
        add_compile_options(-pthread)
        add_link_options(-pthread)
        set(IMMVISION_OPENCV_EMSCRIPTEN_WITH_PTHREAD ON CACHE BOOL "" FORCE)
    endif()

    # Exceptions handlings: by default in emscripten, exception do not work!
    # Our program should not use them, but during development, it is possible to activate them temporarily)
    #add_compile_options(-sNO_DISABLE_EXCEPTION_CATCHING)
    #add_link_options(-sNO_DISABLE_EXCEPTION_CATCHING)
    # This would enable exception to be handled by wasm (and thus may be faster)
    #add_compile_options(-fwasm-exceptions)
    #add_link_options(-fwasm-exceptions)
endif()


#------------------
# Sanitizers
#------------------
#add_compile_options(-fsanitize=address)
#add_link_options(-fsanitize=address)
#add_compile_options(-fsanitize=undefined)
#add_link_options(-fsanitize=undefined)


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
file(GLOB imgui_bundle_sources src/imgui_bundle/*.cpp src/imgui_bundle/*.h)
add_library(imgui_bundle STATIC ${imgui_bundle_sources})
target_include_directories(imgui_bundle PUBLIC src)
hello_imgui_msvc_target_group_sources(imgui_bundle)

#########################################################################
# configure imgui_test_engine (*before* adding hello_imgui)
#########################################################################
if (IMGUI_BUNDLE_WITH_TEST_ENGINE)
    set(HELLOIMGUI_FETCH_IMGUI_TEST_ENGINE OFF CACHE BOOL "" FORCE)
    set(HELLOIMGUI_IMGUI_TEST_ENGINE_SOURCE_DIR
        ${CMAKE_CURRENT_LIST_DIR}/external/imgui_test_engine/imgui_test_engine
        CACHE STRING "" FORCE)
endif()

#########################################################################
# Build external libraries: this will add imgui, hello_imgui, immapp, implot, etc
#########################################################################
add_subdirectory(external)


#########################################################################
# Build python bindings
#########################################################################
if (IMGUI_BUNDLE_BUILD_PYTHON)
    include(cmake/add_imgui_bundle_bindings.cmake)
    add_imgui_bundle_bindings()

    if (IMGUI_BUNDLE_WITH_TEST_ENGINE)
        include(${CMAKE_CURRENT_LIST_DIR}/external/hello_imgui/hello_imgui/src/hello_imgui_test_engine_integration/hello_imgui_test_engine_cmake.cmake)
        configure_imgui_test_engine_with_python_gil()
    endif(IMGUI_BUNDLE_WITH_TEST_ENGINE)
endif()

####################################################
# C++ Apps
####################################################
if (IMGUI_BUNDLE_BUILD_CPP)
    if(IMGUI_BUNDLE_BUILD_DEMOS)
        add_subdirectory(bindings/imgui_bundle/demos_cpp)
    endif()
    if (IMGUI_BUNDLE_BUILD_PYTHON)
        add_subdirectory(pybind_native_debug)
        add_subdirectory(external/_sandbox)
    endif()
endif()

####################################################
# Help msvc tidy up its room
####################################################
if (MSVC)
    hello_imgui_msvc_sort_targets_by_folder(${CMAKE_CURRENT_LIST_DIR})
endif()

####################################################
# Help msvc tidy up its room
####################################################
if (IMGUI_BUNDLE_BUILD_DOC)
    add_subdirectory(bindings/imgui_bundle/doc)
    add_subdirectory(devel_docs)
endif()

####################################################
# Log Immvision status at the end
####################################################
if (IMGUI_BUNDLE_WITH_IMMVISION)
    message(STATUS "  IMGUI_BUNDLE_WITH_IMMVISION: ON")
else()
    message(STATUS "  IMGUI_BUNDLE_WITH_IMMVISION: OFF")
endif()
