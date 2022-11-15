#!/usr/bin/env bash

# exit when any command fails
set -e

# Specify the include folders for OpenCV and Dear ImGui
OpenCV_INCLUDE_DIRS="../../external/vcpkg/installed/x64-osx/include"
imgui_INCLUDE_DIRS="../../external/imgui"

# Specify your OpenGL Loader via IMMVISION_CUSTOM_GL_INCLUDE (i.e how do you include OpenGL?)
# See src/immvision_gl_loader/immvision_gl_loader.h for the different way to customize this
# Note: the build parameter `-I glad_INCLUDE_DIRS` is needed only if you are using glad as the OpenGL loader.
glad_INCLUDE_DIRS="../../src/immvision_gl_loader/glad/include"
IMMVISION_CUSTOM_GL_INCLUDE="$glad_INCLUDE_DIRS/glad/glad.h"

# Set the c++ standard version: can be c++14, c++17 or c++20
CXX_STANDARD="c++14"

cmd="
        g++ --std=$CXX_STANDARD -c immvision.cpp -o immvision.o \
            -Wall \
            \
            -I $imgui_INCLUDE_DIRS \
            -I $OpenCV_INCLUDE_DIRS \
            -I $glad_INCLUDE_DIRS \
            -I $imgui_INCLUDE_DIRS \
            \
            -DIMMVISION_CUSTOM_GL_INCLUDE=$IMMVISION_CUSTOM_GL_INCLUDE
        """

echo $cmd
$cmd
echo
echo "immvision.o was produced"
