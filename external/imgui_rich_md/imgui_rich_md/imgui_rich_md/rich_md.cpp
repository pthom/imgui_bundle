// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "rich_md.h"
#include "rich_md_host.h"
#include "rich_md_internal.h"
#ifdef IMGUI_RICHMD_WITH_CODE_EDITOR
#include "backends/code_editor/snippets.h"
#endif
#ifdef IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES
#include "rich_md_url_download.h"
#endif


#include "imgui.h"
#include "imgui_internal.h"  // RegisterUserTexture
#include "rich_md_renderer.h"

// Platform includes for OpenUrlInBrowser
#if defined(__EMSCRIPTEN__)
#include <emscripten.h>
#elif defined(_WIN32)
#include <windows.h>
#include <shellapi.h>
#elif defined(__APPLE__)
#include <TargetConditionals.h>
#include <unistd.h>   // fork, execlp, _exit
#include <sys/wait.h> // waitpid
#elif defined(__linux__)
#include <unistd.h>
#include <sys/wait.h>
#endif

#ifdef IMGUI_RICHMD_WITH_LATEX
#include "backends/latex/rich_md_latex.h"
#endif

#include "third_party/stb_image.h"

#include <string>
#include <vector>
#include <utility>
#include <map>
#include <unordered_map>
#include <memory>
#include <iostream>
#include <fstream>
#include <filesystem>
#include <cassert>
#include <cctype>
#include <cmath>
#include <cstdio>
#include <cstring>

// Small string helpers (replace fplus, to keep the library decoupled from it).
namespace
{
    std::vector<std::string> _SplitLines(const std::string& s)
    {
        std::vector<std::string> lines;
        std::string cur;
        for (char c : s)
        {
            if (c == '\n') { lines.push_back(cur); cur.clear(); }
            else cur += c;
        }
        lines.push_back(cur);
        return lines;
    }

    std::string _TrimWhitespace(const std::string& s)
    {
        const char* ws = " \t\r\n\f\v";
        size_t b = s.find_first_not_of(ws);
        if (b == std::string::npos)
            return "";
        size_t e = s.find_last_not_of(ws);
        return s.substr(b, e - b + 1);
    }

    std::string _JoinLines(const std::vector<std::string>& lines)
    {
        std::string out;
        for (size_t i = 0; i < lines.size(); ++i)
        {
            if (i > 0)
                out += '\n';
            out += lines[i];
        }
        return out;
    }

    // Opens an url in the default browser (no shell involved: the url is passed as a raw argument)
    void _OpenUrlInBrowser(const char* url)
    {
#if defined(__EMSCRIPTEN__)
        char js_command[1024];
        snprintf(js_command, 1024, "window.open(\"%s\");", url);
        emscripten_run_script(js_command);
#elif defined(_WIN32)
        ShellExecuteA(NULL, "open", url, NULL, NULL, SW_SHOWNORMAL);
#elif TARGET_OS_IPHONE
        (void)url;  // nothing on iOS
#elif TARGET_OS_OSX || defined(__linux__)
#if TARGET_OS_OSX
        const char* opener = "open";
#else
        const char* opener = "xdg-open";
#endif
        pid_t pid = fork();
        if (pid == 0)
        {
            execlp(opener, opener, url, nullptr);
            _exit(1);
        }
        else if (pid > 0)
            waitpid(pid, nullptr, 0);
#else
        (void)url;
#endif
    }

    // See imgui_md_internal.h
    std::string _Unindent(const std::string& text, bool isCode)
    {
        auto lines = _SplitLines(text);
        size_t indent = 0;
        for (const auto& line : lines)
            if (_TrimWhitespace(line).size() > 0)
            {
                indent = line.find_first_not_of(' ');
                break;
            }
        std::vector<std::string> processed;
        for (const auto& line : lines)
        {
            std::string processedLine = line.compare(0, indent, std::string(indent, ' ')) == 0 ? line.substr(indent) : line;
            if (isCode)
                processedLine.erase(processedLine.find_last_not_of(' ') + 1);
            processed.push_back(processedLine);
        }
        while (!processed.empty() && _TrimWhitespace(processed.front()).empty())
            processed.erase(processed.begin());
        while (!processed.empty() && _TrimWhitespace(processed.back()).empty())
            processed.pop_back();
        return _JoinLines(processed);
    }

    std::string _ToLower(const std::string& s)
    {
        std::string out = s;
        for (char& c : out)
            c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
        return out;
    }
}

namespace RichMd
{
    namespace Internal
    {
        std::string Unindent(const std::string& text, bool isCode) { return _Unindent(text, isCode); }
    }

    // Host services (see imgui_md_host.h)
    static HostServices gHostServices;
    // Set by OnImage_Default while an image is downloading (the renderer then draws a spinner)
    static bool gImageIsLoading = false;
    void SetHostServices(const HostServices& services) { gHostServices = services; }
    const HostServices& GetHostServices() { return gHostServices; }
#ifdef IMGUI_RICHMD_HOST_HELLO_IMGUI
    void Priv_InstallHelloImGuiHost();  // hosts/hello_imgui_host.cpp
#endif

