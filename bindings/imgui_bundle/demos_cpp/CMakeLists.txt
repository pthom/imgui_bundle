set(CMAKE_CXX_STANDARD 20)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
include(${IMGUI_BUNDLE_PATH}/imgui_bundle_cmake/imgui_bundle_add_demo.cmake)
include_directories(.)

set(demos_cpp_folder ${CMAKE_CURRENT_LIST_DIR})


add_subdirectory(demo_utils)
add_subdirectory(demos_immapp)
add_subdirectory(demos_node_editor)
add_subdirectory(demos_imguizmo)
add_subdirectory(demos_tex_inspect)
if(IMGUI_BUNDLE_WITH_NANOVG)
    add_subdirectory(demos_nanovg)
endif()
if (IMGUI_BUNDLE_WITH_IMMVISION)
    add_subdirectory(demos_immvision)
endif()
add_subdirectory(sandbox)

ibd_add_this_folder_auto_demos("")
ibd_add_this_folder_as_demos_library()

if (EMSCRIPTEN)
    set(demos_python_folder ${demos_cpp_folder}/../demos_python)

    set(imgui_demo_src_folder ${IMGUI_BUNDLE_PATH}/external/imgui/imgui/)
    set(imgui_demo_tmp_folder ${CMAKE_CURRENT_BINARY_DIR}/tmp/imgui_demo_code)
    file(COPY ${imgui_demo_src_folder}/imgui_demo.cpp DESTINATION ${imgui_demo_tmp_folder})
    file(COPY ${imgui_demo_src_folder}/imgui_demo.py DESTINATION ${imgui_demo_tmp_folder})

    target_link_options(demo_imgui_bundle PRIVATE "SHELL:--preload-file ${demos_cpp_folder}@/demos_cpp")
    target_link_options(demo_imgui_bundle PRIVATE "SHELL:--preload-file ${demos_python_folder}@/demos_python")
    target_link_options(demo_imgui_bundle PRIVATE "SHELL:--preload-file ${imgui_demo_tmp_folder}@code/imgui")
    set(python_backends_folder ${CMAKE_CURRENT_LIST_DIR}/../python_backends)
    target_link_options(demo_imgui_bundle PRIVATE "SHELL:--preload-file ${python_backends_folder}@/python_backends")
endif()


target_link_libraries(demo_imguizmo_launcher PRIVATE demos_imguizmo)
target_link_libraries(demo_node_editor_launcher PRIVATE demos_node_editor)
target_link_libraries(demo_tex_inspect_launcher PRIVATE demos_tex_inspect)
target_link_libraries(demo_imgui_bundle PRIVATE
    demos_cpp
    demos_imguizmo
    demos_tex_inspect
    demos_node_editor
    demo_utils
)
if (IMGUI_BUNDLE_WITH_IMMVISION)
    target_link_libraries(demo_immvision_launcher PRIVATE demos_immvision)
    target_link_libraries(demo_imgui_bundle PRIVATE demos_immvision)
endif()

FILE(COPY ../demos_assets DESTINATION ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})

if (MSVC)
    FILE(COPY msvc_note.txt DESTINATION ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})
endif()

if(EMSCRIPTEN AND HELLOIMGUI_EMSCRIPTEN_PTHREAD)
    # Needed addition for multithread support (required by ImGui Test Engine)
    # Note: see the shell.emscripten.html in this folder we are using a custom shell,
    #       that provides Cross-origin isolation (COOP and COEP) through a service worker
    #       for situations in which you can't control the headers (e.g. GitHub pages).
    #
    # coi-serviceworker.js was found at https://github.com/gzuidhof/coi-serviceworker, and manually patched:
    #    see https://github.com/gzuidhof/coi-serviceworker/issues/20
    #    and https://github.com/gzuidhof/coi-serviceworker/compare/master...tamo:coi-serviceworker:coep-ua-brand
    #
    # coi-serviceworker.js provides Cross-origin isolation (COOP and COEP) through a service worker
    # for situations in which you can't control the headers (e.g. GitHub pages).

    get_property(runtime_output_directory TARGET demo_imgui_bundle PROPERTY RUNTIME_OUTPUT_DIRECTORY)
    FILE(MAKE_DIRECTORY ${runtime_output_directory})
    FILE(COPY_FILE ${CMAKE_CURRENT_LIST_DIR}/coi-serviceworker.js ${runtime_output_directory}/coi-serviceworker.js)

    target_link_options(demo_imgui_bundle PUBLIC -sPTHREAD_POOL_SIZE=2)
endif()
