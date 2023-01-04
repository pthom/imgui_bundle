set(CMAKE_CXX_STANDARD 20)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
include_directories(.)

function(add_demo_cpp)
    set(args ${ARGN})
    list(GET args 0 app_name)
    imgui_bundle_add_app(${args})
    if(MSVC)
        hello_imgui_msvc_target_set_folder(${app_name} demos_cpp)
    endif()
    target_link_libraries(${app_name} PUBLIC demo_utils)
endfunction()


function(add_single_file_demo_cpp demo_cpp_file)
    get_filename_component(app_name "${demo_cpp_file}" NAME_WE)
    add_demo_cpp(${app_name} ${demo_cpp_file})
endfunction()


function(add_this_folder_demos)
    FILE(GLOB demo_cpp_files *.cpp)
    FOREACH(demo_cpp_file ${demo_cpp_files})
        add_single_file_demo_cpp(${demo_cpp_file})
    ENDFOREACH()
endfunction()


add_subdirectory(demo_utils)
add_subdirectory(demos_immapp)
add_subdirectory(demo_texteditor)
add_subdirectory(demo_widgets_docking)
add_subdirectory(demos_node_editor)
add_subdirectory(demos_imguizmo)
add_subdirectory(demos_tex_inspect)

add_demo_cpp(demo_imgui_md demo_imgui_md.cpp)

if (IMGUI_BUNDLE_WITH_IMMVISION)
    add_subdirectory(demos_immvision)
endif()

FILE(COPY assets DESTINATION ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})
