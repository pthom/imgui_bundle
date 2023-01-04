// This file is automatically compiled into demos that are reference via cmake function add_auto_demo()

#include "immapp/immapp.h"
#include "demo_utils/api_demos.h"


void DemoGui();


int main()
{
    HelloImGui::SetAssetsFolder(DemosAssetsFolder());
    ImmApp::RunWithMarkdown(DemoGui, "Demo", false, false, {1000, 800});
}
