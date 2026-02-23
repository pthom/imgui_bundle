# imgui_manual: interactive manual for ImGui, ImPlot, ImPlot3D, ImAnim
#
# Included from ./CMakeLists.txt, which calls iman_main().
#
# Structure (top to bottom):
#   _iman_copy / _iman_copy_as        low-level file-copy helpers
#   iman_setup_demo_code_dir          populate binary demo_code/ at configure time
#   iman_add_imgui_manual_lib         build imgui_manual_lib static library
#   iman_link_imgui_bundle_to_manual  plug into imgui_bundle INTERFACE
#   iman_add_imgui_manual_app         build standalone exe (optional)
#   iman_main                         entry point


# ---------------------------------------------------------------------------
# Low-level copy helpers (private)
# ---------------------------------------------------------------------------

# Copy src → dest/<original-filename>  (keeps the name)
function(_iman_copy src dest)
    get_filename_component(filename ${src} NAME)
    configure_file(${src} ${dest}/${filename} COPYONLY)
endfunction()

# Copy src → dest/<name>  (renames on arrival)
function(_iman_copy_as src name dest)
    configure_file(${src} ${dest}/${name} COPYONLY)
endfunction()


# ---------------------------------------------------------------------------
# Demo code folder
#
# Files are copied to ${CMAKE_BINARY_DIR}/bin/demo_code/ at CMake configure
# time with their natural extensions (.cpp / .py / .h / .pyi).
# They are never placed in assets/ so they are never preloaded/bundled.
#
# Desktop  : read lazily via std::ifstream(IMAN_DEMO_CODE_DIR + "/" + filename)
# Emscripten: served alongside the app, fetched lazily via emscripten_async_wget()
# ---------------------------------------------------------------------------
function(iman_setup_demo_code_dir)
    set(b    ${IMGUI_BUNDLE_PATH})
    set(dest ${CMAKE_BINARY_DIR}/bin/demo_code)
    file(MAKE_DIRECTORY ${dest})

    # C++ demo files
    _iman_copy(${b}/external/ImAnim/ImAnim/im_anim_demo_basics.cpp    ${dest})
    if(IMGUI_BUNDLE_WITH_IMANIM_FULL_DEMOS)
        _iman_copy(${b}/external/ImAnim/ImAnim/im_anim_demo.cpp           ${dest})
        _iman_copy(${b}/external/ImAnim/ImAnim/im_anim_doc.cpp            ${dest})
        _iman_copy(${b}/external/ImAnim/ImAnim/im_anim_usecase.cpp        ${dest})
    endif()
    _iman_copy(${b}/external/imgui/imgui/imgui_demo.cpp               ${dest})
    _iman_copy(${b}/external/implot/implot/implot_demo.cpp            ${dest})
    _iman_copy(${b}/external/implot3d/implot3d/implot3d_demo.cpp      ${dest})

    # Python demo files
    set(pydemos ${b}/bindings/imgui_bundle/demos_python/demos_imgui_manual)
    _iman_copy(${pydemos}/im_anim_demo_basics.py ${dest})
    _iman_copy(${pydemos}/imgui_demo.py          ${dest})
    _iman_copy(${pydemos}/implot_demo.py         ${dest})
    _iman_copy(${pydemos}/implot3d_demo.py       ${dest})

    # C++ API headers
    _iman_copy(${b}/external/imgui/imgui/imgui.h                      ${dest})
    _iman_copy(${b}/external/imgui/imgui/imgui_internal.h             ${dest})
    _iman_copy(${b}/external/implot/implot/implot.h                   ${dest})
    _iman_copy(${b}/external/implot/implot/implot_internal.h          ${dest})
    _iman_copy(${b}/external/implot3d/implot3d/implot3d.h             ${dest})
    _iman_copy(${b}/external/implot3d/implot3d/implot3d_internal.h    ${dest})
    _iman_copy(${b}/external/ImAnim/ImAnim/im_anim.h                  ${dest})

    # Python stubs (renamed: subdir/__init__.pyi → flat name)
    set(stubs ${b}/bindings/imgui_bundle)
    _iman_copy_as(${stubs}/imgui/__init__.pyi     imgui.pyi             ${dest})
    _iman_copy_as(${stubs}/imgui/internal.pyi     imgui_internal.pyi    ${dest})
    _iman_copy_as(${stubs}/implot/__init__.pyi    implot.pyi            ${dest})
    _iman_copy_as(${stubs}/implot/internal.pyi    implot_internal.pyi   ${dest})
    _iman_copy_as(${stubs}/implot3d/__init__.pyi  implot3d.pyi          ${dest})
    _iman_copy_as(${stubs}/implot3d/internal.pyi  implot3d_internal.pyi ${dest})
    _iman_copy_as(${stubs}/im_anim.pyi            im_anim.pyi           ${dest})
