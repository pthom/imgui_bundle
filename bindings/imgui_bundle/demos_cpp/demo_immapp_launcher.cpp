// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// The demos of Dear ImGui Bundle, with their pictures, descriptions and code: see demo_immapp_launcher.h
#include "demo_immapp_launcher.h"

#include "immapp/immapp.h"
#include "immapp/browse_to_url.h"
#include "hello_imgui/hello_imgui.h"
#include "hello_imgui/icons_font_awesome_4.h"
#include "imgui_internal.h"
#include "misc/cpp/imgui_stdlib.h"
#include "ImAnim/im_anim.h"
#include "nlohmann/json.hpp"
#include "demo_utils/api_demos.h"

#include <algorithm>
#include <cctype>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <regex>
#include <sstream>
#include <tuple>

namespace
{
    const std::string SITE = "https://imgui-bundle.pages.dev";
    const std::string PICTURES_URL = SITE + "/resources/playground/";
    const std::string GITHUB = "https://github.com/pthom/imgui_bundle/blob/main/";
    // In a clone of the repository, the pictures are also here, before they reach the website
    const std::string LOCAL_PICTURES = "docs/clone_website_resources/imgui-bundle.pages.dev/resources/playground/";

    const float CARD_WIDTH = 15.f;  // em: the minimum width of a card, by default
    const std::vector<float> CARD_WIDTHS = {8.f, 9.f, 10.f, 11.f, 12.5f, 14.f, 15.f, 17.f, 19.f, 22.f, 25.f, 30.f,
                                            40.f};  // em: the thumbnail sizes
    const float MIN_TEXT_SCALE = 0.75f;  // a card narrower than CARD_WIDTH has smaller texts, down to this scale
    const float DETAIL_WIDTH = 28.f;  // em
    const float PICTURE_ASPECT = 1.6f;  // of the pictures on the cards (cropped to it, or fitted when too different)
    const float MAX_CROP = 1.5f;  // a picture more than 1.5 times wider or taller than the card's shape is fitted
    const int TEXTURES_PER_FRAME = 3;  // decoding all the pictures in one frame would freeze the app for a moment
    const float DEAL_DELAY = 0.05f;  // s: between two cards dealt, when the gallery arrives on screen
    const float DEAL_DURATION = 0.35f;  // s: the flight of one card, from the deck to its place
    const float DEAL_SPIN = 18.f;  // degrees: a card is dealt with a spin of at most this, settling as it lands
    const int DEAL_CAP = 24;  // the cards after this one fly together with it

    const ImVec4 CARD_BG(0.16f, 0.18f, 0.24f, 1.f);  // under the card's text (the picture covers the rest)
    const ImVec4 CARD_BG_HOVERED(0.2f, 0.23f, 0.31f, 1.f);
    const ImVec4 CARD_BORDER(0.25f, 0.25f, 0.3f, 1.f);
    const ImVec4 CARD_BORDER_HOVERED(0.6f, 0.62f, 0.72f, 1.f);
    const ImVec4 CATEGORY_TITLE(0.61f, 0.86f, 1.f, 1.f);
    const std::map<std::string, ImU32> TAG_COLORS = {
        {"Python", IM_COL32(48, 105, 152, 235)}, {"C++", IM_COL32(96, 72, 160, 235)},
        {"Browser only", IM_COL32(190, 105, 30, 235)}, {"Desktop only", IM_COL32(40, 125, 85, 235)}};

    float Em(float n = 1.f) { return HelloImGui::EmSize(n); }
    iam_ease_desc Ease() { return iam_ease_preset(iam_ease_out_cubic); }

    // Markdown as plain text: links keep their text, emphasis and code marks go
    std::string PlainText(const std::string& markdown)
    {
        static const std::regex link(R"(\[([^\]]*)\]\((?:[^()]|\([^()]*\))*\))");  // a URL may hold (...)
        std::string plain = std::regex_replace(markdown, link, "$1");
        std::string cleaned;
        for (size_t i = 0; i < plain.size(); ++i)
        {
            if (plain[i] == '*' || plain[i] == '`')
                continue;
            cleaned += plain[i];
        }
        std::istringstream words(cleaned);
        std::string word, result;
        while (words >> word)
            result += (result.empty() ? "" : " ") + word;
        return result;
    }

