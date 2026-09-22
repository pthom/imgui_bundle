// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui_md_wrapper.h"
#include "imgui_md_host.h"
#ifdef IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES
#include "imgui_md_url_download.h"
#endif

#include "immapp/snippets.h"

#include "imgui.h"
#include "imgui_md/imgui_md.h"

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
#include "imgui_microtex/imgui_microtex.h"
#endif

#include "stb_image.h"

#include <string>
#include <vector>
#include <utility>
#include <map>
#include <memory>
#include <iostream>
#include <fstream>
#include <filesystem>
#include <cassert>
#include <cctype>
#include <cmath>
#include <cstdio>
#include <cstring>

// Small string helpers (replace fplus, to keep imgui_md decoupled from it).
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

    // Removes the common indentation (that of the first non-empty line) and the leading / trailing empty lines.
    // Trailing spaces are kept: two of them are a hard line break in markdown.
    std::string _Unindent(const std::string& text)
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
            processed.push_back(line.compare(0, indent, std::string(indent, ' ')) == 0 ? line.substr(indent) : line);
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

ImVec4 LinkColor(); // See imgui_md.cpp

namespace ImGuiMd
{
    // Host services (see imgui_md_host.h)
    static HostServices gHostServices;
    void SetHostServices(const HostServices& services) { gHostServices = services; }
    const HostServices& GetHostServices() { return gHostServices; }
#ifdef IMGUI_RICHMD_HOST_HELLO_IMGUI
    void Priv_InstallHelloImGuiHost();  // hosts/hello_imgui_host.cpp
#endif

