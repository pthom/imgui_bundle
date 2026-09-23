# imgui_richmd_embed_files(<target> <symbol> BASE_DIR <dir> FILES <relative paths...>)
#
# Embeds files in the binary: generates <symbol>.cpp at build time (regenerated when a file changes)
# with one byte array per file (gzipped: about half the size for fonts) and a table
# `const ImGuiMd::EmbeddedAsset <symbol>[]`, plus `const int <symbol>_count`, and adds it to <target>.
# Paths in the table are the relative paths given.
# Used for the markdown fonts and images (IMGUI_RICHMD_EMBED_ASSETS) and for literate examples.
set(_IMGUI_RICHMD_EMBED_SCRIPT "${CMAKE_CURRENT_LIST_DIR}/imgui_richmd_embed_files_script.cmake")

function(imgui_richmd_embed_files target symbol)
    cmake_parse_arguments(ARG "" "BASE_DIR" "FILES" ${ARGN})
    set(out "${CMAKE_CURRENT_BINARY_DIR}/${symbol}.cpp")
    set(abs_files)
    foreach(f ${ARG_FILES})
        list(APPEND abs_files "${ARG_BASE_DIR}/${f}")
    endforeach()
    add_custom_command(
        OUTPUT "${out}"
        COMMAND ${CMAKE_COMMAND} "-DOUT=${out}" "-DSYMBOL=${symbol}" "-DBASE_DIR=${ARG_BASE_DIR}" "-DFILES=${ARG_FILES}"
                -P "${_IMGUI_RICHMD_EMBED_SCRIPT}"
        DEPENDS ${abs_files} "${_IMGUI_RICHMD_EMBED_SCRIPT}"
        COMMENT "Embedding files into ${symbol}.cpp"
        VERBATIM)
    target_sources(${target} PRIVATE "${out}")
endfunction()