    std::string Lower(std::string s)
    {
        std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c) { return (char)std::tolower(c); });
        return s;
    }

    bool StartsWith(const std::string& s, const std::string& prefix) { return s.rfind(prefix, 0) == 0; }
    bool EndsWith(const std::string& s, const std::string& suffix)
    {
        return s.size() >= suffix.size() && s.compare(s.size() - suffix.size(), suffix.size(), suffix) == 0;
    }

    // The text, cut at a word and ended with an ellipsis, so that it takes at most these lines once wrapped
    std::string Fit(const std::string& text, float width, int lines)
    {
        float maxHeight = lines * ImGui::GetTextLineHeight() + 1.f;
        if (ImGui::CalcTextSize(text.c_str(), nullptr, false, width).y <= maxHeight)
            return text;
        std::istringstream stream(text);
        std::vector<std::string> words;
        std::string word;
        while (stream >> word)
            words.push_back(word);
        auto joined = [&words]() {
            std::string r;
            for (const auto& w : words)
                r += (r.empty() ? "" : " ") + w;
            return r + "\xe2\x80\xa6";  // …
        };
        while (!words.empty() && ImGui::CalcTextSize(joined().c_str(), nullptr, false, width).y > maxHeight)
            words.pop_back();
        return joined();
    }

    // Small pills, right-aligned from this corner (a picture's bottom right: usually its emptiest part)
    void DrawTags(const std::vector<std::string>& tags, ImVec2 bottomRight, ImDrawList* drawList = nullptr,
                  float scale = 1.f)
    {
        if (drawList == nullptr)
            drawList = ImGui::GetWindowDrawList();
        ImGui::PushFont(nullptr, ImGui::GetStyle().FontSizeBase * 0.85f * scale);
        ImVec2 pad(Em(0.4f), Em(0.1f));
        float x = bottomRight.x;
        for (auto it = tags.rbegin(); it != tags.rend(); ++it)
        {
            ImVec2 size = ImGui::CalcTextSize(it->c_str());
            float top = bottomRight.y - size.y - 2 * pad.y;
            x -= size.x + 2 * pad.x;
            drawList->AddRectFilled(ImVec2(x, top), ImVec2(x + size.x + 2 * pad.x, bottomRight.y),
                                    TAG_COLORS.at(*it), Em(0.6f));
            drawList->AddText(ImVec2(x + pad.x, top + pad.y), IM_COL32(240, 245, 255, 255), it->c_str());
            x -= Em(0.25f);
        }
        ImGui::PopFont();
    }

    // A small button with a minus or a plus drawn at its center (an icon font's glyph sits a little high)
    bool SignButton(const char* strId, bool plus)
    {
        float height = ImGui::GetFontSize();
        ImGui::PushStyleVar(ImGuiStyleVar_FramePadding, ImVec2(ImGui::GetStyle().FramePadding.x, 0));  // as SmallButton
        bool clicked = ImGui::Button((std::string("##") + strId).c_str(), ImVec2(height * 1.6f, height));
        ImGui::PopStyleVar();
        ImVec2 a = ImGui::GetItemRectMin(), b = ImGui::GetItemRectMax();
        float cx = std::round((a.x + b.x) / 2), cy = std::round((a.y + b.y) / 2);
        float half = std::round(height * 0.25f), thickness = std::max(1.f, std::round(height * 0.12f));
        ImDrawList* drawList = ImGui::GetWindowDrawList();
        ImU32 color = ImGui::GetColorU32(ImGuiCol_Text);
        drawList->AddRectFilled(ImVec2(cx - half, cy - thickness / 2), ImVec2(cx + half, cy + thickness / 2), color);
        if (plus)
            drawList->AddRectFilled(ImVec2(cx - thickness / 2, cy - half), ImVec2(cx + thickness / 2, cy + half), color);
        return clicked;
    }

    // The scale of a card's texts: they follow its width, from their size on a card of the default width
    float CardTextScale(float width) { return std::clamp(width / Em(CARD_WIDTH), MIN_TEXT_SCALE, 1.f); }

    std::string ReadRepoFile(const std::string& repoRelative)
    {
        std::string path = RepoFile(repoRelative);
        return path.empty() ? "" : ReadCode(path);
    }

    CodeFile MakeCodeFile(const std::string& repoFile, const std::string& language)
    {
        CodeFile file;
        file.language = language;
        file.repoFile = repoFile;
        file.snippet.Code = ReadRepoFile(repoFile);
        file.snippet.Language = language == "Python" ? Snippets::SnippetLanguage::Python
                                                     : Snippets::SnippetLanguage::Cpp;
        file.snippet.DisplayedFilename = std::filesystem::path(repoFile).filename().string();
        return file;
    }

    std::string PlaygroundUrl(const DemoEntry& demo) { return SITE + "/playground/?demo=" + demo.filename; }

    std::vector<DemoCategory> LoadCatalog()
    {
        std::string json;
        if (HelloImGui::AssetExists("demos_catalog.json"))
        {
            auto asset = HelloImGui::LoadAssetFileData("demos_catalog.json");
            json.assign((const char*)asset.data, asset.dataSize);
            HelloImGui::FreeAssetFileData(&asset);
        }
        else  // the launcher alone, without the explorer's assets: the folder beside the executable
        {
            std::ifstream file(DemosAssetsFolder() + "demos_catalog.json");
            std::stringstream buffer;
            buffer << file.rdbuf();
            json = buffer.str();
        }
        std::vector<DemoCategory> categories;
        if (json.empty())
        {
            fprintf(stderr, "demo_immapp_launcher: demos_catalog.json not found\n");
            return categories;
        }
        auto catalog = nlohmann::json::parse(json);
        for (const auto& c : catalog["categories"])
        {
            DemoCategory category;
            category.name = c["name"];
            category.about = c["about"];
            category.tip = c.value("tip", "");
            for (const auto& d : c["demos"])
            {
                DemoEntry demo;
                demo.label = d["label"];
                demo.filename = d["filename"];
                demo.stem = d["stem"];
                demo.where = d["where"];
                demo.text = d["text"];
                demo.summary = d["summary"];
                demo.textPlain = PlainText(demo.text);
                demo.summaryPlain = PlainText(demo.summary);
                demo.uses = d["uses"].get<std::vector<std::string>>();
                demo.pythonFile = d["python_file"];
                demo.cppFile = d["cpp_file"].is_null() ? "" : d["cpp_file"].get<std::string>();
                demo.cppUrl = d["cpp_url"];
                demo.inPlace = d["in_place"];
                for (const auto& v : d["variants"])
                    demo.variants.emplace_back(v["label"], v["python_file"]);
                demo.page = d.value("page", "");
                demo.video = d.value("video", "");
                category.demos.push_back(demo);
            }
            categories.push_back(category);
        }
        return categories;
    }
}


// ---------------------------------------------------------------------------------------------------------------------
// The catalog
// ---------------------------------------------------------------------------------------------------------------------
std::vector<std::string> DemoEntry::Tags() const
{
    std::vector<std::string> tags = {"Python"};
    if (!cppFile.empty())
        tags.push_back("C++");
    if (where == "browser")
        tags.push_back("Browser only");
    if (where == "desktop")
        tags.push_back("Desktop only");
    return tags;
}

std::string CodeFile::GithubUrl() const
{
    return StartsWith(repoFile, "bindings/") ? GITHUB + repoFile : "";
}

// Its C++ version's page is the explorer's own (built beside it), not a custom URL (e.g. a manual's site)
bool ExplorerPage(const DemoEntry& demo) { return EndsWith(demo.cppUrl, "/explorer/" + demo.stem + ".html"); }

std::string RepoFile(const std::string& repoRelative)
{
#ifdef __EMSCRIPTEN__
    // The explorer's build preloads demos_cpp and demos_python at the root of the virtual file system
    const std::string package = "bindings/imgui_bundle/";
    if (!StartsWith(repoRelative, package))
        return "";
    std::string inPackage = repoRelative.substr(package.size());
    if (!StartsWith(inPackage, "demos_cpp/") && !StartsWith(inPackage, "demos_python/"))
        return "";
    return "/" + inPackage;
#else
    auto repo = std::filesystem::path(MainPythonPackageFolder()).parent_path().parent_path();
    return (repo / repoRelative).lexically_normal().string();
#endif
}


// ---------------------------------------------------------------------------------------------------------------------
// The page's shared bits
// ---------------------------------------------------------------------------------------------------------------------
const ImVec4 LAUNCHER_ACCENT(0.45f, 0.65f, 1.f, 1.f);

float Tween(const char* key, float target, float duration, std::optional<float> start)
{
    return iam_tween_float(ImGui::GetID(key), 0, target, duration, Ease(), iam_policy_crossfade,
                           ImGui::GetIO().DeltaTime, start.value_or(target));
}

void BigText(const char* text, float scale, std::optional<ImVec4> color)
{
    ImGui::PushFont(nullptr, ImGui::GetStyle().FontSizeBase * scale);
    if (color.has_value())
        ImGui::TextColored(*color, "%s", text);
    else
        ImGui::TextUnformatted(text);
    ImGui::PopFont();
}

ImVec4 Lerp(ImVec4 a, ImVec4 b, float t)
{
    return ImVec4(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t, a.z + (b.z - a.z) * t, a.w + (b.w - a.w) * t);
}

bool SmallScreen()
{
    return ImGui::GetIO().DisplaySize.x < Em(50.f);
}

ImU32 Curtain(float alpha)
{
    // The theme's background is translucent over black: composited here, so that the veil at alpha 1 hides everything
    ImVec4 bg = ImGui::GetStyleColorVec4(ImGuiCol_WindowBg);
    return IM_COL32((int)(255 * bg.x * bg.w), (int)(255 * bg.y * bg.w), (int)(255 * bg.z * bg.w), (int)(255 * alpha));
}


