# imgui_rich_md: rich markdown for Dear ImGui (headings, lists, tables, code, images, admonitions,
# LaTeX, wikilinks, sections and imports). Renderer by Dmitry Mekhontsev (imgui_md), extensively rewritten.
#
# Requirements from the parent project: a target `imgui` (Dear ImGui 1.92+), and, for the optional
# backends, either the targets (`imgui_color_text_edit`, `freetype`) or the directories below.
# Standalone (this file as the top-level project): the examples fetch Dear ImGui themselves.
cmake_minimum_required(VERSION 3.20)
project(imgui_rich_md LANGUAGES C CXX)

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
    set(_richmd_standalone ON)
else()
    set(_richmd_standalone OFF)
endif()

option(IMGUI_RICHMD_WITH_CODE_EDITOR "Code blocks with syntax highlighting (ImGuiColorTextEdit)" OFF)
option(IMGUI_RICHMD_WITH_LATEX "LaTeX formulas (MicroTeX, needs FreeType)" OFF)
option(IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES "Images from URLs (libcurl on desktop, fetch on Emscripten)" OFF)
option(IMGUI_RICHMD_EMBED_ASSETS "Embed the fonts and images in the library (no assets folder needed)" ${_richmd_standalone})
if(NOT DEFINED IMGUI_RICHMD_EMBED_EXTRA_FILES)  # a parent's normal variable must not be shadowed (CMP0126)
    set(IMGUI_RICHMD_EMBED_EXTRA_FILES "" CACHE STRING "Extra files to embed with the assets (paths relative to assets/, semicolon separated)")
endif()
option(IMGUI_RICHMD_STB_IMAGE_IMPLEMENTATION "Compile stb_image here (OFF when the parent provides it)" ${_richmd_standalone})
option(IMGUI_RICHMD_EMSCRIPTEN_FETCH "Emscripten: link -sFETCH for URL images (not for Pyodide side modules)" ON)
option(IMGUI_RICHMD_WASM_EXCEPTIONS "Emscripten: wasm exceptions on the LaTeX targets, so that an invalid formula does not abort the page" ON)
option(IMGUI_RICHMD_BUILD_EXAMPLES "Build the examples" ${_richmd_standalone})
# Where the optional dependencies are (a parent sets the variables before add_subdirectory, or the user sets
# them on the command line); fetched from the pthom forks otherwise
if(NOT DEFINED IMGUI_RICHMD_COLOR_TEXT_EDIT_DIR)
    set(IMGUI_RICHMD_COLOR_TEXT_EDIT_DIR "" CACHE PATH "ImGuiColorTextEdit sources (fork pthom/ImGuiColorTextEdit, branch rich_md)")
endif()
if(NOT DEFINED IMGUI_RICHMD_MICROTEX_DIR)
    set(IMGUI_RICHMD_MICROTEX_DIR "" CACHE PATH "MicroTeX sources (fork pthom/MicroTeX, branch imgui_bundle)")
endif()

set(_richmd_dir ${CMAKE_CURRENT_LIST_DIR}/imgui_rich_md)
set(_md4c_dir ${CMAKE_CURRENT_LIST_DIR}/external/md4c/src)
if(NOT EXISTS ${_md4c_dir}/md4c.c)
    message(FATAL_ERROR "imgui_rich_md: md4c is missing (git submodule update --init external/md4c)")
endif()

add_library(imgui_rich_md STATIC
    ${_md4c_dir}/md4c.c ${_md4c_dir}/md4c.h
    ${_richmd_dir}/rich_md_renderer.cpp ${_richmd_dir}/rich_md_renderer.h
    ${_richmd_dir}/rich_md.cpp ${_richmd_dir}/rich_md.h
    ${_richmd_dir}/rich_md_imports.cpp
    ${_richmd_dir}/rich_md_host.h ${_richmd_dir}/rich_md_internal.h
)
add_library(RichMd::RichMd ALIAS imgui_rich_md)
target_compile_features(imgui_rich_md PUBLIC cxx_std_17)
target_include_directories(imgui_rich_md PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}>
    $<BUILD_INTERFACE:${_md4c_dir}>
    $<INSTALL_INTERFACE:include>)
target_link_libraries(imgui_rich_md PUBLIC imgui)
if(APPLE)
    # limits.h and md4c both define OFF_MAX
    set_source_files_properties(${_md4c_dir}/md4c.c PROPERTIES COMPILE_OPTIONS "-Wno-macro-redefined")
