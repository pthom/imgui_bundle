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
    set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/external/imgui)
    add_imgui_target(${imgui_dir})

    # 2. Build glfw (also used by hello_imgui)
    add_subdirectory(external/glfw)
    if (UNIX AND NOT APPLE)
        # Those are only needed for wheels build using cibuildwheel (cp36-manylinux_x86_64 wheel)
        # See https://bytemeta.vip/repo/glfw/glfw/issues/2139
        target_compile_definitions(glfw PRIVATE POSIX_REQUIRED_STANDARD=199309L)
        target_compile_definitions(glfw PRIVATE _POSIX_C_SOURCE=POSIX_REQUIRED_STANDARD)
        target_compile_definitions(glfw PRIVATE _POSIX_SOURCE=POSIX_REQUIRED_STANDARD)
    endif()

    # 3. Configure hello-imgui with the following options:
    #     i. use glfw
    set(HELLOIMGUI_USE_GLFW_OPENGL3 ON CACHE BOOL "" FORCE)
    #     ii. use provided imgui version
    set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/external/imgui)
    set(HELLOIMGUI_BUILD_IMGUI OFF CACHE BOOL "" FORCE)
    set(HELLOIMGUI_IMGUI_SOURCE_DIR ${imgui_dir} CACHE STRING "" FORCE)

    # 4. Finally, add hello_imgui
    add_subdirectory(external/hello_imgui)
    target_link_libraries(imgui_bundle PUBLIC hello_imgui)


    # 5. Export hello_imgui symbols on Windows without using __declspec(dllexport)
    if (WIN32)
        set_target_properties(hello_imgui PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
    endif()
endfunction()
