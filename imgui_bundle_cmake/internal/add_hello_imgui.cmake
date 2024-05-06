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

    # 2. Specific options for python bindings:
    #    i.   Use Glfw + OpenGL3 backend
    #    ii.  enable null backend
    #    iii. Build our own glfw as a shared library (see cmake/add_glfw.cmake)
    #         (the reason is that we need to deploy this library with the python bindings)
    if (IMGUI_BUNDLE_BUILD_PYTHON)
        #    i.   Use Opengl3 + glfw backend
        set(HELLOIMGUI_USE_GLFW3 ON CACHE BOOL "" FORCE)
        set(HELLOIMGUI_HAS_OPENGL3 ON CACHE BOOL "" FORCE)
        add_glfw_as_python_shared_library()
    endif()

    # 3. Configure hello-imgui with the following options:
    #     i. use our own imgui submodule
    set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/imgui/imgui)
    set(HELLOIMGUI_BUILD_IMGUI OFF CACHE BOOL "" FORCE)
    set(HELLOIMGUI_IMGUI_SOURCE_DIR ${imgui_dir} CACHE STRING "" FORCE)

    # 4. Finally, add hello_imgui
    if(IMGUI_BUNDLE_INSTALL_CPP)
        set(HELLOIMGUI_INSTALL ON CACHE BOOL "" FORCE)
    endif()
    add_subdirectory(hello_imgui/hello_imgui)
    target_link_libraries(imgui_bundle INTERFACE hello_imgui)
    if(IMGUI_BUNDLE_INSTALL_CPP)
        ibd_add_installable_dependency(hello_imgui)
    endif()

    # 5. Export hello_imgui symbols on Windows without using __declspec(dllexport)
    if (WIN32)
        set_target_properties(hello_imgui PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
    endif()
endfunction()
