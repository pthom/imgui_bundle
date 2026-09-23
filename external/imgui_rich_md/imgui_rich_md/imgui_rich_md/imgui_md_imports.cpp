// Sections and imports: see the documentation of ResolveImports in imgui_md_wrapper.h
#include "imgui_md_wrapper.h"

#include <algorithm>
#include <map>
#include <set>
#include <sstream>
#include <vector>

namespace ImGuiMd
{
namespace
{
    constexpr int kMaxDepth = 8;

    std::string Trim(const std::string& s)
    {
        size_t b = s.find_first_not_of(" \t\r");
        if (b == std::string::npos)
            return "";
        size_t e = s.find_last_not_of(" \t\r");
        return s.substr(b, e - b + 1);
    }

    std::vector<std::string> SplitLines(const std::string& text)
    {
        std::vector<std::string> lines;
        std::stringstream ss(text);
        std::string line;
        while (std::getline(ss, line))
        {
            if (!line.empty() && line.back() == '\r')
                line.pop_back();
            lines.push_back(line);
        }
        return lines;
    }

    std::string JoinLines(const std::vector<std::string>& lines)
    {
        std::string r;
        for (const auto& line : lines)
            r += line + "\n";
        return r;
    }

    void TrimBlankLines(std::vector<std::string>& lines)
    {
        while (!lines.empty() && Trim(lines.back()).empty())
            lines.pop_back();
        size_t first = 0;
        while (first < lines.size() && Trim(lines[first]).empty())
            ++first;
        lines.erase(lines.begin(), lines.begin() + (long)first);
    }

    // Removes the common leading whitespace (blank lines ignored)
    void Dedent(std::vector<std::string>& lines)
    {
        size_t common = std::string::npos;
        for (const auto& line : lines)
        {
            if (Trim(line).empty())
                continue;
            size_t indent = line.find_first_not_of(" \t");
            common = std::min(common, indent);
        }
        if (common == std::string::npos || common == 0)
            return;
        for (auto& line : lines)
            line = Trim(line).empty() ? "" : line.substr(common);
    }

    // The comment prefix of a marker line ("//", "#", or "" inside a block comment)
    std::string CommentPrefix(const std::string& markerLine)
    {
        std::string t = Trim(markerLine);
        if (t.rfind("//", 0) == 0) return "//";
        if (t.rfind("#", 0) == 0) return "#";
        return "";
    }

    // "@@md#Name" (opening, name returned) / "@@/md" (closing), after an optional comment prefix
    bool IsOpeningMarker(const std::string& line, std::string& name)
    {
        std::string t = Trim(line);
        std::string prefix = CommentPrefix(line);
        t = Trim(t.substr(prefix.size()));
        if (t.rfind("@@md#", 0) != 0)
            return false;
        name = Trim(t.substr(5));
        return !name.empty();
    }
    bool IsClosingMarker(const std::string& line)
    {
        std::string t = Trim(line);
        t = Trim(t.substr(CommentPrefix(line).size()));
        return t == "@@/md";
    }

    struct Section
    {
        std::string name;
        std::vector<std::string> prose;  // markdown, comment prefix removed
        std::vector<std::string> code;   // as in the file (dedented on request)
    };

    // The sections of a source file. Error (not closed block): returns false and sets `error`.
    bool ExtractSections(const std::string& source, std::vector<Section>& sections, std::string& error)
    {
        auto lines = SplitLines(source);
        size_t i = 0;
        while (i < lines.size())
        {
            std::string name;
            if (!IsOpeningMarker(lines[i], name))
            {
                ++i;
                continue;
            }
            Section section;
            section.name = name;
            std::string prefix = CommentPrefix(lines[i]);
            size_t j = i + 1;
            bool closed = false;
            for (; j < lines.size(); ++j)
            {
                if (IsClosingMarker(lines[j]))
                {
                    closed = true;
                    break;
                }
                std::string line = lines[j];
                if (!prefix.empty())
                {
                    size_t p = line.find(prefix);
                    if (p != std::string::npos && Trim(line.substr(0, p)).empty())
                        line = line.substr(p + prefix.size());
                }
                section.prose.push_back(line);
            }
            if (!closed)
            {
                error = "block '" + name + "' is not closed (missing @@/md)";
                return false;
            }
            // one leading space after the prefix, and the common indentation
            Dedent(section.prose);
            TrimBlankLines(section.prose);
            // the code: up to the next marker, or the next top-level item (a blank line, then a line at column 0)
            std::string nextName;
            size_t k = j + 1;
            for (; k < lines.size() && !IsOpeningMarker(lines[k], nextName); ++k)
            {
                bool startsTopLevelItem = k > j + 1 && Trim(lines[k - 1]).empty() && !lines[k].empty()
                                          && lines[k][0] != ' ' && lines[k][0] != '\t' && !section.code.empty();
                if (startsTopLevelItem)
                    break;
                section.code.push_back(lines[k]);
            }
            TrimBlankLines(section.code);
            // the next section starts at the next marker
            for (; k < lines.size() && !IsOpeningMarker(lines[k], nextName); ++k) {}
            sections.push_back(section);
            i = k;
        }
        return true;
    }

    std::string LanguageOfFile(const std::string& path)
    {
        size_t dot = path.find_last_of('.');
        std::string ext = (dot == std::string::npos) ? "" : path.substr(dot + 1);
        static const std::map<std::string, std::string> table = {
            {"cpp", "cpp"}, {"cc", "cpp"}, {"cxx", "cpp"}, {"h", "cpp"}, {"hpp", "cpp"}, {"hh", "cpp"},
            {"py", "python"}, {"js", "javascript"}, {"ts", "typescript"}, {"glsl", "glsl"}, {"json", "json"},
            {"cmake", "cmake"}, {"txt", ""}, {"md", ""}};
        auto it = table.find(ext);
        return it == table.end() ? ext : it->second;
    }

