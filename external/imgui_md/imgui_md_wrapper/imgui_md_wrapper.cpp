// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui_md_wrapper.h"
#ifdef IMGUI_MARKDOWN_WITH_DOWNLOAD_IMAGES
#include "imgui_md_url_download.h"
#endif

#ifdef HELLOIMGUI_HAS_OPENGL // Image rendering with markdown only works with OpenGl
#define CAN_RENDER_IMAGES
#endif

#include "hello_imgui/hello_imgui.h"
#include "immapp/snippets.h"

#include "imgui.h"
#include "imgui_md/imgui_md.h"
#include "immapp/code_utils.h"
#include "immapp/browse_to_url.h"

#include <fplus/fplus.hpp>
#include <string>
#include <vector>
#include <utility>
#include <map>
#include <memory>
#include <iostream>
#include <cassert>

ImVec4 LinkColor(); // See imgui_md.cpp

namespace ImGuiMd
{
    ImVec4 LinkColor()
    {
        return ::LinkColor();
    }

    void RenderTextAsLink(const char* text, const char* url)
    {
        ImGui::PushStyleColor(ImGuiCol_Text, LinkColor());
        ImGui::TextUnformatted(text);
        ImGui::PopStyleColor();
        ImGui::SetItemTooltip("%s", url);
        if (ImGui::IsItemHovered())
            ImGui::SetMouseCursor(ImGuiMouseCursor_Hand);
        if (ImGui::IsItemClicked())
            ImmApp::BrowseToUrl(url);
    }


    namespace
    {
        // Factor applied to the font size before displaying
        // Case 1: Platforms which report screen size in "physical pixels": Windows (for "Dpi aware" apps), Linux (with Wayland)
        //    in case 1, fontDpiFactor = screenDpi / 96
        // Case 2: Platforms which report screen size in "density-independent pixels": macOS, iOS, Android, emscripten
        //    in case 2, fontDpiFactor = 1
        float fontDpiFactor()
        {
            auto dpiParams = HelloImGui::GetDpiAwareParams();
            float fontDpiFactor = dpiParams->DpiFontLoadingFactor();
            return fontDpiFactor;
        }

    }

    namespace ImGuiMdFonts
    {
        struct MarkdownEmphasis
        {
            bool italic = false;
            bool bold = false;
        };
        struct MarkdownTextStyle
        {
            MarkdownEmphasis markdownEmphasis;
            int headerLevel = 0;
        };

