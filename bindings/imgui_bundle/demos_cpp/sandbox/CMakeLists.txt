# Make ci_scripts/dev_tools/dev_screenshot.h reachable from sandbox files
# (used by temporary `sandbox_shoot_*.cpp` programs that capture a
#  screenshot for visual validation — see ci_scripts/dev_tools/README.md).
include_directories(${IMGUI_BUNDLE_PATH}/ci_scripts/dev_tools)

ibd_add_this_folder_auto_demos("")
