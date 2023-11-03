cmake_minimum_required(VERSION 3.10)
project(HelloImGuiCiAutomationTests LANGUAGES C CXX)
set(CMAKE_CXX_STANDARD 17)


if(NOT TARGET imgui_bundle)
    add_subdirectory(../../ imgui_bundle)
endif()

imgui_bundle_add_app(ci_automation_test_app_bundle ci_automation_test_app_bundle.cpp)
