#include "immapp/markdown_host.h"
#include "immapp/snippets.h"
#include "imgui_md_wrapper/imgui_md_host.h"

#include <algorithm>
#include <cctype>
#include <map>
#include <string>

namespace ImmApp
{
    static Snippets::SnippetLanguage _SnippetLanguage(const std::string& language)
    {
        std::string lower = language;
        std::transform(lower.begin(), lower.end(), lower.begin(), [](unsigned char c) { return (char)std::tolower(c); });
        if (lower == "cpp") return Snippets::SnippetLanguage::Cpp;
        if (lower == "c") return Snippets::SnippetLanguage::C;
        if (lower == "python") return Snippets::SnippetLanguage::Python;
        if (lower == "glsl") return Snippets::SnippetLanguage::Glsl;
        if (lower == "sql") return Snippets::SnippetLanguage::Sql;
        if (lower == "lua") return Snippets::SnippetLanguage::Lua;
        if (lower == "angelscript") return Snippets::SnippetLanguage::AngelScript;
        return Snippets::DefaultSnippetLanguage();
    }

    // Code blocks rendered with a read-only ImGuiColorTextEdit (one editor per distinct code)
    static void _RenderCodeBlockWithSnippet(const std::string& code, const std::string& language)
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

    void InstallMarkdownHostServices()
    {
        ImGuiMd::HostServices services = ImGuiMd::GetHostServices();
        if (!services.RenderCodeBlock)
            services.RenderCodeBlock = _RenderCodeBlockWithSnippet;
        ImGuiMd::SetHostServices(services);
    }
}