        static bool operator==(const MarkdownEmphasis& lhs, const MarkdownEmphasis& rhs) {
            return (lhs.italic == rhs.italic) && (lhs.bold == rhs.bold);
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


        float MarkdownFontOptions_FontSize(const MarkdownFontOptions &self, int headerLevel)
        {
            if (headerLevel <= 0)
                return self.regularSize * fontDpiFactor();
            else
            {
                int idxSizeFactors = headerLevel - 1;
                if (idxSizeFactors >= 6)
                    idxSizeFactors = 5;
                float multiplicationFactor = self.headerSizeFactors[idxSizeFactors];
                float fontSize = self.regularSize * fontDpiFactor() * multiplicationFactor;
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

        bool IsDefaultMarkdownEmphasis(const MarkdownEmphasis& style)
        {
            return !style.bold && !style.italic;
        }


        class FontCollection
        {
        public:
            FontCollection(const MarkdownFontOptions& options): mMarkdownFontOptions(options)
            {
                LoadFonts();
            }

            SizedFont GetFontCode() const
            {
                return {mFontCode, mMarkdownFontOptions.regularSize * fontDpiFactor()};
            }

            SizedFont GetDefaultFont() const
            {
                auto defaultMarkdownStyle = MarkdownTextStyle{};
                return GetFont(defaultMarkdownStyle);
            }

            SizedFont GetFont(const MarkdownTextStyle& _markdownTextStyle) const
            {
                MarkdownTextStyle markdownTextStyle = _markdownTextStyle;
                if (markdownTextStyle.headerLevel < 0)
                    markdownTextStyle.headerLevel = 0;

                float fontSize = MarkdownFontOptions_FontSize(mMarkdownFontOptions, markdownTextStyle.headerLevel);

                for (auto pair: mFonts)
                {
                    if (pair.first == markdownTextStyle.markdownEmphasis)
                        return SizedFont{ pair.second, fontSize };
                }
                IM_ASSERT(false && "Could not find font for markdown style");
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
│     ├── Inconsolata-Medium.ttf
│     └── fontawesome-webfont.ttf
└── images/
    └── markdown_broken_image.png

You may find these files in the imgui_bundle/imgui_bundle_assets/ folder.
)";
                for (auto emphasisVariant: AllEmphasisVariants())
                {
                    std::string fontFile = MarkdownFontOptions_FontFilename(mMarkdownFontOptions, emphasisVariant);

                    if (! HelloImGui::AssetExists(fontFile))
                    {
                        fprintf(stderr, "Markdown font file \"%s\" not found!\n", fontFile.c_str());
                        fprintf(stderr, "%s", error_message.c_str());
                        IM_ASSERT(false);
                    }

                    // we shall not load the icons for all the fonts variants, since the font atlas
                    // texture might end up too big to fit in the GPU.
                    ImFont * font;
                    float defaultFontLoadingSize = 16.f;  // size at loading time (then Fonts can be resized to any size)
                    if (IsDefaultMarkdownEmphasis(emphasisVariant))
                        font = HelloImGui::LoadFontTTF_WithFontAwesomeIcons(fontFile, defaultFontLoadingSize);
                    else
                        font = HelloImGui::LoadFontTTF(fontFile, defaultFontLoadingSize);

                    if (font == nullptr)
                    {
                        fprintf(stderr, "%s", error_message.c_str());
                        IM_ASSERT(false);
                    }

                    mFonts.push_back(std::make_pair(emphasisVariant, font) );
                }

                float fontSize = MarkdownFontOptions_FontSize(mMarkdownFontOptions, 0);
                mFontCode = HelloImGui::LoadFontTTF(
                    "fonts/Inconsolata-Medium.ttf",
                    fontSize);
                if (mFontCode == nullptr) {
                    // SourceCodePro-Regular was the old default font for code
                    // we try to load it, to be nice with older users
                    mFontCode = HelloImGui::LoadFontTTF(
                        "fonts/SourceCodePro-Regular.ttf",
                        fontSize);
                }
                if (mFontCode == nullptr) {
                    fprintf(stderr, "%s", error_message.c_str());
                    IM_ASSERT(false);
                }
            }

            MarkdownFontOptions mMarkdownFontOptions;
            std::vector<std::pair<MarkdownEmphasis, ImFont*>> mFonts;
            ImFont* mFontCode;
        };

    } //namespace MdFonts

    struct MarkdownCollection
    {
        MarkdownCollection(const MarkdownFontOptions& options)
            : mFontCollection(options)
        {}
        ImGuiMdFonts::FontCollection mFontCollection;

#ifdef CAN_RENDER_IMAGES
        mutable std::map<std::string, HelloImGui::ImageAndSize > mLoadedImages;
#endif
    };


    class MarkdownRenderer : public imgui_md
    {
    private:
        MarkdownOptions *mMarkdownOptions;
        MarkdownCollection mMarkdownCollection;
        std::map<std::string, Snippets::SnippetData> mSnippets;
        int mTableIdCounter = 0;
        bool mTableOpen = false;
        bool mIsFirstBlock = true;
    public:
        MarkdownRenderer(MarkdownOptions* markdownOptions)
            : mMarkdownOptions(markdownOptions)
            , mMarkdownCollection(markdownOptions->fontOptions)
        {
        }

#ifdef CAN_RENDER_IMAGES
        std::map<std::string, HelloImGui::ImageAndSize >& ImageCache()
        {
            return mMarkdownCollection.mLoadedImages;
        }
#endif

        void Render(const std::string& s)
        {
            auto defaultSizedFont = mMarkdownCollection.mFontCollection.GetDefaultFont();
            ImGui::PushFont(defaultSizedFont.font, defaultSizedFont.size);

            const char * start = s.c_str();
            const char * end = start + s.size();
            mTableIdCounter = 0;
            mIsFirstBlock = true;
            this->print(start, end);
            ImGui::PopFont();
        }

        SizedFont get_font_code()
        {
            return mMarkdownCollection.mFontCollection.GetFontCode();
        }

        SizedFont GetFont(const MarkdownFontSpec& fontSpec)
        {
            ImGuiMdFonts::MarkdownTextStyle markdownTextStyle;
            markdownTextStyle.headerLevel = fontSpec.headerLevel;
            markdownTextStyle.markdownEmphasis.bold = fontSpec.bold;
            markdownTextStyle.markdownEmphasis.italic = fontSpec.italic;
            return mMarkdownCollection.mFontCollection.GetFont(markdownTextStyle);
        }


    private:
        imgui_md::MdSizedFont get_font() const override
        {
            if (m_is_code)
            {
                // https://github.com/mekhontsev/imgui_md does not handle correctly code blocks
                // so that we will never reach here...
                auto fontCode = mMarkdownCollection.mFontCollection.GetFontCode();
                return imgui_md::MdSizedFont{ fontCode.font, fontCode.size };
            }
            else
            {
                ImGuiMdFonts::MarkdownTextStyle markdownTextStyle;
                markdownTextStyle.headerLevel = m_hlevel;
                markdownTextStyle.markdownEmphasis.bold = m_is_strong;
                markdownTextStyle.markdownEmphasis.italic = m_is_em;
                auto font  = mMarkdownCollection.mFontCollection.GetFont(markdownTextStyle);
                return imgui_md::MdSizedFont{ font.font, font.size };
            }
        };

        void open_url() const override
        {
            if (mMarkdownOptions->callbacks.OnOpenLink)
                mMarkdownOptions->callbacks.OnOpenLink(m_href);
        }

        bool get_image(image_info& nfo) const override
        {
            if (! mMarkdownOptions->callbacks.OnImage)
                return false;

            std::optional<MarkdownImage> mdImage = mMarkdownOptions->callbacks.OnImage(m_img_src);

            if (! mdImage.has_value())
                return false;

            // Image size adaptive depending on the resolution scale
            {
                float k = HelloImGui::DpiFontLoadingFactor();
                nfo.size = ImVec2(mdImage->size.x * k, mdImage->size.y * k);
            }

            nfo.texture_id = mdImage->texture_id;
            nfo.uv0 = mdImage->uv0;
            nfo.uv1 = mdImage->uv1;

            return true;
        }

        void html_div(const std::string& divClass, bool openingDiv) override
        {
            if (!mMarkdownOptions->callbacks.OnHtmlDiv)
                return;

            mMarkdownOptions->callbacks.OnHtmlDiv(divClass, openingDiv);
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
                {
                    auto& bg = ImGui::GetStyle().Colors[ImGuiCol_WindowBg];
                    float luminance = 0.299f * bg.x + 0.587f * bg.y + 0.114f * bg.z;
                    snippet.Palette = (luminance > 0.5f) ? Snippets::SnippetTheme::Light : Snippets::SnippetTheme::Dark;
                }
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
                snippet.ReadOnly = true;
            }

            ImGui::SetCursorPosX(0.f);
            auto& snippet = mSnippets[m_code_block];
            Snippets::ShowCodeSnippet(snippet);

            ImGui::PopID();
        }

        void BLOCK_TABLE(const MD_BLOCK_TABLE_DETAIL* d, bool e) override
        {
            if (e) {
                // print() pre-compensates for the initial NewLine by moving
                // the cursor up. Only a table as the very first block needs
                // to undo that — later blocks have already consumed it.
                if (mIsFirstBlock)
                    ImGui::SetCursorPosY(ImGui::GetCursorPosY() + ImGui::GetFontSize() * 0.3f + ImGui::GetStyle().ItemSpacing.y);
                mIsFirstBlock = false;
                ImGui::PushID(mTableIdCounter++);
                ImGuiTableFlags flags = ImGuiTableFlags_SizingStretchProp
                                      | ImGuiTableFlags_Resizable;
                if (m_table_border)
                    flags |= ImGuiTableFlags_BordersInnerV
                           | ImGuiTableFlags_BordersOuterV
                           | ImGuiTableFlags_BordersOuterH
                           | ImGuiTableFlags_BordersInnerH;
                mTableOpen = ImGui::BeginTable("##md", d->col_count, flags);
            } else {
                if (mTableOpen)
                    ImGui::EndTable();
                mTableOpen = false;
                ImGui::PopID();
            }
        }

        void BLOCK_THEAD(bool e) override
        {
            if (!mTableOpen) return;
            if (m_table_header_highlight) {
                if (e) {
                    ImGuiMdFonts::MarkdownTextStyle style;
                    style.markdownEmphasis.bold = true;
                    auto font = mMarkdownCollection.mFontCollection.GetFont(style);
                    ImGui::PushFont(font.font, font.size);
                } else {
                    ImGui::PopFont();
                }
            }
        }

        void BLOCK_TBODY(bool) override {}

        void BLOCK_TR(bool e) override
        {
            if (mTableOpen && e) ImGui::TableNextRow();
        }

        void BLOCK_TH(const MD_BLOCK_TD_DETAIL*, bool e) override
        {
            if (mTableOpen && e) ImGui::TableNextColumn();
        }

        void BLOCK_TD(const MD_BLOCK_TD_DETAIL*, bool e) override
        {
            if (mTableOpen && e) ImGui::TableNextColumn();
        }

    };


