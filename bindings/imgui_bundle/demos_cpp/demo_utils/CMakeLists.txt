file(GLOB sources *.h *.cpp)
add_library(demo_utils ${sources})
target_include_directories(demo_utils PUBLIC ${CMAKE_CURRENT_LIST_DIR}/..)
target_link_libraries(demo_utils PUBLIC imgui_bundle immapp)
