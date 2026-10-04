#include "api_index.h"
#include "nlohmann/json.hpp"
#include <algorithm>
#include <cctype>
#include <fstream>
#include <map>
#include <unordered_map>
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#include <sys/stat.h>  // mkdir
#endif

namespace
{
    struct ModuleSlot
    {
        ApiIndexState state = ApiIndexState::NotLoaded;
        ApiModule module;
    };

    // The modules by file name ("imgui", "imgui.internal"); a std::map keeps the ApiModule addresses stable
    std::map<std::string, ModuleSlot> g_modules;
    // The lookup keys, in both languages, qualified and bare: "imgui.button", "button", "ImGui::Button", "Button"
    std::unordered_multimap<std::string, ApiRef> g_keys;

    std::string BareCpp(const std::string& cppName)
    {
        size_t pos = cppName.rfind("::");
        return pos == std::string::npos ? cppName : cppName.substr(pos + 2);
    }

    void AddKeys(const ApiRef& ref)
    {
        const ApiEntry& e = *ref.entry;
        std::vector<std::string> keys = {e.name, ref.PyName()};
        if (ref.owner)
            keys.push_back(ref.owner->name + "." + e.name);
        if (!e.cppName.empty())
        {
            keys.push_back(e.cppName);
            keys.push_back(BareCpp(e.cppName));
        }
        for (const auto& key : keys)
        {
            // one key per entry
            auto range = g_keys.equal_range(key);
            bool present = std::any_of(range.first, range.second, [&](const auto& kv) { return kv.second == ref; });
            if (!present)
                g_keys.emplace(key, ref);
        }
    }

    void IndexModule(const ApiModule& module)
    {
        for (const auto& entry : module.entries)
        {
            ApiRef ref{&module, &entry, nullptr};
            AddKeys(ref);
            for (const auto& child : entry.children)
                AddKeys(ApiRef{&module, &child, &entry});
        }
    }

    ApiEntry ParseEntry(const nlohmann::json& j)
    {
        ApiEntry e;
        e.kind = j.value("kind", "");
        e.name = j.value("name", "");
        e.cppName = j.value("cpp_name", "");
        e.py = j.value("py", "");
        e.cpp = j.value("cpp", "");
        e.doc = j.value("doc", "");
        e.note = j.value("note", "");
        e.bindingsNote = j.value("bindings_note", "");
        e.value = j.value("value", "");
        e.section = j.value("section", "");
        e.sectionText = j.value("section_text", "");
        e.partText = j.value("part_text", "");
        e.part = j.value("part", "");
        e.header = j.value("header", "");
        e.anchor = j.value("anchor", "");
        e.cppAnchor = j.value("cpp_anchor", "");
        if (j.contains("children"))
            for (const auto& c : j["children"])
                e.children.push_back(ParseEntry(c));
        return e;
    }

    void ParseModule(ModuleSlot& slot, const std::string& content)
    {
        nlohmann::json j = nlohmann::json::parse(content, nullptr, false);
        if (j.is_discarded() || !j.contains("entries"))
        {
            slot.state = ApiIndexState::Failed;
            return;
        }
        ApiModule& m = slot.module;
        m.module = j.value("module", "");
        m.pyAlias = j.value("py_alias", "");
        m.cppNamespace = j.value("cpp_namespace", "");
        m.url = j.value("url", "");
        m.cppUrl = j.value("cpp_url", "");
        for (const auto& e : j["entries"])
            m.entries.push_back(ParseEntry(e));
        IndexModule(m);
        slot.state = ApiIndexState::Loaded;
    }

    void LoadFromFile(ModuleSlot& slot, const std::string& path)
    {
        std::ifstream f(path);
        if (!f)
        {
            slot.state = ApiIndexState::Failed;
            return;
        }
        std::string content(std::istreambuf_iterator<char>(f), {});
        ParseModule(slot, content);
    }

#ifdef __EMSCRIPTEN__
    std::map<std::string, std::string> g_pendingFetches;  // MEMFS path -> module name

    void OnWgetDone(const char* arg, bool success)
    {
        std::string key(arg);
        auto it = g_pendingFetches.find(key);
        if (it == g_pendingFetches.end())
            it = g_pendingFetches.find("/" + key);
        if (it == g_pendingFetches.end())
            return;
        std::string name = it->second;
        g_pendingFetches.erase(it);
        ModuleSlot& slot = g_modules[name];
        if (!success)
        {
            slot.state = ApiIndexState::Failed;
            return;
        }
        LoadFromFile(slot, (arg[0] == '/') ? key : ("/" + key));
    }
    void OnWgetLoad(const char* path) { OnWgetDone(path, true); }
    void OnWgetError(const char* path) { OnWgetDone(path, false); }
#endif

