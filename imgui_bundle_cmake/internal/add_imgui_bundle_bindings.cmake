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


function(_nanobind_hack_disable_forceinline)
    # Hack to disable forceinline in nanobind under Windows
    # This speeds up compilation by a factor of 60x during the optimization phase for MSVC in Release mode
    # (see https://github.com/wjakob/nanobind/discussions/791#discussioncomment-11309473)
    execute_process(
        COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
        OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE nanobind_ROOT)
    set(nanobind_include_dir ${nanobind_ROOT}/../include)
    set(nb_defs_file ${nanobind_include_dir}/nanobind/nb_defs.h)
    # Replace
    #     #  define NB_INLINE          __forceinline
    # By
    #     #  define NB_INLINE          inline
    if (NOT EXISTS ${nb_defs_file})
        message(FATAL_ERROR "_nanobind_hack_disable_forceinline, file not found: ${nb_defs_file}")
    endif()
    file(READ ${nb_defs_file} nb_defs_content)
    string(REPLACE
        "#  define NB_INLINE          __forceinline"
        "#  define NB_INLINE          inline"
        nb_defs_content
        "${nb_defs_content}")
    file(WRITE ${nb_defs_file} "${nb_defs_content}")
endfunction()


function(add_imgui_bundle_bindings)
    include(${IMGUI_BUNDLE_PATH}/imgui_bundle_cmake/internal/litgen_setup_module.cmake)
    litgen_find_nanobind()
    if (WIN32)
        _nanobind_hack_disable_forceinline()
    endif()

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

    nanobind_add_module(${python_native_module_name} ${python_module_sources})
    target_compile_definitions(${python_native_module_name} PRIVATE VERSION_INFO=${PROJECT_VERSION})

    litgen_setup_module(${bound_library} ${python_native_module_name} ${python_wrapper_module_name} ${IMGUI_BUNDLE_PATH}/bindings)

    # add cvnp for immvision
    if (IMGUI_BUNDLE_WITH_IMMVISION)
        set(cvnp_nano_dir ${IMGUI_BUNDLE_PATH}/external/immvision/cvnp_nano)
        target_sources(${python_native_module_name} PRIVATE ${cvnp_nano_dir}/cvnp_nano/cvnp_nano.h)
        target_include_directories(${python_native_module_name} PRIVATE ${cvnp_nano_dir})

        target_compile_definitions(${python_native_module_name} PUBLIC IMGUI_BUNDLE_WITH_IMMVISION)
    endif()

    if(IMGUI_BUNDLE_BUILD_PYTHON)
        # if using shared libraries, we need to set the rpath,
        # so that dll/dylibs can be found in the same folder as imgui_bundle python lib.
        _target_set_rpath(${python_native_module_name} ".")
    endif()

    if (IMGUI_BUNDLE_BUILD_PYODIDE)
        ibd_pyodide_manually_link_sdl_to_bindings()
    endif()

    target_link_libraries(${python_native_module_name} PUBLIC ${bound_library})

    # Link with OpenGL (necessary for nanobind)
    if (NOT  EMSCRIPTEN)
        find_package(OpenGL REQUIRED)
        target_link_libraries(${python_native_module_name} PUBLIC OpenGL::GL)
    endif()

    # Disable optimizations on release build for msvc
    # (leads to compilation times of > 3 hours!!!)
    if (MSVC)
        target_compile_options(${python_native_module_name} PRIVATE $<$<CONFIG:Release>:/Od>)
    endif()

    if (WIN32)
        # Band aid for windows debug build, where the python lib may not be found...
        target_link_directories(${python_native_module_name} PRIVATE ${Python_LIBRARY_DIRS})
    endif()
endfunction()
