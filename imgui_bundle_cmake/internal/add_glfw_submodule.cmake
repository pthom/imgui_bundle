####################################################
# Build glfw as a shared library for python
####################################################
function(_set_glfw_build_options_pre_add)
    set(GLFW_BUILD_EXAMPLES OFF PARENT_SCOPE)
    set(GLFW_BUILD_TESTS OFF PARENT_SCOPE)
    set(GLFW_BUILD_DOCS OFF PARENT_SCOPE)
    set(GLFW_INSTALL OFF PARENT_SCOPE)
    set(GLFW_BUILD_WAYLAND OFF PARENT_SCOPE)
endfunction()

function(_set_glfw_build_options_post_add)
    if (UNIX AND NOT APPLE)
        # Those are only needed for wheels build using cibuildwheel (cp36-manylinux_x86_64 wheel)
        # See https://bytemeta.vip/repo/glfw/glfw/issues/2139
        target_compile_definitions(glfw PRIVATE POSIX_REQUIRED_STANDARD=199309L)
        target_compile_definitions(glfw PRIVATE _POSIX_C_SOURCE=POSIX_REQUIRED_STANDARD)
        target_compile_definitions(glfw PRIVATE _POSIX_SOURCE=POSIX_REQUIRED_STANDARD)
    endif()
endfunction()

function(add_glfw_as_python_shared_library)
    # Build glfw as a *shared* library:
    #   this is required if we want to be able to use python bindings
    #   for glfw, using https://github.com/FlorianRhiem/pyGLFW
    _set_glfw_build_options_pre_add()
    set(BUILD_SHARED_LIBS ON)

    # Note: the rpath is set by a call to
    #     lg_target_set_rpath(${python_native_module_name} ".")
    # (inside add_imgui_bundle_bindings)
    add_subdirectory(glfw/glfw)
    # glfw dynamic lib will be installed in the same folder as imgui_bundle (next to the
    # native module, which loads it via @rpath). This covers both wheels and editable
    # installs (pip records it as a package file). The native module is itself deployed
    # to that same site-packages folder by litgen_setup_module, so no separate "copy glfw
    # into bindings/" step is needed (that was only for the legacy PYTHONPATH=bindings
    # workflow; pyGLFW now follows the native module's directory, see _glfw_set_search_path).
    install(TARGETS glfw DESTINATION imgui_bundle)

    set(BUILD_SHARED_LIBS OFF)
    _set_glfw_build_options_post_add()
endfunction()
