####################################################
# Build SDL
####################################################
function(add_sdl)
    if (EMSCRIPTEN)
        # nothing to do, SDL is already included by emscripten
    else()
        if (IMGUI_BUNDLE_BUILD_PYTHON)
            add_sdl_as_python_shared_library()
        else()
            add_sdl_as_static_library()
        endif()
    endif()
endfunction()

function(add_sdl_as_static_library)
    add_subdirectory(SDL/SDL)
endfunction()

function(add_sdl_as_python_shared_library)
    # Build SDL as a *shared* library:
    #   this is required if we want to be able to use python bindings
    set(BUILD_SHARED_LIBS ON)

    # Note: the rpath is set by a call to
    #     lg_target_set_rpath(${python_native_module_name} ".")
    # (inside add_imgui_bundle_bindings)
    add_subdirectory(SDL/SDL)
    # SDL dynamic lib will be in the same folder as imgui_bundle
    install(TARGETS SDL2 DESTINATION .)
    # copy SDL dynamic lib into bindings/imgui_bundle post build, for editable install mode
    lg_copy_target_output_to_python_wrapper_folder(imgui_bundle SDL2)

#    # glfw usually relies on the presence of symlinks: for example libglfw.3.dylib points to libglfw.3.4.dylib
#    #    below, we emulate those symlinks by creating copies of the dynamic library
#    lg_copy_target_output_to_python_wrapper_folder_with_custom_name(imgui_bundle glfw libglfw.3.dylib)
#    lg_copy_target_output_to_python_wrapper_folder_with_custom_name(imgui_bundle glfw libglfw.3.so)

    set(BUILD_SHARED_LIBS OFF)
endfunction()
