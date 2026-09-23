# Markdown with stock Dear ImGui (fetched, v1.92.9) + GLFW + OpenGL3, no HelloImGui, the assets embedded.
#   cmake -S examples/minimal -B build && cmake --build build   (or IMGUI_RICHMD_BUILD_EXAMPLES=ON at the root)
cmake_minimum_required(VERSION 3.20)
project(imgui_rich_md_minimal CXX C)
set(CMAKE_CXX_STANDARD 17)

find_package(glfw3 REQUIRED)
find_package(OpenGL REQUIRED)
if(NOT TARGET imgui)
    include(FetchContent)
    FetchContent_Declare(imgui_stock GIT_REPOSITORY https://github.com/ocornut/imgui.git GIT_TAG v1.92.9 GIT_SHALLOW TRUE)
    FetchContent_MakeAvailable(imgui_stock)
    set(IMGUI_DIR ${imgui_stock_SOURCE_DIR})
    add_library(imgui STATIC
        ${IMGUI_DIR}/imgui.cpp ${IMGUI_DIR}/imgui_draw.cpp ${IMGUI_DIR}/imgui_tables.cpp ${IMGUI_DIR}/imgui_widgets.cpp
        ${IMGUI_DIR}/backends/imgui_impl_glfw.cpp ${IMGUI_DIR}/backends/imgui_impl_opengl3.cpp)
    target_include_directories(imgui PUBLIC ${IMGUI_DIR} ${IMGUI_DIR}/backends)
    target_link_libraries(imgui PUBLIC glfw OpenGL::GL)
endif()
if(NOT TARGET imgui_rich_md)
    set(IMGUI_RICHMD_EMBED_ASSETS ON)
    set(IMGUI_RICHMD_STB_IMAGE_IMPLEMENTATION ON)
    set(IMGUI_RICHMD_EMBED_EXTRA_FILES images/world.png)
    add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/../.. imgui_rich_md_build)
endif()

add_executable(imgui_rich_md_minimal main.cpp)
target_link_libraries(imgui_rich_md_minimal PRIVATE imgui_rich_md glfw OpenGL::GL)
