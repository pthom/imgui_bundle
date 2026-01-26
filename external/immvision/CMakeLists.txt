include(${CMAKE_CURRENT_LIST_DIR}/immvision/cmake/find_opencv.cmake)
immvision_find_opencv()
if (NOT OpenCV_FOUND)
    message(FATAL_ERROR "OpenCV was not found, cannot build immvision module")
endif()


set(IMGUI_BUNDLE_WITH_IMMVISION ON CACHE BOOL "Build with immvision" FORCE)
if (IMGUI_BUNDLE_WITH_IMMVISION)
    add_subdirectory(immvision)
endif()
