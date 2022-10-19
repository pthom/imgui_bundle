#pragma once

#include "imgui.h"

#include <functional>
#include <vector>
#include <string>
#include <memory>


namespace ImGuiMd
{
    struct MarkdownFontOptions
    {
        std::string fontBasePath = "fonts/Roboto/Roboto";
        int maxHeaderLevel = 3;
        float sizeDiffBetweenLevels = 3.f;
        float regularSize = 14.f;
    };


    struct MarkdownImage
    {
        ImTextureID	texture_id;
        ImVec2	size;
        ImVec2	uv0;
        ImVec2	uv1;
        ImVec4	col_tint;
        ImVec4	col_border;
    };


    struct MarkdownCallbacks
    {
        std::function<void(const std::string&)> OnOpenLink;
        std::function<MarkdownImage(const std::string&)> OnImage;
    };

    

    //std::function<void(void)> Markd

    ///////////////////////////////////////////
    class MarkdownRendererPImpl;


    class MarkdownRenderer
    {
    public:
        MarkdownRenderer(const MarkdownFontOptions& options);
        ~MarkdownRenderer();

        void Render(const std::string& markdownString);


        std::function<void(const std::string&)> OnOpenLink; // TODO: make this customizable

    private:
        std::unique_ptr<MarkdownRendererPImpl> mImpl;
    };
}