    // Global renderer
    std::unique_ptr<MarkdownRenderer> gMarkdownRenderer;

#ifdef __EMSCRIPTEN__
#include <emscripten/fetch.h>
#include <mutex>

    // Emscripten async download using emscripten_fetch
    // State for pending downloads
    struct EmscriptenDownloadState {
        MarkdownDownloadStatus status = MarkdownDownloadStatus::NotStarted;
        std::vector<uint8_t> data;
        std::string errorMessage;
    };

    static std::map<std::string, EmscriptenDownloadState> gEmscriptenDownloads;

    static void _emscripten_fetch_success(emscripten_fetch_t *fetch)
    {
        std::string url = fetch->url;
        auto& state = gEmscriptenDownloads[url];
        state.data.assign(
            reinterpret_cast<const uint8_t*>(fetch->data),
            reinterpret_cast<const uint8_t*>(fetch->data) + fetch->numBytes);
        state.status = MarkdownDownloadStatus::Ready;
        emscripten_fetch_close(fetch);
    }

    static void _emscripten_fetch_error(emscripten_fetch_t *fetch)
    {
        std::string url = fetch->url;
        auto& state = gEmscriptenDownloads[url];
        state.status = MarkdownDownloadStatus::Failed;
        state.errorMessage = "HTTP " + std::to_string(fetch->status);
        emscripten_fetch_close(fetch);
    }

