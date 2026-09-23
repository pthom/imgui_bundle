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


namespace RichMd
{
    // A GPU texture owned by the markdown caches (images, LaTeX).
    // keepAlive owns the GPU resource: the texture is freed when the last copy is dropped
    // (e.g. when the caches are cleared by DeInitializeMarkdown).
    struct MarkdownTexture
    {
        ImTextureRef ref;                // a backend id, or an ImTextureData the backend creates at the next frame
        ImVec2 size = ImVec2(0.f, 0.f);
        std::shared_ptr<void> keepAlive; // releases the GPU texture with the last copy

        bool Valid() const { return ref._TexData != nullptr || ref._TexID != ImTextureID_Invalid; }
    };

    // A formula rendered to pixels (see HostServices::RenderLatex)
    struct LatexBitmap
    {
        std::vector<uint8_t> rgba;   // width * height * 4 bytes
        int width = 0, height = 0;
        int baselineY = 0;           // from the top of the bitmap to the text baseline, in pixels
        std::string error;           // set (with no pixels) when the formula is invalid: the source is shown with this message
    };

    // The default UploadRgba: an ImTextureData registered with Dear ImGui, created by the rendering backend at
    // the next frame (backends with ImGuiBackendFlags_RendererHasTextures, Dear ImGui 1.92+; an invalid
    // texture otherwise). A host may call it from its own UploadRgba.
    MarkdownTexture UploadRgbaDefault(const unsigned char* rgba, int w, int h);

    // The content of an asset file, or std::nullopt when it does not exist
    using AssetBytes = std::optional<std::vector<uint8_t>>;

    // An asset embedded in the binary (IMGUI_RICHMD_EMBED_ASSETS, see cmake/imgui_richmd_embed_files.cmake)
    struct EmbeddedAsset
    {
        const char* path;
        const unsigned char* data;   // a gzip stream of the file
        size_t size;                 // of the file
        size_t compressedSize;       // of data
    };

    // The default ReadAsset: the embedded assets, then the file system under the assets folder
    AssetBytes ReadAssetDefault(const std::string& assetPath);

    struct HostServices
    {
        // Uploads an RGBA8 buffer (w * h * 4 bytes, no padding) to a GPU texture.
        // Return an invalid MarkdownTexture on failure. If empty, images and LaTeX are skipped.
        std::function<MarkdownTexture(const unsigned char* rgba, int w, int h)> UploadRgba;

        // Reads an asset file (fonts, images: "fonts/Roboto/Roboto-Regular.ttf", "images/x.png").
        // Return std::nullopt when the asset does not exist. Default: the file system.
        std::function<AssetBytes(const std::string& assetPath)> ReadAsset;

        // Fonts merged into every markdown font (in addition to MarkdownFontOptions::mergeFonts),
        // e.g. the host's icon font. Evaluated when the fonts are loaded. Default: none.
        std::function<std::vector<std::string>()> DefaultMergeFonts;

        // Renders a code block (fenced or indented). Default: a read-only editor with syntax highlighting
        // when built with IMGUI_RICHMD_WITH_CODE_EDITOR, else monospaced text in a frame, with a copy button.
        std::function<void(const std::string& code, const std::string& language)> RenderCodeBlock;

        // Renders a LaTeX formula (without its $ delimiters) to an RGBA bitmap. fontSizePx is in physical
        // pixels; displayStyle is true for $$...$$. Return std::nullopt when LaTeX is not available, or a
        // bitmap with only `error` set when the formula is invalid: the formula's source is shown instead.
        // Default: MicroTeX when built with IMGUI_RICHMD_WITH_LATEX, else none.
        std::function<std::optional<LatexBitmap>(const std::string& latex, float fontSizePx, ImU32 color, bool displayStyle)> RenderLatex;

        // Logs a warning. Default: stderr.
        std::function<void(const std::string& message)> Log;
    };

    // Sets the host services (call before InitializeMarkdown). Empty fields keep their default.
    void SetHostServices(const HostServices& services);
    const HostServices& GetHostServices();
}
