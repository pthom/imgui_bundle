# imgui_manual: interactive manual for ImGui, ImPlot, ImPlot3D, ImAnim

# This file is structured
# - functions first: private start with underscore, grouped by theme (asset copying, force-include)
# - public functions use the prefix iman_
# - then iman_main
# This file is intended to be included from ./CMakeLists.txt, which will call iman_main()

# ---------------------------------------------------------------------------
# Asset copying (copy demo code files to the assets folder so that the demo code viewer can load them at runtime).
# ---------------------------------------------------------------------------
function(_copy_code_file code_file_full_path demo_code_dest)
    get_filename_component(code_file ${code_file_full_path} NAME)
    set(destination ${demo_code_dest}/${code_file}.txt)
    configure_file(${code_file_full_path} ${destination} COPYONLY)
endfunction()

function(_copy_code_file_renamed code_file_full_path new_name demo_code_dest)
    set(destination ${demo_code_dest}/${new_name}.txt)
    configure_file(${code_file_full_path} ${destination} COPYONLY)
endfunction()

function(iman_copy_demo_code_assets demo_code_dest)
    set(bundle_dir ${IMGUI_BUNDLE_PATH})
    set(imanim_dir ${bundle_dir}/external/ImAnim/ImAnim)
    set(imgui_dir  ${bundle_dir}/external/imgui/imgui)
    set(implot_dir ${bundle_dir}/external/implot/implot)
    set(implot3d_dir ${bundle_dir}/external/implot3d/implot3d)
    set(demos_python_dir ${bundle_dir}/bindings/imgui_bundle/demos_python/demos_imgui_manual)

    file(MAKE_DIRECTORY ${demo_code_dest})

    # C++ demos
    _copy_code_file(${imanim_dir}/im_anim_demo_basics.cpp ${demo_code_dest})
    _copy_code_file(${imanim_dir}/im_anim_demo.cpp ${demo_code_dest})
    _copy_code_file(${imanim_dir}/im_anim_doc.cpp ${demo_code_dest})
    _copy_code_file(${imanim_dir}/im_anim_usecase.cpp ${demo_code_dest})
    _copy_code_file(${imgui_dir}/imgui_demo.cpp ${demo_code_dest})
    _copy_code_file(${implot_dir}/implot_demo.cpp ${demo_code_dest})
    _copy_code_file(${implot3d_dir}/implot3d_demo.cpp ${demo_code_dest})
    # Python demos
    _copy_code_file(${demos_python_dir}/im_anim_demo_basics.py ${demo_code_dest})
    _copy_code_file(${demos_python_dir}/imgui_demo.py ${demo_code_dest})
    _copy_code_file(${demos_python_dir}/implot_demo.py ${demo_code_dest})
    _copy_code_file(${demos_python_dir}/implot3d_demo.py ${demo_code_dest})

    # API reference: C++ headers
    _copy_code_file(${imgui_dir}/imgui.h ${demo_code_dest})
    _copy_code_file(${imgui_dir}/imgui_internal.h ${demo_code_dest})
    _copy_code_file(${implot_dir}/implot.h ${demo_code_dest})
    _copy_code_file(${implot_dir}/implot_internal.h ${demo_code_dest})
    _copy_code_file(${implot3d_dir}/implot3d.h ${demo_code_dest})
    _copy_code_file(${implot3d_dir}/implot3d_internal.h ${demo_code_dest})
    _copy_code_file(${imanim_dir}/im_anim.h ${demo_code_dest})
    # API reference: Python stubs
    set(stubs_dir ${bundle_dir}/bindings/imgui_bundle)
    _copy_code_file_renamed(${stubs_dir}/imgui/__init__.pyi    imgui.pyi             ${demo_code_dest})
    _copy_code_file_renamed(${stubs_dir}/imgui/internal.pyi    imgui_internal.pyi    ${demo_code_dest})
    _copy_code_file_renamed(${stubs_dir}/implot/__init__.pyi   implot.pyi            ${demo_code_dest})
    _copy_code_file_renamed(${stubs_dir}/implot/internal.pyi   implot_internal.pyi   ${demo_code_dest})
    _copy_code_file_renamed(${stubs_dir}/implot3d/__init__.pyi implot3d.pyi          ${demo_code_dest})
    _copy_code_file_renamed(${stubs_dir}/implot3d/internal.pyi implot3d_internal.pyi ${demo_code_dest})
    _copy_code_file_renamed(${stubs_dir}/im_anim.pyi           im_anim.pyi           ${demo_code_dest})
endfunction()