    static MarkdownDownloadResult EmscriptenDownloadData(const std::string& url)
    {
        MarkdownDownloadResult result;

        auto it = gEmscriptenDownloads.find(url);
        if (it == gEmscriptenDownloads.end())
        {
            // Start async fetch
            gEmscriptenDownloads[url] = EmscriptenDownloadState{MarkdownDownloadStatus::Downloading, {}, ""};

            emscripten_fetch_attr_t attr;
            emscripten_fetch_attr_init(&attr);
            strcpy(attr.requestMethod, "GET");
            attr.attributes = EMSCRIPTEN_FETCH_LOAD_TO_MEMORY;
            attr.onsuccess = _emscripten_fetch_success;
            attr.onerror = _emscripten_fetch_error;
            emscripten_fetch(&attr, url.c_str());

            result.status = MarkdownDownloadStatus::Downloading;
            return result;
        }

        auto& state = it->second;
        result.status = state.status;
        if (state.status == MarkdownDownloadStatus::Ready)
        {
            result.data = std::move(state.data);
            gEmscriptenDownloads.erase(it);
        }
        else if (state.status == MarkdownDownloadStatus::Failed)
        {
            result.errorMessage = state.errorMessage;
            gEmscriptenDownloads.erase(it);
        }
        return result;
    }
#endif // __EMSCRIPTEN__

