# Add one demo application per file
ibd_add_this_folder_auto_demos("")

# Also add these demos as a library (where IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY will disable existing main() functions)
ibd_add_this_folder_as_demos_library()

target_sources(demo_nanovg_full PRIVATE demo_nanovg_full/demo_nanovg_full_impl.cpp demo_nanovg_full/demo_nanovg_full_impl.h)

# nanovg demos need images/fonts from demos_assets
set(_da ${IMGUI_BUNDLE_PATH}/bindings/imgui_bundle/demos_assets)
hello_imgui_bundle_assets_from_folder(demo_nanovg_full ${_da})
hello_imgui_bundle_assets_from_folder(demo_nanovg_heart ${_da})
