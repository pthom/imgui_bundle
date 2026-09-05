cmake_minimum_required(VERSION 3.22)
project(test_package CXX)
set(CMAKE_CXX_STANDARD 17)

find_package(imgui_bundle CONFIG REQUIRED)
imgui_bundle_add_app(test_package test_package.cpp)