// ---------------------------------------------------------------------------------------------------------------------
// The launcher
// ---------------------------------------------------------------------------------------------------------------------
DemoLauncher::DemoLauncher()
{
    _categories = LoadCatalog();
    _cardWidth = CARD_WIDTH;
    if (!_categories.empty() && !_categories[0].demos.empty())
        _selected = &_categories[0].demos[0];
}

int DemoLauncher::NbDemos() const
{
    int n = 0;
    for (const auto& category : _categories)
        n += (int)category.demos.size();
    return n;
}

const DemoEntry* DemoLauncher::Find(const std::string& stem) const
{
    for (const auto& category : _categories)
        for (const auto& demo : category.demos)
            if (demo.stem == stem)
                return &demo;
    return nullptr;
}

std::vector<std::pair<std::string, int>> DemoLauncher::Libraries() const
{
    // The libraries the demos use, with their counts, the most used first
    std::map<std::string, int> counts;
    for (const auto& category : _categories)
        for (const auto& demo : category.demos)
            for (const auto& library : demo.uses)
                counts[library] += 1;
    std::vector<std::pair<std::string, int>> libraries(counts.begin(), counts.end());
    std::sort(libraries.begin(), libraries.end(), [](const auto& a, const auto& b) {
        return a.second != b.second ? a.second > b.second : a.first < b.first;
    });
    return libraries;
}

std::vector<const DemoEntry*> DemoLauncher::Shown(const DemoCategory& category) const
{
    // The demos that use the library in use, and have all the words of the search box
    std::vector<std::string> words;
    std::istringstream stream(Lower(_search));
    std::string word;
    while (stream >> word)
        words.push_back(word);
    std::vector<const DemoEntry*> shown;
    for (const auto& demo : category.demos)
    {
        if (!_library.empty() && std::find(demo.uses.begin(), demo.uses.end(), _library) == demo.uses.end())
            continue;
        if (!words.empty())
        {
            std::string text = Lower(demo.label + " " + demo.textPlain + " " + category.name);
            for (const auto& library : demo.uses)
                text += " " + Lower(library);
            bool all = true;
            for (const auto& w : words)
                if (text.find(w) == std::string::npos)
                    all = false;
            if (!all)
                continue;
        }
        shown.push_back(&demo);
    }
    return shown;
}

std::string DemoLauncher::ChipLabel(const DemoCategory& category) const
{
    return category.name + " (" + std::to_string(Shown(category).size()) + ")";
}

bool DemoLauncher::Chip(const std::string& label, float highlight)
{
    // A small button, colored with the accent when highlighted (in view, or in use); a row of chips wraps
    float width = ImGui::CalcTextSize(label.c_str()).x + 2 * ImGui::GetStyle().FramePadding.x;
    if (width > ImGui::GetContentRegionAvail().x)
        ImGui::NewLine();
    ImVec4 button = ImGui::GetStyleColorVec4(ImGuiCol_Button);
    ImVec4 accent(LAUNCHER_ACCENT.x, LAUNCHER_ACCENT.y, LAUNCHER_ACCENT.z, 0.55f);
    ImGui::PushStyleColor(ImGuiCol_Button, Lerp(button, accent, highlight));
    bool clicked = ImGui::SmallButton(label.c_str());
    ImGui::PopStyleColor();
    ImGui::SameLine();
    return clicked;
}

// The header: the name, what the bundle is, a chip per category that scrolls to it, and the library filter
void DemoLauncher::Title()
{
    BigText("Dear ImGui Bundle", 2.f);
    ImGui::SameLine();
    float y = ImGui::GetCursorPosY() + Em(0.75f);  // the tagline sits on the title's baseline
    ImGui::SetCursorPosY(y);
    ImGui::TextDisabled("   Interactive apps in Python and C++, for desktop, web and mobile.");
    ImGui::SameLine();
    ImGui::SetCursorPosY(y);
    ImGui::TextUnformatted("Pick a demo: see it, run it, and read its code: each demo is a documented quickstart.");
}

void DemoLauncher::Filters()
{
    for (const auto& category : _categories)
    {
        float highlight = Tween(("chip " + category.name).c_str(), category.name == _categoryInView ? 1.f : 0.f, 0.25f);
        if (Chip(ChipLabel(category), highlight) && !_codeView.has_value())
        {
            if (_categoryY.count(category.name))
                _scrollTarget = _categoryY[category.name];
            _nbScrolls += 1;
        }
    }
    ImGui::Dummy(ImVec2(Em(1.f), 0));
    ImGui::SameLine();
    LibraryFilter();
    ThumbnailSize();
    SearchBox();
    ImGui::NewLine();
    ImGui::Separator();
}

int DemoLauncher::Columns(float cardWidth) const
{
    float spacing = Em(1.f);
    return std::max(1, (int)((_galleryWidth + spacing) / (Em(cardWidth) + spacing)));
}

std::optional<float> DemoLauncher::NextCardWidth(int direction) const
{
    int columns = Columns(_cardWidth);
    std::vector<float> steps;
    for (float w : CARD_WIDTHS)
        if (direction > 0 ? w > _cardWidth : w < _cardWidth)
            steps.push_back(w);
    if (direction < 0)
        std::reverse(steps.begin(), steps.end());
    for (float w : steps)
        if (Columns(w) != columns)
            return w;
    return std::nullopt;
}

std::optional<std::pair<std::string, float>> DemoLauncher::TopCard() const
{
    // The first card shown in the gallery's view (at the last frame): _cardRects also has the cards a filter hides
    float top = _galleryRect.first.y;
    std::optional<std::pair<std::string, float>> best;
    float bestY = 0.f;
    for (const auto& category : _categories)
        for (const DemoEntry* demo : Shown(category))
        {
            auto it = _cardRects.find(demo->filename);
            if (it == _cardRects.end() || it->second.second.y <= top)
                continue;
            if (!best.has_value() || it->second.first.y < bestY)
            {
                best = std::make_pair(demo->filename, it->second.first.y - top);
                bestY = it->second.first.y;
            }
        }
    return best;
}

void DemoLauncher::ThumbnailSize()
{
    const char* label = "Thumbnail size";
    const ImGuiStyle& style = ImGui::GetStyle();
    float buttonWidth = ImGui::GetFontSize() * 1.6f;  // SignButton's
    float width = ImGui::CalcTextSize(label).x + 2 * buttonWidth + 4 * style.ItemSpacing.x;
    if (width > ImGui::GetContentRegionAvail().x)
        ImGui::NewLine();
    ImGui::SeparatorEx(ImGuiSeparatorFlags_Vertical);
    ImGui::SameLine();
    ImGui::TextDisabled("%s", label);
    ImGui::SameLine();
    for (auto [direction, tooltip] : {std::pair{-1, "Smaller thumbnails"}, std::pair{1, "Larger thumbnails"}})
    {
        std::optional<float> target = NextCardWidth(direction);
        ImGui::BeginDisabled(!target.has_value());
        if (SignButton(("thumbnails " + std::to_string(direction)).c_str(), direction > 0) && target)
        {
            _scrollAnchor = TopCard();  // it stays where it is, while the rows change
            _cardWidth = *target;
        }
        ImGui::EndDisabled();
        ImGui::SetItemTooltip("%s", tooltip);
        ImGui::SameLine();
    }
}

