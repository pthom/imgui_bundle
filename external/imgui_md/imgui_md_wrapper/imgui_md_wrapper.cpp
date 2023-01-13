#include "imgui_md_wrapper.h"

#include "hello_imgui/hello_imgui.h"
#include "immapp/snippets.h"

#include "imgui.h"
#include "imgui_md/imgui_md.h"
#include "immapp/code_utils.h"

#include <fplus/fplus.hpp>
#include <string>
#include <vector>
#include <utility>
#include <map>
#include <memory>
#include <iostream>
#include <cassert>

// [sub section]  BrowseToUrl()
// A platform specific utility to open an url in a browser
// (especially useful with emscripten version)
// Specific per platform includes for BrowseToUrl
#if defined(__EMSCRIPTEN__)
#include <emscripten.h>
#elif defined(_WIN32)
#include <windows.h>
#include <Shellapi.h>
#elif defined(__APPLE__)
#include <TargetConditionals.h>
#endif


namespace ImGuiMdBrowser
{
    void BrowseToUrl(const char *url)
    {
#if defined(__EMSCRIPTEN__)
        char js_command[1024];
    snprintf(js_command, 1024, "window.open(\"%s\");", url);
    emscripten_run_script(js_command);
#elif defined(_WIN32)
        ShellExecuteA( NULL, "open", url, NULL, NULL, SW_SHOWNORMAL );
#elif TARGET_OS_IPHONE
        // Nothing on iOS
#elif TARGET_OS_OSX
        char cmd[1024];
        snprintf(cmd, 1024, "open %s", url);
        system(cmd);
#elif defined(__linux__)
        char cmd[1024];
    snprintf(cmd, 1024, "xdg-open %s", url);
    int r = system(cmd);
    (void) r;
#endif
    }
}

namespace ImGuiMd
{

    namespace ImGuiMdFonts
    {
        struct MarkdownEmphasis
        {
            bool italic;
            bool bold;

            bool operator==(const MarkdownEmphasis& rhs) const {
                return (rhs.italic == italic) && (rhs.bold == bold);
            }

            static std::vector<MarkdownEmphasis> AllEmphasisVariants()
            {
                return {
                    { false, false },
                    { false, true },
                    { true, false },
                    { true, true },
                };
            }
        };


        float MarkdownFontOptions_FontSize(const MarkdownFontOptions &self, int headerLevel)
        {
            if (headerLevel <= 0)
                return self.regularSize;
            else
            {
                // maxHeaderLevel = 4, headerLevel = 4
                // => multiplicationFactor = 1
                // maxHeaderLevel = 4, headerLevel = 1
                // => multiplicationFactor = 4
                if (headerLevel > self.maxHeaderLevel)
                    headerLevel = self.maxHeaderLevel;
                int multiplicationFactor = self.maxHeaderLevel - headerLevel + 1;
                float fontSize = self.regularSize + (float)multiplicationFactor * self.sizeDiffBetweenLevels;
                return fontSize;
            }
        };


        std::string MarkdownFontOptions_FontFilename(const MarkdownFontOptions &self, MarkdownEmphasis style)
        {
            std::string r = self.fontBasePath + "-";
            if (style.bold)
                r += "Bold";
            else
                r += "Regular";
            if (style.italic)
                r += "Italic";
            r += ".ttf";
            return r;
        }


        struct MarkdownTextStyle
        {
            MarkdownEmphasis markdownEmphasis;
            int headerLevel;

            bool operator==(const MarkdownTextStyle& rhs) const {
                return (rhs.markdownEmphasis == markdownEmphasis) && (rhs.headerLevel == headerLevel);
            }
        };


        class FontCollection
        {
        public:
            FontCollection(const MarkdownFontOptions& options): mMarkdownFontOptions(options)
            {
                LoadFonts();
            }

