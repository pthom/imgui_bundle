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

    if (APPLE)
        enable_language(OBJC) # See https://gitlab.kitware.com/cmake/cmake/-/issues/24104
    endif()

    # 2. Build glfw
    if (IMGUI_BUNDLE_BUILD_PYTHON)
        # Build glfw as a *shared* library:
        #   this is required if we want to be able to use python bindings
        #   for glfw, using https://github.com/FlorianRhiem/pyGLFW
        # Note: the rpath is set by a call to
        #     lg_target_set_rpath(${python_native_module_name} ".")
        # (inside add_imgui_bundle_bindings)
        set(BUILD_SHARED_LIBS ON)
        add_subdirectory(external/glfw)
        # glfw dynamic lib will be in the same folder as imgui_bundle
         install(TARGETS glfw DESTINATION .)
        # copy glfw dynamic lib into bindings/imgui_bundle post build, for editable install mode
         lg_copy_target_output_to_python_wrapper_folder(imgui_bundle glfw)
        # glfw usually relies on the presence of symlinks: for example libglfw.3.dylib points to libglfw.3.4.dylib
        #    below, we emulate those symlinks by creating copies of the dynamic library
         lg_copy_target_output_to_python_wrapper_folder_with_custom_name(imgui_bundle glfw libglfw.3.dylib)
         lg_copy_target_output_to_python_wrapper_folder_with_custom_name(imgui_bundle glfw libglfw.3.so)
        set(BUILD_SHARED_LIBS OFF)
    else()
        add_subdirectory(external/glfw)
    endif()
    if (UNIX AND NOT APPLE)
        # Those are only needed for wheels build using cibuildwheel (cp36-manylinux_x86_64 wheel)
        # See https://bytemeta.vip/repo/glfw/glfw/issues/2139
        target_compile_definitions(glfw PRIVATE POSIX_REQUIRED_STANDARD=199309L)
        target_compile_definitions(glfw PRIVATE _POSIX_C_SOURCE=POSIX_REQUIRED_STANDARD)
        target_compile_definitions(glfw PRIVATE _POSIX_SOURCE=POSIX_REQUIRED_STANDARD)
    endif()

    # 2.2 Build sdl
    if (IMGUI_BUNDLE_WITH_SDL)
        add_subdirectory(external/SDL)
    endif()

    # 3. Configure hello-imgui with the following options:
    #     i. use glfw
    set(HELLOIMGUI_USE_GLFW_OPENGL3 ON CACHE BOOL "" FORCE)
    #     i. use sdl
    if (IMGUI_BUNDLE_WITH_SDL)
        set(HELLOIMGUI_USE_SDL_OPENGL3 ON CACHE BOOL "" FORCE)
    endif()
    #     ii. use provided imgui version
    set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/external/imgui)
    set(HELLOIMGUI_BUILD_IMGUI OFF CACHE BOOL "" FORCE)
    set(HELLOIMGUI_IMGUI_SOURCE_DIR ${imgui_dir} CACHE STRING "" FORCE)

    # 4. Finally, add hello_imgui
    add_subdirectory(external/hello_imgui)
    target_link_libraries(imgui_bundle PUBLIC hello_imgui)

    if (WIN32 AND IMGUI_BUNDLE_WITH_SDL)
        target_link_libraries(hello_imgui PUBLIC SDL2main)
    endif()

    # 5. Export hello_imgui symbols on Windows without using __declspec(dllexport)
    if (WIN32)
        set_target_properties(hello_imgui PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
    endif()
endfunction()