void DemoLauncher::SearchBox()
{
    // The words to find in the demos (Escape clears them)
    float width = Em(14.f);
    if (width > ImGui::GetContentRegionAvail().x)
        ImGui::NewLine();
    ImGui::SetNextItemWidth(width);
    ImVec2 padding = ImGui::GetStyle().FramePadding;
    ImGui::PushStyleVar(ImGuiStyleVar_FramePadding, ImVec2(padding.x, 0));  // as high as the chips
    ImGui::InputTextWithHint("##search", ICON_FA_SEARCH "  Search the demos", &_search);
    ImGui::PopStyleVar();
    if (ImGui::IsItemActive() && ImGui::IsKeyPressed(ImGuiKey_Escape))
        _search.clear();
    ImGui::SetItemTooltip("Words to find in the title, the description, the category or the libraries of a demo");
    if (!_search.empty() || !_library.empty())  // a discreet way to clear the filters
    {
        ImGui::SameLine();
        if (ImGui::SmallButton(ICON_FA_TIMES "##clear"))
            _search = _library = "";
        ImGui::SetItemTooltip("Clears the search and the library filter");
    }
    ImGui::SameLine();
}

void DemoLauncher::LibraryFilter()
{
    // A button that says which library the gallery is filtered on, and a popup to pick one
    std::string label = _library.empty() ? "Library " ICON_FA_CARET_DOWN : "Library: " + _library + " " ICON_FA_TIMES;
    if (Chip(label, _library.empty() ? 0.f : 1.f))
        ImGui::OpenPopup("library");
    ImGui::SetItemTooltip("Keep only the demos that use a library");
    if (ImGui::BeginPopup("library"))
    {
        if (ImGui::MenuItem("All the demos", nullptr, _library.empty()))
            _library.clear();
        ImGui::Separator();
        for (const auto& [library, count] : Libraries())
            if (ImGui::MenuItem((library + " (" + std::to_string(count) + ")").c_str(), nullptr, library == _library))
                _library = library;
        ImGui::EndPopup();
    }
}