endfunction()



# ---------------------------------------------------------------------------
# imgui_manual_lib: the library exposing ShowImGuiManualGui()
# ---------------------------------------------------------------------------
function(iman_add_imgui_manual_lib)
    set(src ${CMAKE_CURRENT_FUNCTION_LIST_DIR})
    add_library(imgui_manual_lib STATIC
        ${src}/src/imgui_manual.cpp
        ${src}/src/library_config.cpp
        ${src}/src/library_config.h
        ${src}/src/demo_code_viewer.cpp
        ${src}/src/demo_code_viewer.h
        ${src}/imgui_manual.h
    )
    target_link_libraries(imgui_manual_lib PUBLIC
        imgui implot implot3d hello_imgui immapp imgui_color_text_edit imgui_md)
    if(IMGUI_BUNDLE_WITH_IMANIM)
        target_link_libraries(imgui_manual_lib PUBLIC imanim)
        if(IMGUI_BUNDLE_WITH_IMANIM_FULL_DEMOS)
            target_compile_definitions(imgui_manual_lib PRIVATE IMGUI_BUNDLE_WITH_IMANIM_FULL_DEMOS)
        endif()
    endif()

    target_include_directories(imgui_manual_lib
        PUBLIC  $<BUILD_INTERFACE:${src}>        # for imgui_manual.h
        PRIVATE $<BUILD_INTERFACE:${src}/src>    # for internal headers
    )
    # Desktop: demo code is read via std::ifstream from the binary-dir demo_code/ folder.
    # IMAN_DEMO_CODE_DIR is baked in at compile time (Emscripten uses a relative URL instead).
    if(NOT EMSCRIPTEN)
        target_compile_definitions(imgui_manual_lib PRIVATE
            IMAN_DEMO_CODE_DIR="${CMAKE_BINARY_DIR}/bin/demo_code"
        )
    endif()
endfunction()


# ---------------------------------------------------------------------------
# Bundle integration: plug into imgui_bundle INTERFACE and install machinery
# ---------------------------------------------------------------------------
function(iman_link_imgui_bundle_to_manual)
    target_link_libraries(imgui_bundle INTERFACE imgui_manual_lib)
    target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_IMGUI_MANUAL_LIB)
    if(COMMAND ibd_add_installable_dependency AND IMGUI_BUNDLE_INSTALL_CPP)
        install(FILES ${CMAKE_CURRENT_FUNCTION_LIST_DIR}/imgui_manual.h DESTINATION include/imgui_manual)
        ibd_add_installable_dependency(imgui_manual_lib)
    endif()
endfunction()


# ---------------------------------------------------------------------------
# Standalone exe (optional)
# ---------------------------------------------------------------------------
function(iman_add_imgui_manual_app)
    imgui_bundle_add_app(imgui_manual ${CMAKE_CURRENT_FUNCTION_LIST_DIR}/imgui_manual.main.cpp)
    set_target_properties(imgui_manual PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
    if(EMSCRIPTEN)
        set_target_properties(imgui_manual PROPERTIES OUTPUT_NAME index)
    endif()
endfunction()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
function(iman_main)
    # If the app is requested, the lib is required
    if(IMGUI_BUNDLE_BUILD_IMGUI_MANUAL_APP)
        set(IMGUI_BUNDLE_WITH_IMGUI_MANUAL_LIB ON CACHE BOOL "" FORCE)
    endif()
    # Bail out if any required dependency is missing
    if(NOT IMGUI_BUNDLE_WITH_IMMAPP OR NOT IMGUI_BUNDLE_WITH_IMPLOT OR NOT IMGUI_BUNDLE_WITH_IMPLOT3D)
        message(WARNING "Not building imgui_manual_lib (missing dependencies: imanim, immapp, implot, implot3d)")
        set(IMGUI_BUNDLE_WITH_IMGUI_MANUAL_LIB OFF CACHE INTERNAL "" FORCE)
        return()
    endif()
    if(NOT IMGUI_BUNDLE_WITH_IMGUI_MANUAL_LIB)
        return()
    endif()

    iman_add_imgui_manual_lib()
    iman_link_imgui_bundle_to_manual()
    iman_setup_demo_code_dir()   # populate bin/demo_code/ from source files

    if(IMGUI_BUNDLE_BUILD_IMGUI_MANUAL_APP)
        iman_add_imgui_manual_app()
    endif()

    # Note: lazy loading for Python bundle demos is a separate effort.
    # When implemented, it should also use the binary-dir demo_code/ approach.
endfunction()
