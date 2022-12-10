if (IMGUI_BUNDLE_WITH_IMMVISION)
    add_subdirectory(functions_composition_graph)
    add_demo_cpp(demo_compose_image demo_compose_image.main.cpp)
    target_link_libraries(demo_compose_image PRIVATE functions_composition_graph)

    # For Visual studio
    set_target_properties(demo_compose_image PROPERTIES VS_DEBUGGER_WORKING_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})

    add_demo_cpp(demo_compose_add demo_compose_add.main.cpp)
    target_link_libraries(demo_compose_add PRIVATE functions_composition_graph)
endif()
