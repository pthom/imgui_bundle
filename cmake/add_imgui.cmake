
set(_THIS_MODULE_BASE_DIR "${CMAKE_CURRENT_LIST_DIR}")

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
        target_include_directories(imgui PUBLIC ${imgui_dir})
        target_compile_definitions(imgui PRIVATE IMGUI_USER_CONFIG="${_THIS_MODULE_BASE_DIR}/lg_imgui_imconfig.h")
        lg_disable_warning_exception_in_destructor(imgui)
        install(TARGETS imgui DESTINATION ./lib/)

        if (UNIX)
            target_compile_options(imgui PUBLIC -fPIC)
        endif()
    endif()
endfunction()
