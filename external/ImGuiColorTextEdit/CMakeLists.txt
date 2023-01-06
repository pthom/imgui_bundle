add_simple_external_library_with_sources(imgui_color_text_edit ImGuiColorTextEdit)
target_sources(imgui_color_text_edit PRIVATE
    bundle_integration/TextEditorBundle/TextEditorBundle.cpp
    bundle_integration/TextEditorBundle/TextEditorBundle.h
    )
target_include_directories(imgui_color_text_edit PUBLIC bundle_integration)
target_link_libraries(imgui_color_text_edit PUBLIC fplus hello_imgui immapp imgui_md)
if (IMGUI_BUNDLE_BUILD_PYTHON)
    target_compile_definitions(imgui_color_text_edit PRIVATE IMGUI_BUNDLE_BUILD_PYTHON)
endif()
