####################################################
# Build glfw
####################################################
function(add_glfw)
    set_glfw_build_options_pre_add()
    if (IMGUI_BUNDLE_BUILD_PYTHON)
        add_glfw_as_python_shared_library()
    else()
        add_glfw_as_static_library()
    endif()
    set_glfw_build_options_post_add()
endfunction()

function(set_glfw_build_options_pre_add)
    set(GLFW_BUILD_EXAMPLES OFF PARENT_SCOPE)
    set(GLFW_BUILD_TESTS OFF PARENT_SCOPE)
    set(GLFW_BUILD_DOCS OFF PARENT_SCOPE)
    set(GLFW_INSTALL OFF PARENT_SCOPE)
endfunction()

function(set_glfw_build_options_post_add)
    if (UNIX AND NOT APPLE)
        # Those are only needed for wheels build using cibuildwheel (cp36-manylinux_x86_64 wheel)
        # See https://bytemeta.vip/repo/glfw/glfw/issues/2139
        target_compile_definitions(glfw PRIVATE POSIX_REQUIRED_STANDARD=199309L)
        target_compile_definitions(glfw PRIVATE _POSIX_C_SOURCE=POSIX_REQUIRED_STANDARD)
        target_compile_definitions(glfw PRIVATE _POSIX_SOURCE=POSIX_REQUIRED_STANDARD)
    endif()
endfunction()

function(add_glfw_as_static_library)
    add_subdirectory(glfw/glfw)
endfunction()

function(add_glfw_as_python_shared_library)
    # Build glfw as a *shared* library:
    #   this is required if we want to be able to use python bindings
    #   for glfw, using https://github.com/FlorianRhiem/pyGLFW
    set(BUILD_SHARED_LIBS ON)

    # Note: the rpath is set by a call to
    #     lg_target_set_rpath(${python_native_module_name} ".")
    # (inside add_imgui_bundle_bindings)
    add_subdirectory(glfw/glfw)
    # glfw dynamic lib will be in the same folder as imgui_bundle
    install(TARGETS glfw DESTINATION .)
    # copy glfw dynamic lib into bindings/imgui_bundle post build, for editable install mode
    lg_copy_target_output_to_python_wrapper_folder(imgui_bundle glfw)
    # glfw usually relies on the presence of symlinks: for example libglfw.3.dylib points to libglfw.3.4.dylib
    #    below, we emulate those symlinks by creating copies of the dynamic library
    lg_copy_target_output_to_python_wrapper_folder_with_custom_name(imgui_bundle glfw libglfw.3.dylib)
    lg_copy_target_output_to_python_wrapper_folder_with_custom_name(imgui_bundle glfw libglfw.3.so)

    set(BUILD_SHARED_LIBS OFF)
endfunction()
