# Add one demo application per file
ibd_add_this_folder_auto_demos("")

# Also add these demos as a library (where IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY will disable existing main() functions)
ibd_add_this_folder_as_demos_library()

# The image pipeline reads images from demos_assets, and filters them with OpenCV (without it, it shows a message).
# ImmVision does not link OpenCV: the demos that use cv::Mat define IMMVISION_HAS_OPENCV and link OpenCV themselves.
hello_imgui_bundle_assets_from_folder(demo_node_editor_image_pipeline ${IMGUI_BUNDLE_PATH}/bindings/imgui_bundle/demos_assets)
if(IMGUI_BUNDLE_WITH_IMMVISION AND IMGUI_BUNDLE_DEMOS_WITH_OPENCV)
    find_package(OpenCV REQUIRED)
    foreach(target demos_node_editor demo_node_editor_image_pipeline)
        target_compile_definitions(${target} PUBLIC IMMVISION_HAS_OPENCV)
        target_link_libraries(${target} PUBLIC opencv_core opencv_imgproc)
    endforeach()
endif()
