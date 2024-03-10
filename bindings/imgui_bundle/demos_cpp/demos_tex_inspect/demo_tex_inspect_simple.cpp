// Demo imgui_tex_inspect
// See equivalent python program: bindings/imgui_bundle/demos/demos_tex_inspect/demo_tex_inspect.py
#include "immapp/immapp.h"
#ifdef IMGUI_BUNDLE_WITH_TEXT_INSPECT
#include "imgui_tex_inspect/imgui_tex_inspect.h"


void demo_tex_inspect_simple()
{
    static ImTextureID textureId = 0;
    static ImVec2 textureSize(512.f, 512.f);
    if (textureId == 0)
        textureId = HelloImGui::ImTextureIdFromAsset("images/bear_transparent.png");

    ImGui::Text("Simple Demo");
    ImGuiTexInspect::InspectorFlags  flags = 0;
    ImGuiTexInspect::SizeIncludingBorder inspectorSize(ImmApp::EmToVec2(40.f, 40.f));

    if (ImGuiTexInspect::BeginInspectorPanel(
        "Texture inspector",
        textureId,
        textureSize, flags,
        inspectorSize))
    {
        // nothing to do here
    }
    ImGuiTexInspect::EndInspectorPanel(); // Should be called even if BeginInspectorPanel returns false
}


#include "demo_utils/api_demos.h"
// A main() is provided automatically bu demos_cpp/_auto_main/
// However, the version below is left as a documentation reference,
// since imgui_tex_inspect requires to be initialized at startup
int disabled_main()
{
    HelloImGui::SetAssetsFolder(DemosAssetsFolder());

    ImmApp::Run(
        HelloImGui::SimpleRunnerParams {
            .guiFunction=demo_tex_inspect_simple,
            .windowTitle = "demo_tex_inspect_simple",
            .windowSize = {1000, 800}
        },
        ImmApp::AddOnsParams {
            .withTexInspect = true
        }
    );
    return 0;
}

#else // #ifdef IMGUI_BUNDLE_WITH_TEXT_INSPECT
void demo_tex_inspect_simple()
{
    ImGui::Text("This demo requires IMGUI_BUNDLE_WITH_TEXT_INSPECT to be enabled");
}
#endif