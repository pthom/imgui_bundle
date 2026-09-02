include(CMakeFindDependencyMacro)

include(${CMAKE_CURRENT_LIST_DIR}/imgui_bundle-targets.cmake)

# hello_imgui is part of this package (imgui_bundle::hello_imgui);
# hello_imgui_add_app() links against hello_imgui::hello_imgui
if(NOT TARGET hello_imgui::hello_imgui)
    add_library(hello_imgui::hello_imgui INTERFACE IMPORTED)
    target_link_libraries(hello_imgui::hello_imgui INTERFACE imgui_bundle::hello_imgui)
endif()

include(${CMAKE_CURRENT_LIST_DIR}/imgui_bundle_cmake/imgui_bundle_add_app.cmake)
