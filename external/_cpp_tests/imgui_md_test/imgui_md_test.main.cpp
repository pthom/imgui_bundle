#include "hello_imgui/hello_imgui.h"
#include "hello_imgui/image_gl.h"
# include <imgui.h>
#include "imgui_md/imgui_md.h"

#include <string>
#include <vector>
#include <utility>
#include <map>
#include <memory>


struct MarkdownEmphasis
{
    bool italic;
    bool bold;

    static std::vector<MarkdownEmphasis> Variants()
    {
        return {
            { .italic = false, .bold = false },
            { .italic = false, .bold = true },
            { .italic = true, .bold = false },
            { .italic = true, .bold = true },
        };
    }

    bool operator==(const MarkdownEmphasis& rhs) const {
        return (rhs.italic == italic) && (rhs.bold == bold);
    }
};


struct MarkdownTextStyle
{
    MarkdownEmphasis markdownEmphasis;
    int headerLevel;

    bool operator==(const MarkdownTextStyle& rhs) const {
        return (rhs.markdownEmphasis == markdownEmphasis) && (rhs.headerLevel == headerLevel);
    }
};


struct MarkdownFontOptions
{
    std::string fontBasePath = "fonts/Roboto/Roboto";
    int maxHeaderLevel = 3;
    float sizeDiffBetweenLevels = 3.f;
    float regularSize = 14.f;

    float FontSize(int headerLevel) const
    {
        if (headerLevel <= 0)
            return regularSize;
        else
        {
            // maxHeaderLevel = 4, headerLevel = 4
            // => multiplicationFactor = 1
            // maxHeaderLevel = 4, headerLevel = 1
            // => multiplicationFactor = 4
            if (headerLevel > maxHeaderLevel)
                headerLevel = maxHeaderLevel;
            int multiplicationFactor = maxHeaderLevel - headerLevel + 1;
            float fontSize = regularSize + (float)multiplicationFactor * sizeDiffBetweenLevels;
            return fontSize;
        }
    };

    std::string FontFilename(MarkdownEmphasis style) const
    {
        std::string r = fontBasePath + "-";
        if (style.bold)
            r += "Bold";
        else
            r += "Medium";
        if (style.italic)
            r += "Italic";
        r += ".ttf";
        return r;
    }

};


class FontCollection
{
public:
    FontCollection(const MarkdownFontOptions& options): mMarkdownFontOptions(options)
    {
        LoadFonts();
    }

    ImFont* GetFont(const MarkdownTextStyle& _markdownTextStyle) const
    {
        MarkdownTextStyle markdownTextStyle = _markdownTextStyle;
        if (markdownTextStyle.headerLevel < 0)
            markdownTextStyle.headerLevel = 0;
        if (markdownTextStyle.headerLevel > mMarkdownFontOptions.maxHeaderLevel)
            markdownTextStyle.headerLevel = mMarkdownFontOptions.maxHeaderLevel;

        for (auto pair: mFonts)
        {
            if (pair.first == markdownTextStyle)
                return pair.second;
        }
        assert(false);
    }
private:
    void LoadFonts()
    {
        for (int header_level = 0; header_level <= mMarkdownFontOptions.maxHeaderLevel; ++header_level)
        {
            for (auto emphasisVariant: MarkdownEmphasis::Variants())
            {
                MarkdownTextStyle markdownTextStyle;
                markdownTextStyle.markdownEmphasis = emphasisVariant;
                markdownTextStyle.headerLevel = header_level;

                float fontSize = mMarkdownFontOptions.FontSize(header_level);
                std::string fontFile = mMarkdownFontOptions.FontFilename(emphasisVariant);
                ImFont * font = HelloImGui::LoadFontTTF_WithFontAwesomeIcons(fontFile, fontSize);
                mFonts.push_back(std::make_pair(markdownTextStyle, font) );
            }
        }
    }

    MarkdownFontOptions mMarkdownFontOptions;
    std::vector<std::pair<MarkdownTextStyle, ImFont*>> mFonts;
};


