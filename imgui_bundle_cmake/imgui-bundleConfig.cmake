include(CMakeFindDependencyMacro)
#find_dependency(imgui CONFIG REQUIRED)
#find_dependency(glad CONFIG REQUIRED)

include(${CMAKE_CURRENT_LIST_DIR}/imgui_bundle_cmake/imgui_bundle_add_app.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/imgui_bundle-targets.cmake)
