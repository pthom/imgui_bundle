#pragma once
#include <string>
#include <vector>

// The API index: the entries of a library's modules, read from demo_code/api_index/<module>.json (written by
// ci_scripts/api_pages.py from the Python stubs, with the pages' anchors), and looked up from an identifier of the code.

struct ApiEntry
{
    std::string kind;          // function, method, class, enum, attribute, member, typedef
    std::string name;          // the Python name: button, ImDrawList, add_line, no_title_bar
    std::string cppName;       // the C++ name: ImGui::Button, ImDrawList::AddLine, ImGuiWindowFlags_NoTitleBar
    std::string py;            // the Python signature(s)
    std::string cpp;           // the C++ signature(s)
    std::string doc;           // the header's comment
    std::string note;          // a trailing comment (attributes, members)
    std::string bindingsNote;  // litgen's note for Python users
    std::string value;         // an enum member's value
    std::string section, part, header;
    std::string sectionText;   // the section's intro (the header's comments under its title), on its first entry
    std::string partText;      // the part's intro (the banner's lines under its mark), on its first entry
    std::string anchor, cppAnchor;  // the ids on the module's page and on its C++ view
    std::string typedefPy, typedefCpp;  // an enum's typedef: the type of its values in the API (ImGuiWindowFlags)
    std::vector<std::string> aliases;   // other names that lead to the entry (an enum's typedef, in both languages)
    std::vector<ApiEntry> children;
};

struct ApiModule
{
    std::string module;        // imgui_bundle.imgui
    std::string pyAlias;       // imgui
    std::string cppNamespace;  // ImGui
    std::string url, cppUrl;   // the module's page and its C++ view
    std::vector<ApiEntry> entries;
};

// A hit of a lookup: the entry, its owner when it is a method, an attribute or a member, and its module
struct ApiRef
{
    const ApiModule* module = nullptr;
    const ApiEntry* entry = nullptr;
    const ApiEntry* owner = nullptr;

    std::string PyName() const;   // imgui.button, imgui.ImDrawList.add_line, imgui.WindowFlags_.no_title_bar
    std::string CppName() const;  // ImGui::Button; the Python name when the entry has no C++ name
    std::string Url() const;      // the page's anchor (the owner's for an attribute or a member)
    std::string CppUrl() const;   // the C++ view's anchor, or "" when the entry has none
    bool operator==(const ApiRef& other) const { return entry == other.entry; }
    bool operator!=(const ApiRef& other) const { return entry != other.entry; }
};

enum class ApiIndexState { NotLoaded, Loading, Loaded, Failed };

// Loads the modules' index files (once; asynchronous on the web). demoCodeDir: the folder of the demo code on the
// desktop (the web fetches demo_code/api_index/ relative to the page). Returns Loaded when all are read.
ApiIndexState ApiIndex_Load(const std::string& demoCodeDir, const std::vector<std::string>& modules);

// The loaded modules among the given ones, in that order
std::vector<const ApiModule*> ApiIndex_Modules(const std::vector<std::string>& modules);

// The entries that an identifier may denote, within the given modules: "ImGui::Button", "imgui.button", "AddLine",
// "draw_list.add_line", "ImGuiWindowFlags_NoTitleBar". A qualified name that matches wins; otherwise the bare name,
// in both languages (several hits when a method's name exists in several classes)
std::vector<ApiRef> ApiIndex_Lookup(const std::vector<std::string>& modules, const std::string& identifier);

// The identifier at a column of a line of code, with its qualifiers: "ImGui::Button", "io.config_flags"; "" when
// the column is not on an identifier
std::string ApiIndex_IdentifierAt(const std::string& line, size_t column);

// The first sentence of a doc, on one line (for a tooltip)
std::string ApiIndex_FirstSentence(const std::string& doc);