            ImFont* GetFontCode() const
            {
                return mFontCode;
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
                return nullptr;
            }
        private:
            void LoadFonts()
            {
                std::string error_message = R"(
Could not find required assets for ImGuiMd:
We need to find the following files in the assets:

assets/
├── fonts/
│     ├── Roboto/
│     │     ├── LICENSE.txt
│     │     ├── Roboto-Bold.ttf
│     │     ├── Roboto-BoldItalic.ttf
│     │     ├── Roboto-Regular.ttf
│     │     ├── Roboto-RegularItalic.ttf
│     ├── SourceCodePro-Regular
│     └── fontawesome-webfont.ttf
└── images/
    └── markdown_broken_image.png

)";
                for (int header_level = 0; header_level <= mMarkdownFontOptions.maxHeaderLevel; ++header_level)
                {
                    for (auto emphasisVariant: MarkdownEmphasis::AllEmphasisVariants())
                    {
                        MarkdownTextStyle markdownTextStyle;
                        markdownTextStyle.markdownEmphasis = emphasisVariant;
                        markdownTextStyle.headerLevel = header_level;

                        float fontSize = MarkdownFontOptions_FontSize(mMarkdownFontOptions, header_level);
                        std::string fontFile = MarkdownFontOptions_FontFilename(mMarkdownFontOptions, emphasisVariant);
                        try
                        {
                            ImFont * font = HelloImGui::LoadFontTTF_WithFontAwesomeIcons(fontFile, fontSize);
                            mFonts.push_back(std::make_pair(markdownTextStyle, font) );
                        }
                        catch (std::runtime_error)
                        {
                            throw std::runtime_error(error_message);
                        }
                    }
                }

                try
                {
                    float fontSize = MarkdownFontOptions_FontSize(mMarkdownFontOptions, 0);
                    mFontCode = HelloImGui::LoadFontTTF_WithFontAwesomeIcons(
                        "fonts/SourceCodePro-Regular.ttf", fontSize);
                }
                catch (std::runtime_error)
                {
                    throw std::runtime_error(error_message);
                }
            }