    // Default services: the embedded assets, the file system, stderr
#ifdef IMGUI_RICHMD_EMBED_ASSETS
    extern const EmbeddedAsset imgui_richmd_embedded_assets[];
    extern const int imgui_richmd_embedded_assets_count;
#endif
#ifdef IMGUI_RICHMD_EMBED_ASSETS
    // Inflates a gzip stream (RFC 1952: header, deflate data, crc + size) with stb_image's zlib decoder
    static AssetBytes _Gunzip(const unsigned char* gz, size_t gzSize, size_t expectedSize)
    {
        if (gzSize < 18 || gz[0] != 0x1f || gz[1] != 0x8b || gz[2] != 8)
            return std::nullopt;
        unsigned char flags = gz[3];
        size_t pos = 10;
        if (flags & 4)  // FEXTRA
        {
            size_t extraLen = gz[pos] | (gz[pos + 1] << 8);
            pos += 2 + extraLen;
        }
        if (flags & 8)  // FNAME
            while (pos < gzSize && gz[pos++] != 0) {}
        if (flags & 16)  // FCOMMENT
            while (pos < gzSize && gz[pos++] != 0) {}
        if (flags & 2)  // FHCRC
            pos += 2;
        if (pos + 8 > gzSize)
            return std::nullopt;
        int outLen = 0;
        char* inflated = stbi_zlib_decode_malloc_guesssize_headerflag(
            (const char*)gz + pos, (int)(gzSize - pos - 8), (int)expectedSize, &outLen, 0 /* raw deflate */);
        if (inflated == nullptr)
            return std::nullopt;
        std::vector<uint8_t> bytes((const uint8_t*)inflated, (const uint8_t*)inflated + outLen);
        stbi_image_free(inflated);
        return bytes;
    }
#endif

    static std::string gAssetsFolder;
    void SetAssetsFolder(const std::string& folder) { gAssetsFolder = folder; }

    AssetBytes ReadAssetDefault(const std::string& assetPath)
    {
#ifdef IMGUI_RICHMD_EMBED_ASSETS
        for (int i = 0; i < imgui_richmd_embedded_assets_count; ++i)
        {
            const EmbeddedAsset& asset = imgui_richmd_embedded_assets[i];
            if (assetPath == asset.path)
                return _Gunzip(asset.data, asset.compressedSize, asset.size);
        }
#endif
        std::string path = gAssetsFolder.empty() ? assetPath : gAssetsFolder + "/" + assetPath;
        std::ifstream file(path, std::ios::binary);
        if (!file)
            return std::nullopt;
        return std::vector<uint8_t>(std::istreambuf_iterator<char>(file), std::istreambuf_iterator<char>());
    }
#ifdef IMGUI_RICHMD_WITH_LATEX
    static bool gLatexInitFailed = false;  // one-shot: no retry (and no log) storm

    // Default LaTeX renderer: MicroTeX, initialized on first use (the host's assets may not be
    // ready before the first frame), with its fonts read through the host
    static std::optional<LatexBitmap> _RenderLatexWithMicroTeX(const std::string& latex, float fontSizePx, ImU32 color, bool displayStyle)
    {
        if (!RichMd::Latex::IsInitialized())
        {
            if (gLatexInitFailed)
                return std::nullopt;
            auto clmData = gHostServices.ReadAsset("fonts/latex/latinmodern-math.clm1");
            auto otfData = gHostServices.ReadAsset("fonts/latex/latinmodern-math.otf");
            if (!clmData || !otfData)
            {
                gHostServices.Log("LaTeX font assets not found at fonts/latex/. Formulas will be shown as plain text source.");
                gLatexInitFailed = true;
                return std::nullopt;
            }
            RichMd::Latex::InitFromMemory(*clmData, *otfData);
        }
        auto style = displayStyle ? RichMd::Latex::TexStyle::Display : RichMd::Latex::TexStyle::Text;
        RichMd::Latex::RenderedFormula formula;
        try {  // an invalid formula (MicroTeX throws) falls back to its source text
            formula = RichMd::Latex::Render(latex, fontSizePx, color, style);
        } catch (const std::exception& e) {
            LatexBitmap invalid;
            invalid.error = e.what();
            return invalid;
        }
        LatexBitmap bitmap;
        bitmap.rgba = std::move(formula.Pixels);
        bitmap.width = formula.Width;
        bitmap.height = formula.Height;
        bitmap.baselineY = formula.BaselineY;
        return bitmap;
    }
#endif

#ifdef IMGUI_RICHMD_WITH_CODE_EDITOR
    static Snippets::SnippetLanguage _SnippetLanguage(const std::string& language)
    {
        std::string lower = _ToLower(language);
        if (lower == "cpp") return Snippets::SnippetLanguage::Cpp;
        if (lower == "c") return Snippets::SnippetLanguage::C;
        if (lower == "python") return Snippets::SnippetLanguage::Python;
        if (lower == "glsl") return Snippets::SnippetLanguage::Glsl;
        if (lower == "hlsl") return Snippets::SnippetLanguage::Hlsl;
        if (lower == "sql") return Snippets::SnippetLanguage::Sql;
        if (lower == "lua") return Snippets::SnippetLanguage::Lua;
        if (lower == "angelscript") return Snippets::SnippetLanguage::AngelScript;
        return Snippets::DefaultSnippetLanguage();
    }

