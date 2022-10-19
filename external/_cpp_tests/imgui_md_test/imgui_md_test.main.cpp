#include "hello_imgui/hello_imgui.h"
# include <imgui.h>
#include "imgui_md_wrapper.h"


//HelloImgGui::CallLoadFont(VoidFunction);

void gui(ImGuiMd::MarkdownRenderer& markdownRenderer)
{
    ImGui::Text("Hello");
    ImGui::Button("Truc");

//    static MarkdownFontOptions markdownFontOptions;
//    // Cannot modify a locked ImFontAtlas between NewFrame() and EndFrame/Render()
//    static std::unique_ptr<MarkdownRenderer> markdownRenderer;
//
//    if (! markdownRenderer)
//    {
//        params.callbacks.LoadAdditionalFonts = [&](){
//            markdownRenderer = std::make_unique<MarkdownRenderer>(markdownFontOptions);
//        };
//        return;
//    }

    ImGui::Text("Hello");

    std::string m = R"md(
# Title 1
This is some text *italic* **bold**

## Title 2

### Title 3

# Table

Name &nbsp; &nbsp; &nbsp; &nbsp; | Multiline &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;<br>header  | [Link&nbsp;](#link1)
:------|:-------------------|:--
Value-One | Long <br>explanation <br>with \<br\>\'s|1
~~Value-Two~~ | __text auto wrapped__\: long explanation here |25 37 43 56 78 90
**etc** | [~~Some **link**~~](https://github.com/mekhontsev/imgui_md)|3

![Alt text](world.jpg "a title")
)md";
    markdownRenderer.Render(m);
}


int main(int , char *[])
{
    ImGuiMd::MarkdownFontOptions markdownFontOptions;
     std::unique_ptr<ImGuiMd::MarkdownRenderer> markdownRenderer;

    HelloImGui::overrideAssetsFolder(
        "/Users/pascal/dvp/OpenSource/ImGuiWork/litgen/demos/litgen/imgui_bundle/external/_cpp_tests/imgui_md_test/assets");

    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.LoadAdditionalFonts = [&]() {
        markdownRenderer = std::make_unique<ImGuiMd::MarkdownRenderer>(markdownFontOptions);
    };
    runnerParams.callbacks.ShowGui = [&]() {
        gui(*markdownRenderer);
    };

    HelloImGui::Run(runnerParams);
    return 0;
}
