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