    // Default code block with the code editor backend: a read-only snippet with syntax highlighting
    // (one editor per distinct code)
    static void _RenderCodeBlockWithEditor(const std::string& code, const std::string& language)
    {
        static std::map<std::string, Snippets::SnippetData> snippets;
        auto it = snippets.find(code);
        if (it == snippets.end())
        {
            Snippets::SnippetData snippet;
            snippet.Code = code;
            snippet.Language = _SnippetLanguage(language);
            snippet.ShowCursorPosition = false;
            snippet.ReadOnly = true;
            it = snippets.emplace(code, snippet).first;
        }
        Snippets::ShowCodeSnippet(it->second);
    }
#endif

    // Default UploadRgba: an ImTextureData registered with Dear ImGui (1.92+, backends with
    // ImGuiBackendFlags_RendererHasTextures): the backend creates the GPU texture at the next frame,
    // and destroys it when asked; the ImTextureData is freed once the backend reports it destroyed.
    static std::vector<ImTextureData*> gTexturesToFree;  // asked to be destroyed, freed once the backend did it

    static void _SweepDestroyedTextures()
    {
        for (auto it = gTexturesToFree.begin(); it != gTexturesToFree.end(); )
        {
            if ((*it)->Status == ImTextureStatus_Destroyed)
            {
                if (ImGui::GetCurrentContext())
                    ImGui::UnregisterUserTexture(*it);
                IM_DELETE(*it);
                it = gTexturesToFree.erase(it);
            }
            else
                ++it;
        }
    }

    MarkdownTexture UploadRgbaDefault(const unsigned char* rgba, int w, int h)
    {
        MarkdownTexture tex;
        if (!(ImGui::GetIO().BackendFlags & ImGuiBackendFlags_RendererHasTextures))
        {
            static bool warned = false;
            if (!warned)
                gHostServices.Log("UploadRgba: the rendering backend does not support ImTextureData (ImGuiBackendFlags_RendererHasTextures): no images, set HostServices::UploadRgba");
            warned = true;
            return tex;
        }
        ImTextureData* data = IM_NEW(ImTextureData)();
        data->Create(ImTextureFormat_RGBA32, w, h);
        memcpy(data->GetPixels(), rgba, (size_t)w * (size_t)h * 4);
        data->SetStatus(ImTextureStatus_WantCreate);
        ImGui::RegisterUserTexture(data);
        tex.ref._TexData = data;
        tex.size = ImVec2((float)w, (float)h);
        tex.keepAlive = std::shared_ptr<void>(data, [](void* p) {
            auto* d = (ImTextureData*)p;
            d->SetStatus(ImTextureStatus_WantDestroy);
            gTexturesToFree.push_back(d);
        });
        return tex;
    }

    static void _InstallDefaultHostServices()
    {
        if (!gHostServices.UploadRgba)
            gHostServices.UploadRgba = UploadRgbaDefault;
#ifdef IMGUI_RICHMD_WITH_CODE_EDITOR
        if (!gHostServices.RenderCodeBlock)
            gHostServices.RenderCodeBlock = _RenderCodeBlockWithEditor;
#endif
#ifdef IMGUI_RICHMD_WITH_LATEX
        if (!gHostServices.RenderLatex)
            gHostServices.RenderLatex = _RenderLatexWithMicroTeX;
#endif
        if (!gHostServices.ReadAsset)
            gHostServices.ReadAsset = ReadAssetDefault;
        if (!gHostServices.Log)
            gHostServices.Log = [](const std::string& message) { fprintf(stderr, "rich_md: %s\n", message.c_str()); };
    }

    // Default code block: monospaced text in a frame, with a copy button
    static void _RenderCodeBlockPlain(const std::string& code)
    {
        ImGui::PushStyleColor(ImGuiCol_ChildBg, ImGui::GetStyleColorVec4(ImGuiCol_FrameBg));
        if (ImGui::BeginChild("code", ImVec2(0.f, 0.f), ImGuiChildFlags_AutoResizeY | ImGuiChildFlags_AlwaysUseWindowPadding))
        {
            float copyWidth = ImGui::CalcTextSize("Copy").x + ImGui::GetStyle().FramePadding.x * 2.f;
            ImGui::SetCursorPosX(ImGui::GetCursorPosX() + ImGui::GetContentRegionAvail().x - copyWidth);
            if (ImGui::SmallButton("Copy"))
                ImGui::SetClipboardText(code.c_str());
            ImGui::SetCursorPosX(ImGui::GetStyle().WindowPadding.x);
            SizedFont codeFont = GetCodeFont();
            ImGui::PushFont(codeFont.font, codeFont.size);
            ImGui::TextUnformatted(code.c_str());
            ImGui::PopFont();
        }
        ImGui::EndChild();
        ImGui::PopStyleColor();
    }



    // Note: font sizes below are expressed at their nominal (96 PPI) value.
    // HighDPI scaling is applied automatically at display time by ImGui via
    // ImGui::GetStyle().FontScaleDpi (set by HelloImGui from dpiWindowSizeFactor),
    // so we must *not* pre-multiply font sizes by the DPI factor here anymore.