    void StartLoad(const std::string& demoCodeDir, const std::string& name)
    {
        ModuleSlot& slot = g_modules[name];
        if (slot.state != ApiIndexState::NotLoaded)
            return;
        slot.state = ApiIndexState::Loading;
#ifdef __EMSCRIPTEN__
        (void)demoCodeDir;
        static bool dirCreated = false;
        if (!dirCreated)
        {
            mkdir("/demo_code", 0777);
            mkdir("/demo_code/api_index", 0777);
            dirCreated = true;
        }
        std::string url = "demo_code/api_index/" + name + ".json";
        std::string localPath = "/" + url;
        g_pendingFetches[localPath] = name;
        emscripten_async_wget(url.c_str(), localPath.c_str(), OnWgetLoad, OnWgetError);
#else
        if (demoCodeDir.empty())
            slot.state = ApiIndexState::Failed;
        else
            LoadFromFile(slot, demoCodeDir + "/api_index/" + name + ".json");
#endif
    }

    bool IsIdentifierChar(char c) { return std::isalnum((unsigned char)c) || c == '_'; }

    // The parts of a qualified name; a selection is cut at its first other character ("ImGui::Button(" -> ImGui, Button)
    std::vector<std::string> SplitQualified(const std::string& identifier)
    {
        std::vector<std::string> parts;
        std::string current;
        size_t first = identifier.find_first_not_of(" \t");
        for (size_t i = (first == std::string::npos ? 0 : first); i < identifier.size(); ++i)
        {
            char c = identifier[i];
            if (c == '.' || c == ':')
            {
                if (!current.empty())
                    parts.push_back(current);
                current.clear();
            }
            else if (IsIdentifierChar(c))
                current += c;
            else
                break;
        }
        if (!current.empty())
            parts.push_back(current);
        return parts;
    }

    std::vector<ApiRef> Hits(const std::string& key, const std::vector<const ApiModule*>& modules)
    {
        std::vector<ApiRef> hits;
        auto range = g_keys.equal_range(key);
        for (auto it = range.first; it != range.second; ++it)
            if (std::find(modules.begin(), modules.end(), it->second.module) != modules.end())
                hits.push_back(it->second);
        return hits;
    }
}


std::string ApiRef::PyName() const
{
    std::string prefix = module->pyAlias.empty() ? "" : module->pyAlias + ".";
    if (owner)
        return prefix + owner->name + "." + entry->name;
    return prefix + entry->name;
}

std::string ApiRef::CppName() const
{
    if (!entry->cppName.empty())
        return entry->cppName;
    if (owner && !owner->cppName.empty())
        return owner->cppName + "::" + entry->name;
    return entry->name;
}

std::string ApiRef::Url() const
{
    const ApiEntry* anchored = entry->anchor.empty() && owner ? owner : entry;
    return anchored->anchor.empty() ? module->url : module->url + "#" + anchored->anchor;
}

std::string ApiRef::CppUrl() const
{
    if (module->cppUrl.empty())
        return "";
    const ApiEntry* anchored = entry->cppAnchor.empty() && owner ? owner : entry;
    return anchored->cppAnchor.empty() ? "" : module->cppUrl + "#" + anchored->cppAnchor;
}


ApiIndexState ApiIndex_Load(const std::string& demoCodeDir, const std::vector<std::string>& modules)
{
    ApiIndexState result = ApiIndexState::Loaded;
    for (const auto& name : modules)
    {
        StartLoad(demoCodeDir, name);
        ApiIndexState state = g_modules[name].state;
        if (state == ApiIndexState::Loading && result != ApiIndexState::Failed)
            result = ApiIndexState::Loading;
        if (state == ApiIndexState::Failed)
            result = ApiIndexState::Failed;
    }
    if (modules.empty())
        result = ApiIndexState::Failed;
    return result;
}

std::vector<const ApiModule*> ApiIndex_Modules(const std::vector<std::string>& modules)
{
    std::vector<const ApiModule*> out;
    for (const auto& name : modules)
    {
        auto it = g_modules.find(name);
        if (it != g_modules.end() && it->second.state == ApiIndexState::Loaded)
            out.push_back(&it->second.module);
    }
    return out;
}

