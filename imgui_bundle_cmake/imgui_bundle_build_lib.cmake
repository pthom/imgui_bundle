set(IMGUI_BUNDLE_CMAKE_PATH ${CMAKE_CURRENT_LIST_DIR} CACHE STRING "" FORCE)



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
    if(IMGUI_BUNDLE_BUILD_PYTHON AND HELLOIMGUI_USE_FREETYPE)
        # if using vcpkg, we suppose it uses the static version of freetype
        if(NOT "$ENV{CMAKE_TOOLCHAIN_FILE}" MATCHES "vcpkg")
            set(HELLOIMGUI_FREETYPE_STATIC ON CACHE BOOL "" FORCE)
        endif()
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
            message(STATUS "MACOSX_DEPLOYMENT_TARGET is less than 14.0, freetype willbe disabled")
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