# ---------------------------------------------------------------------------
# Force-include imgui_demo_marker_hooks.h into imgui/implot/implot3d/imanim
# so that IMGUI_DEMO_MARKER hooks into the code viewer at runtime.
# Uses -include<path> (no space) so flag+path are a single atom.
# ---------------------------------------------------------------------------
function(_force_include target header)
    if(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
        target_compile_options(${target} PRIVATE /FI${header})
    else()
        target_compile_options(${target} PRIVATE -include${header})
    endif()
endfunction()

function(iman_force_include_marker_hooks)
    set(marker_hooks_header ${CMAKE_CURRENT_FUNCTION_LIST_DIR}/src/imgui_demo_marker_hooks.h)
    set(marker_hooks_impl   ${CMAKE_CURRENT_FUNCTION_LIST_DIR}/src/imgui_demo_marker_hooks.cpp)
    foreach(lib imgui implot implot3d imanim)
        if(TARGET ${lib})
            _force_include(${lib} ${marker_hooks_header})
        endif()
    endforeach()
    # Compile the hooks implementation into imgui itself, so that libimgui.a
    # contains both the IMGUI_DEMO_MARKER call sites AND their definition.
    # This avoids a GNU ld link-order problem: if the definition lived in a
    # separate library (imgui_manual_lib) that CMake orders before libimgui.a,
    # the single-pass linker would never extract it (no pending undefined ref yet).
    if(TARGET imgui)
        target_sources(imgui PRIVATE ${marker_hooks_impl})
    endif()
endfunction()


# ---------------------------------------------------------------------------
# imgui_manual_lib: the library exposing ShowImGuiManualGui()
# ---------------------------------------------------------------------------
function(iman_add_imgui_manual_lib)
    # Note:
    # - the marker hooks implementation (${src}/src/imgui_demo_marker_hooks.cpp)
    #   is compiled into imgui itself (see iman_force_include_marker_hooks)
    #   This solves link issues.
    #
    set(src ${CMAKE_CURRENT_FUNCTION_LIST_DIR})
    add_library(imgui_manual_lib STATIC
        ${src}/src/imgui_manual.cpp
        ${src}/src/library_config.cpp
        ${src}/src/library_config.h
        ${src}/src/demo_code_viewer.cpp
        ${src}/src/demo_code_viewer.h
        ${src}/src/imgui_demo_marker_hooks.h
        ${src}/imgui_manual.h
    )
    target_link_libraries(imgui_manual_lib PUBLIC
        imgui implot implot3d imanim hello_imgui immapp imgui_color_text_edit imgui_md)
    target_include_directories(imgui_manual_lib
        PUBLIC  $<BUILD_INTERFACE:${src}>        # for imgui_manual.h
        PRIVATE $<BUILD_INTERFACE:${src}/src>    # for internal headers
    )
endfunction()


# Bundle integration: plug into imgui_bundle INTERFACE and install machinery
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
    # target_link_libraries(imgui_manual PRIVATE imgui_manual_lib)
    set_target_properties(imgui_manual PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
    if(EMSCRIPTEN)
        set_target_properties(imgui_manual PROPERTIES OUTPUT_NAME index)
    endif()
endfunction()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
function(iman_main)
    #
    # Sanity checks and early exits
    # =============================
    # # If the app is requested, the lib is required
    if(IMGUI_BUNDLE_BUILD_IMGUI_MANUAL_APP)
        set(IMGUI_BUNDLE_WITH_IMGUI_MANUAL_LIB ON CACHE BOOL "" FORCE)
    endif()
    # If the lib is requested, warn if any of the dependencies are missing and disable the lib
    if(NOT IMGUI_BUNDLE_WITH_IMMAPP OR NOT IMGUI_BUNDLE_WITH_IMANIM OR NOT IMGUI_BUNDLE_WITH_IMPLOT OR NOT IMGUI_BUNDLE_WITH_IMPLOT3D)
        message(WARNING "Not building imgui_manual_lib (missing dependencies: imanim, immapp, implot, implot3d)")
        set(IMGUI_BUNDLE_WITH_IMGUI_MANUAL_LIB OFF CACHE INTERNAL "" FORCE)
        return()
    endif()
    # If the lib is not requested, skip everything
    if(NOT IMGUI_BUNDLE_WITH_IMGUI_MANUAL_LIB)
        return()
    endif()

    # Build the library
    iman_add_imgui_manual_lib()
    # Force-include the marker hooks into imgui/implot/implot3d/imanim
    iman_force_include_marker_hooks()
    # Link the library to imgui_bundle INTERFACE and install machinery
    iman_link_imgui_bundle_to_manual()

    # Build the standalone app (optional)
    if(IMGUI_BUNDLE_BUILD_IMGUI_MANUAL_APP)
        iman_add_imgui_manual_app()
        # Refresh demo code assets from live bundle sources
        iman_copy_demo_code_assets(${CMAKE_CURRENT_FUNCTION_LIST_DIR}/assets/demo_code)
    endif()

    # Add demo_code assets to python
    if (IMGUI_BUNDLE_BUILD_PYTHON)
        iman_copy_demo_code_assets(${IMGUI_BUNDLE_PATH}/bindings/imgui_bundle/demos_assets/demo_code)
    endif()
endfunction()
