#pragma once

#include "imgui.h"

#include <functional>
#include <vector>
#include <string>
#include <memory>
#include <optional>


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

    std::optional<MarkdownImage> OnImage_Default(const std::string& image_path);
    void OnOpenLink_Default(const std::string& url);


    struct MarkdownCallbacks
    {
        // The default version will open the link in a browser iif it starts with "http"
        std::function<void(const std::string&)> OnOpenLink = OnOpenLink_Default;

        // The default version will load the image as a cached texture and display it
        std::function<std::optional<MarkdownImage>(const std::string&)> OnImage = OnImage_Default;

        // OnHtmlDiv does nothing by default, by you could write:
        //     In  C++:
        //        markdownOptions.callbacks.openingDiv = [](const std::string& divClass, bool openingDiv)
        //        {
        //            if (divClass == "red")
        //            {
        //                if (e)
        //                    ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(255, 0, 0, 255));
        //                else
        //                    ImGui::PopStyleColor();
        //            }
        //        };
        std::function<void(const std::string& divClass, bool openingDiv)> OnHtmlDiv;
    };


    struct MarkdownOptions
    {
        MarkdownFontOptions fontOptions;
        MarkdownCallbacks callbacks;
    };

    // InitializeMarkdown: Call this once at application startup
    void InitializeMarkdown(const MarkdownOptions& options);

    // GetFontLoaderFunction() will return a function that you should call during ImGui initialization.
    // If using HelloImGui, then simply add this:
    //     For C++:
    //         runnerParams.callbacks.LoadAdditionalFonts = ImGuiMd::GetFontLoaderFunction()
    //     For Python:
    //         runnerParams.callbacks.load_additional_fonts = ImGuiMd::get_font_loader_function()
    std::function<void(void)> GetFontLoaderFunction();

    void Render(const std::string& markdownString);

}
