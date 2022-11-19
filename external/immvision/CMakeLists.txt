include(${CMAKE_CURRENT_LIST_DIR}/find_opencv_with_conan.cmake)
find_opencv_with_conan()

add_library(immvision immvision.h immvision.cpp)
target_include_directories(immvision PUBLIC ${CMAKE_CURRENT_LIST_DIR}/..)
target_link_libraries(immvision PUBLIC imgui opencv_core opencv_imgproc opencv_highgui opencv_imgcodecs)

# Set glad as OpenGl loader, found inside hello_imgui
set(hello_imgui_dir ${CMAKE_CURRENT_LIST_DIR}/../hello_imgui)
set(glad_dir ${hello_imgui_dir}/external/OpenGL_Loaders/glad)
target_compile_definitions(immvision PRIVATE IMMVISION_USE_GLAD)
target_include_directories(immvision PRIVATE ${glad_dir}/include)
