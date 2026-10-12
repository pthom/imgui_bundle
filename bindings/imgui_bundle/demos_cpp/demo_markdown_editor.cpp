// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// Markdown editor: the source and its live preview.
// A markdown editor in a few lines: ImGuiColorTextEdit edits the source, rich_md previews it as you type. On a narrow
// screen (a phone), two tabs show one of them at a time.
#include "ImGuiColorTextEdit/TextEditor.h"
#include "demo_utils/api_demos.h"
#include "hello_imgui/hello_imgui.h"
#include "imgui_rich_md/rich_md.h"
#include "immapp/immapp.h"

#include <string>

namespace
{
    // Below this width (in em), one panel at a time
    constexpr float kNarrowWidthEm = 50.f;

    const char* kSample = R"md(# A markdown editor

Edit this text: the preview follows as you type.

The editor is [ImGuiColorTextEdit](https://github.com/goossens/ImGuiColorTextEdit), with its markdown colors. The preview is [rich_md](https://github.com/pthom/imgui_rich_md). Both are Dear ImGui widgets: no browser, no HTML engine.

## Text

*Emphasis*, **bold**, ~~strikethrough~~, `inline code`, and [links](https://github.com/pthom/imgui_bundle).

- [x] write a list
- [ ] add a heading: a line that starts with `## `
- [ ] change the table below

> [!TIP]
> A quote that starts with `[!TIP]`, `[!NOTE]` or `[!WARNING]` becomes a callout.

## A table

| Panel   | Library            | Role    |
|---------|--------------------|---------|
| Source  | ImGuiColorTextEdit | edits   |
| Preview | rich_md            | renders |

## Code

The two lines that join them:

```cpp
editor.SetChangeCallback([&] { markdown = editor.GetText(); });
RichMd::RenderDocument("##preview", markdown);
```

## Math

The roots of $ax^2 + bx + c = 0$ are

$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$
)md";

    // The editor's palette follows the app's theme: light on a light background
    const TextEditor::Palette& ThemePalette()
    {
        ImVec4 bg = ImGui::GetStyleColorVec4(ImGuiCol_WindowBg);
        bool light = 0.299f * bg.x + 0.587f * bg.y + 0.114f * bg.z > 0.5f;
        return light ? TextEditor::GetLightPalette() : TextEditor::GetDarkPalette();
    }

    struct MarkdownEditor
    {
        TextEditor editor;
        std::string markdown = kSample;  // what the preview shows: a copy of the editor's text

        MarkdownEditor()
        {
            editor.SetText(markdown);
            editor.SetLanguage(TextEditor::Language::Markdown());
            editor.SetWordWrapEnabled(true);
            editor.SetShowWhitespacesEnabled(false);  // prose, not code: no dots for the spaces
            // Called after each change: the preview reads the new text (GetText() makes a copy: not at every frame)
            editor.SetChangeCallback([this] { markdown = editor.GetText(); });
        }

        void Source(ImVec2 size)
        {
            editor.SetPalette(ThemePalette());
            auto codeFont = RichMd::GetCodeFont();  // a monospaced font
            ImGui::PushFont(codeFont.font, codeFont.size);
            editor.Render("##source", size);
            ImGui::PopFont();
        }

        void Preview(ImVec2 size) { RichMd::RenderDocument("##preview", markdown, size); }
    };
}

void gui_demo_markdown_editor()
{
    static MarkdownEditor md;
    ImVec2 avail = ImGui::GetContentRegionAvail();
    if (avail.x < HelloImGui::EmSize(kNarrowWidthEm))
    {
        if (ImGui::BeginTabBar("##panels"))
        {
            if (ImGui::BeginTabItem("Source"))
            {
                md.Source(ImGui::GetContentRegionAvail());
                ImGui::EndTabItem();
            }
            if (ImGui::BeginTabItem("Preview"))
            {
                md.Preview(ImGui::GetContentRegionAvail());
                ImGui::EndTabItem();
            }
            ImGui::EndTabBar();
        }
        return;
    }
    float gap = ImGui::GetStyle().ItemSpacing.x;
    ImVec2 half((avail.x - gap) * 0.5f, avail.y);
    md.Source(half);
    ImGui::SameLine(0.f, gap);
    md.Preview(half);
}


#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char**)
{
    // This call is specific to the ImGui Bundle Explorer. In a standard application, you could write:
    //         HelloImGui::SetAssetsFolder("my_assets"); // (By default, HelloImGui will search inside "assets")
    ChdirBesideAssetsFolder();

    HelloImGui::SimpleRunnerParams runnerParams{.guiFunction = gui_demo_markdown_editor,
                                                .windowTitle = "Markdown editor",
                                                .windowSize = {1200, 800}};
    ImmApp::AddOnsParams addons{.withLatex = true};  // markdown, with its math formulas
    ImmApp::Run(runnerParams, addons);
    return 0;
}
#endif