    // Global options
    MarkdownOptions gMarkdownOptions;
    static Priv_OnInitializeMarkdownCallback gOnInitializeMarkdownCallback;
    static bool gMarkdownWasInitialized = false;

    void Priv_SetOnInitializeMarkdownCallback(Priv_OnInitializeMarkdownCallback callback)
    {
        gOnInitializeMarkdownCallback = std::move(callback);
    }

    void DeInitializeMarkdown()
    {
        // Clear per-frame callbacks that may hold Python objects before the interpreter shuts down.
        // Keep gOnInitializeMarkdownCallback alive: it is set once at module import time
        // and must survive teardown/setup cycles (e.g. Pyodide playground re-runs).
        gMarkdownOptions.callbacks.OnDownloadData = nullptr;
        gMarkdownRenderer.release();
        gMarkdownWasInitialized = false;
#ifdef IMGUI_MARKDOWN_WITH_DOWNLOAD_IMAGES
        ClearDesktopDownloads();
#endif
    }

    void InitializeMarkdown(const MarkdownOptions& options)
    {
        if (gMarkdownWasInitialized)
            return;

        gMarkdownOptions = options;
        if (gOnInitializeMarkdownCallback)
            gOnInitializeMarkdownCallback(gMarkdownOptions);
#ifdef __EMSCRIPTEN__
        // On Emscripten, set a default download callback using emscripten_fetch
        // (unless one was already set, e.g. by Python)
        if (!gMarkdownOptions.callbacks.OnDownloadData)
            gMarkdownOptions.callbacks.OnDownloadData = EmscriptenDownloadData;
#elif defined(IMGUI_MARKDOWN_WITH_DOWNLOAD_IMAGES)
        // On desktop C++, set a default download callback using libcurl
        // (unless one was already set, e.g. by Python)
        if (!gMarkdownOptions.callbacks.OnDownloadData)
            gMarkdownOptions.callbacks.OnDownloadData = DesktopDownloadData;
#endif
        gMarkdownWasInitialized = true;
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
            gMarkdownRenderer = std::make_unique<MarkdownRenderer>(&gMarkdownOptions);
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
        ImmApp::BrowseToUrl(url.c_str());
    }


    static bool _IsUrl(const std::string& path)
    {
        return path.rfind("http://", 0) == 0 || path.rfind("https://", 0) == 0;
    }

    static std::optional<MarkdownImage> _MakeMarkdownImage(const HelloImGui::ImageAndSize& imageInfo)
    {
        MarkdownImage r;
        r.texture_id = imageInfo.textureId;
        r.size = imageInfo.size;
        r.uv0 = { 0,0 };
        r.uv1 = {1,1};
        r.col_tint = { 1,1,1,1 };
        r.col_border = { 0,0,0,0 };
        return r;
    }

