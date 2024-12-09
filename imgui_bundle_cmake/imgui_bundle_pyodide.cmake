###################################################################################################
# Specific build options for pyodide
###################################################################################################

function(ibd_pyodide_set_build_options_if_needed)
    # Determine if we need to build pyodide
    if (SKBUILD AND EMSCRIPTEN)
        message(STATUS "Building for pyodide! IMGUI_BUNDLE_BUILD_PYODIDE=${IMGUI_BUNDLE_BUILD_PYODIDE}")
        set(IMGUI_BUNDLE_BUILD_PYODIDE ON CACHE BOOL "" FORCE)
    endif()

    # If so, set the build options (backend selection, lib selection, etc.)
    if(IMGUI_BUNDLE_BUILD_PYODIDE)
        _ibd_pyodide_set_build_options()
    else()
        set(IMGUI_BUNDLE_BUILD_PYODIDE OFF CACHE BOOL "" FORCE)
    endif()
endfunction()

function(ibd_pyodide_manually_link_sdl_to_bindings)
    # Important: SDL2 link notes
    # ==========================
    # See https://github.com/pyodide/pyodide/issues/5248

    # SDL2 must be linked to the native bindings _imgui_bundle.
    # We are already linked to library_sdl.js (via -s USE_SDL=2) in the emscripten bindings.
    # However, we need to link to the native SDL2 library as well (other we will get a runtime error: "SDL_SetHint" not found).
    # This has something to do with the fact that this is a SIDE library, with dynamic linking.
    # For whatever reason, this does not work with find_package.
    # Also, libsdl2.a is not in the default search path, so we need to specify the path to it.

    # We also need to link to html5.a, which contains emscripten_compute_dom_pk_code
    # (cf https://github.com/pyodide/pyodide/issues/5029:
    #     emscripten_compute_dom_pk_code is in html5.a (not html5.js))


    # instead we link manually libSDL2.a:
    if(IMGUI_BUNDLE_BUILD_PYODIDE AND EMSCRIPTEN)

        # See https://github.com/pyodide/pyodide/issues/5248#issuecomment-2527421669
        # (this force the compilation of SDL as a relocatable library)
        target_compile_options(_imgui_bundle PUBLIC "-sRELOCATABLE=1")
        target_link_options(_imgui_bundle PUBLIC "-sRELOCATABLE=1")

        # Manually link native side of html5
        set(ems_lib_path_pic ${EMSCRIPTEN_SYSROOT}/lib/wasm32-emscripten/pic)
        target_link_libraries(_imgui_bundle PUBLIC ${ems_lib_path_pic}/libhtml5.a)

        # Manually link native side of SDL2
        # Unfortunately, we cannot use the emscripten version of SDL2, because it is broken
        # (see https://github.com/pyodide/pyodide/issues/5248#issuecomment-2527713044)

        # Instead, we use a custom **manual** build of SDL2 for pyodide with fPIC
        set(sdl_lib_file ${IMGUI_BUNDLE_PATH}/bindings/pyodide_web_demo/build_resources/libSDL2_emscripten_fPIC/libSDL2.a)
        target_link_libraries(_imgui_bundle PUBLIC ${sdl_lib_file})
    endif()
endfunction()


function(_ibd_pyodide_set_build_options)
    if (NOT IMGUI_BUNDLE_BUILD_PYODIDE)
        message(FATAL_ERROR "ibd_pyodide_set_build_options: IMGUI_BUNDLE_BUILD_PYODIDE is not set")
    endif()
    add_compile_definitions(IMGUI_BUNDLE_BUILD_PYODIDE)

    # No native demos for pyodide
    set(IMGUI_BUNDLE_BUILD_DEMOS OFF CACHE BOOL "" FORCE)

    # FreeType
    set(HELLOIMGUI_USE_FREETYPE ON CACHE BOOL "" FORCE)

    # Backend selection
    set(HELLOIMGUI_USE_SDL2 ON CACHE BOOL "" FORCE)
    set(HELLOIMGUI_HAS_OPENGL3 ON CACHE BOOL "" FORCE)
    set(HELLOIMGUI_USE_GLFW3 OFF CACHE BOOL "" FORCE)

    # No test engine for pyodide
    # (We cannot afford to have test engines, because severe headaches would happen
    #  since we would need to handle threads in between javascript, python and C++...)
    set(HELLOIMGUI_WITH_TEST_ENGINE OFF CACHE BOOL "" FORCE)

    # We need to keep the pthreads enabled, for compatibility with precompiled emscripten OpenCV
    set(HELLOIMGUI_EMSCRIPTEN_PTHREAD ON CACHE BOOL "" FORCE)

    # Disable some features
    set(IMGUI_BUNDLE_DISABLE_IMFILEDIALOG ON CACHE BOOL "" FORCE)

    # Those features are now available in pyodide
    # set(IMGUI_BUNDLE_DISABLE_IMMVISION OFF CACHE BOOL "" FORCE)
    # set(IMGUI_BUNDLE_DISABLE_IMPLOT ON CACHE BOOL "" FORCE)
    # set(IMGUI_BUNDLE_DISABLE_IMGUI_NODE_EDITOR ON CACHE BOOL "" FORCE)
    # set(IMGUI_BUNDLE_DISABLE_IMGUIZMO ON CACHE BOOL "" FORCE)
    # set(IMGUI_BUNDLE_DISABLE_IMGUI_TEX_INSPECT ON CACHE BOOL "" FORCE)
    # set(IMGUI_BUNDLE_DISABLE_NANOVG ON CACHE BOOL "" FORCE)

    # Failed attempts to try to reduce the link time for pyodide (which takes 10 minutes, be patient...)
    # add_link_options("-flto=auto")  # run link time optimization on several threads (no clear benefit)
    # add_link_options("-fno-lto")  # disable link time optimization
    # if (CMAKE_BUILD_TYPE STREQUAL "Release")
    #     add_compile_options("-O0")
    #     add_link_options("-O0")
    # endif()
endfunction()