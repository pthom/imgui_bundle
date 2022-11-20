set(himgui_cmake_path ${CMAKE_CURRENT_LIST_DIR}/../external/hello_imgui/hello_imgui_cmake)
include(${himgui_cmake_path}/hello_imgui_add_app.cmake)

#
# imgui_bundle_add_app is a helper function, similar to cmake's "add_executable"
#
# Usage:
# imgui_bundle_add_app(app_name file1.cpp file2.cpp ...)
#
# Features: see the doc for hello_imgui_prepare_app, which is called by this function
function(imgui_bundle_add_app)
    set(args ${ARGN})
    list(GET args 0 app_name)

    hello_imgui_add_app(${args})
    target_link_libraries(${app_name} PRIVATE imgui_bundle)
endfunction()
