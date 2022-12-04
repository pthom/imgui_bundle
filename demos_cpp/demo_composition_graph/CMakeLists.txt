add_subdirectory(functions_composition_graph)

if (IMGUI_BUNDLE_WITH_IMMVISION)
    imgui_bundle_add_app(demo_compose_image demo_compose_image.main.cpp)
    target_link_libraries(demo_compose_image PRIVATE functions_composition_graph)

    # For Visual studio
    set_target_properties(demo_compose_image PROPERTIES VS_DEBUGGER_WORKING_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})
endif()

imgui_bundle_add_app(demo_compose_add demo_compose_add.main.cpp)
target_link_libraries(demo_compose_add PRIVATE functions_composition_graph)
