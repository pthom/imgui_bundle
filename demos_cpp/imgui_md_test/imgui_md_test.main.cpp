#include "hello_imgui/hello_imgui.h"
# include <imgui.h>
#include "imgui_md_wrapper.h"


//HelloImgGui::CallLoadFont(VoidFunction);

void gui()
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
    //markdownRenderer.Render(m);

    ImGuiMd::Render(m);
}


int main(int , char *[])
{
    ImGuiMd::MarkdownOptions markdownOptions;
    ImGuiMd::InitializeMarkdown(markdownOptions);

    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.LoadAdditionalFonts = ImGuiMd::GetFontLoaderFunction();
    runnerParams.callbacks.ShowGui = [&]() {
        gui();
    };

    HelloImGui::Run(runnerParams);
    return 0;
}
