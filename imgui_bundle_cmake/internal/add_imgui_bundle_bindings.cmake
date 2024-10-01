# Set the rpath for Linux and  MacOS (see https://github.com/pybind/cmake_example/issues/11)
function(_target_set_rpath target relative_path)
    set_target_properties(${target} PROPERTIES BUILD_WITH_INSTALL_RPATH TRUE)
    if(UNIX AND NOT APPLE)
        set_target_properties(${target} PROPERTIES INSTALL_RPATH "$ORIGIN/${relative_path}/")
    elseif(APPLE)
        set_target_properties(${target} PROPERTIES INSTALL_RPATH "@loader_path/${relative_path}/")
    endif()
    set_target_properties(${target} PROPERTIES INSTALL_RPATH_USE_LINK_PATH TRUE)
endfunction()


function(add_imgui_bundle_bindings)
    set(bindings_main_folder ${IMGUI_BUNDLE_PATH}/external/bindings_generation/cpp/)
    include(${bindings_main_folder}/all_pybind_files.cmake)

    #########################################################################
    # Build python module that provides bindings to the library hello_imgui
    #########################################################################
    set(bound_library imgui_bundle)                 # The library for which we are building bindings
    set(python_native_module_name _imgui_bundle)    # This is the native python module name
    set(python_wrapper_module_name imgui_bundle)    # This is the python wrapper around the native module
    set(python_module_sources
        ${bindings_main_folder}/module.cpp
        ${bindings_main_folder}/pybind_imgui_bundle.cpp
        ${all_pybind_files}
        )

    pybind11_add_module(${python_native_module_name} ${python_module_sources})
    target_compile_definitions(${python_native_module_name} PRIVATE VERSION_INFO=${PROJECT_VERSION})

    litgen_setup_module(${bound_library} ${python_native_module_name} ${python_wrapper_module_name} ${IMGUI_BUNDLE_PATH}/bindings)

    # add cvnp for immvision
    if (IMGUI_BUNDLE_WITH_IMMVISION)
        add_subdirectory(external/immvision/cvnp)
        target_link_libraries(${python_native_module_name} PUBLIC cvnp)
        target_compile_definitions(${python_native_module_name} PUBLIC IMGUI_BUNDLE_WITH_IMMVISION)
    endif()

    if(IMGUI_BUNDLE_BUILD_PYTHON)
        # if using shared libraries, we need to set the rpath,
        # so that dll/dylibs can be found in the same folder as imgui_bundle python lib.
        _target_set_rpath(${python_native_module_name} ".")
    endif()

    if (IMGUI_BUNDLE_BUILD_PYODIDE)
        # Important: SDL2 link notes
        # ==========================
        # SDL2 must be linked to this library. For whatever reason, this does not work with find_package.
        # This has something to do with the fact that this is a SIDE library, with dynamic linking.
        # Also, libsdl2.a is not in the default search path, so we need to specify the path to it.

        # This will not work:
        # find_package(SDL2 REQUIRED)
        # target_link_libraries(_daft2 PUBLIC SDL2::SDL2)

        # instead we link manually libSDL2.a:
        set(sdl_lib_path ${EMSCRIPTEN_SYSROOT}/lib/wasm32-emscripten/lto/)
        target_link_directories(_imgui_bundle PUBLIC ${sdl_lib_path})
        target_link_libraries(_imgui_bundle PUBLIC SDL2)
    endif()

    target_link_libraries(${python_native_module_name} PUBLIC ${bound_library})
endfunction()
