set(_THIS_MODULE_DIR ${CMAKE_CURRENT_LIST_DIR})


function(lg_disable_warning_exception_in_destructor target)
    # Disable warning due to IM_ASSERT implementation which uses exceptions (see lg_imgui_imconfig.h)
    #  and raises warnings in destructors like this:
    #       warning: '~ImGuiWindow' has a non-throwing exception specification but can still throw [-Wexceptions]
    if ("${CMAKE_CXX_COMPILER_ID}" MATCHES "Clang")
        target_compile_options(${target} PRIVATE -Wno-exceptions)
    elseif (CMAKE_COMPILER_IS_GNUCC)
        target_compile_options(${target} PRIVATE -Wno-terminate)
    elseif(MSVC)
        target_compile_options(${target} PRIVATE "/wd4297")
    endif()
endfunction()



# This will create an imgui target with the correct install, include and link options
function(add_imgui imgui_dir)
    if(NOT TARGET imgui)
        file(GLOB imgui_sources ${imgui_dir}/*.h ${imgui_dir}/*.cpp ${imgui_dir}/misc/cpp/*.cpp ${imgui_dir}/misc/cpp/*.h)
        add_library(imgui STATIC ${imgui_sources})
        if (IMGUI_BUNDLE_BUILD_PYTHON)
            # For python bindings we add opengl2 backend
            target_sources(imgui PRIVATE ${imgui_dir}/backends/imgui_impl_opengl2.cpp ${imgui_dir}/backends/imgui_impl_opengl2.h)
        endif()
        set(HELLOIMGUI_IMGUI_SOURCE_DIR ${imgui_dir})
        target_include_directories(imgui PUBLIC
            $<BUILD_INTERFACE:${HELLOIMGUI_IMGUI_SOURCE_DIR}>
            $<BUILD_INTERFACE:${HELLOIMGUI_IMGUI_SOURCE_DIR}/backends>
            $<BUILD_INTERFACE:${HELLOIMGUI_IMGUI_SOURCE_DIR}/misc/cpp>
            $<BUILD_INTERFACE:${HELLOIMGUI_IMGUI_SOURCE_DIR}/misc/freetype>
        )
        target_compile_definitions(imgui PUBLIC IMGUI_USER_CONFIG="${IMGUI_BUNDLE_CMAKE_PATH}/imgui_bundle_config.h")
        lg_disable_warning_exception_in_destructor(imgui)
        if(PROJECT_IS_TOP_LEVEL AND NOT SKBUILD)
            install(TARGETS imgui DESTINATION ./lib/)
        endif()

        if(IMGUI_BUNDLE_BUILD_PYTHON)
            target_compile_definitions(imgui PUBLIC ImTextureID=int)
        endif()

        if (UNIX)
            target_compile_options(imgui PUBLIC -fPIC)
        endif()
        hello_imgui_msvc_target_group_sources(imgui)

        if(IMGUI_BUNDLE_INSTALL_CPP)
            ibd_add_installable_dependency(imgui)
        endif()
    endif()
endfunction()
