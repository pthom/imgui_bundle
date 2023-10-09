add_this_folder_demos()

if(UNIX AND NOT APPLE)
    target_link_libraries(imgui_example_glfw_opengl3 PUBLIC GL)
endif()
