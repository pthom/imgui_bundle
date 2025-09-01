// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#pragma once

#include "imgui.h"

#include <functional>
#include <vector>
#include <string>
#include <memory>
#include <optional>
#include <array>


namespace ImGuiMd
{
    struct MarkdownFontOptions
    {
        std::string fontBasePath = "fonts/Roboto/Roboto";
        // This size is in density-independent pixels
        float regularSize = 16.f;

        // Multipliers for header sizes, from h1 to h6
        float headerSizeFactors[6] = { 1.42f, 1.33f, 1.24f, 1.15f, 1.10f, 1.05f };
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

    // Note: Since v1.92, Fonts can be displayed at any size:
    // in order to display a font at a given size, we need to call
    //   ImGui::PushFont(font, size) (or call separately ImGui::PushFontSize)
    struct SizedFont
    {
        ImFont* font;
        float size;
    };

    using VoidFunction = std::function<void(void)>;
    using StringFunction = std::function<void(std::string)>;
    using HtmlDivFunction = std::function<void(const std::string& divClass, bool openingDiv)>;
    using MarkdownImageFunction = std::function<std::optional<MarkdownImage>(const std::string&)>;


    std::optional<MarkdownImage> OnImage_Default(const std::string& image_path);
    void OnOpenLink_Default(const std::string& url);


    struct MarkdownCallbacks
    {
        // The default version will open the link in a browser iif it starts with "http"
        StringFunction OnOpenLink = OnOpenLink_Default;

        // The default version will load the image as a cached texture and display it
        MarkdownImageFunction OnImage = OnImage_Default;

        // OnHtmlDiv does nothing by default, by you could write:
        //     In  C++:
        //        markdownOptions.callbacks.onHtmlDiv = [](const std::string& divClass, bool openingDiv)
        //        {
        //            if (divClass == "red")
        //            {
        //                if (openingDiv)
        //                    ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(255, 0, 0, 255));
        //                else
        //                    ImGui::PopStyleColor();
        //            }
        //        };
        //     In  Python:
        //        def on_html_div(div_class: str, opening_div: bool) -> None:
        //            if div_class == 'red':
        //                if opening_div:
        //                    imgui.push_style_color(imgui.Col_.text.value, imgui.ImColor(255, 0, 0, 255).value)
        //                else:
        //                    imgui.pop_style_color()
        //        md_options = imgui_md.MarkdownOptions()
        //        md_options.callbacks.on_html_div = on_html_div
        //        immapp.run(
        //            gui_function=gui, with_markdown_options=md_options #, more options here
        //        )
        HtmlDivFunction OnHtmlDiv;
    };


    struct MarkdownOptions
    {
        MarkdownFontOptions fontOptions;
        MarkdownCallbacks callbacks;
    };

    // InitializeMarkdown: Call this once at application startup
    // Don't forget to later call GetFontLoaderFunction(): it will return a function that you should call
    // during ImGui initialization (and before rendering the first frame, since it will load the fonts)
    //
    // If using HelloImGui, the code would look like:
    //     Python:
    //        runner_params = hello_imgui.RunnerParams()
    //
    //        ... // Fill runner_params callbacks
    //
    //        # Initialize markdown and ask HelloImGui to load the required fonts
    //        imgui_md.initialize_markdown()
    //        runner_params.callbacks.load_additional_fonts = imgui_md.get_font_loader_function()
    //
    //        hello_imgui.run(runner_params)
    void InitializeMarkdown(const MarkdownOptions& options = MarkdownOptions());
    void DeInitializeMarkdown();

    // GetFontLoaderFunction() will return a function that you should call during ImGui initialization.
    VoidFunction GetFontLoaderFunction();

    // Renders a markdown string
    void Render(const std::string& markdownString);

    // Renders a markdown string (after having unindented its main indentation)
    void RenderUnindented(const std::string& markdownString);

    SizedFont GetCodeFont();

    struct MarkdownFontSpec
    {
        bool italic = false;
        bool bold = false;
        int headerLevel = 0;  // 0 means no header, 1 means h1, 2 means h2, etc.

        MarkdownFontSpec(bool italic_ = false, bool bold_ = false, int headerLevel_ = 0) :
            italic(italic_), bold(bold_), headerLevel(headerLevel_) {}
    };
    SizedFont GetFont(const MarkdownFontSpec& fontSpec);
}
