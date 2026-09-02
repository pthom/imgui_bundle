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
    #    ii. Build our own glfw as a shared library (see cmake/add_glfw.cmake)
    #         The reason is that we need to deploy this library with the python bindings,
    #         except for conda, which can deploy it as a conda package (see condition IMGUI_BUNDLE_PYTHON_USE_SYSTEM_LIBS)
    if (IMGUI_BUNDLE_BUILD_PYTHON AND NOT IMGUI_BUNDLE_BUILD_PYODIDE)
        #    i.   Use Opengl3 + glfw backend
        set(HELLOIMGUI_USE_GLFW3 ON CACHE BOOL "" FORCE)
        set(HELLOIMGUI_HAS_OPENGL3 ON CACHE BOOL "" FORCE)
        #    ii.  build glfw
        if (NOT IMGUI_BUNDLE_PYTHON_USE_SYSTEM_LIBS)
            add_glfw_as_python_shared_library()
        endif()
    endif()

    # 3. Configure hello-imgui with the following options:
    #     i. use our own imgui submodule
    set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/imgui/imgui)
    set(HELLOIMGUI_BUILD_IMGUI OFF CACHE BOOL "" FORCE)
    set(HELLOIMGUI_IMGUI_SOURCE_DIR ${imgui_dir} CACHE STRING "" FORCE)

    # 4. Finally, add hello_imgui
    if(IMGUI_BUNDLE_INSTALL_CPP)
        # hello_imgui is installed as part of the imgui_bundle package:
        # its targets join the imgui_bundle export set (namespace imgui_bundle::),
        # and hello_imgui_cmake/ + hello_imgui_assets/ land next to imgui_bundle-config.cmake
        set(HELLOIMGUI_INSTALL ON CACHE BOOL "" FORCE)
        set(HELLOIMGUI_INSTALL_EXPORT "imgui_bundle-targets" CACHE STRING "" FORCE)
        set(HELLOIMGUI_INSTALL_CMAKE_DIR "lib/cmake/imgui_bundle" CACHE STRING "" FORCE)
    endif()
    add_subdirectory(hello_imgui/hello_imgui)
    target_link_libraries(imgui_bundle INTERFACE hello_imgui)
    # (no ibd_add_installable_dependency(hello_imgui): hello_imgui installs itself
    #  and its dependencies into the imgui_bundle export set, see above)

    # 5. Export hello_imgui symbols on Windows without using __declspec(dllexport)
    if (WIN32)
        set_target_properties(hello_imgui PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
    endif()
endfunction()
