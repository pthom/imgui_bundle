// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// The demos of Dear ImGui Bundle, with their pictures, descriptions and code: the C++ twin of demo_immapp_launcher.py
//
// The playground's examples, the immapp demos and the explorer's demos, by category. Pick one to see its picture and
// description, then run it, read its code, or open it online. The catalog is demos_assets/demos_catalog.json, written
// by ci_scripts/playground_examples_docs.py from the playground's examples.json; the pictures come from the website.
#pragma once
#include "imgui.h"
#include "imgui_rich_md/rich_md.h"
#include "imgui_rich_md/backends/code_editor/snippets.h"

#include <functional>
#include <map>
#include <optional>
#include <string>
#include <utility>
#include <vector>


struct DemoEntry
{
    std::string label;
    std::string filename;   // as in examples.json (e.g. explorables/julia_map.py): the playground knows it by this name
    std::string stem;       // the picture's name on the site, the demo's page in the explorer, its C++ function
    std::string where;      // both, desktop or browser
    std::string text;       // a paragraph for visitors (markdown)
    std::string summary;    // its first sentences, for the card (markdown)
    std::string textPlain, summaryPlain;  // the same as plain text (the card, and its tooltip's test)
    std::vector<std::string> uses;        // the libraries it uses
    std::string pythonFile;  // relative to the repository
    std::string cppFile;     // its C++ version, relative to the repository; empty when there is none
    std::string cppUrl;      // where its C++ version runs online (the explorer's page by default; "" when it cannot)
    bool inPlace = false;    // its function may be linked in the explorer
    std::vector<std::pair<std::string, std::string>> variants;  // the same demo in other files: label, Python file
    std::string page;        // a page entry (e.g. the notebooks): its URL; it has no code to run or show
    std::string video;       // a page entry's video, if any

    std::vector<std::string> Tags() const;
};

struct DemoCategory
{
    std::string name, about, tip;  // tip: a second line, when the category has one to give (empty otherwise)
    std::vector<DemoEntry> demos;
};

// A source file of a demo, shown by the code view
struct CodeFile
{
    std::string language;  // "Python" or "C++"
    std::string repoFile;  // relative to the repository
    Snippets::SnippetData snippet;
    std::string GithubUrl() const;  // its page on GitHub, for the bundle's own files (empty for a submodule's)
};

using VoidFunction = std::function<void()>;


class DemoLauncher
{
public:
    DemoLauncher();

    void Gui(bool withTitle = true);  // the launcher; without its title when the explorer draws its own header above
    void Title();
    void Filters();  // the category chips, the library filter and the search box, then a separator

    // Escape's levels: the code view, then the detail page of a small screen
    int Depth() const;
    void Back();
    // The level shown, as a route for the browser's history ("", "code/<stem>", "detail/<stem>"), and the way to one
    std::string Route() const;
    void GoTo(const std::string& route);

    // For the explorer's page
    void Deal();  // when the gallery arrives on screen: its cards in view are dealt one after another
    bool Dealing() const;
    std::string ChipLabel(const DemoCategory& category) const;
    const std::vector<DemoCategory>& Categories() const { return _categories; }
    int NbDemos() const;
    const DemoEntry* Find(const std::string& stem) const;
    void ShowCodeOf(const DemoEntry& demo);
    // On screen, this frame (the intro's automations click on them)
    const std::map<std::string, std::pair<ImVec2, ImVec2>>& CardRects() const { return _cardRects; }