    // Draw a simple rotating spinner using ImGui's DrawList (no external dependencies)
    static void _DrawLoadingSpinner()
    {
        float size = ImGui::GetFontSize() * 2.0f;
        ImVec2 cursor = ImGui::GetCursorScreenPos();
        ImVec2 center(cursor.x + size * 0.5f, cursor.y + size * 0.5f);
        float radius = size * 0.4f;
        float thickness = 2.0f;
        ImU32 color = ImGui::GetColorU32(ImGuiCol_Text, 0.6f);
        float t = (float)ImGui::GetTime();

        ImDrawList* dl = ImGui::GetWindowDrawList();
        int segments = 12;
        for (int i = 0; i < segments; i++)
        {
            float a = (float)i / (float)segments * 3.14159265358979f * 2.0f;
            // Fade based on rotation phase
            float fade = fmodf((float)i / (float)segments + t * 1.5f, 1.0f);
            ImU32 c = ImGui::GetColorU32(ImGuiCol_Text, fade * 0.8f);
            float inner = radius * 0.5f;
            ImVec2 p1(center.x + cosf(a) * inner, center.y + sinf(a) * inner);
            ImVec2 p2(center.x + cosf(a) * radius, center.y + sinf(a) * radius);
            dl->AddLine(p1, p2, c, thickness);
        }
        ImGui::Dummy(ImVec2(size, size));
    }

    static HelloImGui::ImageAndSize _BrokenImageAndSize()
    {
        std::string errorImage = "images/markdown_broken_image.png";
        if (HelloImGui::AssetExists(errorImage))
            return HelloImGui::ImageAndSizeFromAsset(errorImage.c_str());
        return {};
    }

    static std::optional<MarkdownImage> _BrokenImage()
    {
        auto ias = _BrokenImageAndSize();
        if (ias.textureId != ImTextureID(0))
            return _MakeMarkdownImage(ias);
        return std::nullopt;
    }

    std::optional<MarkdownImage> OnImage_Default(const std::string& image_path)
    {
#ifdef CAN_RENDER_IMAGES
        if (!gMarkdownRenderer)
        {
            std::cerr << "Did you initialize ImGuiMd?\n";
            return std::nullopt;
        }

        auto & imageCache = gMarkdownRenderer->ImageCache();

        // If already cached, return it
        if (imageCache.find(image_path) != imageCache.end())
            return _MakeMarkdownImage(imageCache.at(image_path));

        // Handle URL images via OnDownloadData callback
        if (_IsUrl(image_path) && gMarkdownOptions.callbacks.OnDownloadData)
        {
            auto result = gMarkdownOptions.callbacks.OnDownloadData(image_path);
            switch (result.status)
            {
            case MarkdownDownloadStatus::Ready:
                imageCache[image_path] = HelloImGui::ImageAndSizeFromEncodedData(
                    result.data.data(), result.data.size(), image_path);
                return _MakeMarkdownImage(imageCache.at(image_path));

            case MarkdownDownloadStatus::Downloading:
                // Show spinner while downloading (don't cache - will be called again next frame)
                _DrawLoadingSpinner();
                return std::nullopt;  // nullopt so SPAN_IMG doesn't also draw an image

            case MarkdownDownloadStatus::Failed:
                if (!result.errorMessage.empty())
                    std::cerr << "imgui_md: download failed for " << image_path << ": " << result.errorMessage << "\n";
                imageCache[image_path] = _BrokenImageAndSize(); // Cache broken image to avoid retrying
                return _BrokenImage();

            case MarkdownDownloadStatus::NotStarted:
            default:
                return _BrokenImage();
            }
        }

        // Handle local asset images
        if (HelloImGui::AssetExists(image_path))
        {
            imageCache[image_path] = HelloImGui::ImageAndSizeFromAsset(image_path.c_str());
            return _MakeMarkdownImage(imageCache.at(image_path));
        }

        return _BrokenImage();
#else
        return std::nullopt;
#endif
    }

    SizedFont GetCodeFont()
    {
        return gMarkdownRenderer->get_font_code();
    }

    SizedFont GetFont(const MarkdownFontSpec& fontSpec)
    {
        return gMarkdownRenderer->GetFont(fontSpec);
    }


    // Renders a markdown string (after having unindented its main indentation)
    void RenderUnindented(const std::string& markdownString)
    {
        Render(CodeUtils::UnindentMarkdown(markdownString));
    }

} // namespace ImGuiMdBrowser
