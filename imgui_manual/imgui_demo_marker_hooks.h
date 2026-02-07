// Copied from imgui repo : https://github.com/pthom/imgui/blob/DemoCodeDockingSplit/imgui_demo_marker_hooks.h
// (pthom fork, branch DemoCodeDockingSplit)

// Helper to wire demo markers located in code to an interactive browser
typedef void (*ImGuiDemoMarkerHook)(const char* file, int line, const char* section);
extern ImGuiDemoMarkerHook      GImGuiDemoMarkerHook;

// Show controls for the demo markers (checkbox, line number, etc.)
void DemoMarker_ShowShortInfo();

// Internal marker callback handling: set line info number, may call the callback
void DemoMarker_HandleCallback(const char* file, int line, const char* section);

// The macro uses __FILE__ directly; path is stripped at runtime in the handler.
// This allows demo files to be standalone (just use #ifndef IMGUI_DEMO_MARKER guard).
#define IMGUI_DEMO_MARKER(section)  do { DemoMarker_HandleCallback(__FILE__, __LINE__, section); } while (0)
#define IMGUI_DEMO_MARKER_SHOW_SHORT_INFO() DemoMarker_ShowShortInfo()
