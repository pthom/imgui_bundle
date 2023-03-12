include(../cmake/add_simple_library.cmake) # Tooling to build libraries and link them to imgui_bundle

# Add fplus
add_library(fplus INTERFACE)
target_include_directories(fplus INTERFACE fplus)


# Build imgui + hello_imgui
include(../cmake/add_hello_imgui.cmake)
add_hello_imgui()
if (IMGUI_BUNDLE_BUILD_PYTHON)
    target_compile_definitions(imgui PUBLIC IMGUI_BUNDLE_BUILD_PYTHON)
endif()
# Add imgui_pywrappers
if (IMGUI_BUNDLE_BUILD_PYTHON)
    add_simple_external_library(imgui_pywrappers imgui/imgui_pywrappers)
    target_sources(imgui_pywrappers PRIVATE
        imgui/imgui_pywrappers/imgui_pywrappers.cpp imgui/imgui_pywrappers/imgui_pywrappers.h
        imgui/imgui_pywrappers/imgui_internal_pywrappers.cpp imgui/imgui_pywrappers/imgui_internal_pywrappers.h
        )
    target_link_libraries(imgui_pywrappers PUBLIC pybind11::pybind11)
endif()
# Build immvision
add_subdirectory(immvision)
if (IMGUI_BUNDLE_WITH_IMMVISION)
    target_link_libraries(imgui_bundle PUBLIC immvision)
    hello_imgui_msvc_target_group_sources(immvision)
    target_compile_definitions(imgui_bundle PUBLIC IMGUI_BUNDLE_WITH_IMMVISION)
endif()
# Build immapp (Immediate App lib, internal to ImGui Bundle)
add_subdirectory(immapp/immapp)
# Build implot
add_simple_external_library_with_sources(implot implot)
target_compile_definitions(implot PRIVATE "IMPLOT_CUSTOM_NUMERIC_TYPES=(signed char)(unsigned char)(signed short)(unsigned short)(signed int)(unsigned int)(signed long)(unsigned long)(signed long long)(unsigned long long)(float)(double)(long double)")
lg_target_force_include(implot ${CMAKE_CURRENT_LIST_DIR}/../cmake/imgui_bundle_config.h)
lg_disable_warning_exception_in_destructor(implot)
# Build ImguiColorTextEdit
add_subdirectory(ImGuiColorTextEdit)
# Build imgui-node-editor
add_simple_external_library_with_sources(imgui_node_editor imgui-node-editor)
target_sources(imgui_node_editor PRIVATE
    imgui-node-editor/imgui_node_editor_immapp/node_editor_default_context.cpp
    imgui-node-editor/imgui_node_editor_immapp/node_editor_default_context.h
    )
target_link_libraries(imgui_node_editor PUBLIC immapp)
# Build imgui-knobs
add_simple_external_library_with_sources(imgui_knobs imgui-knobs)
# Build ImFileDialog
add_simple_external_library(im_file_dialog ImFileDialog)
target_sources(im_file_dialog PRIVATE
    ImFileDialog/ImFileDialog/ImFileDialog.cpp
    ImFileDialog/ImFileDialog/ImFileDialog.h
)
add_additional_sources_to_external_library(im_file_dialog ImFileDialog bundle_integration)
target_include_directories(im_file_dialog PRIVATE hello_imgui/hello_imgui/src/hello_imgui/internal)
target_include_directories(im_file_dialog PRIVATE imgui)
target_link_libraries(im_file_dialog PRIVATE hello_imgui)
# Build imspinner
add_simple_external_library_with_sources(imspinner imspinner)
# Build imgui_toggle
add_simple_external_library_with_sources(imgui_toggle imgui_toggle)
# Build imgui_command_palette
add_simple_external_library_with_sources(imgui_command_palette imgui-command-palette)
# Build imgui_md
add_simple_external_library(imgui_md imgui_md)
target_sources(imgui_md PRIVATE
    imgui_md/imgui_md/imgui_md.cpp
    imgui_md/imgui_md/imgui_md.h
    imgui_md/md4c/src/md4c.c
    imgui_md/md4c/src/md4c.h
    imgui_md/imgui_md_wrapper/imgui_md_wrapper.cpp
    imgui_md/imgui_md_wrapper/imgui_md_wrapper.h
    )
target_include_directories(imgui_md PUBLIC imgui_md/md4c/src)
target_include_directories(imgui_md PUBLIC imgui_md/imgui_md_wrapper)
target_link_libraries(imgui_md PUBLIC hello_imgui imgui_color_text_edit fplus immapp)
hello_imgui_msvc_target_group_sources(imgui_md)
# Build ImGuizmo
add_simple_external_library_with_sources(imguizmo ImGuizmo)
add_additional_sources_to_external_library(imguizmo ImGuizmo ImGuizmoPure)
# Build imgui_tex_inspect
add_simple_external_library_with_sources(imgui_tex_inspect imgui_tex_inspect)
target_sources(imgui_tex_inspect PRIVATE
    imgui_tex_inspect/imgui_tex_inspect/backends/tex_inspect_opengl.cpp
    imgui_tex_inspect/imgui_tex_inspect/backends/tex_inspect_opengl.h
    )
# Add portable_file_dialogs
add_library(portable_file_dialogs INTERFACE)
target_include_directories(portable_file_dialogs INTERFACE portable_file_dialogs)
target_link_libraries(imgui_bundle PUBLIC portable_file_dialogs)

target_include_directories(imgui_tex_inspect PRIVATE imgui_tex_inspect/imgui_tex_inspect)
target_include_directories(imgui_tex_inspect PRIVATE imgui/imgui/backends)
target_compile_definitions(imgui_tex_inspect PRIVATE IMGUI_IMPL_OPENGL_LOADER_GLAD)
target_include_directories(imgui_tex_inspect PRIVATE hello_imgui/hello_imgui/external/OpenGL_Loaders/glad/include)
target_link_libraries(imgui_tex_inspect PUBLIC hello_imgui)
