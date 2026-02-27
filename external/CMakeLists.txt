include(../imgui_bundle_cmake/imgui_bundle_build_lib.cmake)
include(../imgui_bundle_cmake/internal/add_simple_library.cmake) # Tooling to build libraries and link them to imgui_bundle

function(_target_force_include target include_file)
    if (MSVC)
        target_compile_options(${target} PRIVATE /FI${include_file})
    else()
        target_compile_options(${target} PRIVATE -include ${include_file})
    endif()
endfunction()


# Add fplus
add_library(fplus INTERFACE)
target_include_directories(fplus INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/fplus>)
if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    target_compile_options(fplus INTERFACE -Wno-psabi)  # "note: parameter passing for argument of type ‘std::pair<double, double>’ when C++17 is enabled changed to match C++14 in GCC 10.1"
endif()
if(IMGUI_BUNDLE_INSTALL_CPP)
    install(DIRECTORY fplus/fplus DESTINATION include)
    ibd_add_installable_dependency(fplus)
endif()


###############################################################################
# Build ImGui & Hello ImGui
###############################################################################
# Build imgui + hello_imgui (or imgui standalone if hello_imgui is disabled)
if(IMGUI_BUNDLE_WITH_HELLO_IMGUI)
    # Standard path: build hello_imgui (which includes imgui)
    include(../imgui_bundle_cmake/internal/add_hello_imgui.cmake)
    add_hello_imgui()
    if (IMGUI_BUNDLE_BUILD_PYTHON)
        target_compile_definitions(imgui PUBLIC IMGUI_BUNDLE_BUILD_PYTHON)
    endif()
    set(IMGUI_BUNDLE_WITH_HELLO_IMGUI ON CACHE INTERNAL "" FORCE)
    target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_HELLO_IMGUI)
else()
    # Library-only mode: build imgui standalone without hello_imgui
    message(STATUS "═══════════════════════════════════════════════════════════")
    message(STATUS "Building imgui_bundle in LIBRARY-ONLY mode")
    message(STATUS "  - No window management (no hello_imgui)")
    message(STATUS "  - No high-level app framework (no immapp)")
    message(STATUS "  - Core ImGui + widget libraries only")
    message(STATUS "═══════════════════════════════════════════════════════════")

    # Build imgui standalone using the bundle's modified version
    # (external/imgui/imgui contains Python binding modifications)
    include(../imgui_bundle_cmake/internal/add_imgui.cmake)
    add_imgui(${CMAKE_CURRENT_LIST_DIR}/imgui/imgui)

    if (IMGUI_BUNDLE_BUILD_PYTHON)
        target_compile_definitions(imgui PUBLIC IMGUI_BUNDLE_BUILD_PYTHON)
    endif()

    # Link imgui to imgui_bundle so that bindings can find it
    target_link_libraries(imgui_bundle INTERFACE imgui)
endif()

# Add imgui_pywrappers
if (IMGUI_BUNDLE_BUILD_PYTHON)
    add_simple_external_library(imgui_pywrappers imgui/imgui_pywrappers)
    target_sources(imgui_pywrappers PRIVATE
        imgui/imgui_pywrappers/imgui_pywrappers.cpp imgui/imgui_pywrappers/imgui_pywrappers.h
        imgui/imgui_pywrappers/imgui_internal_pywrappers.cpp imgui/imgui_pywrappers/imgui_internal_pywrappers.h
        )
endif()


# =============================================================================
# Dependency Chain Resolution — Phase 2
# =============================================================================
# HelloImGui is now configured; HELLOIMGUI_HAS_OPENGL3 / HELLOIMGUI_HAS_METAL
# reflect actual platform support. Resolve rendering-backend dependencies.
# =============================================================================
imgui_bundle_resolve_rendering_backend_dependencies()

