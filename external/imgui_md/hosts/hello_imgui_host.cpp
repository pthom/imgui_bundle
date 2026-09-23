// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// Host services for ImGui Bundle: assets, textures and logging through HelloImGui.
// Compiled into imgui_md only in the bundle (IMGUI_RICHMD_HOST_HELLO_IMGUI); installed by
// InitializeMarkdown for the fields the application did not set.
#include "imgui_rich_md/imgui_md_host.h"

#include "hello_imgui/hello_imgui.h"

namespace ImGuiMd
{
    // Backends with ImGuiBackendFlags_RendererHasTextures (all of HelloImGui's since Dear ImGui 1.92) get the
    // default upload (an ImTextureData registered with Dear ImGui); HelloImGui's TextureGpu is the fallback.
    static MarkdownTexture _UploadRgba(const unsigned char* rgba, int w, int h)
    {
        if (ImGui::GetIO().BackendFlags & ImGuiBackendFlags_RendererHasTextures)
            return UploadRgbaDefault(rgba, w, h);
        MarkdownTexture tex;
        auto gpu = HelloImGui::CreateTextureGpuFromRgbaData(rgba, w, h);
        if (gpu)
        {
            tex.ref = ImTextureRef(gpu->TextureID());
            tex.size = ImVec2((float)w, (float)h);
            tex.keepAlive = gpu;  // shared_ptr<TextureGpu> -> shared_ptr<void>
        }
        return tex;
    }

    static AssetBytes _ReadAsset(const std::string& assetPath)
    {
        if (!HelloImGui::AssetExists(assetPath))
            return ReadAssetDefault(assetPath);  // embedded assets, if any
        HelloImGui::AssetFileData fileData = HelloImGui::LoadAssetFileData(assetPath.c_str());
        std::vector<uint8_t> bytes((const uint8_t*)fileData.data, (const uint8_t*)fileData.data + fileData.dataSize);
        HelloImGui::FreeAssetFileData(&fileData);
        return bytes;
    }

    // The icon font of the application (FontAwesome 4 or 6), known once the runner is up
    static std::vector<std::string> _DefaultMergeFonts()
    {
        std::string iconFont = "fonts/fontawesome-webfont.ttf";
        if (HelloImGui::IsUsingHelloImGui())
            if (HelloImGui::GetRunnerParams()->callbacks.defaultIconFont == HelloImGui::DefaultIconFont::FontAwesome6)
                iconFont = "fonts/Font_Awesome_6_Free-Solid-900.otf";
        return {iconFont};
    }

    static void _Log(const std::string& message)
    {
        HelloImGui::Log(HelloImGui::LogLevel::Warning, "%s", message.c_str());
    }

    void Priv_InstallHelloImGuiHost()
    {
        HostServices services = GetHostServices();
        if (!services.UploadRgba)
            services.UploadRgba = _UploadRgba;
        if (!services.ReadAsset)
            services.ReadAsset = _ReadAsset;
        if (!services.DefaultMergeFonts)
            services.DefaultMergeFonts = _DefaultMergeFonts;
        if (!services.Log)
            services.Log = _Log;
        SetHostServices(services);
    }
}
