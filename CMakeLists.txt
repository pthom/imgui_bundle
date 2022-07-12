cmake_minimum_required(VERSION 3.17)
project(lg_imgui_bundle VERSION "0.1.0")

include(lg_cmake_utils/lg_cmake_utils.cmake)

set(CMAKE_CXX_STANDARD 20)

add_subdirectory(external/pybind11)


####################################################
# Build hello_imgui Bound C++ library
####################################################
if (UNIX)
    add_compile_options(-fPIC)
endif()
#   i. Build static libraries
set(BUILD_SHARED_LIBS OFF)
# 1. Build imgui (lib used by hello_imgui)
set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/external/imgui)
add_imgui_target(${imgui_dir})
# 2. Build glfw (also used by hello_imgui)
add_subdirectory(external/glfw)

# 3. Configure hello-imgui with the following options:
#     i. use glfw
set(HELLOIMGUI_USE_GLFW_OPENGL3 ON CACHE BOOL "" FORCE)
#     ii. use provided imgui version
set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/external/imgui)
set(HELLOIMGUI_BUILD_IMGUI OFF CACHE BOOL "" FORCE)
set(HELLOIMGUI_IMGUI_SOURCE_DIR ${imgui_dir} CACHE STRING "" FORCE)

# 4. Finally, add hello_imgui
add_subdirectory(external/hello_imgui)

# 5. Export hello_imgui symbols on Windows without using __declspec(dllexport)
if (WIN32)
    set_target_properties(hello_imgui PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()


####################################################
# Build implot and link it into hello_imgui
####################################################
set(implot_dir ${CMAKE_CURRENT_LIST_DIR}/external/implot)
file(GLOB implot_sources ${implot_dir}/*.cpp ${implot_dir}/*.h)
add_library(implot STATIC ${implot_sources})
target_link_libraries(implot PUBLIC imgui)
target_include_directories(implot PUBLIC ${implot_dir})
lg_target_force_include(implot ${CMAKE_CURRENT_LIST_DIR}/lg_cmake_utils/lg_imgui_imconfig.h)
lg_disable_warning_exception_in_destructor(implot)

# finally link implot into hello_imgui
target_link_libraries(hello_imgui PUBLIC implot)


#########################################################################
# Build python module that provides bindings to the library hello_imgui
#########################################################################
set(bound_library hello_imgui)                 # The library for which we are building bindings
set(python_native_module_name _lg_imgui_bundle)    # This is the native python module name
set(python_wrapper_module_name lg_imgui_bundle)    # This is the python wrapper around the native module
set(python_module_sources

    bindings/module.cpp
    bindings/pybind_${bound_library}.cpp

    bindings/imgui_boxed_types.h
    bindings/imgui_docking_internal_types.h
    bindings/pybind_imgui.cpp

    bindings/pybind_implot.cpp
    )

pybind11_add_module(${python_native_module_name} ${python_module_sources})
target_compile_definitions(${python_native_module_name} PRIVATE VERSION_INFO=${PROJECT_VERSION})
lg_setup_module(
    ${bound_library}
    ${python_native_module_name}
    ${python_wrapper_module_name}
)

target_link_libraries(${python_native_module_name} PUBLIC ${bound_library})