###############################################################################
# "Big" libraries, which can be disabled individually, for C++
#     see options IMGUI_BUNDLE_WITH_XXX.
#     (those options will fail for python bindings)
###############################################################################
# Build immvision
if(HELLOIMGUI_HAS_OPENGL AND IMGUI_BUNDLE_WITH_IMMVISION)
    set(IMMVISION_SERIALIZE_JSON ON CACHE INTERNAL "" FORCE)
    add_subdirectory(immvision)
    if (IMGUI_BUNDLE_WITH_IMMVISION)

        find_package(nlohmann_json CONFIG QUIET)
        if(nlohmann_json_FOUND)
            target_link_libraries(immvision PRIVATE nlohmann_json::nlohmann_json)
        else()
            # use nlohmann_json provided by hello_imgui if not found in package
            target_link_libraries(immvision PRIVATE nlohmann_json)
        endif()

        target_link_libraries(imgui_bundle INTERFACE immvision)
        hello_imgui_msvc_target_group_sources(immvision)
        target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_IMMVISION)

        if(IMGUI_BUNDLE_INSTALL_CPP)
            set(immvision_src_dir ${CMAKE_CURRENT_LIST_DIR}/immvision/immvision/src)
            FILE(GLOB immvision_headers ${immvision_src_dir}/immvision/*.h)
            install(FILES ${immvision_headers} DESTINATION include/immvision)
            ibd_add_installable_dependency(immvision)
            if(TARGET immvision_gl_loader)
                ibd_add_installable_dependency(immvision_gl_loader)
            endif()
            if(TARGET glad_imm)
                ibd_add_installable_dependency(glad_imm)
            endif()
        endif()
    endif()
endif()

# Build implot
if(IMGUI_BUNDLE_WITH_IMPLOT)
    add_simple_external_library_with_sources(implot implot)
    target_compile_definitions(implot PRIVATE "IMPLOT_CUSTOM_NUMERIC_TYPES=(signed char)(unsigned char)(signed short)(unsigned short)(signed int)(unsigned int)(signed long)(unsigned long)(signed long long)(unsigned long long)(float)(double)(long double)")
    _target_force_include(implot ${IMGUI_BUNDLE_CMAKE_PATH}/imgui_bundle_config.h)
    lg_disable_warning_exception_in_destructor(implot)
    target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_IMPLOT)
    set(IMGUI_BUNDLE_WITH_IMPLOT ON CACHE INTERNAL "" FORCE)
endif()

# Build implot3d
if(IMGUI_BUNDLE_WITH_IMPLOT3D)
    add_simple_external_library_with_sources(implot3d implot3d)
    target_compile_definitions(implot3d PRIVATE "IMPLOT3D_CUSTOM_NUMERIC_TYPES=(signed char)(unsigned char)(signed short)(unsigned short)(signed int)(unsigned int)(signed long)(unsigned long)(signed long long)(unsigned long long)(float)(double)(long double)")
    _target_force_include(implot3d ${IMGUI_BUNDLE_CMAKE_PATH}/imgui_bundle_config.h)
#    lg_disable_warning_exception_in_destructor(implot3d)
    target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_IMPLOT3D)
    set(IMGUI_BUNDLE_WITH_IMPLOT3D ON CACHE INTERNAL "" FORCE)
endif()


# Build imgui-node-editor
if(IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR)
    add_simple_external_library_with_sources(imgui_node_editor imgui-node-editor)

    # Always compile the immapp integration shim; only link immapp when available.
    # When immapp is absent, IMGUI_BUNDLE_DISABLE_IMMAPP is set so the .cpp
    # compiles stub implementations instead of calling into immapp.
    target_sources(imgui_node_editor PRIVATE
        imgui-node-editor/imgui_node_editor_immapp/node_editor_default_context.cpp
        imgui-node-editor/imgui_node_editor_immapp/node_editor_default_context.h
    )
    if(IMGUI_BUNDLE_WITH_IMMAPP)
        target_link_libraries(imgui_node_editor PUBLIC immapp)
    else()
        target_compile_definitions(imgui_node_editor PRIVATE IMGUI_BUNDLE_DISABLE_IMMAPP)
    endif()

    target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR)
    set(IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR ON CACHE INTERNAL "" FORCE)
endif()

# Build ImFileDialog
if(IMGUI_BUNDLE_WITH_IMFILEDIALOG AND IMGUI_BUNDLE_WITH_HELLO_IMGUI)
    if(HELLOIMGUI_HAS_OPENGL)
        add_simple_external_library(im_file_dialog ImFileDialog)
        target_sources(im_file_dialog PRIVATE
            ImFileDialog/ImFileDialog/ImFileDialog.cpp
            ImFileDialog/ImFileDialog/ImFileDialog.h
        )
        add_additional_sources_to_external_library(im_file_dialog ImFileDialog bundle_integration)
        target_include_directories(im_file_dialog PRIVATE hello_imgui/hello_imgui/src/hello_imgui/internal)
        target_include_directories(im_file_dialog PRIVATE imgui)
        target_link_libraries(im_file_dialog PRIVATE hello_imgui)

        target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_IMFILEDIALOG)
        set(IMGUI_BUNDLE_WITH_IMFILEDIALOG ON CACHE INTERNAL "" FORCE)

        if(IMGUI_BUNDLE_INSTALL_CPP)
            install(FILES ImFileDialog/ImFileDialog/ImFileDialog.h DESTINATION include/ImFileDialog)
        endif()
    endif()
endif()

# Build ImGuizmo
if(IMGUI_BUNDLE_WITH_IMGUIZMO)
    add_simple_external_library_with_sources(imguizmo ImGuizmo)
    add_additional_sources_to_external_library(imguizmo ImGuizmo ImGuizmoPure)

    target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_IMGUIZMO)
    set(IMGUI_BUNDLE_WITH_IMGUIZMO ON CACHE INTERNAL "" FORCE)
endif()

# Build imgui_tex_inspect
if(IMGUI_BUNDLE_WITH_IMGUI_TEX_INSPECT AND IMGUI_BUNDLE_WITH_HELLO_IMGUI)
    add_simple_external_library_with_sources(imgui_tex_inspect imgui_tex_inspect)
    target_sources(imgui_tex_inspect PRIVATE
        imgui_tex_inspect/imgui_tex_inspect/backends/tex_inspect_opengl.cpp
        imgui_tex_inspect/imgui_tex_inspect/backends/tex_inspect_opengl.h
    )
    target_include_directories(imgui_tex_inspect PRIVATE imgui_tex_inspect/imgui_tex_inspect)
    target_include_directories(imgui_tex_inspect PRIVATE imgui/imgui/backends)
    target_compile_definitions(imgui_tex_inspect PRIVATE IMGUI_IMPL_OPENGL_LOADER_GLAD)
    target_compile_definitions(imgui_tex_inspect PUBLIC IMGUI_BUNDLE_WITH_TEXT_INSPECT)
    target_include_directories(imgui_tex_inspect PRIVATE hello_imgui/hello_imgui/external/OpenGL_Loaders/glad/include)
    target_link_libraries(imgui_tex_inspect PUBLIC hello_imgui)

    target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_IMGUI_TEX_INSPECT)
    set(IMGUI_BUNDLE_WITH_IMGUI_TEX_INSPECT ON CACHE INTERNAL "" FORCE)
endif()

# Add nanovg & nvg_imgui
if(IMGUI_BUNDLE_WITH_NANOVG)
    if (NOT (HELLOIMGUI_HAS_OPENGL OR HELLOIMGUI_HAS_METAL))
        message(FATAL_ERROR "nanovg requires OpenGL or Metal support in hello_imgui")
    endif()
    if(HELLOIMGUI_HAS_METAL)
        enable_language(OBJC)
    endif()

    # Add nanovg
    add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/nanovg/nanovg)
    # fix include for nanovg
    set_target_properties(nanovg PROPERTIES INTERFACE_INCLUDE_DIRECTORIES
        $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/nanovg/nanovg/src>  # wonderfully terse, isn't it?
    )

    target_compile_definitions(nanovg PUBLIC NANOVG_INSIDE_IMGUI_BUNDLE)
    target_compile_definitions(nanovg PUBLIC IMGUI_BUNDLE_WITH_NANOVG)
    target_link_libraries(imgui_bundle INTERFACE nanovg)
    hello_imgui_msvc_target_group_sources(nanovg)

    # Add support for metal
    if(HELLOIMGUI_HAS_METAL)
        target_sources(nanovg PRIVATE nanovg/MetalNanoVG/src/nanovg_mtl.m nanovg/MetalNanoVG/src/nanovg_mtl.h)
        target_link_libraries(nanovg PUBLIC "-framework Metal" "-framework QuartzCore")
        target_include_directories(nanovg PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/nanovg/MetalNanoVG/src>)
    endif()

    # Add nvg_imgui
    add_simple_external_library(nvg_imgui nanovg)
    target_link_libraries(nvg_imgui PUBLIC nanovg hello_imgui)
    file(GLOB_RECURSE nvg_imgui_sources nanovg/nvg_imgui/*.cpp nanovg/nvg_imgui/*.h)
    if (HELLOIMGUI_HAS_METAL)
        set(nvg_imgui_sources ${nvg_imgui_sources}
            nanovg/nvg_imgui/nvg_mtl_hello_imgui.mm
            nanovg/nvg_imgui/nvg_mtl_hello_imgui.h
        )
    endif()
    target_sources(nvg_imgui PRIVATE ${nvg_imgui_sources})

    target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_NANOVG)
    set(IMGUI_BUNDLE_WITH_NANOVG ON CACHE INTERNAL "" FORCE)

    if(IMGUI_BUNDLE_INSTALL_CPP)
        set(nanovg_headers nanovg/nanovg/src/nanovg.h nanovg/nanovg/src/nanovg_gl.h nanovg/nanovg/src/nanovg_gl_utils.h)
        install(FILES ${nanovg_headers} DESTINATION include)
        if(HELLOIMGUI_HAS_METAL)
            install(FILES nanovg/MetalNanoVG/src/nanovg_mtl.h DESTINATION include)
        endif()
        ibd_add_installable_dependency(nanovg)
    endif()
endif()

# Add ImAnim
if(IMGUI_BUNDLE_WITH_IMANIM)
    add_simple_external_library_with_sources(imanim ImAnim)
    target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_IMANIM)
    target_include_directories(imanim PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/ImAnim/ImAnim>)
    set(IMGUI_BUNDLE_WITH_IMANIM ON CACHE INTERNAL "" FORCE)
endif()


###############################################################################
# Core libraries, used everywhere in the demos
# (can not be disabled)
###############################################################################
# Build ImguiColorTextEdit
add_subdirectory(ImGuiColorTextEdit)

# Build imgui_md (requires hello_imgui and immapp for the wrapper)
if(IMGUI_BUNDLE_WITH_IMGUI_MD AND IMGUI_BUNDLE_WITH_HELLO_IMGUI)
    add_simple_external_library(imgui_md imgui_md)
    target_sources(imgui_md PRIVATE
        imgui_md/imgui_md/imgui_md.cpp
        imgui_md/imgui_md/imgui_md.h
        imgui_md/md4c/src/md4c.c
        imgui_md/md4c/src/md4c.h
        imgui_md/imgui_md_wrapper/imgui_md_wrapper.cpp
        imgui_md/imgui_md_wrapper/imgui_md_wrapper.h
    )
    target_include_directories(imgui_md PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/imgui_md/md4c/src>)
    target_include_directories(imgui_md PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/imgui_md/imgui_md_wrapper>)
    target_link_libraries(imgui_md PUBLIC hello_imgui imgui_color_text_edit fplus immapp)
    hello_imgui_msvc_target_group_sources(imgui_md)
    if(IMGUI_BUNDLE_INSTALL_CPP)
        install(FILES imgui_md/imgui_md_wrapper/imgui_md_wrapper.h DESTINATION include/imgui_md_wrapper)
    endif()

    target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_IMGUI_MD)
    set(IMGUI_BUNDLE_WITH_IMGUI_MD ON CACHE INTERNAL "" FORCE)
else()
    message(STATUS "Skipping imgui_md (disabled or hello_imgui not available)")
endif()


###############################################################################
# Lightweight widget libraries
###############################################################################
# Build imgui-knobs
add_simple_external_library_with_sources(imgui_knobs imgui-knobs)
# Build imspinner
add_simple_external_library_with_sources(imspinner imspinner)
target_compile_definitions(imspinner PUBLIC IMSPINNER_DEMO)
# Build imgui_toggle
add_simple_external_library_with_sources(imgui_toggle imgui_toggle)
# Build imgui_command_palette
add_simple_external_library_with_sources(imgui_command_palette imgui-command-palette)
# Add ImCoolBar
add_simple_external_library_with_sources(imcoolbar ImCoolBar)
# Add portable_file_dialogs
add_library(portable_file_dialogs INTERFACE)
target_include_directories(portable_file_dialogs INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/portable_file_dialogs>)
target_link_libraries(imgui_bundle INTERFACE portable_file_dialogs)
if(IMGUI_BUNDLE_INSTALL_CPP)
    install(FILES portable_file_dialogs/portable_file_dialogs/portable_file_dialogs.h DESTINATION include/portable_file_dialogs)
    ibd_add_installable_dependency(portable_file_dialogs)
endif()


###############################################################################
# immapp (Core Library)
###############################################################################
# Build immapp (Immediate App lib, internal to ImGui Bundle) if hello_imgui is available
if(IMGUI_BUNDLE_WITH_IMMAPP AND IMGUI_BUNDLE_WITH_HELLO_IMGUI)
    add_subdirectory(immapp/immapp)
    # And add info about the active libraries
    target_link_libraries(immapp PUBLIC imgui_bundle)
    set(IMGUI_BUNDLE_WITH_IMMAPP ON CACHE INTERNAL "" FORCE)
    target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_IMMAPP)
else()
    message(STATUS "Skipping immapp (disabled or hello_imgui not available)")
endif()


###############################################################################
# imgui_explorer (interactive demo viewer for ImGui, ImPlot, ImPlot3D, ImAnim)
###############################################################################
add_subdirectory(imgui_explorer/imgui_explorer)

