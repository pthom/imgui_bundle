file(GLOB input_docpart_files ${CMAKE_CURRENT_LIST_DIR}/doc_parts/*.adoc)
set(input_doc_files
    ${input_docpart_files}
    ${CMAKE_CURRENT_LIST_DIR}/Readme_source.adoc
    ${CMAKE_CURRENT_LIST_DIR}/Readme_source_pypi.adoc
    ${CMAKE_CURRENT_LIST_DIR}/faq_source.adoc
    )
file(GLOB output_html_files ${IMGUI_BUNDLE_PATH}/docs/*.html)

add_custom_command(
    OUTPUT
        ${output_html_files}
        ${CMAKE_CURRENT_LIST_DIR}/Readme.adoc
        ${IMGUI_BUNDLE_PATH}/bindings/imgui_bundle/Readme_pypi.md
    COMMAND /bin/bash ${CMAKE_CURRENT_LIST_DIR}/scripts/build_doc.sh
    DEPENDS ${input_doc_files}
)
add_custom_target(build_doc ALL DEPENDS ${CMAKE_CURRENT_LIST_DIR}/Readme.adoc)
