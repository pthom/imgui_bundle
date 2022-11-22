set(CMAKE_CXX_STANDARD 20)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

add_subdirectory(demo_haiku_implot_heart)
add_subdirectory(demo_texteditor)
add_subdirectory(demo_widgets_docking)
add_subdirectory(demo_imgui_node_editor)
add_subdirectory(demo_powersave)

add_subdirectory(demos_immvision)
add_subdirectory(demo_composition_graph)
