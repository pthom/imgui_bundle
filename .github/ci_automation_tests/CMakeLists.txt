cmake_minimum_required(VERSION 3.10)
project(HelloImGuiCiAutomationTests LANGUAGES C CXX)
set(CMAKE_CXX_STANDARD 17)


if(NOT TARGET imgui_bundle)
    add_subdirectory(../../ imgui_bundle)
endif()

imgui_bundle_add_app(ci_automation_test_app_bundle ci_automation_test_app_bundle.cpp)

# Tests of imgui-node-editor: the tests live in the fork (runner-agnostic), this is their runner
set(node_editor_tests_dir ${CMAKE_CURRENT_LIST_DIR}/../../external/imgui-node-editor/imgui-node-editor/tests)
imgui_bundle_add_app(ci_node_editor_tests ci_node_editor_tests.cpp ${node_editor_tests_dir}/node_editor_tests.cpp)
target_include_directories(ci_node_editor_tests PRIVATE ${node_editor_tests_dir})