            MarkdownFontOptions mMarkdownFontOptions;
            std::vector<std::pair<MarkdownTextStyle, ImFont*>> mFonts;
            ImFont* mFontCode;
        };

    } //namespace MdFonts

    struct MarkdownCollection
    {
        MarkdownCollection(const MarkdownFontOptions& options)
            : mFontCollection(options)
        {}
        ImGuiMdFonts::FontCollection mFontCollection;
        mutable std::map<std::string, HelloImGui::ImageGlPtr > mLoadedImages;
    };


    class MarkdownRenderer : public imgui_md
    {
    private:
        MarkdownOptions mMarkdownOptions;
        MarkdownCollection mMarkdownCollection;
        std::map<std::string, Snippets::SnippetData> mSnippets;
    public:
        MarkdownRenderer(MarkdownOptions markdownOptions)
            : mMarkdownOptions(markdownOptions)
            , mMarkdownCollection(markdownOptions.fontOptions)
        {
        }

        std::map<std::string, HelloImGui::ImageGlPtr >& ImageCache()
        {
            return mMarkdownCollection.mLoadedImages;
        }

        void Render(const std::string& s)
        {
            const char * start = s.c_str();
            const char * end = start + s.size();
            this->print(start, end);
        }

        ImFont* get_font_code()
        {
            return mMarkdownCollection.mFontCollection.GetFontCode();
        }

    private:
        ImFont* get_font() const override
        {
            if (m_is_code)
            {
                // https://github.com/mekhontsev/imgui_md does not handle correctly code blocks
                // so that we will never reach here...
                return mMarkdownCollection.mFontCollection.GetFontCode();
            }
            else
            {
                ImGuiMdFonts::MarkdownTextStyle markdownTextStyle;
                markdownTextStyle.headerLevel = m_hlevel;
                markdownTextStyle.markdownEmphasis.bold = m_is_strong;
                markdownTextStyle.markdownEmphasis.italic = m_is_em;
                return mMarkdownCollection.mFontCollection.GetFont(markdownTextStyle);
            }
        };

        void open_url() const override
        {
            if (mMarkdownOptions.callbacks.OnOpenLink)
                mMarkdownOptions.callbacks.OnOpenLink(m_href);
        }

        bool get_image(image_info& nfo) const override
        {
            if (! mMarkdownOptions.callbacks.OnImage)
                return false;

            std::optional<MarkdownImage> mdImage = mMarkdownOptions.callbacks.OnImage(m_img_src);

            if (! mdImage.has_value())
                return false;

            nfo.size = mdImage->size;
            nfo.col_border = mdImage->col_border;
            nfo.col_tint = mdImage->col_tint;
            nfo.texture_id = mdImage->texture_id;
            nfo.uv0 = mdImage->uv0;
            nfo.uv1 = mdImage->uv1;

            return true;
        }

        void html_div(const std::string& divClass, bool openingDiv) override
        {
            if (!mMarkdownOptions.callbacks.OnHtmlDiv)
                return;

            mMarkdownOptions.callbacks.OnHtmlDiv(divClass, openingDiv);
        }

        void render_code_block() override
        {
            auto code_without_last_empty_lines = [](const std::string code_)
            {
                // remove last line if empty
                std::string code = code_;
                {
                    auto lines = fplus::split_lines(true, code);
                    if (lines.size() > 0)
                    {
                        if (fplus::trim_whitespace(lines.back()).size() == 0)
                            lines.pop_back();
                        code = fplus::join(std::string("\n"), lines);
                    }
                }
                return code;
            };

            ImGui::PushID(m_code_block.c_str());
            if (mSnippets.find(m_code_block) == mSnippets.end())
            {
                mSnippets[m_code_block] = Snippets::SnippetData();
                auto& snippet = mSnippets[m_code_block];
                snippet.Palette = Snippets::SnippetTheme::Dark;
                snippet.Code = code_without_last_empty_lines(m_code_block);

                // set language
                if (fplus::to_lower_case(m_code_block_language) == "cpp")
                    snippet.Language = Snippets::SnippetLanguage::Cpp;
                else if (fplus::to_lower_case(m_code_block_language) == "c")
                    snippet.Language = Snippets::SnippetLanguage::C;
                else if (fplus::to_lower_case(m_code_block_language) == "python")
                    snippet.Language = Snippets::SnippetLanguage::Python;
                else if (fplus::to_lower_case(m_code_block_language) == "glsl")
                    snippet.Language = Snippets::SnippetLanguage::Glsl;
                else if (fplus::to_lower_case(m_code_block_language) == "sql")
                    snippet.Language = Snippets::SnippetLanguage::Sql;
                else if (fplus::to_lower_case(m_code_block_language) == "lua")
                    snippet.Language = Snippets::SnippetLanguage::Lua;
                else if (fplus::to_lower_case(m_code_block_language) == "angelscript")
                    snippet.Language = Snippets::SnippetLanguage::AngelScript;

                snippet.ShowCursorPosition = false;
            }

            ImGui::SetCursorPosX(0.f);
            auto& snippet = mSnippets[m_code_block];
            Snippets::ShowCodeSnippet(snippet);

            ImGui::PopID();
        }

    };


    // Global renderer
    std::unique_ptr<MarkdownRenderer> gMarkdownRenderer;

    // Global options
    MarkdownOptions gMarkdownOptions;


    void InitializeMarkdown(const MarkdownOptions& options)
    {
        static bool wasCalledAlready = false;
        if (wasCalledAlready)
        {
            //std::cerr << "InitializeMarkdown can only be called once at application startup!\n";
            return;
        }


        gMarkdownOptions = options;
        wasCalledAlready = true;
    }


    void Render(const std::string& markdownString)
    {
        if (!gMarkdownRenderer)
        {
            std::cerr << "ImGuiMd::Render : Markdown was not initialized!\n";
            return;
        }
        gMarkdownRenderer->Render(markdownString);
    }

    std::function<void(void)> GetFontLoaderFunction()
    {
        auto fontLoaderFunction = []()
        {
            gMarkdownRenderer = std::make_unique<MarkdownRenderer>(gMarkdownOptions);
        };
        return fontLoaderFunction;
    }


    void OnOpenLink_Default(const std::string& url)
    {
        if (strncmp(url.c_str(), "http", strlen("http")) != 0)
        {
            std::cerr << "ImGuiMd::OnOpenLink_Default url \"" << url << "\" should start with http!\n";
            return;
        }
        ImGuiMdBrowser::BrowseToUrl(url.c_str());
    }


    std::optional<MarkdownImage> OnImage_Default(const std::string& image_path)
    {
        if (!gMarkdownRenderer)
        {
            std::cerr << "Did you initialize ImGuiMd?\n";
            return std::nullopt;
        }

        auto & imageCache = gMarkdownRenderer->ImageCache();
        if (imageCache.find(image_path) == imageCache.end())
        {
            try
            {
                imageCache[image_path] = HelloImGui::ImageGl::FactorImage(image_path.c_str());
            }
            catch (std::runtime_error)
            {
                try
                {
                    imageCache[image_path] = HelloImGui::ImageGl::FactorImage("images/markdown_broken_image.png");
                }
                catch (std::runtime_error)
                {
                    return std::nullopt;
                }
            }
        }

        auto imageGl = imageCache.at(image_path).get();

        MarkdownImage r;

        r.texture_id = imageGl->imTextureId;
        r.size = imageGl->imageSize;
        r.uv0 = { 0,0 };
        r.uv1 = {1,1};
        r.col_tint = { 1,1,1,1 };
        r.col_border = { 0,0,0,0 };
        return r;
    }

    ImFont* GetCodeFont()
    {
        return gMarkdownRenderer->get_font_code();
    }

    // Renders a markdown string (after having unindented its main indentation)
    void RenderUnindented(const std::string& markdownString)
    {
        Render(CodeUtils::UnindentMarkdown(markdownString));
    }

} // namespace ImGuiMdBrowser
