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
# Build immvision (OpenCV is optional — immvision works without it)
if(HELLOIMGUI_HAS_OPENGL AND IMGUI_BUNDLE_WITH_IMMVISION)
    set(IMMVISION_SERIALIZE_JSON ON CACHE INTERNAL "" FORCE)
    add_subdirectory(immvision)

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

# Build implot
if(IMGUI_BUNDLE_WITH_IMPLOT)
    add_simple_external_library_with_sources(implot implot)
    target_compile_definitions(implot PRIVATE "IMPLOT_CUSTOM_NUMERIC_TYPES=(signed char)(unsigned char)(signed short)(unsigned short)(signed int)(unsigned int)(signed long)(unsigned long)(signed long long)(unsigned long long)(float)(double)(long double)")
    _target_force_include(implot ${IMGUI_BUNDLE_CMAKE_PATH}/imgui_bundle_config.h)
    lg_disable_warning_exception_in_destructor(implot)
    if(MSVC)
        target_compile_options(implot PRIVATE /bigobj)
    endif()
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

    # Handwritten wrappers, only needed by the python bindings
    if (IMGUI_BUNDLE_BUILD_PYTHON)
        target_sources(imgui_node_editor PRIVATE
            imgui-node-editor/imgui_node_editor_pywrappers/imgui_node_editor_pywrappers.cpp
            imgui-node-editor/imgui_node_editor_pywrappers/imgui_node_editor_pywrappers.h
        )
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
    add_additional_sources_to_external_library(imguizmo ImGuizmo ImGuizmo/src)
    target_include_directories(imguizmo PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/ImGuizmo/ImGuizmo/src>)
    if(IMGUI_BUNDLE_INSTALL_CPP)
        # In-tree, ImGuizmo/src is an include dir (#include "ImGuizmo.h"): keep the same include paths from an install
        file(GLOB imguizmo_headers ${CMAKE_CURRENT_SOURCE_DIR}/ImGuizmo/ImGuizmo/src/*.h)
        install(FILES ${imguizmo_headers} DESTINATION include)
        file(GLOB imguizmo_pure_headers ${CMAKE_CURRENT_SOURCE_DIR}/ImGuizmo/ImGuizmoPure/*.h)
        install(FILES ${imguizmo_pure_headers} DESTINATION include/ImGuizmoPure)
    endif()
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
        # MetalNanoVG was written with ARC enabled — compile with -fobjc-arc
        set_source_files_properties(nanovg/MetalNanoVG/src/nanovg_mtl.m
            TARGET_DIRECTORY nanovg
            PROPERTIES COMPILE_FLAGS "-fobjc-arc")
    endif()

    # Add nvg_imgui
    add_simple_external_library(nvg_imgui nanovg)
    target_link_libraries(nvg_imgui PUBLIC nanovg hello_imgui)
    file(GLOB_RECURSE nvg_imgui_sources nanovg/nvg_imgui/*.cpp nanovg/nvg_imgui/*.h)
    if(IMGUI_BUNDLE_INSTALL_CPP)
        file(GLOB nvg_imgui_headers nanovg/nvg_imgui/*.h)
        install(FILES ${nvg_imgui_headers} DESTINATION include/nvg_imgui)
    endif()
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
    # Suppress warnings in third-party ImAnim code
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
        target_compile_options(imanim PRIVATE -Wno-unused-result -Wno-format-truncation)
    endif()
    if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        target_compile_options(imanim PRIVATE -Wno-unknown-warning-option -Wno-nontrivial-memaccess -Wno-nontrivial-memcall)
    endif()
    set(IMGUI_BUNDLE_WITH_IMANIM ON CACHE INTERNAL "" FORCE)
endif()


###############################################################################
# Core libraries, used everywhere in the demos
# (can not be disabled)
###############################################################################
# Build ImguiColorTextEdit
add_subdirectory(ImGuiColorTextEdit)

# Build imgui_rich_md (requires hello_imgui and immapp for the wrapper)
if(IMGUI_BUNDLE_WITH_IMGUI_MD AND IMGUI_BUNDLE_WITH_HELLO_IMGUI)
    # The markdown stack is imgui_rich_md (external/imgui_rich_md, target imgui_rich_md). The bundle sets its
    # options and dependency dirs, then adds its host (assets, textures, fonts through HelloImGui), the
    # MicroTeX Level 2 adapter (formula textures on HelloImGui::TextureGpu), and the historical include paths.
    option(IMGUI_RICHMD_WITH_CODE_EDITOR "Code blocks with syntax highlighting in markdown (ImGuiColorTextEdit)" ON)
    # IMGUI_RICHMD_WITH_LATEX is derived from the bundle-level IMGUI_BUNDLE_WITH_MICROTEX option, and needs FreeType
    if(DEFINED IMGUI_BUNDLE_WITH_MICROTEX AND IMGUI_BUNDLE_WITH_MICROTEX AND HELLOIMGUI_USE_FREETYPE)
        set(_IMGUI_RICHMD_LATEX_DEFAULT ON)
    else()
        set(_IMGUI_RICHMD_LATEX_DEFAULT OFF)
    endif()
    option(IMGUI_RICHMD_WITH_LATEX "Enable native LaTeX rendering in markdown (via MicroTeX)" ${_IMGUI_RICHMD_LATEX_DEFAULT})
    if(IMGUI_RICHMD_WITH_LATEX AND NOT HELLOIMGUI_USE_FREETYPE)
        message(FATAL_ERROR "IMGUI_RICHMD_WITH_LATEX requires FreeType (normally provided by HelloImGui). "
                            "Either enable HELLOIMGUI_USE_FREETYPE or set IMGUI_RICHMD_WITH_LATEX=OFF.")
    endif()
    # URL image download: libcurl on desktop C++, emscripten fetch on the web (not in Pyodide side modules,
    # where Python installs a JS fetch() callback; -sFETCH would also force a non-PIC library into the link)
    if(IOS OR ANDROID OR IMGUI_BUNDLE_BUILD_PYTHON AND NOT EMSCRIPTEN)
        set(_IMGUI_MD_DOWNLOAD_DEFAULT OFF)
    else()
        set(_IMGUI_MD_DOWNLOAD_DEFAULT ON)
    endif()
    option(IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES "Enable URL image download in markdown (requires libcurl)" ${_IMGUI_MD_DOWNLOAD_DEFAULT})
    if(IMGUI_BUNDLE_BUILD_PYODIDE)
        set(IMGUI_RICHMD_EMSCRIPTEN_FETCH OFF)
        set(IMGUI_RICHMD_WASM_EXCEPTIONS OFF)  # the side module already builds with exceptions on
    endif()
    option(IMGUI_RICHMD_EMBED_ASSETS "Embed the markdown fonts and images in the imgui_rich_md library (the bundle serves them from its assets folder)" OFF)
    set(IMGUI_RICHMD_STB_IMAGE_IMPLEMENTATION OFF)  # provided by HelloImGui
    set(IMGUI_RICHMD_MICROTEX_DIR ${CMAKE_CURRENT_LIST_DIR}/imgui_microtex/MicroTeX)
    set(IMGUI_RICHMD_INSTALL ${IMGUI_BUNDLE_INSTALL_CPP})
    add_subdirectory(imgui_rich_md/imgui_rich_md)

    # The bundle's host, include shims and bindings (external/imgui_rich_md/{hosts,compat,bindings}), the MicroTeX
    # texture adapter (external/imgui_microtex); the former target names stay as aliases
    add_library(imgui_md ALIAS imgui_rich_md)
    target_sources(imgui_rich_md PRIVATE imgui_rich_md/hosts/hello_imgui_host.cpp)
    target_compile_definitions(imgui_rich_md PRIVATE IMGUI_RICHMD_HOST_HELLO_IMGUI)
    target_include_directories(imgui_rich_md PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/imgui_rich_md/compat>)  # imgui_md_wrapper/*.h
    target_link_libraries(imgui_rich_md PUBLIC hello_imgui)
    target_link_libraries(imgui_bundle INTERFACE imgui_rich_md)
    if(HELLOIMGUI_USE_SDL2)
        target_compile_definitions(imgui_rich_md PRIVATE IMGUI_RICHMD_EMSCRIPTEN_SDL2)  # clipboard to the browser
    endif()
    if(IMGUI_BUNDLE_BUILD_PYTHON)
        target_compile_definitions(imgui_rich_md PUBLIC IMGUI_RICHMD_DEFAULT_SNIPPET_LANGUAGE_PYTHON)
    endif()
    if(IMGUI_RICHMD_WITH_LATEX)
        target_sources(imgui_rich_md_latex PRIVATE imgui_microtex/imgui_microtex/imgui_microtex.cpp imgui_microtex/imgui_microtex/imgui_microtex.h)
        target_include_directories(imgui_rich_md_latex PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/imgui_microtex>)
        target_link_libraries(imgui_rich_md_latex PUBLIC hello_imgui)
        add_library(imgui_microtex ALIAS imgui_rich_md_latex)
        message(STATUS "imgui_rich_md: native LaTeX rendering enabled (via MicroTeX)")
    endif()
    if(IMGUI_RICHMD_LINKS_CURL)
        message(STATUS "imgui_rich_md: URL image download enabled (using system libcurl)")
    endif()
    set(IMGUI_BUNDLE_LINKS_CURL ${IMGUI_RICHMD_LINKS_CURL} CACHE INTERNAL "imgui_rich_md links libcurl (read by imgui_bundle-config.cmake.in)" FORCE)
    hello_imgui_msvc_target_group_sources(imgui_rich_md)

    if(IMGUI_BUNDLE_INSTALL_CPP)
        ibd_add_installable_dependency(imgui_rich_md)
        # the historical include paths
        install(FILES imgui_rich_md/compat/imgui_md_wrapper/imgui_md_wrapper.h imgui_rich_md/compat/imgui_md_wrapper/imgui_md_host.h DESTINATION include/imgui_md_wrapper)
        if(IMGUI_RICHMD_WITH_CODE_EDITOR)
            install(FILES imgui_rich_md/compat/imgui_md_wrapper/backends/code_editor/snippets.h DESTINATION include/imgui_md_wrapper/backends/code_editor)
        endif()
        if(IMGUI_RICHMD_WITH_LATEX)
            ibd_add_installable_dependency(microtex)
            ibd_add_installable_dependency(imgui_rich_md_latex)
            install(FILES imgui_microtex/imgui_microtex/imgui_microtex.h DESTINATION include/imgui_microtex)
            # MicroTeX is added with EXCLUDE_FROM_ALL, which also discards its own install() rules,
            # while its exported target advertises include/microtex. Install the headers it would
            # have installed (same list as MicroTeX/lib/CMakeLists.txt, "installation" section).
            set(_microtex_lib ${CMAKE_CURRENT_LIST_DIR}/imgui_microtex/MicroTeX/lib)
            install(FILES
                ${CMAKE_CURRENT_BINARY_DIR}/imgui_rich_md/imgui_rich_md/microtex_build/lib/microtexconfig.h
                ${_microtex_lib}/microtexexport.h ${_microtex_lib}/microtex.h ${_microtex_lib}/microtexapi.h
                DESTINATION include/microtex)
            install(FILES ${_microtex_lib}/utils/types.h DESTINATION include/microtex/utils)
            install(FILES ${_microtex_lib}/render/render.h DESTINATION include/microtex/render)
            install(FILES ${_microtex_lib}/unimath/font_src.h ${_microtex_lib}/unimath/font_meta.h
                DESTINATION include/microtex/unimath)
            install(FILES ${_microtex_lib}/graphic/graphic.h ${_microtex_lib}/graphic/font_style.h ${_microtex_lib}/graphic/graphic_basic.h
                DESTINATION include/microtex/graphic)
        endif()
    endif()

    if(IMGUI_BUNDLE_WITH_MICROTEX)
        target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_MICROTEX)
    endif()
    target_compile_definitions(imgui_bundle INTERFACE IMGUI_BUNDLE_WITH_IMGUI_MD)
    set(IMGUI_BUNDLE_WITH_IMGUI_MD ON CACHE INTERNAL "" FORCE)
else()
    message(STATUS "Skipping imgui_rich_md (disabled or hello_imgui not available)")
endif()


###############################################################################
# Lightweight widget libraries
###############################################################################
# Build imgui-knobs
add_simple_external_library_with_sources(imgui_knobs imgui-knobs)
# Build imspinner
add_simple_external_library(imspinner imspinner)
target_sources(imspinner PRIVATE ${CMAKE_CURRENT_LIST_DIR}/imspinner/imspinner_bundle.cpp)
if(IMGUI_BUNDLE_INSTALL_CPP)
    # Install only imspinner*.h (skip the cimspinner* C-API headers)
    file(GLOB imspinner_headers ${CMAKE_CURRENT_LIST_DIR}/imspinner/imspinner/imspinner*.h)
    install(FILES ${imspinner_headers} DESTINATION include/imspinner)
endif()
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