    // A demo in place: the explorer registers the functions it links (by stem); "Run" then asks it to show the demo
    std::map<std::string, VoidFunction> inPlaceFunctions;
    std::optional<std::string> demoToShowInPlace;  // set by "Run", taken by the explorer

private:
    std::vector<const DemoEntry*> Shown(const DemoCategory& category) const;
    std::vector<std::pair<std::string, int>> Libraries() const;
    bool Chip(const std::string& label, float highlight);
    void SearchBox();
    void LibraryFilter();
    void ThumbnailSize();  // "Thumbnail size", then "-" and "+": each press changes the number of columns
    int Columns(float cardWidth) const;  // of the gallery, for this minimal width of a card (em), at its width
    std::optional<float> NextCardWidth(int direction) const;  // 1: larger thumbnails, -1: smaller; none if no change
    std::optional<std::pair<std::string, float>> TopCard() const;  // the first card in view, its offset from the top
    void Card(const DemoEntry& demo, float width);
    void CardFace(ImDrawList* drawList, const DemoEntry& demo, ImVec2 topLeft, float width, float height);
    void FlyingCard(const DemoEntry& demo, ImVec2 topLeft, float width, float height, float flight, int index);
    std::optional<float> Flight(const std::string& filename) const;
    void SmoothScroll();
    void Gallery();
    bool Action(const char* label, const char* tooltip);
    void LinkAction(const char* label, const char* tooltip, const char* url);
    void Detail();
    void DetailPage();
    void ShowCode();
    bool DrawPicture(ImDrawList* drawList, const std::string& stem, ImVec2 topLeft, float width, float aspect,
                     float rounding, ImDrawFlags corners);
    void NewFrame();
    bool PicturesLoading() const;

    std::vector<DemoCategory> _categories;
    const DemoEntry* _selected = nullptr;
    std::map<std::string, std::optional<RichMd::MarkdownImage>> _pictures;  // by stem, once loaded (or failed)
    int _picturesBudget = 0;  // textures created this frame
    double _lastPictureTime = 0.0;
    std::map<std::string, float> _categoryY;  // the position of each category in the gallery (scroll coordinates)
    std::string _categoryInView;
    std::optional<float> _scrollTarget;  // a click on a category chip scrolls smoothly to it
    int _nbScrolls = 0;
    std::optional<std::pair<const DemoEntry*, std::vector<CodeFile>>> _codeView;
    std::string _codeLanguage = "Side by side";  // or "Python", "C++": what the code view shows of a demo in two languages
    std::map<std::string, int> _variant;  // per demo with variants: the one picked in the detail pane
    std::string _library;  // the library in use: the gallery shows the demos that use it (all when empty)
    std::string _search;   // the words typed in the search box: the gallery shows the demos that have them all
    std::optional<double> _dealtAt;  // when the gallery last arrived on screen: its cards are dealt one by one
    std::optional<std::map<std::string, int>> _dealOrder;  // the cards dealt, in their order: those in view when it began
    std::pair<ImVec2, ImVec2> _galleryRect;  // on screen, this frame: the cards are dealt from below it
    bool _detailOpen = false;  // on a small screen, the detail is a page of its own (a card opens it), not a pane
    std::map<std::string, std::pair<ImVec2, ImVec2>> _cardRects;
    std::map<std::string, bool> _cardHovered;  // the card's item, last frame (the colors are pushed before it)
    float _cardWidth;  // em: the minimal width of a card (the thumbnail size buttons change it)
    float _galleryWidth = 0.f;  // last frame: the columns that the thumbnail size buttons can reach depend on it
    std::optional<std::pair<std::string, float>> _scrollAnchor;  // a size change: the card at the top, and its offset
};


void gui_demo_immapp_launcher();  // the launcher alone (a standalone app)

// Shared with the explorer's page
extern const ImVec4 LAUNCHER_ACCENT;  // the selected card, the chip of the category in view, the state's switch
// A value that eases toward its target (ImAnim), from `start` the first time (default: the target itself),
// identified by this key in the current ID stack
float Tween(const char* key, float target, float duration, std::optional<float> start = std::nullopt);
void BigText(const char* text, float scale, std::optional<ImVec4> color = std::nullopt);
ImVec4 Lerp(ImVec4 a, ImVec4 b, float t);
bool SmallScreen();  // a phone or a small tablet (under about 800 px): the detail is a page, the header wraps
ImU32 Curtain(float alpha);  // the color of a veil that hides what is under it: the background, at this opacity
std::string RepoFile(const std::string& repoRelative);  // a file of the repository, where this build can read it
bool ExplorerPage(const DemoEntry& demo);  // its C++ version's page is the explorer's own (built beside it)
