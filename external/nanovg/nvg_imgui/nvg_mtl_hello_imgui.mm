#if defined(IMGUI_BUNDLE_WITH_NANOVG) && defined(HELLOIMGUI_HAS_METAL)
#include "nvg_imgui.h"

#include "nanovg.h"
#include "nanovg_mtl.h"
#include "hello_imgui/internal/backend_impls/rendering_metal.h"


namespace NvgHelloImGui
{
    NVGcontext* CreateNvgContext_Mtl_HelloImGui(int flags)
    {
        return nvgCreateMTL(HelloImGui::GetMetalGlobals().caMetalLayer, flags);
    }

    void DeleteNvgContext_Mtl_HelloImGui(NVGcontext* vg)
    {
        nvgDeleteMTL(vg);
    }
}

#endif // #if defined(IMGUI_BUNDLE_WITH_NANOVG) && defined(HELLOIMGUI_HAS_METAL)
