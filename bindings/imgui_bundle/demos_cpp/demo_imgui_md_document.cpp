// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// A markdown document: renders and widgets that share a table of contents, links between their sections, a search
// (Ctrl+F, Cmd+F on macOS) that also finds the text of the code blocks and of the collapsed sections, and headings
// that fold.
#ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include "demo_utils/api_demos.h"
#include "imgui_rich_md/rich_md.h"
#include "immapp/immapp.h"
#include "implot/implot.h"

#include <cmath>
#include <string>
#include <vector>

namespace
{
    // The paragraphs of the long section: enough text to scroll
    constexpr int kParagraphs = 12;

    const char* kIntro = R"md(
# A document

`RichMd::BeginDocument()` and `RichMd::EndDocument()` frame the renders and the widgets of a document. They share a
scroll area, and a table of contents on the left: its edge can be dragged, and the arrow at its top hides it.

Between them, call `RichMd::Render()` as many times as you like, and any other widget, as the plot below: they all
belong to the document, with one table of contents and one search (see the code in "The search").

Links to the sections, wherever they are: [the widgets](#a-section-of-widgets), [the collapsed
section](#inside-a-collapsed-section), [the end](#the-end).

The headings fold: the arrow at their left, shown under the mouse, hides their section. The menu of a right click,
and the "..." menu at the top of the table of contents, fold or unfold them all.

## Headings and anchors

Each heading has a *slug*, made from its text as GitHub does: `## Headings and anchors` is `#headings-and-anchors`. A
link to it scrolls the document there, also when the heading is in another render of the document.

A repeated title gets a number: the second "Notes" below is `#notes-1`.

## Notes

The first section named "Notes".

## Collapsed sections

<details>
<summary>A collapsed section</summary>

### Inside a collapsed section

A heading hidden in a collapsed section is listed in the table of contents, dimmed. A click on it, or a link to it,
opens the section.

</details>
)md";

    const char* kSecondRender = R"md(
## Notes

The second section named "Notes", in the second render of the document: its slug is `#notes-1`.

## The search

Ctrl+F (Cmd+F on macOS) opens the find bar. The search also finds the text of the collapsed sections (a jump to one of
their matches opens them), and of the code blocks:

```cpp
RichMd::DocumentOptions options;
options.foldableHeadings = true;  // an arrow at the left of each heading folds its section
RichMd::BeginDocument("document", ImVec2(0.f, 0.f), options);
RichMd::Render(intro);  // markdown: as many renders as you like

// Widgets, under a heading of the document (false: its section is folded)
if (RichMd::DocumentHeading(2, "A section of widgets"))
{
    ImGui::SliderFloat("Frequency", &frequency, 0.5f, 5.f);
    if (ImPlot::BeginPlot("##wave"))
    {
        ImPlot::PlotLine("sin(f x)", xs, ys, count);
        ImPlot::EndPlot();
    }
}

RichMd::Render(moreMarkdown);  // the same document: one table of contents, one search
RichMd::EndDocument();
```

## Long text

The table of contents marks the section at the top of the view, and follows it as the document scrolls.

)md";

    std::string LongText()
    {
        std::string md = kSecondRender;
        for (int i = 1; i <= kParagraphs; ++i)
            md += "Paragraph " + std::to_string(i) + ": some text to scroll through, long enough to wrap on a narrow "
                  "window, so that the document has a length worth a table of contents.\n\n";
        md += "## The end\n\nBack to [the top](#a-document).\n";
        return md;
    }

    // A section made of widgets: a slider and the plot it drives
    void WidgetsSection()
    {
        static float frequency = 2.f;
        ImGui::SliderFloat("Frequency", &frequency, 0.5f, 5.f);
        static std::vector<double> xs, ys;
        xs.resize(400);
        ys.resize(400);
        for (size_t i = 0; i < xs.size(); ++i)
        {
            xs[i] = 10.0 * (double)i / (double)(xs.size() - 1);
            ys[i] = std::sin((double)frequency * xs[i]);
        }
        if (ImPlot::BeginPlot("##wave", ImVec2(-1.f, ImGui::GetFontSize() * 12.f)))
        {
            ImPlot::PlotLine("sin(f x)", xs.data(), ys.data(), (int)xs.size());
            ImPlot::EndPlot();
        }
    }
}

void gui_demo_imgui_md_document()
{
    static const std::string longText = LongText();
    RichMd::DocumentOptions options;
    options.foldableHeadings = true;  // an arrow at the left of each heading folds its section
    RichMd::BeginDocument("document", ImVec2(0.f, 0.f), options);
    RichMd::Render(kIntro);
    // DocumentHeading() draws its title as a markdown heading, and gives it a slug: the widgets below are a section.
    // It returns false when the section is folded: its widgets are skipped.
    if (RichMd::DocumentHeading(2, "A section of widgets"))
        WidgetsSection();
    RichMd::Render(longText);
    RichMd::EndDocument();
}


#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char**)
{
    // This call is specific to the ImGui Bundle Explorer. In a standard application, you could write:
    //         HelloImGui::SetAssetsFolder("my_assets"); // (By default, HelloImGui will search inside "assets")
    ChdirBesideAssetsFolder();

    HelloImGui::SimpleRunnerParams runnerParams{.guiFunction = gui_demo_imgui_md_document,
                                                .windowTitle = "A markdown document",
                                                .windowSize = {1000, 800}};
    ImmApp::AddOnsParams addons{.withImplot = true, .withMarkdown = true};
    ImmApp::Run(runnerParams, addons);
    return 0;
}
#endif
#else // #ifdef IMGUI_BUNDLE_WITH_IMPLOT
#include "imgui.h"
#include <cstdio>
void gui_demo_imgui_md_document() { ImGui::Text("This demo requires ImPlot."); }
#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char**) { std::printf("This demo requires ImPlot.\n"); }
#endif
#endif