endif()
if(IMGUI_RICHMD_STB_IMAGE_IMPLEMENTATION)
    target_sources(imgui_rich_md PRIVATE ${_richmd_dir}/third_party/stb_image_impl.cpp)
endif()

# --- code editor backend
if(IMGUI_RICHMD_WITH_CODE_EDITOR)
    if(NOT TARGET imgui_color_text_edit)
        if(NOT IMGUI_RICHMD_COLOR_TEXT_EDIT_DIR)
            include(FetchContent)
            # checked out under a folder named ImGuiColorTextEdit: the sources include "ImGuiColorTextEdit/TextEditor.h"
            # (SOURCE_SUBDIR names a folder without CMakeLists.txt: the sources are only fetched, the target is made below)
            FetchContent_Declare(imgui_color_text_edit_src GIT_REPOSITORY https://github.com/pthom/ImGuiColorTextEdit.git GIT_TAG rich_md GIT_SHALLOW TRUE
                                 SOURCE_DIR ${CMAKE_BINARY_DIR}/_deps/ImGuiColorTextEdit SOURCE_SUBDIR not_added)
            FetchContent_MakeAvailable(imgui_color_text_edit_src)
            set(IMGUI_RICHMD_COLOR_TEXT_EDIT_DIR ${imgui_color_text_edit_src_SOURCE_DIR})
        endif()
        file(GLOB _cte_sources ${IMGUI_RICHMD_COLOR_TEXT_EDIT_DIR}/*.cpp)
        add_library(imgui_color_text_edit STATIC ${_cte_sources})
        target_include_directories(imgui_color_text_edit PUBLIC ${IMGUI_RICHMD_COLOR_TEXT_EDIT_DIR}/..)
        target_link_libraries(imgui_color_text_edit PUBLIC imgui)
    endif()
    target_sources(imgui_rich_md PRIVATE
        ${_richmd_dir}/backends/code_editor/snippets.cpp ${_richmd_dir}/backends/code_editor/snippets.h)
    target_link_libraries(imgui_rich_md PUBLIC imgui_color_text_edit)
    target_compile_definitions(imgui_rich_md PUBLIC IMGUI_RICHMD_WITH_CODE_EDITOR)
endif()

# --- LaTeX backend (MicroTeX + FreeType)
if(IMGUI_RICHMD_WITH_LATEX)
    if(NOT IMGUI_RICHMD_MICROTEX_DIR)
        include(FetchContent)
        # fetched only (SOURCE_SUBDIR without CMakeLists.txt): added below, once the options are set
        FetchContent_Declare(microtex_src GIT_REPOSITORY https://github.com/pthom/MicroTeX.git GIT_TAG imgui_bundle GIT_SHALLOW TRUE SOURCE_SUBDIR not_added)
        FetchContent_MakeAvailable(microtex_src)
        set(IMGUI_RICHMD_MICROTEX_DIR ${microtex_src_SOURCE_DIR})
    endif()
    # Options of the MicroTeX fork (CMP0077: normal variables are honored as option defaults)
    set(MICROTEX_BUILD_STATIC ON)
    set(MICROTEX_GLYPH_RENDER_TYPE 2)      # typeface only (no vector path data)
    set(MICROTEX_HAVE_AUTO_FONT_FIND OFF)  # the fonts are given explicitly
    set(HAVE_LOG OFF)
    add_subdirectory(${IMGUI_RICHMD_MICROTEX_DIR} microtex_build EXCLUDE_FROM_ALL)

    add_library(imgui_rich_md_latex STATIC EXCLUDE_FROM_ALL
        ${_richmd_dir}/backends/latex/rich_md_latex.cpp ${_richmd_dir}/backends/latex/rich_md_latex.h
        ${_richmd_dir}/backends/latex/internal/graphic_freetype.cpp ${_richmd_dir}/backends/latex/internal/graphic_freetype.h)
    target_include_directories(imgui_rich_md_latex PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}>
        $<BUILD_INTERFACE:${IMGUI_RICHMD_MICROTEX_DIR}/lib>)
    if(TARGET freetype)
        target_link_libraries(imgui_rich_md_latex PUBLIC microtex freetype imgui)
    elseif(TARGET Freetype::Freetype)
        target_link_libraries(imgui_rich_md_latex PUBLIC microtex Freetype::Freetype imgui)
    else()
        find_package(Freetype REQUIRED)
        target_link_libraries(imgui_rich_md_latex PUBLIC microtex Freetype::Freetype imgui)
    endif()
    target_link_libraries(imgui_rich_md PUBLIC imgui_rich_md_latex)
    target_compile_definitions(imgui_rich_md PUBLIC IMGUI_RICHMD_WITH_LATEX)
    if(EMSCRIPTEN AND IMGUI_RICHMD_WASM_EXCEPTIONS)
        # MicroTeX reports an invalid formula with a C++ exception, which the wrapper catches. Emscripten
        # disables exception catching by default (a throw aborts the page): native wasm exceptions on the
        # LaTeX targets only cost nothing in size. setjmp users (FreeType, plutovg) must use the same
        # scheme, since the link switches to wasm setjmp/longjmp.
        foreach(_t microtex imgui_rich_md_latex imgui_rich_md freetype plutovg plutosvg)
            if(TARGET ${_t})
                target_compile_options(${_t} PRIVATE -fwasm-exceptions)
            endif()
        endforeach()
        target_link_options(imgui_rich_md PUBLIC -fwasm-exceptions)
    endif()
endif()

# --- URL images
set(IMGUI_RICHMD_LINKS_CURL OFF CACHE INTERNAL "imgui_rich_md links libcurl (for a parent's config file)" FORCE)
if(IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES)
    if(EMSCRIPTEN)
        if(IMGUI_RICHMD_EMSCRIPTEN_FETCH)
            target_link_options(imgui_rich_md PUBLIC -sFETCH)
            target_compile_definitions(imgui_rich_md PRIVATE IMGUI_RICHMD_EMSCRIPTEN_FETCH)
        endif()
    else()
        find_package(CURL)
        if(CURL_FOUND)
            target_sources(imgui_rich_md PRIVATE ${_richmd_dir}/rich_md_url_download.cpp ${_richmd_dir}/rich_md_url_download.h)
            target_link_libraries(imgui_rich_md PRIVATE CURL::libcurl)
            target_compile_definitions(imgui_rich_md PUBLIC IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES)
            set(IMGUI_RICHMD_LINKS_CURL ON CACHE INTERNAL "" FORCE)
        else()
            message(WARNING "imgui_rich_md: IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES is ON but libcurl was not found: URL images disabled "
                            "(Linux: apt install libcurl4-openssl-dev, Windows: vcpkg install curl)")
        endif()
    endif()
endif()

# --- embedded assets
if(IMGUI_RICHMD_EMBED_ASSETS)
    include(${CMAKE_CURRENT_LIST_DIR}/cmake/imgui_richmd_embed_files.cmake)
    set(_richmd_assets
        fonts/Roboto/Roboto-Regular.ttf fonts/Roboto/Roboto-Bold.ttf
        fonts/Roboto/Roboto-RegularItalic.ttf fonts/Roboto/Roboto-BoldItalic.ttf
        fonts/Inconsolata-Medium.ttf
        images/markdown_broken_image.png)
    if(IMGUI_RICHMD_WITH_LATEX)
        list(APPEND _richmd_assets fonts/latex/latinmodern-math.clm1 fonts/latex/latinmodern-math.otf)
    endif()
    list(APPEND _richmd_assets ${IMGUI_RICHMD_EMBED_EXTRA_FILES})
    imgui_richmd_embed_files(imgui_rich_md imgui_richmd_embedded_assets
        BASE_DIR ${CMAKE_CURRENT_LIST_DIR}/assets FILES ${_richmd_assets})
    target_compile_definitions(imgui_rich_md PUBLIC IMGUI_RICHMD_EMBED_ASSETS)
endif()

# --- install (headers under include/imgui_rich_md, targets exported by the parent or here)
if(_richmd_standalone OR IMGUI_RICHMD_INSTALL)
    install(FILES ${_richmd_dir}/rich_md.h ${_richmd_dir}/rich_md_host.h ${_richmd_dir}/rich_md_renderer.h
            DESTINATION include/imgui_rich_md)
    install(FILES ${_md4c_dir}/md4c.h DESTINATION include)
    if(IMGUI_RICHMD_WITH_CODE_EDITOR)
        install(FILES ${_richmd_dir}/backends/code_editor/snippets.h DESTINATION include/imgui_rich_md/backends/code_editor)
    endif()
    if(IMGUI_RICHMD_WITH_LATEX)
        install(FILES ${_richmd_dir}/backends/latex/rich_md_latex.h DESTINATION include/imgui_rich_md/backends/latex)
    endif()
endif()

if(IMGUI_RICHMD_BUILD_EXAMPLES)
    add_subdirectory(examples/minimal)
endif()
