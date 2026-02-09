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
set(demos_python_dir ${bundle_dir}/bindings/imgui_bundle/demos_python)
file(MAKE_DIRECTORY ${demo_code_dest})

# C++ demos
configure_file(${imanim_dir}/im_anim_demo_basics.cpp ${demo_code_dest}/im_anim_demo_basics.cpp.txt COPYONLY)
configure_file(${imanim_dir}/im_anim_demo.cpp ${demo_code_dest}/im_anim_demo.cpp.txt COPYONLY)
configure_file(${imanim_dir}/im_anim_doc.cpp ${demo_code_dest}/im_anim_doc.cpp.txt COPYONLY)
configure_file(${imanim_dir}/im_anim_usecase.cpp ${demo_code_dest}/im_anim_usecase.cpp.txt COPYONLY)
configure_file(${imgui_dir}/imgui_demo.cpp ${demo_code_dest}/imgui_demo.cpp.txt COPYONLY)
configure_file(${implot_dir}/implot_demo.cpp ${demo_code_dest}/implot_demo.cpp.txt COPYONLY)
configure_file(${implot3d_dir}/implot3d_demo.cpp ${demo_code_dest}/implot3d_demo.cpp.txt COPYONLY)

# Python demos (from bindings/imgui_bundle/demos_python/)
configure_file(${demos_python_dir}/demos_imanim/im_anim_demo_basics.py ${demo_code_dest}/im_anim_demo_basics.py.txt COPYONLY)
configure_file(${demos_python_dir}/demos_immapp/imgui_demo.py ${demo_code_dest}/imgui_demo.py.txt COPYONLY)
configure_file(${demos_python_dir}/demos_implot/implot_demo.py ${demo_code_dest}/implot_demo.py.txt COPYONLY)
configure_file(${demos_python_dir}/demos_implot3d/implot3d_demo.py ${demo_code_dest}/implot3d_demo.py.txt COPYONLY)

# API reference files: C++ headers
configure_file(${imgui_dir}/imgui.h ${demo_code_dest}/imgui.h.txt COPYONLY)
configure_file(${imgui_dir}/imgui_internal.h ${demo_code_dest}/imgui_internal.h.txt COPYONLY)
configure_file(${implot_dir}/implot.h ${demo_code_dest}/implot.h.txt COPYONLY)
configure_file(${implot_dir}/implot_internal.h ${demo_code_dest}/implot_internal.h.txt COPYONLY)
configure_file(${implot3d_dir}/implot3d.h ${demo_code_dest}/implot3d.h.txt COPYONLY)
configure_file(${implot3d_dir}/implot3d_internal.h ${demo_code_dest}/implot3d_internal.h.txt COPYONLY)
configure_file(${imanim_dir}/im_anim.h ${demo_code_dest}/im_anim.h.txt COPYONLY)

# API reference files: Python stubs
set(stubs_dir ${bundle_dir}/bindings/imgui_bundle)
configure_file(${stubs_dir}/imgui/__init__.pyi ${demo_code_dest}/imgui.pyi.txt COPYONLY)
configure_file(${stubs_dir}/imgui/internal.pyi ${demo_code_dest}/imgui_internal.pyi.txt COPYONLY)
configure_file(${stubs_dir}/implot/__init__.pyi ${demo_code_dest}/implot.pyi.txt COPYONLY)
configure_file(${stubs_dir}/implot/internal.pyi ${demo_code_dest}/implot_internal.pyi.txt COPYONLY)
configure_file(${stubs_dir}/implot3d/__init__.pyi ${demo_code_dest}/implot3d.pyi.txt COPYONLY)
configure_file(${stubs_dir}/implot3d/internal.pyi ${demo_code_dest}/implot3d_internal.pyi.txt COPYONLY)
configure_file(${stubs_dir}/im_anim.pyi ${demo_code_dest}/im_anim.pyi.txt COPYONLY)


# Force use Glfw (using pongasoft/emscripten-glfw) on emscripten, which has a good support for the clipboard
#set(HELLOIMGUI_USE_GLFW3 ON CACHE BOOL "" FORCE)
#set(HELLOIMGUI_HAS_OPENGL3 ON CACHE BOOL "" FORCE)


# Force-include the marker hooks header to imgui, implot, implot3d and imanim
set(marker_hooks_header ${CMAKE_CURRENT_LIST_DIR}/imgui_demo_marker_hooks.h)
force_include(imgui ${marker_hooks_header})
force_include(implot ${marker_hooks_header})
force_include(implot3d ${marker_hooks_header})
force_include(imanim ${marker_hooks_header})

# Add library imgui_manual_lib
add_library(imgui_manual_lib
    demo_code_viewer.cpp
    imgui_demo_marker_hooks.cpp
    library_config.cpp
)
target_link_libraries(imgui_manual_lib PUBLIC imgui implot implot3d imanim hello_imgui imgui_color_text_edit imgui_md)
# target_link_libraries(imgui_manual_lib PUBLIC imgui_bundle)

target_link_libraries(imgui_bundle INTERFACE imgui_manual_lib)

imgui_bundle_add_app(imgui_manual imgui_manual.main.cpp)
target_link_libraries(imgui_manual PRIVATE imgui_manual_lib)
