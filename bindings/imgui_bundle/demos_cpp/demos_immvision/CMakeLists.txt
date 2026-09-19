# Add one demo application per file
ibd_add_this_folder_auto_demos("")

# Also add these demos as a library (where IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY will disable existing main() functions)
ibd_add_this_folder_as_demos_library()

# immvision demos need images from demos_assets
set(_da ${IMGUI_BUNDLE_PATH}/bindings/imgui_bundle/demos_assets)
hello_imgui_bundle_assets_from_folder(demo_immvision_display ${_da})
hello_imgui_bundle_assets_from_folder(demo_immvision_inspector ${_da})
hello_imgui_bundle_assets_from_folder(demo_immvision_process ${_da})
hello_imgui_bundle_assets_from_folder(demo_immvision_link ${_da})

# Some immvision demos use OpenCV for advanced image processing (Sobel, blur, etc.)
# These parts are guarded behind #ifdef IMMVISION_HAS_OPENCV in the source.
# ImmVision does not link OpenCV: like any application that wants cv::Mat interop,
# the demos define IMMVISION_HAS_OPENCV and link OpenCV themselves.
if(IMGUI_BUNDLE_DEMOS_WITH_OPENCV)
    find_package(OpenCV QUIET)
    if(NOT OpenCV_FOUND)
        message(FATAL_ERROR "IMGUI_BUNDLE_DEMOS_WITH_OPENCV requires OpenCV: install it, set OpenCV_DIR, or pass -DIMMVISION_FETCH_OPENCV=ON")
    endif()
    foreach(target demos_immvision demo_immvision_process demo_immvision_inspector)
        target_compile_definitions(${target} PUBLIC IMMVISION_HAS_OPENCV)
        target_link_libraries(${target} PUBLIC opencv_core opencv_imgproc)
    endforeach()
endif()
