file(GLOB sources *.h *.cpp)
add_library(functions_composition_graph ${sources})
target_include_directories(functions_composition_graph PUBLIC ${CMAKE_CURRENT_LIST_DIR}/..)
target_link_libraries(functions_composition_graph PUBLIC imgui_bundle)
