set(IMGUI_BUNDLE_CMAKE_PATH ${CMAKE_CURRENT_LIST_DIR} CACHE STRING "" FORCE)


###################################################################################################
# Dependency chain resolution — Phase 1 (early)
# Resolves dependencies between IMGUI_BUNDLE_WITH_* module flags.
# Call this after all IMGUI_BUNDLE_WITH_* options are declared (in CMakeLists.txt),
# before add_subdirectory(external).
# Does NOT consult HELLOIMGUI_HAS_OPENGL3 / HELLOIMGUI_HAS_METAL — those are only
# reliably set after HelloImGui has been configured. See Phase 2 below.
###################################################################################################
macro(imgui_bundle_resolve_early_dependencies)
    if(NOT IMGUI_BUNDLE_WITH_HELLO_IMGUI)
        message(STATUS "
    ===========================================================
     IMGUI_BUNDLE_WITH_HELLO_IMGUI is OFF, automatically disabling dependent modules:
        immapp              (depends on hello_imgui)
        imgui_md            (depends on hello_imgui + immapp)
        imgui_test_engine   (needs GIL management)
        GLFW backend        (not needed)
    ===========================================================")
        set(IMGUI_BUNDLE_WITH_IMMAPP OFF CACHE BOOL "Auto-disabled: depends on hello_imgui" FORCE)
        set(IMGUI_BUNDLE_WITH_IMGUI_MD OFF CACHE BOOL "Auto-disabled: depends on hello_imgui" FORCE)
        set(HELLOIMGUI_WITH_TEST_ENGINE OFF CACHE BOOL "Auto-disabled: needs GIL management from hello_imgui" FORCE)
        set(HELLOIMGUI_USE_GLFW3 OFF CACHE BOOL "Auto-disabled: not needed without hello_imgui" FORCE)
        set(HELLOIMGUI_HAS_OPENGL3 OFF CACHE BOOL "Auto-disabled: not needed without hello_imgui" FORCE)
    endif()
    if(NOT IMGUI_BUNDLE_WITH_HELLO_IMGUI AND IMGUI_BUNDLE_WITH_IMMAPP)
        message(WARNING "Auto-disabling immapp (immapp depends on hello_imgui)")
        set(IMGUI_BUNDLE_WITH_IMMAPP OFF CACHE BOOL "Auto-disabled: immapp depends on hello_imgui" FORCE)
    endif()
    if(NOT IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR AND IMGUI_BUNDLE_WITH_IMMAPP)
        message(STATUS "Auto-disabling immapp (immapp depends on imgui_node_editor)")
        set(IMGUI_BUNDLE_WITH_IMMAPP OFF CACHE BOOL "Auto-disabled: immapp depends on imgui_node_editor" FORCE)
    endif()
    if(NOT IMGUI_BUNDLE_WITH_IMMAPP AND IMGUI_BUNDLE_WITH_IMGUI_MD)
        message(STATUS "Auto-disabling imgui_md (imgui_md depends on immapp)")
        set(IMGUI_BUNDLE_WITH_IMGUI_MD OFF CACHE BOOL "Auto-disabled: imgui_md depends on immapp" FORCE)
    endif()
endmacro()


###################################################################################################
# Dependency chain resolution — Phase 2 (after HelloImGui)
# Resolves dependencies on the rendering backend.
# Call this in external/CMakeLists.txt, after add_hello_imgui() has been called,
# so that HELLOIMGUI_HAS_OPENGL3 and HELLOIMGUI_HAS_METAL reflect actual platform support.
###################################################################################################
macro(imgui_bundle_resolve_rendering_backend_dependencies)
    if(NOT HELLOIMGUI_HAS_OPENGL3)
        message(STATUS "
    ===========================================================
     HELLOIMGUI_HAS_OPENGL3 is OFF, automatically disabling dependent modules:
        im_file_dialog      (needs OpenGL context)
        imgui_tex_inspect   (needs OpenGL context)
        immvision           (needs OpenGL context)
    ")
        set(IMGUI_BUNDLE_WITH_IMFILEDIALOG OFF CACHE BOOL "Auto-disabled: needs OpenGL context" FORCE)
        set(IMGUI_BUNDLE_WITH_IMGUI_TEX_INSPECT OFF CACHE BOOL "Auto-disabled: needs OpenGL context" FORCE)
        set(IMGUI_BUNDLE_WITH_IMMVISION OFF CACHE BOOL "Auto-disabled: needs OpenGL context" FORCE)
    endif()
    if(IMGUI_BUNDLE_WITH_NANOVG AND NOT(HELLOIMGUI_HAS_OPENGL3 OR HELLOIMGUI_HAS_METAL))
        message(WARNING "Auto-disabling nanovg (nanovg depends on OpenGL3 or Metal)")
        set(IMGUI_BUNDLE_WITH_NANOVG OFF CACHE BOOL "Auto-disabled: nanovg depends on OpenGL3 or Metal" FORCE)
    endif()
endmacro()


###################################################################################################
# Backward compatibility layer for legacy IMGUI_BUNDLE_DISABLE_* options
###################################################################################################
# This macro translates legacy IMGUI_BUNDLE_DISABLE_* options to new IMGUI_BUNDLE_WITH_* options
# with deprecation warnings. Support will be removed circa January 2028.
macro(imgui_bundle_translate_legacy_disable_options)
    set(_all_options
        HELLO_IMGUI
        IMMAPP
        IMGUI_MD
        NANOVG
        IMPLOT
        IMPLOT3D
        IMGUI_NODE_EDITOR
        IMGUIZMO
        IMGUI_TEX_INSPECT
        IMFILEDIALOG
        IMMVISION
    )

    foreach(_opt ${_all_options})
        if(DEFINED IMGUI_BUNDLE_DISABLE_${_opt})
            message(DEPRECATION
                "IMGUI_BUNDLE_DISABLE_${_opt} is deprecated and will be removed in a future version (circa January 2028). "
                "Please use IMGUI_BUNDLE_WITH_${_opt}=OFF instead.")

            # Invert the boolean value: DISABLE_X=ON means WITH_X=OFF
            if(IMGUI_BUNDLE_DISABLE_${_opt})
                set(IMGUI_BUNDLE_WITH_${_opt} OFF CACHE BOOL "Translated from legacy DISABLE option" FORCE)
            else()
                set(IMGUI_BUNDLE_WITH_${_opt} ON CACHE BOOL "Translated from legacy DISABLE option" FORCE)
            endif()
        endif()
    endforeach()
endmacro()


###################################################################################################
# Environment variable handling for Python builds
###################################################################################################
# This macro allows environment variables to override IMGUI_BUNDLE_WITH_* options
# Usage: Call this macro after defining all IMGUI_BUNDLE_WITH_* options in CMakeLists.txt
macro(imgui_bundle_apply_env_var_overrides)
    if(IMGUI_BUNDLE_BUILD_PYTHON)
        # List of all options that can be controlled via environment variables
        set(_with_options
            HELLO_IMGUI
            IMMAPP
            IMGUI_MD
            NANOVG
            IMPLOT
            IMPLOT3D
            IMGUI_NODE_EDITOR
            IMGUIZMO
            IMGUI_TEX_INSPECT
            IMFILEDIALOG
            IMMVISION
        )

        foreach(_opt ${_with_options})
            # Support new WITH_* environment variables
            if(DEFINED ENV{IMGUI_BUNDLE_WITH_${_opt}})
                set(IMGUI_BUNDLE_WITH_${_opt} "$ENV{IMGUI_BUNDLE_WITH_${_opt}}" CACHE BOOL "Set from environment variable" FORCE)
                message(STATUS "IMGUI_BUNDLE_WITH_${_opt} set to $ENV{IMGUI_BUNDLE_WITH_${_opt}} from environment")
            endif()

            # Support legacy DISABLE_* environment variables with deprecation warning
            if(DEFINED ENV{IMGUI_BUNDLE_DISABLE_${_opt}})
                message(DEPRECATION
                    "Environment variable IMGUI_BUNDLE_DISABLE_${_opt} is deprecated and will be removed in a future version (circa January 2028). "
                    "Please use IMGUI_BUNDLE_WITH_${_opt} instead (with inverted logic).")

                # Invert the value: DISABLE_X=ON means WITH_X=OFF
                if("$ENV{IMGUI_BUNDLE_DISABLE_${_opt}}")
                    set(IMGUI_BUNDLE_WITH_${_opt} OFF CACHE BOOL "Set from legacy environment variable" FORCE)
                else()
                    set(IMGUI_BUNDLE_WITH_${_opt} ON CACHE BOOL "Set from legacy environment variable" FORCE)
                endif()
                message(STATUS "IMGUI_BUNDLE_WITH_${_opt} set to ${IMGUI_BUNDLE_WITH_${_opt}} from legacy environment variable IMGUI_BUNDLE_DISABLE_${_opt}")
            endif()
        endforeach()
    endif()
endmacro()


###################################################################################################
# Store installable dependencies
###################################################################################################
function(ibd_add_installable_dependency dependency_name)
    set(IMGUI_BUNDLE_INSTALLABLE_DEPENDENCIES ${IMGUI_BUNDLE_INSTALLABLE_DEPENDENCIES} ${dependency_name} CACHE INTERNAL "" FORCE)
    # message(STATUS "Added installable dependency ${dependency_name}, IMGUI_BUNDLE_INSTALLABLE_DEPENDENCIES=${IMGUI_BUNDLE_INSTALLABLE_DEPENDENCIES}")
endfunction()

function(ibd_reset_installable_dependencies)
    set(IMGUI_BUNDLE_INSTALLABLE_DEPENDENCIES "" CACHE INTERNAL "" FORCE)
endfunction()

###################################################################################################
# Misc
###################################################################################################

# make imgui_bundle_add_app available
function(ibd_include_imgui_bundle_add_app)
    list(APPEND CMAKE_MODULE_PATH "${IMGUI_BUNDLE_CMAKE_PATH}")
    include(imgui_bundle_add_app)
endfunction()

function(ibd_force_freetype_static_for_python)
    # For python bindings, we force the usage of a static version of freetype
    if(IMGUI_BUNDLE_BUILD_PYTHON AND HELLOIMGUI_USE_FREETYPE AND NOT IMGUI_BUNDLE_PYTHON_USE_SYSTEM_LIBS)
        # if using vcpkg, we suppose it uses the static version of freetype
        if(NOT "$ENV{CMAKE_TOOLCHAIN_FILE}" MATCHES "vcpkg")
            set(HELLOIMGUI_FREETYPE_STATIC ON CACHE BOOL "" FORCE)
        endif()
    endif()
endfunction()

# See https://github.com/pthom/imgui_bundle/issues/261 and https://chatgpt.com/share/66ffb718-6408-8004-be5b-9e74064a8709
function(ibd_disable_system_libraries_for_python_for_pure_pip)
    if( IMGUI_BUNDLE_BUILD_PYTHON
        AND NOT "$ENV{CMAKE_TOOLCHAIN_FILE}" MATCHES "vcpkg" # Not using vcpkg
        AND NOT DEFINED CONAN_BUILD  # Not using conan
        AND NOT IMGUI_BUNDLE_PYTHON_USE_SYSTEM_LIBS  # Not using system libraries (for conda)
       )
        message(STATUS "ibd_disable_system_libraries_for_python_for_pure_pip: Disabling system libraries for python bindings")
        set(CMAKE_FIND_FRAMEWORK NEVER CACHE STRING "" FORCE)
        set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY CACHE STRING "" FORCE)
    endif()
endfunction()

# Check if freetype is available: ON by default, except on Android and MinGW
# On MacOS, if building a distributable wheel with cibuilwheel for a version less than 14.0, we disable freetype
function(ibd_check_freetype_availability result_var)
    # freetype is available by default
    set(${result_var} ON PARENT_SCOPE)

    # Except on Android and MinGW
    # Freetype is not available on Android. The mix SDL + Freetype cause issues (cannot find SDL.h)
    # Freetype currently fails to build on MinGW
    if(ANDROID OR MINGW)
        set(${result_var} OFF PARENT_SCOPE)
        return()
    endif()

    # On MacOS, if building a distributable wheel with cibuilwheel for a version less than 14.0, we disable freetype
    # (we are using dynamic libraries provided by homebrew, and they require a minimum version of MacOS)
    # Those libraries are zlib, libpng, harfbuzz, brotli, ...
    if(DEFINED ENV{CIBUILDWHEEL} AND APPLE)
        if (NOT DEFINED ENV{MACOSX_DEPLOYMENT_TARGET})
            message(FATAL_ERROR "MACOSX_DEPLOYMENT_TARGET is not set!")
            return()
        endif()

        if("$ENV{MACOSX_DEPLOYMENT_TARGET}" VERSION_LESS "14.0")
            message(STATUS "MACOSX_DEPLOYMENT_TARGET is less than 14.0, freetype will be disabled")
            set(${result_var} OFF PARENT_SCOPE)
        else()
            set(${result_var} ON PARENT_SCOPE)
        endif()
        return()
    endif()
endfunction()

function(ibd_add_sanitizer_options)
    # Also see scan-build (clang static analyzer). No bugs reported on 2023-10-21
    #     brew install llvm
    #     mkdir build_llvm && cd llvm
    #     export PATH=/opt/homebrew/opt/llvm/bin:$PATH
    #     cmake .. -DIMMVISION_FETCH_OPENCV=ON
    #     scan-build make -j$
    option(IMGUI_BUNDLE_BUILD_WITH_ASAN "Build ImGui Bundle with address sanitizer" OFF)
    if(IMGUI_BUNDLE_BUILD_WITH_ASAN)
        add_compile_options(-fsanitize=address -fsanitize-address-use-after-scope)
        add_link_options(-fsanitize=address -fsanitize-address-use-after-scope)
    endif()
    option(IMGUI_BUNDLE_BUILD_WITH_TSAN "Build ImGui Bundle with thread sanitizer" OFF)
    if(IMGUI_BUNDLE_BUILD_WITH_TSAN)
        add_compile_options(-fsanitize=thread)
        add_link_options(-fsanitize=thread)
    endif()
    option(IMGUI_BUNDLE_BUILD_WITH_MEMORY_SANITIZER "Build ImGui Bundle with memory sanitizer" OFF)
    if(IMGUI_BUNDLE_BUILD_WITH_MEMORY_SANITIZER)
        add_compile_options(-fsanitize=memory)
        add_link_options(-fsanitize=memory)
    endif()
    option(IMGUI_BUNDLE_BUILD_WITH_UB_SANITIZER "Build ImGui Bundle with undefined behavior sanitizer" OFF)
    if(IMGUI_BUNDLE_BUILD_WITH_UB_SANITIZER)
        add_compile_options(-fsanitize=undefined)
        add_link_options(-fsanitize=undefined)
    endif()
endfunction()

function(ibd_shout_on_deprecated_options)
    if (DEFINED IMGUI_BUNDLE_WITH_GLFW)
        message(FATAL_ERROR "IMGUI_BUNDLE_WITH_GLFW is deprecated. Please use HELLOIMGUI_USE_GLFW3 + HELLOIMGUI_HAS_OPENGL3 instead")
    endif()
    if (DEFINED IMGUI_BUNDLE_WITH_SDL)
        message(FATAL_ERROR "IMGUI_BUNDLE_WITH_SDL is deprecated. Please use HELLOIMGUI_USE_SDL2 + HELLOIMGUI_HAS_OPENGL3 instead")
    endif()
endfunction()

# if building the python package, do some cleanup:
#   remove .ruff_cache, remove bindings/imgui_bundle/*.so *.dylib *.dll *.pyd
# -----------------------------------------------------------------------------
function(ibd_clean_bindings_imgui_bundle_before_pip_build)
    if(SKBUILD)
        message(STATUS "Cleaning bindings/imgui_bundle before pip build")
        # Remove all .ruff_cache folders below bindings/imgui_bundle
        set(bundle_folder ${IMGUI_BUNDLE_PATH}/bindings/imgui_bundle)
        set(ruff_cache_folders
            ${bundle_folder}/.ruff_cache
            ${bundle_folder}/demos_python/.ruff_cache
        )
        foreach(ruff_cache_folder ${ruff_cache_folders})
            file(REMOVE_RECURSE ${ruff_cache_folder})
        endforeach ()

        # Remove all .so, .dylib, .dll, .pyd files below bindings/imgui_bundle
        file(GLOB_RECURSE bundle_files
            ${bundle_folder}/*.so
            ${bundle_folder}/*.dylib
            ${bundle_folder}/*.dll
            ${bundle_folder}/*.pyd
        )
        foreach(bundle_file ${bundle_files})
            file(REMOVE ${bundle_file})
        endforeach ()
    endif()
endfunction()

function(ibd_clone_submodules_if_needed)
    if(NOT EXISTS ${IMGUI_BUNDLE_PATH}/external/imgui/imgui/imgui.h)
        if(NOT IMGUI_BUNDLE_AUTO_CLONE_SUBMODULES)
            message(FATAL_ERROR "Please run
            git submodule update --init
           ")
        else()
            execute_process(
                COMMAND git submodule update --init
                WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
            )
            execute_process(
                COMMAND git submodule update --init
                # needed since ImGuiColorTextEdit  added a dependency to boost/regex.hpp
                WORKING_DIRECTORY ${IMGUI_BUNDLE_PATH}/external/ImGuiColorTextEdit/ImGuiColorTextEdit
            )
        endif()
    endif()
endfunction()

function(ibd_add_emscripten_otions)
    add_compile_definitions(EMSCRIPTEN)
    # enable assertions in emscripten (IM_ASSERT will log and terminate on error)
    add_link_options(-sASSERTIONS)

    # If  building emscripten and building demos, we need to activate multithreading support (for ImGuiTestEngine)
    if (IMGUI_BUNDLE_BUILD_DEMOS)
        set(HELLOIMGUI_EMSCRIPTEN_PTHREAD ON CACHE BOOL "" FORCE)
        set(HELLOIMGUI_EMSCRIPTEN_PTHREAD_ALLOW_MEMORY_GROWTH ON CACHE BOOL "" FORCE)
        add_link_options(-Wno-pthreads-mem-growth)
    endif()
    if (HELLOIMGUI_EMSCRIPTEN_PTHREAD)
        add_compile_options(-pthread)
        add_link_options(-pthread)
        set(IMMVISION_OPENCV_EMSCRIPTEN_WITH_PTHREAD ON CACHE BOOL "" FORCE)
    endif()

    # Exceptions handlings: by default in emscripten, exception do not work!
    # Our program should not use them, but during development, it is possible to activate them temporarily)
    #add_compile_options(-sNO_DISABLE_EXCEPTION_CATCHING)
    #add_link_options(-sNO_DISABLE_EXCEPTION_CATCHING)
    # This would enable exception to be handled by wasm (and thus may be faster)
    #add_compile_options(-fwasm-exceptions)
    #add_link_options(-fwasm-exceptions)
endfunction()