// ---------------------------------------------------------------------------------------------------------------------
// The pictures: from the repository's clone of the website when it is there, else downloaded by rich_md's image
// service (in the background, when the build has one); made into textures a few per frame
// ---------------------------------------------------------------------------------------------------------------------
namespace
{
    // A picture, once it is there: nullopt while it downloads; a texture of size 0 when it cannot come
    std::optional<RichMd::MarkdownImage> LoadPicture(const std::string& stem)
    {
        RichMd::MarkdownImage none;
        none.texture_id = ImTextureID(0);
        none.size = ImVec2(0, 0);
#ifndef __EMSCRIPTEN__
        std::string local = RepoFile(LOCAL_PICTURES + stem + ".jpg");
        if (!local.empty() && std::filesystem::exists(local))
        {
            std::ifstream file(local, std::ios::binary);
            std::string data((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
            auto image = HelloImGui::ImageAndSizeFromEncodedData(data.data(), data.size(), "launcher " + stem);
            RichMd::MarkdownImage picture = none;
            picture.texture_id = image.textureId;
            picture.size = image.size;
            return picture;
        }
#endif
        if (!RichMd::GetHostServices().Download)  // no download service in this build (e.g. the Python build's)
            return none;
        auto image = RichMd::OnImage_Default(PICTURES_URL + stem + ".jpg");  // nullopt while it downloads
        if (image.has_value() && image->texture_id == ImTextureID(0))
            return std::nullopt;  // its texture comes on a later frame (its size is known first): asked again then
        if (image.has_value())
        {
            // rich_md answers a failed download with its broken-image icon: the placeholder is better here
            static std::optional<ImTextureID> broken;
            if (!broken.has_value())
            {
                auto brokenImage = RichMd::OnImage_Default("images/markdown_broken_image.png");
                broken = brokenImage.has_value() ? brokenImage->texture_id : ImTextureID(0);
            }
            if (image->texture_id == *broken)
                return none;
        }
        return image;
    }
}

void DemoLauncher::NewFrame()
{
    _picturesBudget = TEXTURES_PER_FRAME;
}

bool DemoLauncher::PicturesLoading() const
{
    // Some pictures are still being downloaded, or fading in
    return (int)_pictures.size() < NbDemos() || ImGui::GetTime() - _lastPictureTime < 1.0;
}

bool DemoLauncher::DrawPicture(ImDrawList* drawList, const std::string& stem, ImVec2 topLeft, float width, float aspect,
                               float rounding, ImDrawFlags corners)
{
    // The picture on this draw list, from this corner, cropped to the aspect ratio from its top-left corner (or
    // fitted, when its shape is too different), fading in over a placeholder once it is loaded. Returns whether it
    // is drawn.
    std::optional<RichMd::MarkdownImage> image;
    auto it = _pictures.find(stem);
    if (it != _pictures.end())
        image = it->second;
    else if (_picturesBudget > 0)
    {
        image = LoadPicture(stem);
        if (image.has_value())
        {
            if (image->size.x <= 0)
                image.reset();  // it cannot come: the placeholder stays
            _pictures[stem] = image;
            _picturesBudget -= 1;
            _lastPictureTime = ImGui::GetTime();
        }
    }
    float imageAspect = image.has_value() ? image->size.x / image->size.y : PICTURE_ASPECT;
    ImVec2 bottomRight(topLeft.x + width, topLeft.y + width / aspect);
    drawList->AddRectFilled(topLeft, bottomRight, IM_COL32(44, 46, 68, 255), rounding, corners);
    if (!image.has_value())
    {
        ImVec2 iconSize = ImGui::CalcTextSize(ICON_FA_CODE);
        ImVec2 iconPos((topLeft.x + bottomRight.x - iconSize.x) / 2, (topLeft.y + bottomRight.y - iconSize.y) / 2);
        drawList->AddText(iconPos, IM_COL32(200, 200, 220, 160), ICON_FA_CODE);
        return false;
    }
    float alpha = Tween(("picture " + stem).c_str(), 1.f, 0.5f, 0.f);
    ImVec2 uv0(0, 0), uv1(1, 1);
    if (std::max(imageAspect / aspect, aspect / imageAspect) > MAX_CROP)  // fit it, centered, on a dark background
    {
        drawList->AddRectFilled(topLeft, bottomRight, IM_COL32(20, 22, 26, 255), rounding, corners);
        rounding = 0.f;  // the picture floats inside the background: square
        if (imageAspect > aspect)
        {
            float height = width / imageAspect;
            topLeft.y = (topLeft.y + bottomRight.y - height) / 2;
            bottomRight.y = topLeft.y + height;
        }
        else
        {
            float pictureWidth = (bottomRight.y - topLeft.y) * imageAspect;
            topLeft.x = (topLeft.x + bottomRight.x - pictureWidth) / 2;
            bottomRight.x = topLeft.x + pictureWidth;
        }
    }
    else if (imageAspect > aspect)  // crop its right side (the pictures are laid out from their top-left corner)
        uv1 = ImVec2(aspect / imageAspect, 1);
    else if (imageAspect < aspect)  // crop its bottom
        uv1 = ImVec2(1, imageAspect / aspect);
    drawList->AddImageRounded(ImTextureRef(image->texture_id), topLeft, bottomRight, uv0, uv1,
                              IM_COL32(255, 255, 255, (int)(255 * alpha)), rounding, corners);
    return true;
}


// ---------------------------------------------------------------------------------------------------------------------
// The gallery
// ---------------------------------------------------------------------------------------------------------------------
void DemoLauncher::Card(const DemoEntry& demo, float width)
{
    // The demo's picture, its label and the first sentences of its description; a click selects it
    float padding = Em(0.6f);
    const float titleScale = 1.1f;
    float textScale = CardTextScale(width);
    float height = width / PICTURE_ASPECT + ImGui::GetTextLineHeight() * textScale * (titleScale + 2) + Em(1.6f);
    if (_scrollAnchor.has_value() && _scrollAnchor->first == demo.filename)  // after a size change
    {
        ImGui::SetScrollY(ImGui::GetCursorPosY() - _scrollAnchor->second);
        _scrollAnchor.reset();
    }
    ImVec2 topLeft = ImGui::GetCursorScreenPos();
    ImVec2 bottomRight(topLeft.x + width, topLeft.y + height);
    _cardRects[demo.filename] = {topLeft, bottomRight};
    bool hovered = _cardHovered.count(demo.filename) ? _cardHovered[demo.filename] : false;  // the item's, last frame
    float hover = Tween(("hover " + demo.filename).c_str(), hovered ? 1.f : 0.f, 0.15f);
    bool isSelected = &demo == _selected;

    // A shadow, as if the card lifted under the mouse: offset downward only (offset sideways, its rounded corner
    // showed as a notch outside the frame's rounded corner)
    float shadow = Em(0.5f) * hover;
    ImGui::GetWindowDrawList()->AddRectFilled(ImVec2(topLeft.x, topLeft.y + shadow),
                                              ImVec2(bottomRight.x, bottomRight.y + shadow),
                                              IM_COL32(0, 0, 0, (int)(110 * hover)), Em(0.5f));
    ImVec4 border = isSelected ? LAUNCHER_ACCENT : Lerp(CARD_BORDER, CARD_BORDER_HOVERED, hover);
    ImGui::PushStyleColor(ImGuiCol_Border, border);
    ImGui::PushStyleColor(ImGuiCol_ChildBg, Lerp(CARD_BG, CARD_BG_HOVERED, hover));
    ImGui::PushStyleVar(ImGuiStyleVar_ChildRounding, Em(0.5f));
    ImGui::PushStyleVar(ImGuiStyleVar_ChildBorderSize, isSelected ? 2.f : 1.f);
    ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(0, 0));
    ImGui::BeginChild(("##card " + demo.filename).c_str(), ImVec2(width, height), ImGuiChildFlags_Borders,
                      ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoScrollWithMouse);
    // Rounded more than the card: the border is stroked inside the card's rect with the card's radius, so a
    // picture with that radius pokes out of the border's curve at the corner (visible on a high-DPI screen)
    ImVec2 pictureTopLeft = ImGui::GetCursorScreenPos();
    // The card is one item, under its contents: its hover and click go through ImGui's active id (a touch swipe
    // that starts on it holds the id, so its release is not a click), and the test engine can find it
    bool clicked = ImGui::InvisibleButton("##hit", ImGui::GetContentRegionAvail());
    _cardHovered[demo.filename] = ImGui::IsItemHovered();
    ImGui::SetCursorScreenPos(pictureTopLeft);
    ImGui::Dummy(ImVec2(width, width / PICTURE_ASPECT));
    DrawPicture(ImGui::GetWindowDrawList(), demo.stem, pictureTopLeft, width, PICTURE_ASPECT, Em(0.8f),
                ImDrawFlags_RoundCornersTop);
    ImVec2 pictureBottomRight = ImGui::GetItemRectMax();
    DrawTags(demo.Tags(), ImVec2(pictureBottomRight.x - Em(0.4f), pictureBottomRight.y - Em(0.4f)), nullptr,
             textScale);
    ImGui::SetCursorPos(ImVec2(padding, ImGui::GetCursorPosY() + Em(0.4f)));
    ImGui::PushFont(nullptr, ImGui::GetStyle().FontSizeBase * titleScale * textScale);
    ImGui::TextUnformatted(Fit(demo.label, width - 2 * padding, 1).c_str());
    ImGui::PopFont();
    ImGui::SetCursorPosX(padding);
    ImGui::PushTextWrapPos(width - padding);
    ImGui::PushFont(nullptr, ImGui::GetStyle().FontSizeBase * textScale);
    std::string shown = Fit(demo.summaryPlain, width - 2 * padding, 2);
    ImGui::TextDisabled("%s", shown.c_str());
    bool summaryHovered = ImGui::IsItemHovered(ImGuiHoveredFlags_ForTooltip | ImGuiHoveredFlags_AllowWhenOverlappedByItem);
    ImGui::PopFont();
    ImGui::PopTextWrapPos();
    auto flight = Flight(demo.filename);
    if (flight.has_value() && *flight < 1.f && _dealOrder.has_value())
    {
        // Hidden under a veil while its double flies from the deck to here
        ImDrawList* drawList = ImGui::GetWindowDrawList();
        drawList->PushClipRectFullScreen();  // over the border too
        drawList->AddRectFilled(ImVec2(topLeft.x - 1, topLeft.y - 1), ImVec2(bottomRight.x + 1, bottomRight.y + 1),
                                Curtain(1.f));  // a pixel more: the border's stroke
        drawList->PopClipRect();
        if (*flight > 0.f)
            FlyingCard(demo, topLeft, width, height, *flight, _dealOrder->at(demo.filename));
    }
    ImGui::EndChild();
    ImGui::PopStyleVar(3);
    ImGui::PopStyleColor(2);
    // The whole description, on the summary, when the card cuts it or shows its first sentences only
    if (summaryHovered && shown != demo.textPlain)  // after the pops: the card's styles stay out of it
    {
        ImGui::SetNextWindowSize(ImVec2(Em(25.f), 0));  // the markdown wraps at this width
        if (ImGui::BeginTooltip())
        {
            RichMd::Render(demo.text);
            ImGui::EndTooltip();
        }
    }
    if (clicked)
    {
        _selected = &demo;
        if (SmallScreen())
            _detailOpen = true;
    }
}

void DemoLauncher::SmoothScroll()
{
    // Eases the gallery's scroll toward the chip's category (a new ImAnim channel per click, starting here)
    if (!_scrollTarget.has_value())
        return;
    float target = std::min(*_scrollTarget, ImGui::GetScrollMaxY());
    float y = iam_tween_float(ImGui::GetID(("scroll " + std::to_string(_nbScrolls)).c_str()), 0, target, 0.5f, Ease(),
                              iam_policy_crossfade, ImGui::GetIO().DeltaTime, ImGui::GetScrollY());
    ImGui::SetScrollY(y);
    if (std::fabs(y - target) < 1.f || ImGui::GetIO().MouseWheel != 0.f)
        _scrollTarget.reset();
}

void DemoLauncher::Deal()
{
    // The cards in view are dealt one after another, from the top left (the others, scrolled away, are simply there)
    _dealtAt = ImGui::GetTime();
    _dealOrder = std::map<std::string, int>();  // filled by the first frame's cards
}

bool DemoLauncher::Dealing() const
{
    return _dealtAt.has_value() && ImGui::GetTime() < *_dealtAt + DEAL_CAP * DEAL_DELAY + DEAL_DURATION;
}

std::optional<float> DemoLauncher::Flight(const std::string& filename) const
{
    // Where this card is in its flight, from 0 (leaving the deck) to 1 (in place), while the gallery is being
    // dealt: nullopt when it is not, or when the card is not dealt; below 0 when it waits in the deck
    if (!_dealOrder.has_value() || !Dealing() || !_dealOrder->count(filename))
        return std::nullopt;
    int index = _dealOrder->at(filename);
    return (float)(ImGui::GetTime() - *_dealtAt - std::min(index, DEAL_CAP) * DEAL_DELAY) / DEAL_DURATION;
}

void DemoLauncher::FlyingCard(const DemoEntry& demo, ImVec2 topLeft, float width, float height, float flight, int index)
{
    // The card's double on the foreground, sliding from the deck (below the gallery, at its center) to the card's
    // place, with a spin that settles as it lands (the vertices are rotated after the fact)
    float eased = 1.f - (1.f - flight) * (1.f - flight) * (1.f - flight);
    auto [galleryMin, galleryMax] = _galleryRect;
    ImVec2 deck((galleryMin.x + galleryMax.x - width) / 2, galleryMax.y + height * 0.3f);
    ImVec2 pos(deck.x + (topLeft.x - deck.x) * eased, deck.y + (topLeft.y - deck.y) * eased);
    ImDrawList* drawList = ImGui::GetForegroundDrawList();
    drawList->PushClipRect(galleryMin, galleryMax, true);
    int firstVertex = drawList->VtxBuffer.Size;
    CardFace(drawList, demo, pos, width, height);
    if (DEAL_SPIN != 0.f)
    {
        float degrees = DEAL_SPIN * (float)((index * 7) % 5 - 2) / 2.f;  // this card's own, settled on landing
        float angle = degrees * (3.14159265f / 180.f) * (1.f - eased);
        ImVec2 center(pos.x + width / 2, pos.y + height / 2);
        ImGui::ShadeVertsTransformPos(drawList, firstVertex, drawList->VtxBuffer.Size, center,
                                      std::cos(angle), std::sin(angle), center);
    }
    drawList->PopClipRect();
}

void DemoLauncher::CardFace(ImDrawList* drawList, const DemoEntry& demo, ImVec2 topLeft, float width, float height)
{
    // The card as primitives on a draw list (the flying double of Card, which lays it out as widgets)
    ImVec2 bottomRight(topLeft.x + width, topLeft.y + height);
    float padding = Em(0.6f), rounding = Em(0.5f);
    const float titleScale = 1.1f;
    float textScale = CardTextScale(width);
    drawList->AddRectFilled(topLeft, bottomRight, ImGui::ColorConvertFloat4ToU32(CARD_BG), rounding);
    DrawPicture(drawList, demo.stem, topLeft, width, PICTURE_ASPECT, Em(0.8f), ImDrawFlags_RoundCornersTop);
    float pictureBottom = topLeft.y + width / PICTURE_ASPECT;
    DrawTags(demo.Tags(), ImVec2(bottomRight.x - Em(0.4f), pictureBottom - Em(0.4f)), drawList, textScale);
    ImFont* font = ImGui::GetFont();
    float fontSize = ImGui::GetFontSize() * textScale;
    ImGui::PushFont(nullptr, ImGui::GetStyle().FontSizeBase * titleScale * textScale);
    std::string title = Fit(demo.label, width - 2 * padding, 1);
    ImGui::PopFont();
    ImGui::PushFont(nullptr, ImGui::GetStyle().FontSizeBase * textScale);
    std::string summary = Fit(demo.summaryPlain, width - 2 * padding, 2);
    ImGui::PopFont();
    float y = pictureBottom + Em(0.4f);
    drawList->AddText(font, fontSize * titleScale, ImVec2(topLeft.x + padding, y), ImGui::GetColorU32(ImGuiCol_Text),
                      title.c_str());
    y += fontSize * titleScale + ImGui::GetStyle().ItemSpacing.y;
    drawList->AddText(font, fontSize, ImVec2(topLeft.x + padding, y), ImGui::GetColorU32(ImGuiCol_TextDisabled),
                      summary.c_str(), nullptr, width - 2 * padding);
    drawList->AddRect(topLeft, bottomRight, ImGui::ColorConvertFloat4ToU32(CARD_BORDER), rounding);
}

void DemoLauncher::Gallery()
{
    SmoothScroll();
    ImVec2 pos = ImGui::GetWindowPos(), size = ImGui::GetWindowSize();
    _galleryRect = {pos, ImVec2(pos.x + size.x, pos.y + size.y)};
    float spacing = Em(1.f);
    float avail = ImGui::GetContentRegionAvail().x;
    _galleryWidth = avail;
    int columns = Columns(_cardWidth);
    float cardWidth = (avail - (columns - 1) * spacing) / columns;  // the cards fill the width
    std::vector<std::pair<const DemoCategory*, std::vector<const DemoEntry*>>> categories;
    for (const auto& category : _categories)
    {
        auto shown = Shown(category);
        if (!shown.empty())
            categories.emplace_back(&category, shown);
    }
    if (categories.empty())
    {
        ImGui::TextDisabled("No demo matches.");
        return;
    }
    _categoryInView = categories[0].first->name;
    for (size_t i = 0; i < categories.size(); ++i)
    {
        const auto& [category, shown] = categories[i];
        if (i)
            ImGui::Dummy(ImVec2(0, Em(0.6f)));
        _categoryY[category->name] = ImGui::GetCursorPosY();
        bool atTheEnd = ImGui::GetScrollY() >= ImGui::GetScrollMaxY() - 1;  // the last categories can't reach the top
        if (_categoryY[category->name] <= ImGui::GetScrollY() + Em(3.f) || atTheEnd)
            _categoryInView = category->name;
        BigText(category->name.c_str(), 1.45f, CATEGORY_TITLE);
        ImGui::TextDisabled("%s", category->about.c_str());
        if (!category->tip.empty())
            ImGui::TextDisabled("%s", category->tip.c_str());
        ImGui::Dummy(ImVec2(0, Em(0.3f)));
        for (size_t j = 0; j < shown.size(); ++j)
        {
            if (j % columns)
                ImGui::SameLine(0, spacing);
            else if (j)
                ImGui::Dummy(ImVec2(0, Em(0.3f)));  // a little space between the rows
            const DemoEntry& demo = *shown[j];
            if (_dealOrder.has_value() && !_dealOrder->count(demo.filename) && Dealing())
            {
                // In view when the deal begins: dealt, in this order
                float top = ImGui::GetCursorScreenPos().y;
                float height = cardWidth / PICTURE_ASPECT + ImGui::GetTextLineHeight() * 3.1f + Em(1.6f);
                if (top + height > _galleryRect.first.y && top < _galleryRect.second.y)
                    (*_dealOrder)[demo.filename] = (int)_dealOrder->size();
            }
            Card(demo, cardWidth);
        }
        ImGui::Dummy(ImVec2(0, Em(0.8f)));
    }
}


// ---------------------------------------------------------------------------------------------------------------------
// The detail pane, and the code view
// ---------------------------------------------------------------------------------------------------------------------
bool DemoLauncher::Action(const char* label, const char* tooltip)
{
    bool clicked = ImGui::Button(label, ImVec2(-1, 0));
    ImGui::SetItemTooltip("%s", tooltip);
    return clicked;
}

void DemoLauncher::ShowCodeOf(const DemoEntry& demo)
{
    std::string pythonFile = demo.pythonFile;
    if (!demo.variants.empty())
        pythonFile = demo.variants[_variant[demo.filename]].second;
    std::vector<CodeFile> files = {MakeCodeFile(pythonFile, "Python")};
    if (!demo.cppFile.empty())
        files.push_back(MakeCodeFile(demo.cppFile, "C++"));
    _codeView = std::make_pair(&demo, files);
}

// An action that opens a URL. In a browser, on a touch screen, the page opens it from the tap itself (a tap seen by
// ImGui is too late for the browser to allow a new tab)
void DemoLauncher::LinkAction(const char* label, const char* tooltip, const char* url)
{
    bool clicked = Action(label, tooltip);
#ifdef __EMSCRIPTEN__
    if (ImGui::GetIO().MouseSource == ImGuiMouseSource_TouchScreen)
    {
        HelloImGui::SetTapOpensUrl(ImGui::GetItemRectMin(), ImGui::GetItemRectMax(), url);
        return;
    }
#endif
    if (clicked)
        ImmApp::BrowseToUrl(url);
}

void DemoLauncher::Detail()
{
    // The selected demo: its picture, its description, and what to do with it
    if (_selected == nullptr)
        return;
    const DemoEntry& demo = *_selected;
    float appear = Tween(("appear " + demo.filename).c_str(), 1.f, 0.35f, 0.f);  // a new selection fades in
    ImGui::PushStyleVar(ImGuiStyleVar_Alpha, appear);
    ImGui::SetCursorPosY(ImGui::GetCursorPosY() + (1.f - appear) * Em(1.f));  // it slides in a little
    float width = ImGui::GetContentRegionAvail().x;
    ImVec2 pictureTopLeft = ImGui::GetCursorScreenPos();
    ImGui::Dummy(ImVec2(width, width / PICTURE_ASPECT));
    DrawPicture(ImGui::GetWindowDrawList(), demo.stem, pictureTopLeft, width, PICTURE_ASPECT, Em(0.5f),
                ImDrawFlags_RoundCornersAll);
    ImVec2 pictureBottomRight = ImGui::GetItemRectMax();
    DrawTags(demo.Tags(), ImVec2(pictureBottomRight.x - Em(0.4f), pictureBottomRight.y - Em(0.4f)));
    ImGui::Dummy(ImVec2(0, Em(0.4f)));
    RichMd::Render("## " + demo.label + "\n\n" + demo.text);
    if (!demo.uses.empty())
    {
        std::string uses;
        for (const auto& library : demo.uses)
            uses += (uses.empty() ? "" : ", ") + library;
        ImGui::TextDisabled("Uses: %s", uses.c_str());
    }
    ImGui::Dummy(ImVec2(0, Em(0.6f)));

    if (!demo.page.empty())  // a page entry: its page and its video, nothing to run
    {
        LinkAction(ICON_FA_BOOK "  Read the page", "Opens the page in your browser", demo.page.c_str());
        if (!demo.video.empty())
            LinkAction(ICON_FA_FILM "  Watch the video", "Opens the video in your browser", demo.video.c_str());
        ImGui::PopStyleVar();
        return;
    }
    if (!demo.variants.empty())  // e.g. the Python backends: one card, a combo picks the file to run and to show
    {
        int& index = _variant[demo.filename];
        ImGui::SetNextItemWidth(-1);
        if (ImGui::BeginCombo("##variant", demo.variants[index].first.c_str()))
        {
            for (int i = 0; i < (int)demo.variants.size(); ++i)
                if (ImGui::Selectable(demo.variants[i].first.c_str(), i == index))
                    index = i;
            ImGui::EndCombo();
        }
    }
    if (inPlaceFunctions.count(demo.stem))
    {
        if (Action(ICON_FA_PLAY "  Run", "Shows the demo here"))
            demoToShowInPlace = demo.stem;
    }
    if (!demo.cppFile.empty())  // and, in a tab or a window of its own, when it has one
    {
#ifdef __EMSCRIPTEN__
        // "where" is about the Python version: the C++ one has a page of its own online, or none. On a touch screen,
        // the page opens a tab from the touch itself (a tap seen by ImGui is too late for the browser), and the
        // button does nothing more; on a desktop browser, a window of its own
        if (!demo.cppUrl.empty())
        {
            bool touch = ImGui::GetIO().MouseSource == ImGuiMouseSource_TouchScreen;
            bool clicked = Action(touch ? ICON_FA_PLAY "  Run in a new tab" : ICON_FA_PLAY "  Run in a new window",
                                  "Runs its C++ version in a browser window of its own");
            std::string url = ExplorerPage(demo) ? demo.stem + ".html" : demo.cppUrl;
            if (touch)
                HelloImGui::SetTapOpensUrl(ImGui::GetItemRectMin(), ImGui::GetItemRectMax(), url);
            else if (clicked)
            {
                if (ExplorerPage(demo))
                    SpawnDemo(demo.stem);
                else
                    ImmApp::BrowseToUrl(demo.cppUrl.c_str());
            }
        }
#else
        if (HasDemoExeFile(demo.stem))
            if (Action(ICON_FA_PLAY "  Run in a new window", "Runs its C++ version on your machine, in a new window"))
                SpawnDemo(demo.stem);
#endif
    }
    if (Action(ICON_FA_CODE "  View code", "Shows its code: Python, and C++ side by side when there is a C++ version"))
        ShowCodeOf(demo);
    if (demo.where != "desktop")
        if (Action(ICON_FA_GLOBE "  Open in the Python playground",
                   "Opens it in your browser, in the Python playground: edit its code, and run it again"))
            ImmApp::BrowseToUrl(PlaygroundUrl(demo).c_str());
#ifndef __EMSCRIPTEN__
    if (!demo.cppFile.empty() && !demo.cppUrl.empty())
        if (Action(ICON_FA_GLOBE "  Run the C++ version online",
                   "Opens its C++ version in your browser, compiled to WebAssembly"))
            ImmApp::BrowseToUrl(demo.cppUrl.c_str());
#endif
    ImGui::PopStyleVar();
}

void DemoLauncher::ShowCode()
{
    // The demo's code: its files (where they are, a way to open each), then the code, one language or both
    auto& [demo, files] = *_codeView;
    if (ImGui::Button(ICON_FA_ARROW_LEFT "  All the demos"))
    {
        _codeView.reset();
        return;
    }
    ImGui::SameLine();
    BigText(demo->label.c_str(), 1.3f);
    for (auto& file : files)  // where the file is, and how to open it
    {
        ImGui::PushID(file.language.c_str());
        ImGui::TextDisabled("%s:", file.language.c_str());
        ImGui::SameLine();
        ImGui::TextUnformatted(file.repoFile.c_str());
#ifndef __EMSCRIPTEN__
        ImGui::SameLine();
        if (ImGui::SmallButton(ICON_FA_FOLDER_OPEN "  Open"))
            ImmApp::BrowseToUrl(("file://" + RepoFile(file.repoFile)).c_str());
        ImGui::SetItemTooltip("Opens the file with the application your system uses for it");
#endif
        if (!file.GithubUrl().empty())
        {
            ImGui::SameLine();
            if (ImGui::SmallButton(ICON_FA_GLOBE "  GitHub"))
                ImmApp::BrowseToUrl(file.GithubUrl().c_str());
        }
        ImGui::PopID();
    }
    std::vector<CodeFile*> shown;
    if (files.size() == 2)  // one language, or both side by side
    {
        for (const char* choice : {"Side by side", "Python", "C++"})
            if (Chip(choice, choice == _codeLanguage ? 1.f : 0.f))
                _codeLanguage = choice;
        ImGui::NewLine();
    }
    for (auto& file : files)
        if (files.size() < 2 || _codeLanguage == "Side by side" || _codeLanguage == file.language)
            shown.push_back(&file);
    int lines = (int)(ImGui::GetContentRegionAvail().y / ImGui::GetTextLineHeight()) - 4;
    for (auto* file : shown)
    {
        file->snippet.HeightInLines = lines;
        file->snippet.MaxHeightInLines = lines;
        if (file->snippet.Code.empty())
            file->snippet.Code = "(this file is not available here)";
    }
    if (shown.size() == 2)
        Snippets::ShowSideBySideSnippets(shown[0]->snippet, shown[1]->snippet);
    else if (!shown.empty())
        Snippets::ShowCodeSnippet(shown[0]->snippet);
}

int DemoLauncher::Depth() const
{
    return (_codeView.has_value() ? 1 : 0) + (_detailOpen ? 1 : 0);
}

void DemoLauncher::Back()
{
    // One level back: closes the code view, else the detail page of a small screen
    if (_codeView.has_value())
        _codeView.reset();
    else if (_detailOpen)
        _detailOpen = false;
}

std::string DemoLauncher::Route() const
{
    if (_codeView.has_value())
        return "code/" + _codeView->first->stem;
    if (_detailOpen && _selected != nullptr)
        return "detail/" + _selected->stem;
    return "";
}

void DemoLauncher::GoTo(const std::string& route)
{
    // A route that names no level, or no demo of the catalog, leaves the gallery
    _codeView.reset();
    _detailOpen = false;
    size_t slash = route.find('/');
    if (slash == std::string::npos)
        return;
    const DemoEntry* demo = Find(route.substr(slash + 1));
    if (demo == nullptr)
        return;
    std::string level = route.substr(0, slash);
    if (level == "code")
        ShowCodeOf(*demo);
    else if (level == "detail")
    {
        _selected = demo;
        _detailOpen = SmallScreen();  // on a larger screen, the detail is beside the gallery
    }
}

void DemoLauncher::DetailPage()
{
    // On a small screen: the detail alone, full width, with the way back to the gallery
    if (ImGui::Button(ICON_FA_ARROW_LEFT "  All the demos"))
    {
        _detailOpen = false;
        return;
    }
    ImVec2 avail = ImGui::GetContentRegionAvail();
    ImGui::BeginChild("detail", avail);
    ImGui::BeginChild("detail content", ImVec2(avail.x - ImGui::GetStyle().ScrollbarSize, 0),
                      ImGuiChildFlags_AutoResizeY);
    Detail();
    ImGui::EndChild();
    ImGui::EndChild();
}

void DemoLauncher::Gui(bool withTitle)
{
    NewFrame();
    if (PicturesLoading() || _scrollTarget.has_value() || Dealing())
        HelloImGui::RequestRefresh();  // pictures that load, a scroll or a deal move on their own
    if (ImGui::IsKeyPressed(ImGuiKey_Escape) && !ImGui::IsAnyItemActive())  // active: the search box
        Back();
    if (_codeView.has_value())  // no header: the demo's title and the way back are the only row
    {
        ShowCode();
        return;
    }
    if (SmallScreen() && _detailOpen)
    {
        DetailPage();
        return;
    }
    if (withTitle)
        Title();
    Filters();
    ImVec2 avail = ImGui::GetContentRegionAvail();
    if (SmallScreen())  // the gallery alone: a card opens the detail as a page
    {
        ImGui::BeginChild("gallery", avail);
        Gallery();
        ImGui::EndChild();
        return;
    }
    float detailWidth = Em(DETAIL_WIDTH);
    ImGui::BeginChild("gallery", ImVec2(avail.x - detailWidth - Em(1.f), avail.y));
    Gallery();
    ImGui::EndChild();
    ImGui::SameLine(0, Em(1.f));
    ImGui::BeginChild("detail", ImVec2(detailWidth, avail.y));
    // The content in a child of fixed width (a scrollbar's width less than the pane), sized to its height: its
    // picture and markdown take the child's width, so the pane's scrollbar, which comes and goes with that height,
    // never changes their width
    ImGui::BeginChild("detail content", ImVec2(detailWidth - ImGui::GetStyle().ScrollbarSize, 0),
                      ImGuiChildFlags_AutoResizeY);
    Detail();
    ImGui::EndChild();
    ImGui::EndChild();
}

void gui_demo_immapp_launcher()
{
    static DemoLauncher launcher;
    launcher.Gui();
}
