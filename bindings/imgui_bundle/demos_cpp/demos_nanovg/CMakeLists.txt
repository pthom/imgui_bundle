# Add one demo application per file
add_this_folder_auto_demos()

# Also add these demos as a library (where IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY will disable existing main() functions)
add_this_folder_as_demos_library()

target_sources(demo_nanovg_full PRIVATE demo_nanovg_full/demo_nanovg_full_impl.cpp demo_nanovg_full/demo_nanovg_full_impl.h)
