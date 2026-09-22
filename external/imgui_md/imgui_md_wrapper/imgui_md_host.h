// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
#pragma once
// Host services: what the markdown renderer needs from the application or the framework
// that hosts it (GPU textures, asset files, logging). Every service is optional and has a
// plain default; a host (e.g. ImGui Bundle with HelloImGui) installs richer ones with
// SetHostServices() before InitializeMarkdown(). Not part of the Python API.

#include "imgui.h"

#include <cstdint>
#include <functional>
#include <memory>
#include <optional>
#include <string>
#include <vector>


namespace ImGuiMd
{
    // A GPU texture owned by the markdown caches (images, LaTeX).
    // keepAlive owns the GPU resource: the texture is freed when the last copy is dropped
    // (e.g. when the caches are cleared by DeInitializeMarkdown).
    struct MarkdownTexture
    {
        ImTextureID id = ImTextureID(0);
        ImVec2 size = ImVec2(0.f, 0.f);
        std::shared_ptr<void> keepAlive;

        bool Valid() const { return id != ImTextureID(0); }
    };

    struct HostServices
    {
        // Uploads an RGBA8 buffer (w * h * 4 bytes, no padding) to a GPU texture.
        // Return an invalid MarkdownTexture on failure. If empty, images and LaTeX are skipped.
        std::function<MarkdownTexture(const unsigned char* rgba, int w, int h)> UploadRgba;

        // Reads an asset file (fonts, images: "fonts/Roboto/Roboto-Regular.ttf", "images/x.png").
        // Return std::nullopt when the asset does not exist. Default: the file system.
        std::function<std::optional<std::vector<uint8_t>>(const std::string& assetPath)> ReadAsset;

        // Path of an asset on the file system, for the libraries that cannot read from memory
        // (MicroTeX's fonts). Return std::nullopt when the asset does not exist. Default: the file system.
        std::function<std::optional<std::string>(const std::string& assetPath)> AssetFilePath;

        // Fonts merged into every markdown font (in addition to MarkdownFontOptions::mergeFonts),
        // e.g. the host's icon font. Evaluated when the fonts are loaded. Default: none.
        std::function<std::vector<std::string>()> DefaultMergeFonts;

        // Logs a warning. Default: stderr.
        std::function<void(const std::string& message)> Log;
    };

    // Sets the host services (call before InitializeMarkdown). Empty fields keep their default.
    void SetHostServices(const HostServices& services);
    const HostServices& GetHostServices();
}