    std::string DirectoryOf(const std::string& path)
    {
        size_t slash = path.find_last_of("/\\");
        return slash == std::string::npos ? "" : path.substr(0, slash + 1);
    }

    struct Directive
    {
        std::string file;    // empty: the current file
        std::string id;      // empty: every section
        std::string part = "both";
        bool dedent = true;
    };

    // `@import "file" {key=value, ...}`: false with an error when malformed
    bool ParseDirective(const std::string& line, Directive& d, std::string& error)
    {
        std::string t = Trim(line).substr(7);  // after "@import"
        t = Trim(t);
        if (!t.empty() && t[0] == '"')
        {
            size_t close = t.find('"', 1);
            if (close == std::string::npos) { error = "unterminated file name"; return false; }
            d.file = t.substr(1, close - 1);
            t = Trim(t.substr(close + 1));
        }
        if (t.empty())
            return true;
        if (t.front() != '{' || t.back() != '}') { error = "expected {key=value, ...}"; return false; }
        std::stringstream ss(t.substr(1, t.size() - 2));
        std::string item;
        while (std::getline(ss, item, ','))
        {
            item = Trim(item);
            if (item.empty())
                continue;
            size_t eq = item.find('=');
            if (eq == std::string::npos) { error = "expected key=value: " + item; return false; }
            std::string key = Trim(item.substr(0, eq)), value = Trim(item.substr(eq + 1));
            if (key == "md_id") d.id = value;
            else if (key == "part")
            {
                if (value != "prose" && value != "code" && value != "both") { error = "part must be prose, code or both"; return false; }
                d.part = value;
            }
            else if (key == "dedent")
            {
                if (value != "true" && value != "false") { error = "dedent must be true or false"; return false; }
                d.dedent = (value == "true");
            }
            else { error = "unknown attribute: " + key; return false; }
        }
        return true;
    }

    std::string ErrorSpan(const std::string& line, const std::string& reason)
    {
        std::string title = reason;
        std::replace(title.begin(), title.end(), '"', '\'');
        return "<md-error title=\"" + title + "\">`" + Trim(line) + "`</md-error>\n";
    }

    struct Resolver
    {
        const ReadTextFile& readFile;
        std::set<std::string> visiting;  // "file#id" being expanded (cycle detection)

        std::string Resolve(const std::string& text, const std::string& currentFile, int depth)
        {
            if (text.find("@import") == std::string::npos)
                return text;
            std::string out;
            for (const auto& line : SplitLines(text))
            {
                if (Trim(line).rfind("@import", 0) != 0)
                {
                    out += line + "\n";
                    continue;
                }
                // the imported content starts a new paragraph (a directive right after a line of prose)
                if (!out.empty() && out.back() == '\n' && out.size() >= 2 && out[out.size() - 2] != '\n')
                    out += "\n";
                out += ResolveDirective(line, currentFile, depth);
            }
            return out;
        }

        std::string ResolveDirective(const std::string& line, const std::string& currentFile, int depth)
        {
            Directive d;
            std::string error;
            if (!ParseDirective(line, d, error))
                return ErrorSpan(line, error);
            if (depth >= kMaxDepth)
                return ErrorSpan(line, "imports nested too deeply");
            std::string file = d.file.empty() ? currentFile : DirectoryOf(currentFile) + d.file;
            if (file.empty())
                return ErrorSpan(line, "no file given, and no current file");
            std::string key = file + "#" + d.id;
            if (visiting.count(key))
                return ErrorSpan(line, "import cycle: " + key);
            auto content = readFile(file);
            if (!content)
                return ErrorSpan(line, "file not found: " + file);

            visiting.insert(key);
            std::string r;
            if (LanguageOfFile(file).empty() && d.id.empty() && d.part == "both")
                r = Resolve(*content, file, depth + 1);  // a markdown file, as is
            else
            {
                std::vector<Section> sections;
                if (!ExtractSections(*content, sections, error))
                    r = ErrorSpan(line, error + " in " + file);
                else if (!d.id.empty())
                {
                    auto it = std::find_if(sections.begin(), sections.end(), [&](const Section& s) { return s.name == d.id; });
                    if (it == sections.end())
                        r = ErrorSpan(line, "no block '" + d.id + "' in " + file);
                    else
                        r = RenderSection(*it, d, file, depth);
                }
                else
                    for (const auto& s : sections)
                        r += RenderSection(s, d, file, depth);
            }
            visiting.erase(key);
            return r;
        }

        std::string RenderSection(const Section& s, const Directive& d, const std::string& file, int depth)
        {
            std::string r;
            if (d.part != "code")
                r += Resolve(JoinLines(s.prose), file, depth + 1) + "\n";
            if (d.part != "prose" && !s.code.empty())
            {
                auto code = s.code;
                if (d.dedent)
                    Dedent(code);
                r += "```" + LanguageOfFile(file) + "\n" + JoinLines(code) + "```\n\n";
            }
            return r;
        }
    };
}  // namespace

std::string ResolveImports(const std::string& markdown, const ReadTextFile& readFile, const std::string& currentFile)
{
    Resolver resolver{readFile, {}};
    return resolver.Resolve(markdown, currentFile, 0);
}

}  // namespace ImGuiMd
