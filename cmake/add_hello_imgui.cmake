include(${CMAKE_CURRENT_LIST_DIR}/add_imgui.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/add_glfw.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/add_sdl.cmake)

####################################################
# Build hello_imgui Bound C++ library
####################################################
function (add_hello_imgui)
    if (UNIX)
        add_compile_options(-fPIC)
    endif()
    #   i. Build static libraries
    set(BUILD_SHARED_LIBS OFF)
    # 1. Build imgui (lib used by hello_imgui)
    set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/imgui/imgui)
    add_imgui(${imgui_dir})

    if (APPLE)
        enable_language(OBJC) # See https://gitlab.kitware.com/cmake/cmake/-/issues/24104
    endif()

    # 2. Build glfw if required
    if (IMGUI_BUNDLE_WITH_GLFW)
        add_glfw()
    endif()

    # 2.2 Build sdl if required
    if (IMGUI_BUNDLE_WITH_SDL)
        add_sdl()
    endif()

    # 3. Configure hello-imgui with the following options:
    #     i. use glfw
    if (IMGUI_BUNDLE_WITH_GLFW)
        set(HELLOIMGUI_USE_GLFW_OPENGL3 ON CACHE BOOL "" FORCE)
    endif()
    #     ii. use sdl
    if (IMGUI_BUNDLE_WITH_SDL)
        set(HELLOIMGUI_USE_SDL_OPENGL3 ON CACHE BOOL "" FORCE)
    endif()
    #     iii. use provided imgui version
    set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/imgui/imgui)
    set(HELLOIMGUI_BUILD_IMGUI OFF CACHE BOOL "" FORCE)
    set(HELLOIMGUI_IMGUI_SOURCE_DIR ${imgui_dir} CACHE STRING "" FORCE)

    # 4. Finally, add hello_imgui
    add_subdirectory(hello_imgui/hello_imgui)
    target_link_libraries(imgui_bundle PUBLIC hello_imgui)

    if (WIN32 AND IMGUI_BUNDLE_WITH_SDL)
        target_link_libraries(hello_imgui PUBLIC SDL2main)
    endif()

    # 5. Export hello_imgui symbols on Windows without using __declspec(dllexport)
    if (WIN32)
        set_target_properties(hello_imgui PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
    endif()
endfunction()