struct MarkdownCollection
{
    MarkdownCollection(const MarkdownFontOptions& options)
        : mFontCollection(options)
    {}
    FontCollection mFontCollection;
    mutable std::map<std::string, HelloImGui::ImageGlPtr > mLoadedImages;
};


struct MyMarkdownRenderer : public imgui_md
{
private:
    MarkdownCollection mMarkdownCollection;
public:
    MyMarkdownRenderer(const MarkdownFontOptions& markdownFontOptions)
        : mMarkdownCollection(markdownFontOptions)
    {
    }

    ImFont* get_font() const override
    {
        MarkdownTextStyle markdownTextStyle;
        markdownTextStyle.headerLevel = m_hlevel;
        markdownTextStyle.markdownEmphasis.bold = m_is_strong;
        markdownTextStyle.markdownEmphasis.italic = m_is_em;

        ImFont *r = mMarkdownCollection.mFontCollection.GetFont(markdownTextStyle);
        return r;
    };

    void open_url() const override
    {
        //platform dependent code
        //SDL_OpenURL(m_href.c_str());
    }

    bool get_image(image_info& nfo) const override
    {
        std::string url = m_href;
        if (mMarkdownCollection.mLoadedImages.find(url) == mMarkdownCollection.mLoadedImages.end())
        {
            try
            {
                mMarkdownCollection.mLoadedImages[url] = HelloImGui::ImageGl::FactorImage(m_href.c_str());
            }
            catch (std::runtime_error)
            {
                try
                {
                    mMarkdownCollection.mLoadedImages[url] = HelloImGui::ImageGl::FactorImage("broken.png");
                }
                catch (std::runtime_error)
                {
                    return false;
                }
            }
        }

        auto imageGl = mMarkdownCollection.mLoadedImages[url].get();

        //use m_href to identify images
        nfo.texture_id = imageGl->imTextureId;
        nfo.size = imageGl->imageSize;
        nfo.uv0 = { 0,0 };
        nfo.uv1 = {1,1};
        nfo.col_tint = { 1,1,1,1 };
        nfo.col_border = { 0,0,0,0 };
        return true;
    }

    void html_div(const std::string& dclass, bool e) override
    {
        if (dclass == "red") {
            if (e) {
                m_table_border = false;
                ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(255, 0, 0, 255));
            } else {
                ImGui::PopStyleColor();
                m_table_border = true;
            }
        }
    }

    void render(const std::string& s)
    {
        const char * start = s.c_str();
        const char * end = start + s.size();
        this->print(start, end);
    }
};


////call this function to render your markdown
//void markdown(const char* str, const char* str_end)
//{
//    static MyMarkdownRenderer s_renderer;
//    //s_renderer.print(str, str_end);
//}


void gui(MyMarkdownRenderer& renderer)
{
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

![Alt text](world2.jpg "a title")
)md";
    renderer.render(m);
}


void LoadDefaultFont_WithFontAwesomeIcons(const MarkdownFontOptions& options)
{
    // Load default font
    {
        float fontSize = 14.f;
        std::string fontFilename = "fonts/DroidSans.ttf";
        ImFont* main_font = HelloImGui::LoadFontTTF_WithFontAwesomeIcons(fontFilename, fontSize, false);
    }
}


int main(int , char *[])
{
    MarkdownFontOptions markdownFontOptions;
    std::unique_ptr<MyMarkdownRenderer> myMarkdownRenderer;

    HelloImGui::overrideAssetsFolder(
        "/Users/pascal/dvp/OpenSource/ImGuiWork/litgen/demos/litgen/imgui_bundle/external/_cpp_tests/imgui_md_test/assets");

    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.LoadAdditionalFonts = [&]() {
        myMarkdownRenderer = std::make_unique<MyMarkdownRenderer>(markdownFontOptions);
    };
    runnerParams.callbacks.ShowGui = [&]() {
        gui(*myMarkdownRenderer);
    };
    HelloImGui::Run(runnerParams);
    return 0;
}
