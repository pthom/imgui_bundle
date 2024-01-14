#pragma once
#ifdef IMGUI_BUNDLE_WITH_NANOVG
#include "nanovg.h"


namespace NvgHelloImGui
{
    NVGcontext* CreateNvgContext_Mtl_HelloImGui(int flags);
    void DeleteNvgContext_Mtl_HelloImGui(NVGcontext* vg);
}

#endif // #ifdef IMGUI_BUNDLE_WITH_NANOVG
