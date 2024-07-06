file(GLOB input_docpart_files ${CMAKE_CURRENT_LIST_DIR}/devdoc_parts/*.adoc)
set(input_doc_files ${input_docpart_files} ${CMAKE_CURRENT_LIST_DIR}/index.adoc)
add_custom_command(
    OUTPUT ${IMGUI_BUNDLE_PATH}/docs/devel_docs/cmake_marker.lock
    COMMAND /bin/bash ${CMAKE_CURRENT_LIST_DIR}/scripts/build_devel_doc.sh
    DEPENDS ${input_doc_files}
)
add_custom_target(build_develdoc ALL DEPENDS ${output_html_files})
