add_this_folder_demos()
if(EMSCRIPTEN)
    target_link_libraries(imgui_example_glfw_opengl3 PUBLIC GL)
else()
    if (UNIX OR (APPLE AND NOT IOS))
        find_package(OpenGL REQUIRED)
        target_link_libraries(imgui_example_glfw_opengl3 PUBLIC OpenGL::GL)
    endif()
endif()

if(EMSCRIPTEN AND HELLOIMGUI_EMSCRIPTEN_PTHREAD)
    # Needed addition for multithread support (required by ImGui Test Engine)
    # Note: see the shell.emscripten.html in this folder we are using a custom shell,
    #       that provides Cross-origin isolation (COOP and COEP) through a service worker
    #       for situations in which you can't control the headers (e.g. GitHub pages).
    #
    # coi-serviceworker.js was found at https://github.com/gzuidhof/coi-serviceworker, and manually patched:
    #    see https://github.com/gzuidhof/coi-serviceworker/issues/20
    #    and https://github.com/gzuidhof/coi-serviceworker/compare/master...tamo:coi-serviceworker:coep-ua-brand
    #
    # coi-serviceworker.js provides Cross-origin isolation (COOP and COEP) through a service worker
    # for situations in which you can't control the headers (e.g. GitHub pages).

    get_property(runtime_output_directory TARGET demo_testengine PROPERTY RUNTIME_OUTPUT_DIRECTORY)
    FILE(MAKE_DIRECTORY ${runtime_output_directory})
    FILE(COPY_FILE ${CMAKE_CURRENT_LIST_DIR}/coi-serviceworker.js ${runtime_output_directory}/coi-serviceworker.js)

    target_link_options(demo_testengine PUBLIC -sPTHREAD_POOL_SIZE=2)
endif()