std::vector<ApiRef> ApiIndex_Lookup(const std::vector<std::string>& modules, const std::string& identifier)
{
    auto loaded = ApiIndex_Modules(modules);
    auto parts = SplitQualified(identifier);
    if (loaded.empty() || parts.empty())
        return {};

    // The longest qualified name first, then its suffixes: "imgui.ImDrawList.add_line", "ImDrawList.add_line",
    // "add_line" (the receiver of a method call is unknown: "draw_list.add_line" matches by its suffixes)
    for (size_t start = 0; start < parts.size(); ++start)
    {
        std::string dotted, scoped;
        for (size_t i = start; i < parts.size(); ++i)
        {
            dotted += (i > start ? "." : "") + parts[i];
            scoped += (i > start ? "::" : "") + parts[i];
        }
        auto hits = Hits(dotted, loaded);
        if (dotted != scoped)
            for (const auto& h : Hits(scoped, loaded))
                if (std::find(hits.begin(), hits.end(), h) == hits.end())
                    hits.push_back(h);
        // A struct and its constructor share a name: the struct is the answer
        hits.erase(std::remove_if(hits.begin(), hits.end(), [&](const ApiRef& h) {
            return h.owner != nullptr && std::any_of(hits.begin(), hits.end(),
                                                     [&](const ApiRef& o) { return o.entry == h.owner; });
        }), hits.end());
        if (!hits.empty())
            return hits;
    }

    // A Python alias of an enum (SliderFlags for SliderFlags_)
    const std::string& last = parts.back();
    {
        auto hits = Hits(last + "_", loaded);
        if (!hits.empty())
            return hits;
    }
    // A C++ class or enum whose Python name lost the library's prefix (ImGuiIO -> IO, ImGuiWindowFlags -> WindowFlags_)
    for (const ApiModule* m : loaded)
    {
        const std::string& ns = m->cppNamespace;
        if (ns.empty() || last.size() <= ns.size() || last.compare(0, ns.size(), ns) != 0)
            continue;
        std::string rest = last.substr(ns.size());
        for (const auto& candidate : {rest, rest + "_"})
        {
            auto hits = Hits(candidate, loaded);
            if (!hits.empty())
                return hits;
        }
    }
    return {};
}

std::string ApiIndex_IdentifierAt(const std::string& line, size_t column)
{
    // Just after a word counts too: a double-click or a search leaves the cursor there
    if ((column >= line.size() || !IsIdentifierChar(line[column])) && column > 0 && column <= line.size()
        && IsIdentifierChar(line[column - 1]))
        --column;
    if (column >= line.size() || !IsIdentifierChar(line[column]))
        return "";
    size_t start = column, end = column;
    while (start > 0 && IsIdentifierChar(line[start - 1]))
        --start;
    while (end < line.size() && IsIdentifierChar(line[end]))
        ++end;
    // The qualifiers on the left: "ImGui::" or "io."; a word on the right after "." or "::"
    while (true)
    {
        size_t sep = 0;
        if (start >= 1 && line[start - 1] == '.')
            sep = 1;
        else if (start >= 2 && line[start - 1] == ':' && line[start - 2] == ':')
            sep = 2;
        if (sep == 0 || start - sep == 0 || !IsIdentifierChar(line[start - sep - 1]))
            break;
        start -= sep;
        while (start > 0 && IsIdentifierChar(line[start - 1]))
            --start;
    }
    while (true)
    {
        size_t sep = 0;
        if (end < line.size() && line[end] == '.')
            sep = 1;
        else if (end + 1 < line.size() && line[end] == ':' && line[end + 1] == ':')
            sep = 2;
        if (sep == 0 || end + sep >= line.size() || !IsIdentifierChar(line[end + sep]))
            break;
        end += sep;
        while (end < line.size() && IsIdentifierChar(line[end]))
            ++end;
    }
    return line.substr(start, end - start);
}

std::string ApiIndex_FirstSentence(const std::string& doc)
{
    std::string text;
    for (char c : doc)
        text += (c == '\n' || c == '\t') ? ' ' : c;
    size_t dot = text.find(". ");
    if (dot != std::string::npos)
        text = text.substr(0, dot + 1);
    if (text.size() > 160)
        text = text.substr(0, 157) + "...";
    return text;
}
