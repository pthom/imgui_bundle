# The installed package holds every library: each one's main header compiles, and one function of each links.
# Built by `just test_cpp_install_headers`, and by the CI workflow cpp_install_package.yml.
cmake_minimum_required(VERSION 3.22)
project(imgui_bundle_cpp_install_headers)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(imgui_bundle CONFIG REQUIRED)

add_executable(all_headers_check all_headers_check.cpp)
target_link_libraries(all_headers_check PRIVATE imgui_bundle::imgui_bundle)