    // Default services: plain file system, stderr
    static std::optional<std::vector<uint8_t>> _ReadAssetFromFileSystem(const std::string& assetPath)
    {
        std::ifstream file(assetPath, std::ios::binary);
        if (!file)
            return std::nullopt;
        return std::vector<uint8_t>(std::istreambuf_iterator<char>(file), std::istreambuf_iterator<char>());
    }
    static std::optional<std::string> _AssetFilePathFromFileSystem(const std::string& assetPath)
    {
        if (!std::filesystem::exists(assetPath))
            return std::nullopt;
        return assetPath;
    }
    static void _InstallDefaultHostServices()
    {
        if (!gHostServices.ReadAsset)
            gHostServices.ReadAsset = _ReadAssetFromFileSystem;
        if (!gHostServices.AssetFilePath)
            gHostServices.AssetFilePath = _AssetFilePathFromFileSystem;
        if (!gHostServices.Log)
            gHostServices.Log = [](const std::string& message) { fprintf(stderr, "imgui_md: %s\n", message.c_str()); };
    }

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
            _OpenUrlInBrowser(url);
    }


    // Note: font sizes below are expressed at their nominal (96 PPI) value.
    // HighDPI scaling is applied automatically at display time by ImGui via
    // ImGui::GetStyle().FontScaleDpi (set by HelloImGui from dpiWindowSizeFactor),
    // so we must *not* pre-multiply font sizes by the DPI factor here anymore.

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
                    "ImGuiMd needs these assets: fonts/Roboto/Roboto-{Regular,Bold,RegularItalic,BoldItalic}.ttf, "
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
        ImGuiMdFonts::FontCollection mFontCollection;

        mutable std::map<std::string, MarkdownTexture > mLoadedImages;
    };


    class MarkdownRenderer : public imgui_md
    {
    private:
        MarkdownOptions *mMarkdownOptions;
        MarkdownCollection mMarkdownCollection;
        std::map<std::string, Snippets::SnippetData> mSnippets;
    public:
        MarkdownRenderer(MarkdownOptions* markdownOptions)
            : mMarkdownOptions(markdownOptions)
            , mMarkdownCollection(markdownOptions->fontOptions)
        {
#ifdef IMGUI_RICHMD_WITH_LATEX
            if (mMarkdownOptions->withLatex)
                EnableLatex();
#endif
            set_flag(MD_FLAG_PERMISSIVEAUTOLINKS, mMarkdownOptions->autolinks);
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
                markdownTextStyle.markdownEmphasis.bold =
                    m_is_strong || (m_is_table_header && m_table_header_highlight);
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

            // Image size adaptive depending on the resolution scale.
            // Unlike fonts, ImGui::Image() draw sizes are not scaled by FontScaleDpi,
            // so we apply the DPI factor explicitly to match the (DPI-scaled) text.
            {
                float k = ImGui::GetStyle().FontScaleDpi;
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
            return imgui_md::check_html(str, str_end);
        }

        bool can_use_child_windows() const override
        {
            if (!mMarkdownOptions->callbacks.CanUseChildWindows)
                return true;
            return mMarkdownOptions->callbacks.CanUseChildWindows();
        }

        void render_code_block() override
        {
            auto code_without_last_empty_lines = [](const std::string code_)
            {
                // remove last line if empty
                std::string code = code_;
                {
                    auto lines = _SplitLines(code);
                    if (lines.size() > 0)
                    {
                        if (_TrimWhitespace(lines.back()).size() == 0)
                            lines.pop_back();
                        code = _JoinLines(lines);
                    }
                }
                return code;
            };

            ImGui::PushID(m_code_block.c_str());
            if (mSnippets.find(m_code_block) == mSnippets.end())
            {
                mSnippets[m_code_block] = Snippets::SnippetData();
                auto& snippet = mSnippets[m_code_block];
                snippet.Code = code_without_last_empty_lines(m_code_block);

                // set language
                if (_ToLower(m_code_block_language) == "cpp")
                    snippet.Language = Snippets::SnippetLanguage::Cpp;
                else if (_ToLower(m_code_block_language) == "c")
                    snippet.Language = Snippets::SnippetLanguage::C;
                else if (_ToLower(m_code_block_language) == "python")
                    snippet.Language = Snippets::SnippetLanguage::Python;
                else if (_ToLower(m_code_block_language) == "glsl")
                    snippet.Language = Snippets::SnippetLanguage::Glsl;
                else if (_ToLower(m_code_block_language) == "sql")
                    snippet.Language = Snippets::SnippetLanguage::Sql;
                else if (_ToLower(m_code_block_language) == "lua")
                    snippet.Language = Snippets::SnippetLanguage::Lua;
                else if (_ToLower(m_code_block_language) == "angelscript")
                    snippet.Language = Snippets::SnippetLanguage::AngelScript;

                snippet.ShowCursorPosition = false;
                snippet.ReadOnly = true;
            }

            ImGui::SetCursorPosX(0.f);
            auto& snippet = mSnippets[m_code_block];
            Snippets::ShowCodeSnippet(snippet);

            ImGui::PopID();
        }

#ifdef IMGUI_RICHMD_WITH_LATEX
        // Lazy-initialize MicroTeX on first LaTeX span.
        // We cannot do this in InitializeMarkdown() because the host's asset
        // system may not be ready until after the fonts have loaded / backend started.
        // Lazy MicroTeX init. Defensive: if the font assets are missing
        // (corrupted install, or Pyodide download failed, etc.), log a
        // warning once and leave MicroTeX uninitialized. The SPAN_LATEXMATH
        // handlers below check IsInitialized() and fall back to rendering
        // the LaTeX source as plain text instead of crashing on the asset
        // lookup IM_ASSERT.
        void EnsureMicroTeXInitialized()
        {
            if (ImGuiMicroTeX::IsInitialized())
                return;
            // One-shot failure flag: if init failed once, don't keep retrying
            // (and re-logging) on every render.
            if (mLatexInitFailed)
                return;
            // MicroTeX reads its fonts from files: ask the host for their paths
            auto clmFile = gHostServices.AssetFilePath("fonts/latex/latinmodern-math.clm1");
            auto otfFile = gHostServices.AssetFilePath("fonts/latex/latinmodern-math.otf");
            if (!clmFile || !otfFile)
            {
                gHostServices.Log("LaTeX font assets not found at fonts/latex/. Formulas will be shown as plain text source.");
                mLatexInitFailed = true;
                return;
            }
            ImGuiMicroTeX::Init(*clmFile, *otfFile);
        }

        // Set true once if MicroTeX init has failed, to avoid retry storms.
        bool mLatexInitFailed = false;

        // Returns physical-pixels-per-logical-pixel for the current display.
        // On macOS retina this is 2.0; on standard DPI displays it is 1.0.
        // Used to rasterize formulas at the framebuffer pixel density and
        // display them at logical size (sharp on HiDPI screens).
        static float PixelScale()
        {
            float s = ImGui::GetIO().DisplayFramebufferScale.y;
            return (s > 0.01f) ? s : 1.0f;
        }

        void SPAN_LATEXMATH(bool e) override
        {
            imgui_md::SPAN_LATEXMATH(e);
            if (e)
                return;
            EnsureMicroTeXInitialized();
            if (!ImGuiMicroTeX::IsInitialized())
            {
                // Fallback: show the original LaTeX source inline, with the
                // delimiters, so the user recognizes it as a math expression.
                std::string fallback = "$" + m_latex_buffer + "$";
                ImGui::TextUnformatted(fallback.c_str());
                ImGui::SameLine(0.0f, 0.0f);
                return;
            }
            // DPI-aware: rasterize at framebuffer density, display at logical size.
            float pixelScale = PixelScale();
            float logicalFontSize = ImGui::GetFontSize();
            float physicalFontSize = logicalFontSize * pixelScale;
            ImU32 color = ImGui::GetColorU32(ImGuiCol_Text);
            auto tex = ImGuiMicroTeX::RenderToTexture(m_latex_buffer, physicalFontSize, color, ImGuiMicroTeX::TexStyle::Text);
            ImTextureID texId = tex.TextureId();
            if (texId == (ImTextureID)0)
                return;
            // tex.Width/Height/BaselineY are in physical pixels (the bitmap was
            // rasterized at the higher density). Convert to logical pixels for
            // ImGui layout.
            float logicalW = (float)tex.Width / pixelScale;
            float logicalH = (float)tex.Height / pixelScale;
            float logicalBaselineY = (float)tex.BaselineY / pixelScale;
            // Vertically align the formula so its baseline matches the surrounding text.
            // ImGui::Text() draws starting at cursor.y, with the typographic baseline
            // at cursor.y + baked->Ascent. To put the formula's baseline at the same
            // position, the image top must be at cursor.y + textAscent - logicalBaselineY.
            ImFontBaked* baked = ImGui::GetFontBaked();
            float textAscent = baked ? baked->Ascent : logicalFontSize * 0.8f;
            float savedY = ImGui::GetCursorPosY();
            ImGui::SetCursorPosY(savedY + textAscent - logicalBaselineY);
            ImGui::Image(texId, ImVec2(logicalW, logicalH));
            ImGui::SameLine(0.0f, 0.0f);
            // Restore cursor Y so subsequent inline content lands on the original line.
            ImGui::SetCursorPosY(savedY);
        }

        void SPAN_LATEXMATH_DISPLAY(bool e) override
        {
            imgui_md::SPAN_LATEXMATH_DISPLAY(e);
            if (e)
                return;
            EnsureMicroTeXInitialized();
            if (!ImGuiMicroTeX::IsInitialized())
            {
                // Fallback: show the original LaTeX source on its own line.
                ImGui::NewLine();
                std::string fallback = "$$" + m_latex_buffer + "$$";
                ImGui::TextUnformatted(fallback.c_str());
                ImGui::NewLine();
                return;
            }
            float pixelScale = PixelScale();
            float logicalFontSize = ImGui::GetFontSize();
            float physicalFontSize = logicalFontSize * pixelScale;
            ImU32 color = ImGui::GetColorU32(ImGuiCol_Text);
            // Note: ImGuiMicroTeX::TexStyle::Display renders a bit bigger than ImGuiMicroTeX::TexStyle::Text
            auto tex = ImGuiMicroTeX::RenderToTexture(m_latex_buffer, physicalFontSize, color, ImGuiMicroTeX::TexStyle::Display);
            ImTextureID texId = tex.TextureId();
            if (texId == (ImTextureID)0)
                return;
            float logicalW = (float)tex.Width / pixelScale;
            float logicalH = (float)tex.Height / pixelScale;
            // Display math: centered on its own line.
            ImGui::NewLine();
            float avail = ImGui::GetContentRegionAvail().x;
            float padX = (avail - logicalW) * 0.5f;
            if (padX > 0.0f)
                ImGui::SetCursorPosX(ImGui::GetCursorPosX() + padX);
            ImGui::Image(texId, ImVec2(logicalW, logicalH));
            ImGui::NewLine();
        }
#endif

    };


    // Global renderer
    std::unique_ptr<MarkdownRenderer> gMarkdownRenderer;

// Not for pyodide: emscripten's FETCH cannot run in a pyodide side module
// (no fetch JS glue in pyodide's main module); Python installs a JS fetch()
// based OnDownloadData callback instead (see _imgui_md_image_loader.py).
#if defined(__EMSCRIPTEN__) && !defined(IMGUI_BUNDLE_BUILD_PYODIDE)
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
#endif // __EMSCRIPTEN__ && !IMGUI_BUNDLE_BUILD_PYODIDE

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
        // reset() (not release()): actually destroy the renderer so its image
        // cache is cleared. Each cached MarkdownTexture owns its GPU texture via
        // keepAlive, so destroying the cache frees the textures here — while the
        // rendering backend is still live (relevant when running outside
        // HelloImGui::Run(), where Priv_TearDown does not run).
        gMarkdownRenderer.reset();
        gMarkdownWasInitialized = false;
#ifdef IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES
        ClearDesktopDownloads();
#endif
#ifdef IMGUI_RICHMD_WITH_LATEX
        // Release MicroTeX resources (textures, FreeType, etc.)
        // Safe to call even if Init() was never called.
        if (ImGuiMicroTeX::IsInitialized())
            ImGuiMicroTeX::Release();
#endif
    }

    void InitializeMarkdown(const MarkdownOptions& options)
    {
        if (gMarkdownWasInitialized)
            return;

        gMarkdownOptions = options;
        if (gOnInitializeMarkdownCallback)
            gOnInitializeMarkdownCallback(gMarkdownOptions);
#ifdef IMGUI_RICHMD_HOST_HELLO_IMGUI
        Priv_InstallHelloImGuiHost();  // fills the host services the application did not set
#endif
        _InstallDefaultHostServices();
#if defined(__EMSCRIPTEN__) && !defined(IMGUI_BUNDLE_BUILD_PYODIDE)
        // On Emscripten (but not pyodide), set a default download callback using
        // emscripten_fetch (unless one was already set, e.g. by Python)
        if (!gMarkdownOptions.callbacks.OnDownloadData)
            gMarkdownOptions.callbacks.OnDownloadData = EmscriptenDownloadData;
#elif defined(IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES)
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
        _OpenUrlInBrowser(url.c_str());
    }


    static bool _IsUrl(const std::string& path)
    {
        return path.rfind("http://", 0) == 0 || path.rfind("https://", 0) == 0;
    }

    static std::optional<MarkdownImage> _MakeMarkdownImage(const MarkdownTexture& tex)
    {
        MarkdownImage r;
        r.texture_id = tex.id;
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

    // The broken-image texture is loaded once and kept in the image cache
    // (the cache owns the textures: a texture returned as a temporary would be
    // freed at the end of the frame, leaving a dangling id).
    static const MarkdownTexture& _BrokenImageTexture()
    {
        auto& imageCache = gMarkdownRenderer->ImageCache();
        std::string errorImage = "images/markdown_broken_image.png";
        auto it = imageCache.find(errorImage);
        if (it == imageCache.end())
            it = imageCache.emplace(errorImage, _LoadTextureFromAsset(errorImage)).first;
        return it->second;
    }

    // Cache image_path as broken (no retry on the next frames) and return the broken-image
    static std::optional<MarkdownImage> _BrokenImage(const std::string& image_path)
    {
        auto& imageCache = gMarkdownRenderer->ImageCache();
        imageCache[image_path] = _BrokenImageTexture();
        const auto& tex = imageCache.at(image_path);
        if (tex.Valid())
            return _MakeMarkdownImage(tex);
        return std::nullopt;
    }

    std::optional<MarkdownImage> OnImage_Default(const std::string& image_path)
    {
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
                imageCache[image_path] = _LoadTextureFromEncodedData(result.data);
                return _MakeMarkdownImage(imageCache.at(image_path));

            case MarkdownDownloadStatus::Downloading:
                // Show spinner while downloading (don't cache - will be called again next frame)
                _DrawLoadingSpinner();
                return std::nullopt;  // nullopt so SPAN_IMG doesn't also draw an image

            case MarkdownDownloadStatus::Failed:
                if (!result.errorMessage.empty())
                    std::cerr << "imgui_md: download failed for " << image_path << ": " << result.errorMessage << "\n";
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
        Render(_Unindent(markdownString));
    }

} // namespace ImGuiMdBrowser
