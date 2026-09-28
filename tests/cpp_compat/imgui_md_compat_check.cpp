// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
//
// A compatibility check: code written for the markdown API of v1.92.900 (imgui_md_wrapper.h, namespace ImGuiMd)
// must still compile and link. The library is now imgui_rich_md (namespace RichMd). The former API is only
// referenced here: this program renders nothing. Built by `just test_cpp_compat` (see CMakeLists.txt).
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include <cstdio>

// Uses each name of v1.92.900's ImGuiMd, as its users wrote them
static void UseTheFormerApi()
{
    ImGuiMd::MarkdownOptions options;
    options.fontOptions.fontBasePath = "fonts/Roboto/Roboto";
    options.fontOptions.regularSize = 16.f;
    options.fontOptions.headerSizeFactors[0] = 1.42f;
    options.withLatex = false;
    options.autolinks = true;

    ImGuiMd::StringFunction onOpenLink = ImGuiMd::OnOpenLink_Default;
    ImGuiMd::MarkdownImageFunction onImage = ImGuiMd::OnImage_Default;
    ImGuiMd::HtmlDivFunction onHtmlDiv = [](const std::string&, bool) {};
    ImGuiMd::HtmlSpanFunction onHtmlSpan = [](const std::string&, bool) { return false; };
    ImGuiMd::MarkdownDownloadFunction onDownloadData = [](const std::string&) {
        ImGuiMd::MarkdownDownloadResult result;
        result.status = ImGuiMd::MarkdownDownloadStatus::Ready;
        result.FillFromData("x", 1);
        result.errorMessage = "";
        return result;
    };
    options.callbacks.OnOpenLink = onOpenLink;
    options.callbacks.OnImage = onImage;
    options.callbacks.OnHtmlDiv = onHtmlDiv;
    options.callbacks.OnHtmlSpan = onHtmlSpan;
    options.callbacks.OnDownloadData = onDownloadData;

    ImGuiMd::InitializeMarkdown(options);
    ImGuiMd::VoidFunction fontLoader = ImGuiMd::GetFontLoaderFunction();
    fontLoader();
    ImGuiMd::Render("# Title\n*emphasis*");
    ImGuiMd::RenderUnindented("    **indented**");
    ImGuiMd::SizedFont codeFont = ImGuiMd::GetCodeFont();
    ImGuiMd::SizedFont headerFont = ImGuiMd::GetFont(ImGuiMd::MarkdownFontSpec(false, true, 1));
    ImVec4 linkColor = ImGuiMd::LinkColor();
    ImGuiMd::RenderTextAsLink("Dear ImGui Bundle", "https://github.com/pthom/imgui_bundle");

    std::optional<ImGuiMd::MarkdownImage> image = ImGuiMd::OnImage_Default("images/world.png");
    if (image)
        std::printf("%p %f %f %f %f\n", (void*)image->texture_id, image->size.x, image->uv0.x, image->uv1.x,
                    image->col_tint.x + image->col_border.x);
    std::printf("%p %f %p %f %f\n", (void*)codeFont.font, codeFont.size, (void*)headerFont.font, headerFont.size,
                linkColor.x);
    ImGuiMd::DeInitializeMarkdown();
}

int main(int argc, char**)
{
    if (argc > 1000)  // never true: the former API has to compile and link, not to run
        UseTheFormerApi();
    std::printf("imgui_md_compat_check: the markdown API of v1.92.900 compiles and links\n");
    return 0;
}
