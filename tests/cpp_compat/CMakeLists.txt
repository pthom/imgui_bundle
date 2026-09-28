# A compatibility check: code written for the markdown API of v1.92.900 (imgui_md_wrapper.h, namespace ImGuiMd)
# must still compile and link against the installed package. Built by `just test_cpp_compat`, and by the CI
# workflow cpp_install_package.yml.
cmake_minimum_required(VERSION 3.22)
project(imgui_bundle_cpp_compat)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(imgui_bundle CONFIG REQUIRED)

add_executable(imgui_md_compat_check imgui_md_compat_check.cpp)
target_link_libraries(imgui_md_compat_check PRIVATE imgui_bundle::imgui_bundle)
