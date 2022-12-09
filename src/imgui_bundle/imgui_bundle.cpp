#include "imgui_bundle/imgui_bundle.h"
#include "imgui_tex_inspect/imgui_tex_inspect.h"
#include "imgui_tex_inspect/imgui_tex_inspect_demo.h"
#include "hello_imgui/hello_imgui.h"

#include <string>


namespace ImGuiTexInspect
{
    Texture LoadTexture(const char * path)
    {
        auto textureId = HelloImGui::ImTextureIdFromAsset(path);
        Texture r;
        r.size = ImVec2(512.f, 512.f); // This function is only by used the demo, which uses a 51x512 image
        r.texture = textureId;
        return r;
    }
}
