add_simple_external_library_with_sources(imgui_color_text_edit ImGuiColorTextEdit)
if (IMGUI_BUNDLE_BUILD_PYTHON)
    target_compile_definitions(imgui_color_text_edit PRIVATE IMGUI_BUNDLE_BUILD_PYTHON)
endif()
