// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// The explorer's page, for the intro's "Show me" automations (which drive it)
#pragma once
#include "hello_imgui/runner_params.h"
#include "immapp/immapp.h"
#include <utility>

class DemoLauncher;

// The explorer's parameters, apart from its run (a test can drive the page)
std::pair<HelloImGui::RunnerParams, ImmApp::AddOnsParams> ExplorerParams();

namespace BundleExplorer
{
    extern const char* WELCOME_LABEL;  // the switch of the header: two chips
    extern const char* DEMOS_LABEL;
    bool OnDemos();            // the page shows the demos (or is going there)
    DemoLauncher* Launcher();  // nullptr when the explorer is not running (a demo alone)
}
