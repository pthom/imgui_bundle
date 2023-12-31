include(${CMAKE_CURRENT_LIST_DIR}/add_imgui.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/add_glfw_submodule.cmake)

####################################################
# Build hello_imgui Bound C++ library
####################################################
function (add_hello_imgui)
    if (UNIX)
        add_compile_options(-fPIC)
    endif()
    #   i. Build static libraries
    set(BUILD_SHARED_LIBS OFF)
    # 1. Build imgui (lib used by hello_imgui)
    set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/imgui/imgui)
    add_imgui(${imgui_dir})

    if (APPLE)
        enable_language(OBJC) # See https://gitlab.kitware.com/cmake/cmake/-/issues/24104
    endif()

    # 2. Use glfw submodule for python bindings
    # When building python bindings, glfw is always built as a shared library (see cmake/add_glfw.cmake)
    if (IMGUI_BUNDLE_BUILD_PYTHON)
        add_glfw_submodule()
    endif()

    # 3. Configure hello-imgui with the following options:
    #     i. use our own imgui submodule
    set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/imgui/imgui)
    set(HELLOIMGUI_BUILD_IMGUI OFF CACHE BOOL "" FORCE)
    set(HELLOIMGUI_IMGUI_SOURCE_DIR ${imgui_dir} CACHE STRING "" FORCE)

    # 4. Finally, add hello_imgui
    add_subdirectory(hello_imgui/hello_imgui)
    target_link_libraries(imgui_bundle PUBLIC hello_imgui)

    # 5. Export hello_imgui symbols on Windows without using __declspec(dllexport)
    if (WIN32)
        set_target_properties(hello_imgui PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
    endif()
endfunction()
