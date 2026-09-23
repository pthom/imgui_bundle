# Stock Dear ImGui check: the markdown wrapper + renderer + md4c against stock Dear ImGui (fetched, v1.92.9), with
# GLFW + OpenGL3 backends, no HelloImGui, the assets embedded. The future examples/minimal of RichMd.
#   cmake -S external/imgui_md/standalone_check -B builds/claude_richmd_standalone && cmake --build builds/claude_richmd_standalone
cmake_minimum_required(VERSION 3.20)
project(imgui_md_standalone_check CXX C)
set(CMAKE_CXX_STANDARD 17)

set(BUNDLE_DIR ${CMAKE_CURRENT_LIST_DIR}/../../..)
set(RICHMD_DIR ${CMAKE_CURRENT_LIST_DIR}/..)

find_package(glfw3 REQUIRED)
find_package(OpenGL REQUIRED)

# Stock Dear ImGui (the bundle's fork carries patches: this check must not depend on them)
include(FetchContent)
FetchContent_Declare(imgui_stock GIT_REPOSITORY https://github.com/ocornut/imgui.git GIT_TAG v1.92.9 GIT_SHALLOW TRUE)
FetchContent_MakeAvailable(imgui_stock)
set(IMGUI_DIR ${imgui_stock_SOURCE_DIR})

add_library(imgui STATIC
    ${IMGUI_DIR}/imgui.cpp ${IMGUI_DIR}/imgui_draw.cpp ${IMGUI_DIR}/imgui_tables.cpp ${IMGUI_DIR}/imgui_widgets.cpp
    ${IMGUI_DIR}/backends/imgui_impl_glfw.cpp ${IMGUI_DIR}/backends/imgui_impl_opengl3.cpp)
target_include_directories(imgui PUBLIC ${IMGUI_DIR} ${IMGUI_DIR}/backends)
target_link_libraries(imgui PUBLIC glfw OpenGL::GL)

add_library(imgui_md STATIC
    ${RICHMD_DIR}/md4c/src/md4c.c
    ${RICHMD_DIR}/imgui_md/imgui_md.cpp
    ${RICHMD_DIR}/imgui_md_wrapper/imgui_md_wrapper.cpp
    ${RICHMD_DIR}/imgui_md_wrapper/imgui_md_imports.cpp
    stb_image_impl.cpp)
target_include_directories(imgui_md PUBLIC ${RICHMD_DIR} ${RICHMD_DIR}/md4c/src ${RICHMD_DIR}/imgui_md_wrapper
    ${BUNDLE_DIR}/external/immvision/immvision/src/immvision/internal/stb)  # stb_image.h (to vendor in the standalone repo)
target_link_libraries(imgui_md PUBLIC imgui)
if(APPLE)
    set_source_files_properties(${RICHMD_DIR}/md4c/src/md4c.c PROPERTIES COMPILE_OPTIONS "-Wno-macro-redefined")
endif()

include(${RICHMD_DIR}/cmake/imgui_richmd_embed_files.cmake)
imgui_richmd_embed_files(imgui_md imgui_richmd_embedded_assets
    BASE_DIR ${BUNDLE_DIR}/bindings/imgui_bundle/assets
    FILES fonts/Roboto/Roboto-Regular.ttf fonts/Roboto/Roboto-Bold.ttf fonts/Roboto/Roboto-RegularItalic.ttf
          fonts/Roboto/Roboto-BoldItalic.ttf fonts/Inconsolata-Medium.ttf images/markdown_broken_image.png images/world.png)
target_compile_definitions(imgui_md PUBLIC IMGUI_RICHMD_EMBED_ASSETS)

add_executable(imgui_md_standalone_check main.cpp)
target_link_libraries(imgui_md_standalone_check PRIVATE imgui_md)