    namespace RichMdFonts
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
                return self.regularSize;
            else
            {
                int idxSizeFactors = headerLevel - 1;
                if (idxSizeFactors >= 6)
                    idxSizeFactors = 5;
                float multiplicationFactor = self.headerSizeFactors[idxSizeFactors];
                float fontSize = self.regularSize * multiplicationFactor;
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
                return {mFontCode, mMarkdownFontOptions.regularSize};
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
            // Adds a font from an asset (nullptr if the asset is missing). merge: into the last added font.
            static ImFont* AddFontFromAsset(const std::string& assetPath, float fontSize, bool merge)
            {
                auto bytes = GetHostServices().ReadAsset(assetPath);
                if (!bytes)
                    return nullptr;
                ImFontConfig cfg;
                cfg.MergeMode = merge;
                cfg.FontDataOwnedByAtlas = true;
                std::string stem = std::filesystem::path(assetPath).stem().string();
                snprintf(cfg.Name, sizeof(cfg.Name), "%s %d", stem.c_str(), (int)std::lround(fontSize));
                void* data = IM_ALLOC(bytes->size());
                memcpy(data, bytes->data(), bytes->size());
                return ImGui::GetIO().Fonts->AddFontFromMemoryTTF(data, (int)bytes->size(), fontSize, &cfg);
            }

            // Loads a markdown font and merges the merge fonts (options + host) into it
            ImFont* LoadMarkdownFont(const std::string& assetPath, float fontSize) const
            {
                ImFont* font = AddFontFromAsset(assetPath, fontSize, false);
                if (font == nullptr)
                    return nullptr;
                std::vector<std::string> mergeFonts = mMarkdownFontOptions.mergeFonts;
                if (GetHostServices().DefaultMergeFonts)
                    for (const auto& f : GetHostServices().DefaultMergeFonts())
                        mergeFonts.push_back(f);
                for (const auto& mergeFont : mergeFonts)
                    if (AddFontFromAsset(mergeFont, fontSize, true) == nullptr)
                        GetHostServices().Log("merge font not found: " + mergeFont);
                return font;
            }

            void LoadFonts()
            {
                const char* help =
                    "RichMd needs these assets: fonts/Roboto/Roboto-{Regular,Bold,RegularItalic,BoldItalic}.ttf, "
                    "fonts/Inconsolata-Medium.ttf and images/markdown_broken_image.png "
                    "(see imgui_bundle/imgui_bundle_assets/).";
                float defaultFontLoadingSize = 16.f;  // size at loading time (then Fonts can be resized to any size)
                for (auto emphasisVariant: AllEmphasisVariants())
                {
                    std::string fontFile = MarkdownFontOptions_FontFilename(mMarkdownFontOptions, emphasisVariant);
                    ImFont* font = LoadMarkdownFont(fontFile, defaultFontLoadingSize);
                    if (font == nullptr)
                    {
                        GetHostServices().Log("Markdown font file \"" + fontFile + "\" not found! " + help);
                        IM_ASSERT(false);
                    }
                    mFonts.push_back(std::make_pair(emphasisVariant, font) );
                }

                float fontSize = MarkdownFontOptions_FontSize(mMarkdownFontOptions, 0);
                mFontCode = LoadMarkdownFont("fonts/Inconsolata-Medium.ttf", fontSize);
                if (mFontCode == nullptr) {
                    // SourceCodePro-Regular was the old default font for code
                    // we try to load it, to be nice with older users
                    mFontCode = LoadMarkdownFont("fonts/SourceCodePro-Regular.ttf", fontSize);
                }
                if (mFontCode == nullptr) {
                    GetHostServices().Log(std::string("Markdown code font not found! ") + help);
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
        RichMdFonts::FontCollection mFontCollection;

        mutable std::map<std::string, MarkdownTexture > mLoadedImages;

        // Formula textures, keyed by source + size + color + style
        struct LatexEntry { MarkdownTexture texture; int baselineY = 0; int lastUsedFrame = 0; std::string error; };
        mutable std::map<std::string, LatexEntry> mLatexCache;
    };
    // Formulas not displayed for this many frames are dropped from the cache (lazily, when a new one is inserted)
    static const int gLatexEvictionFrames = 60;


    class MarkdownRenderer;
    struct Context;
    static Context* gCurrentContext = nullptr;

    struct Context
    {
        MarkdownOptions options;
        std::unique_ptr<MarkdownRenderer> renderer;  // created on first use (it loads the fonts)
        std::map<std::string, std::function<void(const std::string& code)>> fencedBlockRenderers;
        std::unordered_map<std::string, std::string> resolvedImports;  // text -> text with its @import resolved
        int fragmentFrame = -1;    // frame of the last Render call
        int fragmentCounter = 0;   // Render calls in this frame (seeds their ImGui ids)
        ~Context();
    };

    class MarkdownRenderer : public Renderer
    {
    private:
        MarkdownOptions *mMarkdownOptions;
        MarkdownCollection mMarkdownCollection;
    public:
        MarkdownRenderer(MarkdownOptions* markdownOptions)
            : mMarkdownOptions(markdownOptions)
            , mMarkdownCollection(markdownOptions->fontOptions)
        {
            if (mMarkdownOptions->withLatex && gHostServices.RenderLatex)
                EnableLatex();
            set_flag(MD_FLAG_PERMISSIVEAUTOLINKS, mMarkdownOptions->autolinks);
            set_flag(MD_FLAG_HARD_SOFT_BREAKS, mMarkdownOptions->hardSoftBreaks);
            set_flag(MD_FLAG_WIKILINKS, (bool)mMarkdownOptions->callbacks.OnWikiLink);
        }

        std::map<std::string, MarkdownTexture >& ImageCache()
        {
            return mMarkdownCollection.mLoadedImages;
        }

        void Render(const std::string& s)
        {
            auto defaultSizedFont = mMarkdownCollection.mFontCollection.GetDefaultFont();
            ImGui::PushFont(defaultSizedFont.font, defaultSizedFont.size);

            const char * start = s.c_str();
            const char * end = start + s.size();
            this->print(start, end);
            ImGui::PopFont();
        }

        SizedFont get_font_code()
        {
            return mMarkdownCollection.mFontCollection.GetFontCode();
        }

        SizedFont GetFont(const MarkdownFontSpec& fontSpec)
        {
            RichMdFonts::MarkdownTextStyle markdownTextStyle;
            markdownTextStyle.headerLevel = fontSpec.headerLevel;
            markdownTextStyle.markdownEmphasis.bold = fontSpec.bold;
            markdownTextStyle.markdownEmphasis.italic = fontSpec.italic;
            return mMarkdownCollection.mFontCollection.GetFont(markdownTextStyle);
        }


    private:
        Renderer::MdSizedFont get_font() const override
        {
            if (m_is_code)
            {
                // https://github.com/mekhontsev/imgui_md does not handle correctly code blocks
                // so that we will never reach here...
                auto fontCode = mMarkdownCollection.mFontCollection.GetFontCode();
                return Renderer::MdSizedFont{ fontCode.font, fontCode.size };
            }
            else
            {
                RichMdFonts::MarkdownTextStyle markdownTextStyle;
                markdownTextStyle.headerLevel = m_hlevel;
                markdownTextStyle.markdownEmphasis.bold =
                    m_is_strong || (m_is_table_header && m_table_header_highlight);
                markdownTextStyle.markdownEmphasis.italic = m_is_em;
                auto font  = mMarkdownCollection.mFontCollection.GetFont(markdownTextStyle);
                return Renderer::MdSizedFont{ font.font, font.size };
            }
        };

        void open_url() const override
        {
            if (mMarkdownOptions->callbacks.OnOpenLink)
                mMarkdownOptions->callbacks.OnOpenLink(m_href);
        }

        void open_wikilink() const override
        {
            if (mMarkdownOptions->callbacks.OnWikiLink)
                mMarkdownOptions->callbacks.OnWikiLink(m_href);
        }

        void heading(int level, const std::string& text) override
        {
            if (mMarkdownOptions->callbacks.OnHeading)
                mMarkdownOptions->callbacks.OnHeading(level, text);
        }

        image_status get_image(image_info& nfo) const override
        {
            if (! mMarkdownOptions->callbacks.OnImage)
                return image_status::none;

            gImageIsLoading = false;
            std::optional<MarkdownImage> mdImage = mMarkdownOptions->callbacks.OnImage(m_img_src);
            if (! mdImage.has_value())
                return gImageIsLoading ? image_status::loading : image_status::none;

            nfo.texture = ImTextureRef(mdImage->texture_id);
            // A texture of the image cache may not have its backend id yet (created at the next frame):
            // draw it through its ImTextureRef
            const auto& cache = mMarkdownCollection.mLoadedImages;
            auto cached = cache.find(m_img_src);
            if (cached != cache.end() && cached->second.ref.GetTexID() == mdImage->texture_id)
                nfo.texture = cached->second.ref;
            nfo.size = mdImage->size;
            nfo.uv0 = mdImage->uv0;
            nfo.uv1 = mdImage->uv1;
            return image_status::ready;
        }

        void html_div(const std::string& divClass, bool openingDiv) override
        {
            if (!mMarkdownOptions->callbacks.OnHtmlDiv)
                return;

            mMarkdownOptions->callbacks.OnHtmlDiv(divClass, openingDiv);
        }

        bool check_html(const char* str, const char* str_end) override
        {
            // Give the user callback first shot at the tag; fall through to
            // the base class so built-ins (<u>, <br>, <hr>, <sub>, <sup>,
            // <kbd>, <mark>, <img>, <div>) still work if the callback is
            // unset or returns false.
            if (mMarkdownOptions->callbacks.OnHtmlSpan)
            {
                const size_t sz = (size_t)(str_end - str);
                if (sz >= 3 && str[0] == '<')
                {
                    // Skip past '<' and optional '/'
                    const char* p = str + 1;
                    bool opening = true;
                    if (p < str_end && *p == '/') { opening = false; ++p; }
                    // Tag name ends at space, '>', or '/'
                    const char* name_end = p;
                    while (name_end < str_end && *name_end != ' ' && *name_end != '>' && *name_end != '/' && *name_end != '\t')
                        ++name_end;
                    if (name_end > p)
                    {
                        std::string tag(p, name_end);
                        if (mMarkdownOptions->callbacks.OnHtmlSpan(tag, opening))
                            return true;
                    }
                }
            }
            return Renderer::check_html(str, str_end);
        }

        bool can_use_child_windows() const override
        {
            if (!mMarkdownOptions->callbacks.CanUseChildWindows)
                return true;
            return mMarkdownOptions->callbacks.CanUseChildWindows();
        }

        void render_code_block() override
        {
            // remove the last line if empty
            std::string code = m_code_block;
            auto lines = _SplitLines(code);
            if (!lines.empty() && _TrimWhitespace(lines.back()).empty())
            {
                lines.pop_back();
                code = _JoinLines(lines);
            }

            ImGui::PushID(m_code_block.c_str());
            ImGui::SetCursorPosX(0.f);
            auto& fenced = gCurrentContext->fencedBlockRenderers;
            auto it = fenced.find(_ToLower(m_code_block_language));
            if (it != fenced.end())
                it->second(code);
            else if (gHostServices.RenderCodeBlock)
                gHostServices.RenderCodeBlock(code, m_code_block_language);
            else
                _RenderCodeBlockPlain(code);
            ImGui::PopID();
        }

        // The formula's texture, from the cache or rendered through the host.
        // nullopt: LaTeX is not available; an entry with an error: the formula is invalid (cached too,
        // so that it is parsed once). The source is shown in both cases.
        std::optional<MarkdownCollection::LatexEntry> GetLatexTexture(const std::string& latex, float fontSizePx, ImU32 color, bool displayStyle) const
        {
            if (!gHostServices.RenderLatex || !gHostServices.UploadRgba)
                return std::nullopt;
            auto& cache = mMarkdownCollection.mLatexCache;
            int frame = ImGui::GetFrameCount();
            std::string key = latex + '\x1f' + std::to_string(fontSizePx) + '\x1f' + std::to_string(color) + (displayStyle ? "D" : "T");
            auto it = cache.find(key);
            if (it != cache.end())
            {
                it->second.lastUsedFrame = frame;
                return it->second;
            }
            for (auto e = cache.begin(); e != cache.end(); )
                if (frame - e->second.lastUsedFrame > gLatexEvictionFrames)
                    e = cache.erase(e);
                else
                    ++e;
            auto bitmap = gHostServices.RenderLatex(latex, fontSizePx, color, displayStyle);
            if (!bitmap)
                return std::nullopt;
            MarkdownCollection::LatexEntry entry;
            entry.error = bitmap->error;
            if (entry.error.empty() && bitmap->width > 0 && bitmap->height > 0)
                entry.texture = gHostServices.UploadRgba(bitmap->rgba.data(), bitmap->width, bitmap->height);
            entry.baselineY = bitmap->baselineY;
            entry.lastUsedFrame = frame;
            cache[key] = entry;
            return entry;
        }

        bool get_latex_texture(const std::string& latex, float fontSizePx, ImU32 color, bool display, latex_texture& out) const override
        {
            auto entry = GetLatexTexture(latex, fontSizePx, color, display);
            if (!entry)
                return false;
            if (!entry->error.empty())
            {
                out.error = entry->error;
                return false;
            }
            out.texture = entry->texture.ref;
            out.size_px = entry->texture.size;
            out.baseline_px = (float)entry->baselineY;
            return true;
        }
    };


    Context::~Context() = default;
    static std::unique_ptr<Context> gDefaultContext;   // the one created by InitializeMarkdown

    // The current context's renderer, created on first use: this loads the fonts, which is possible
    // any time after ImGui::CreateContext() (nullptr when no context is current)
    static MarkdownRenderer* _Renderer()
    {
        if (!gCurrentContext)
            return nullptr;
        if (!gCurrentContext->renderer)
            gCurrentContext->renderer = std::make_unique<MarkdownRenderer>(&gCurrentContext->options);
        return gCurrentContext->renderer.get();
    }

// Emscripten's FETCH, when the library is linked with -sFETCH (IMGUI_RICHMD_EMSCRIPTEN_FETCH). Not
// for pyodide side modules, where Python installs a JS fetch() based OnDownloadData callback instead.
#if defined(__EMSCRIPTEN__) && defined(IMGUI_RICHMD_EMSCRIPTEN_FETCH)
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
#endif // __EMSCRIPTEN__ && IMGUI_RICHMD_EMSCRIPTEN_FETCH

    static Priv_OnInitializeMarkdownCallback gOnInitializeMarkdownCallback;

    void Priv_SetOnInitializeMarkdownCallback(Priv_OnInitializeMarkdownCallback callback)
    {
        gOnInitializeMarkdownCallback = std::move(callback);
    }

    Context* CreateContext(const MarkdownOptions& options)
    {
        Context* context = new Context();
        context->options = options;
        if (gOnInitializeMarkdownCallback)
            gOnInitializeMarkdownCallback(context->options);
#ifdef IMGUI_RICHMD_HOST_HELLO_IMGUI
        Priv_InstallHelloImGuiHost();  // fills the host services the application did not set
#endif
        _InstallDefaultHostServices();
#if defined(__EMSCRIPTEN__) && defined(IMGUI_RICHMD_EMSCRIPTEN_FETCH)
        // On Emscripten (but not pyodide), set a default download callback using
        // emscripten_fetch (unless one was already set, e.g. by Python)
        if (!context->options.callbacks.OnDownloadData)
            context->options.callbacks.OnDownloadData = EmscriptenDownloadData;
#elif defined(IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES)
        // On desktop C++, set a default download callback using libcurl
        // (unless one was already set, e.g. by Python)
        if (!context->options.callbacks.OnDownloadData)
            context->options.callbacks.OnDownloadData = DesktopDownloadData;
#endif
        if (!gCurrentContext)
            gCurrentContext = context;
        return context;
    }

    void DestroyContext(Context* context)
    {
        if (!context)
            return;
        if (gCurrentContext == context)
            gCurrentContext = nullptr;
        // Deleting the renderer clears its caches: each cached MarkdownTexture owns its GPU texture
        // (keepAlive), so the textures are freed here, while the rendering backend is still alive.
        // The options' callbacks (which may hold Python objects) go with it.
        delete context;
        _SweepDestroyedTextures();
    }

    void SetCurrentContext(Context* context) { gCurrentContext = context; }
    Context* GetCurrentContext() { return gCurrentContext; }

    void InitializeMarkdown(const MarkdownOptions& options)
    {
        if (gDefaultContext)
            return;
        gDefaultContext.reset(CreateContext(options));
        SetCurrentContext(gDefaultContext.get());
    }

    void DeInitializeMarkdown()
    {
        // gOnInitializeMarkdownCallback stays: it is set once at module import time and must
        // survive teardown/setup cycles (e.g. Pyodide playground re-runs).
        DestroyContext(gDefaultContext.release());
#ifdef IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES
        ClearDesktopDownloads();
#endif
#ifdef IMGUI_RICHMD_WITH_LATEX
        // Release MicroTeX resources (its own texture cache, unused here; safe if Init() was never called)
        if (RichMd::Latex::IsInitialized())
            RichMd::Latex::Release();
        gLatexInitFailed = false;
#endif
    }


    void RenderRaw(const std::string& markdownString)
    {
        MarkdownRenderer* renderer = _Renderer();
        if (!renderer)
        {
            std::cerr << "RichMd::Render : Markdown was not initialized!\n";
            return;
        }
        // Each fragment rendered in a frame gets its own id scope (two identical fragments must not collide)
        Context* context = gCurrentContext;
        int frame = ImGui::GetFrameCount();
        if (context->fragmentFrame != frame)
        {
            context->fragmentFrame = frame;
            context->fragmentCounter = 0;
        }
        ImGui::PushID(context->fragmentCounter++);
        renderer->Render(markdownString);
        ImGui::PopID();
        _SweepDestroyedTextures();
    }

    // A text file: from the assets, else from the file system as is (a source file rendering itself)
    static std::optional<std::string> _ReadTextAssetOrFile(const std::string& path)
    {
        AssetBytes bytes = gHostServices.ReadAsset ? gHostServices.ReadAsset(path) : ReadAssetDefault(path);
        if (!bytes)
        {
            std::ifstream ifs(path, std::ios::binary);
            if (!ifs)
                return std::nullopt;
            return std::string((std::istreambuf_iterator<char>(ifs)), std::istreambuf_iterator<char>());
        }
        return std::string(bytes->begin(), bytes->end());
    }

    // The resolved imports of a text (cached per text: the files are read once)
    static const std::string& _ResolveImportsCached(const std::string& text)
    {
        if (text.find("@import") == std::string::npos)
            return text;
        auto& cache = gCurrentContext->resolvedImports;
        auto it = cache.find(text);
        if (it != cache.end())
            return it->second;
        return cache[text] = ResolveImports(text, _ReadTextAssetOrFile);
    }

    void Render(const std::string& markdownString)
    {
        RenderRaw(_ResolveImportsCached(_Unindent(markdownString, false)));
    }

    void RenderFile(const std::string& path, const std::string& mdId, const std::string& part)
    {
        std::string directive = "@import \"" + path + "\" {" + (mdId.empty() ? "" : "md_id=" + mdId + ", ") + "part=" + part + "}";
        RenderRaw(_ResolveImportsCached(directive));
    }

    void RegisterFencedBlockRenderer(const std::string& language, std::function<void(const std::string& code)> renderer)
    {
        IM_ASSERT(gCurrentContext && "RichMd: call InitializeMarkdown first");
        gCurrentContext->fencedBlockRenderers[_ToLower(language)] = std::move(renderer);
    }

    Renderer::Style& GetStyle()
    {
        IM_ASSERT(_Renderer() && "RichMd: call InitializeMarkdown first");
        return _Renderer()->style;
    }

    std::function<void(void)> GetFontLoaderFunction()
    {
        return []() { _Renderer(); };
    }


    void OnOpenLink_Default(const std::string& url)
    {
        if (strncmp(url.c_str(), "http", strlen("http")) != 0)
        {
            std::cerr << "RichMd::OnOpenLink_Default url \"" << url << "\" should start with http!\n";
            return;
        }
        _OpenUrlInBrowser(url.c_str());
    }


    static bool _IsUrl(const std::string& path)
    {
        return path.rfind("http://", 0) == 0 || path.rfind("https://", 0) == 0;
    }

    static std::optional<MarkdownImage> _MakeMarkdownImage(const MarkdownTexture& tex)
    {
        MarkdownImage r;
        r.texture_id = tex.ref.GetTexID();  // 0 until the backend creates a registered texture (see get_image)
        r.size = tex.size;
        r.uv0 = { 0,0 };
        r.uv1 = {1,1};
        r.col_tint = { 1,1,1,1 };
        r.col_border = { 0,0,0,0 };
        return r;
    }

    // Decodes an encoded image (png, jpg, ...) and uploads it through the host
    static MarkdownTexture _UploadEncodedImage(const uint8_t* data, size_t size)
    {
        if (!gHostServices.UploadRgba)
            return {};
        int w = 0, h = 0, channels = 0;
        unsigned char* rgba = stbi_load_from_memory(data, (int)size, &w, &h, &channels, 4);
        if (rgba == nullptr)
            return {};
        MarkdownTexture tex = gHostServices.UploadRgba(rgba, w, h);
        stbi_image_free(rgba);
        return tex;
    }

    static MarkdownTexture _LoadTextureFromAsset(const std::string& assetPath)
    {
        auto bytes = gHostServices.ReadAsset(assetPath);
        if (!bytes)
            return {};
        return _UploadEncodedImage(bytes->data(), bytes->size());
    }

    static MarkdownTexture _LoadTextureFromEncodedData(const std::vector<uint8_t>& data)
    {
        return _UploadEncodedImage(data.data(), data.size());
    }

    // The broken-image texture is loaded once and kept in the image cache
    // (the cache owns the textures: a texture returned as a temporary would be
    // freed at the end of the frame, leaving a dangling id).
    static const MarkdownTexture& _BrokenImageTexture()
    {
        auto& imageCache = _Renderer()->ImageCache();
        std::string errorImage = "images/markdown_broken_image.png";
        auto it = imageCache.find(errorImage);
        if (it == imageCache.end())
            it = imageCache.emplace(errorImage, _LoadTextureFromAsset(errorImage)).first;
        return it->second;
    }

    // Cache image_path as broken (no retry on the next frames) and return the broken-image
    static std::optional<MarkdownImage> _BrokenImage(const std::string& image_path)
    {
        auto& imageCache = _Renderer()->ImageCache();
        imageCache[image_path] = _BrokenImageTexture();
        const auto& tex = imageCache.at(image_path);
        if (tex.Valid())
            return _MakeMarkdownImage(tex);
        return std::nullopt;
    }

    std::optional<MarkdownImage> OnImage_Default(const std::string& image_path)
    {
        MarkdownRenderer* renderer = _Renderer();
        if (!renderer)
        {
            std::cerr << "Did you initialize RichMd?\n";
            return std::nullopt;
        }

        auto & imageCache = renderer->ImageCache();

        // If already cached, return it
        if (imageCache.find(image_path) != imageCache.end())
            return _MakeMarkdownImage(imageCache.at(image_path));

        // Handle URL images via OnDownloadData callback
        if (_IsUrl(image_path) && gCurrentContext->options.callbacks.OnDownloadData)
        {
            auto result = gCurrentContext->options.callbacks.OnDownloadData(image_path);
            switch (result.status)
            {
            case MarkdownDownloadStatus::Ready:
                imageCache[image_path] = _LoadTextureFromEncodedData(result.data);
                return _MakeMarkdownImage(imageCache.at(image_path));

            case MarkdownDownloadStatus::Downloading:
                // The renderer draws a spinner (not cached: called again next frame)
                gImageIsLoading = true;
                return std::nullopt;

            case MarkdownDownloadStatus::Failed:
                if (!result.errorMessage.empty())
                    std::cerr << "rich_md: download failed for " << image_path << ": " << result.errorMessage << "\n";
                return _BrokenImage(image_path);

            case MarkdownDownloadStatus::NotStarted:
            default:
                return _BrokenImage(image_path);
            }
        }

        // Handle local asset images
        MarkdownTexture tex = _LoadTextureFromAsset(image_path);
        if (!tex.Valid())
            return _BrokenImage(image_path);
        imageCache[image_path] = tex;
        return _MakeMarkdownImage(imageCache.at(image_path));
    }

    ImVec4 LinkColor()
    {
        MarkdownRenderer* renderer = _Renderer();
        return renderer ? renderer->link_color() : Renderer::default_link_color();
    }

    // Same look and behaviour as the links inside markdown
    void RenderTextAsLink(const char* text, const char* url)
    {
        static const Renderer::Style defaultStyle;
        MarkdownRenderer* renderer = _Renderer();
        const Renderer::Style& style = renderer ? renderer->style : defaultStyle;
        ImGui::PushStyleColor(ImGuiCol_Text, LinkColor());
        ImGui::TextUnformatted(text);
        ImGui::PopStyleColor();
        if (Renderer::link_item(style, url))
            _OpenUrlInBrowser(url);
    }

    bool HasLatex() { return (bool)gHostServices.RenderLatex; }
    bool HasUrlImages() { return gCurrentContext && gCurrentContext->options.callbacks.OnDownloadData; }
    bool HasCodeEditor() { return (bool)gHostServices.RenderCodeBlock; }

    SizedFont GetCodeFont()
    {
        IM_ASSERT(_Renderer() && "RichMd: call InitializeMarkdown first");
        return _Renderer()->get_font_code();
    }

    SizedFont GetFont(const MarkdownFontSpec& fontSpec)
    {
        IM_ASSERT(_Renderer() && "RichMd: call InitializeMarkdown first");
        return _Renderer()->GetFont(fontSpec);
    }


    // Renders a markdown string (after having unindented its main indentation)
    void RenderUnindented(const std::string& markdownString)
    {
        Render(markdownString);
    }

} // namespace RichMdBrowser
