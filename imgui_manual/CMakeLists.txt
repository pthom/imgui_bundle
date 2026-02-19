# force_include: used to define IMGUI_DEMO_MARKER in demo files
function(force_include target header)
    if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        target_compile_options(${target} PUBLIC -include${header})
    elseif (CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
        target_compile_options(${target} PUBLIC /FI${header})
    else()
        message(FATAL_ERROR "Unsupported compiler: ${CMAKE_CXX_COMPILER_ID}")
    endif()
endfunction()

function(copy_code_file code_file_full_path)
    # The code files are copied to the demo_code_dest directory with a .txt extension for runtime loading as text.
    set(code_file ${code_file_full_path})
    # Extract filename and append .txt extension for runtime loading as text
    get_filename_component(code_file ${code_file_full_path} NAME)
    set(destination ${demo_code_dest}/${code_file}.txt)
    # Copy the code file to the destination
    configure_file(${code_file_full_path} ${destination} COPYONLY)
endfunction()

#
# set path variables for libraries featured in the manual (imgui, implot, implot3d and im_anim)
#
set(bundle_dir ${CMAKE_CURRENT_LIST_DIR}/..)
set(imanim_dir ${bundle_dir}/external/ImAnim/ImAnim)
set(imgui_dir ${bundle_dir}/external/imgui/imgui)
set(implot_dir ${bundle_dir}/external/implot/implot)
set(implot3d_dir ${bundle_dir}/external/implot3d/implot3d)


# Copy demo source files to assets/demo_code/ for runtime loading
set(demo_code_dest ${CMAKE_CURRENT_LIST_DIR}/assets/demo_code)
set(demos_python_dir ${bundle_dir}/bindings/imgui_bundle/demos_python/demos_imgui_manual)
file(MAKE_DIRECTORY ${demo_code_dest})

# C++ demos
copy_code_file(${imanim_dir}/im_anim_demo_basics.cpp)
copy_code_file(${imanim_dir}/im_anim_demo.cpp)
copy_code_file(${imanim_dir}/im_anim_doc.cpp)
copy_code_file(${imanim_dir}/im_anim_usecase.cpp)
copy_code_file(${imgui_dir}/imgui_demo.cpp)
copy_code_file(${implot_dir}/implot_demo.cpp)
copy_code_file(${implot3d_dir}/implot3d_demo.cpp)

# Python demos (from bindings/imgui_bundle/demos_python/demos_imgui_manual)
copy_code_file(${demos_python_dir}/im_anim_demo_basics.py)
copy_code_file(${demos_python_dir}/imgui_demo.py)
copy_code_file(${demos_python_dir}/implot_demo.py)
copy_code_file(${demos_python_dir}/implot3d_demo.py)

# API reference files: C++ headers
copy_code_file(${imgui_dir}/imgui.h)
copy_code_file(${imgui_dir}/imgui_internal.h)
copy_code_file(${implot_dir}/implot.h)
copy_code_file(${implot_dir}/implot_internal.h)
copy_code_file(${implot3d_dir}/implot3d.h)
copy_code_file(${implot3d_dir}/implot3d_internal.h)
copy_code_file(${imanim_dir}/im_anim.h)

# API reference files: Python stubs
set(stubs_dir ${bundle_dir}/bindings/imgui_bundle)
copy_code_file(${stubs_dir}/imgui/__init__.pyi)
copy_code_file(${stubs_dir}/imgui/internal.pyi)
copy_code_file(${stubs_dir}/implot/__init__.pyi)
copy_code_file(${stubs_dir}/implot/internal.pyi)
copy_code_file(${stubs_dir}/implot3d/__init__.pyi)
copy_code_file(${stubs_dir}/implot3d/internal.pyi)
copy_code_file(${stubs_dir}/im_anim.pyi)

# Force-include the marker hooks header to imgui, implot, implot3d and imanim
set(marker_hooks_header ${CMAKE_CURRENT_LIST_DIR}/imgui_demo_marker_hooks.h)
force_include(imgui ${marker_hooks_header})
force_include(implot ${marker_hooks_header})
force_include(implot3d ${marker_hooks_header})
force_include(imanim ${marker_hooks_header})

# Add library imgui_manual_lib
add_library(imgui_manual_lib
    demo_code_viewer.cpp
    demo_code_viewer.h
    imgui_demo_marker_hooks.cpp
    imgui_demo_marker_hooks.h
    imgui_manual.cpp
    imgui_manual.h
    library_config.cpp
    library_config.h
)
target_link_libraries(imgui_manual_lib PUBLIC imgui implot implot3d imanim hello_imgui imgui_color_text_edit imgui_md)
# target_link_libraries(imgui_manual_lib PUBLIC imgui_bundle)

target_link_libraries(imgui_bundle INTERFACE imgui_manual_lib)

imgui_bundle_add_app(imgui_manual imgui_manual.main.cpp)
target_link_libraries(imgui_manual PRIVATE imgui_manual_lib)

set_target_properties(imgui_manual PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# For Emscripten, change output name from imgui_manual.html to index.html
if (EMSCRIPTEN)
    set_target_properties(imgui_manual PROPERTIES OUTPUT_NAME index)
endif()

