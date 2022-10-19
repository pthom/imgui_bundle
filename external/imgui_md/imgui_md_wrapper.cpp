#include "imgui_md_wrapper.h"

#include "hello_imgui/hello_imgui.h"
#include "hello_imgui/image_gl.h"

# include <imgui.h>
#include "imgui_md/imgui_md.h"

#include <string>
#include <vector>
#include <utility>
#include <map>
#include <memory>

namespace ImGuiMd
{

    namespace MdFonts
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
                    { .italic = false, .bold = false },
                    { .italic = false, .bold = true },
                    { .italic = true, .bold = false },
                    { .italic = true, .bold = true },
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
                r += "Medium";
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
                    for (auto emphasisVariant: MarkdownEmphasis::AllEmphasisVariants())
                    {
                        MarkdownTextStyle markdownTextStyle;
                        markdownTextStyle.markdownEmphasis = emphasisVariant;
                        markdownTextStyle.headerLevel = header_level;

                        float fontSize = MarkdownFontOptions_FontSize(mMarkdownFontOptions, header_level);
                        std::string fontFile = MarkdownFontOptions_FontFilename(mMarkdownFontOptions, emphasisVariant);
                        ImFont * font = HelloImGui::LoadFontTTF_WithFontAwesomeIcons(fontFile, fontSize);
                        mFonts.push_back(std::make_pair(markdownTextStyle, font) );
                    }
                }
            }

            MarkdownFontOptions mMarkdownFontOptions;
            std::vector<std::pair<MarkdownTextStyle, ImFont*>> mFonts;
        };

    } //namespace MdFonts


    struct MarkdownCollection
    {
        MarkdownCollection(const MarkdownFontOptions& options)
            : mFontCollection(options)
        {}
        MdFonts::FontCollection mFontCollection;
        mutable std::map<std::string, HelloImGui::ImageGlPtr > mLoadedImages;
    };


    class MarkdownRendererPImpl : public imgui_md
    {
    private:
        MarkdownCollection mMarkdownCollection;
    public:
        MarkdownRendererPImpl(const MarkdownFontOptions& markdownFontOptions)
            : mMarkdownCollection(markdownFontOptions)
        {
        }

        void Render(const std::string& s)
        {
            const char * start = s.c_str();
            const char * end = start + s.size();
            this->print(start, end);
        }


    private:
        ImFont* get_font() const override
        {
            MdFonts::MarkdownTextStyle markdownTextStyle;
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
    };

//
// PImpl glue
//
    MarkdownRenderer::MarkdownRenderer(const MarkdownFontOptions& options)
        : mImpl(std::make_unique<MarkdownRendererPImpl>(options)) {}
    MarkdownRenderer::~MarkdownRenderer() = default;
    void MarkdownRenderer::Render(const std::string& markdownString) { mImpl->Render(markdownString); }

}
