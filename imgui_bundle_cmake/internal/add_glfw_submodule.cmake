####################################################
# Build glfw as a shared library for python
####################################################
function(_set_glfw_build_options_pre_add)
    set(GLFW_BUILD_EXAMPLES OFF PARENT_SCOPE)
    set(GLFW_BUILD_TESTS OFF PARENT_SCOPE)
    set(GLFW_BUILD_DOCS OFF PARENT_SCOPE)
    set(GLFW_INSTALL OFF PARENT_SCOPE)
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
    # glfw dynamic lib will be in the same folder as imgui_bundle
    install(TARGETS glfw DESTINATION imgui_bundle)

    # deploy glfw for editable mode:
    #    usually relies on the presence of symlinks: for example libglfw.3.dylib points to libglfw.3.4.dylib
    #    below, we emulate those symlinks by creating copies of the dynamic library
    if (IMGUI_BUNDLE_BUILD_PYTHON AND NOT SKBUILD)
        add_custom_target(
            glfw_deploy_editable
            ALL
            COMMAND
                ${CMAKE_COMMAND} -E copy $<TARGET_FILE:glfw>  ${IMGUI_BUNDLE_PATH}/bindings/imgui_bundle/$<TARGET_FILE_NAME:glfw>
            COMMAND
                ${CMAKE_COMMAND} -E copy $<TARGET_FILE:glfw>  ${IMGUI_BUNDLE_PATH}/bindings/imgui_bundle/libglfw.3.dylib
            COMMAND
                ${CMAKE_COMMAND} -E copy $<TARGET_FILE:glfw>  ${IMGUI_BUNDLE_PATH}/bindings/imgui_bundle/libglfw.3.so
            DEPENDS glfw
        )
    endif()
    set(BUILD_SHARED_LIBS OFF)
    _set_glfw_build_options_post_add()
endfunction()
