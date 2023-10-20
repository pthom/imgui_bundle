add_this_folder_demos()

if(UNIX AND NOT APPLE)
    target_link_libraries(imgui_example_glfw_opengl3 PUBLIC GL)
endif()

if(EMSCRIPTEN)
    # hello_imgui_set_emscripten_target_initial_memory_megabytes(demo_testengine 400)
    target_link_options(demo_testengine PUBLIC -pthread -sPTHREAD_POOL_SIZE=2)
endif()