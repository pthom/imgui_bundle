#include "demo_code_viewer.h"
#include "library_config.h"
#include "imgui.h"
#include "hello_imgui/hello_imgui.h"
#include "hello_imgui/icons_font_awesome_4.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include <string>
#include <map>
#include <vector>
#include <algorithm>
#include <cctype>
#include <fstream>
#include <optional>
#include "immapp/browse_to_url.h"
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#include <sys/stat.h>  // mkdir
#endif



namespace
{
    enum class LoadState { NotLoaded, Loading, Loaded, Failed };

    struct CodeFile
    {
        LoadState cppState = LoadState::NotLoaded;
        LoadState pyState  = LoadState::NotLoaded;
        std::string cppContent;
        std::string pyContent;
        TextEditor cppEditor;
        TextEditor pyEditor;
        std::map<std::string, int> pyMarkers;  // section_name → 1-based line number
    };

    std::map<std::string, CodeFile> g_codeFiles;  // Keyed by baseName (all files loaded)
    int g_currentFileIndex = 0;
    int g_pendingScrollLine = -1;
    std::string g_pendingScrollFile;
    std::string g_pendingScrollSection;  // section name from IMGUI_DEMO_MARKER
    bool g_showPython = false;      // Effective display state (may be temporarily overridden by Follow Source)
    bool g_userPrefPython = false;  // User's manual C++/Python preference (radio button)

    // Search state
    bool g_searchBarOpen = false;
    bool g_searchBarJustOpened = false;  // To auto-focus the input
    char g_searchBuffer[256] = "";
    bool g_searchCaseSensitive = true;
    bool g_searchMatchWord = true;
    size_t g_lastMatchOffset = std::string::npos;  // Byte offset of last match found

    bool g_pendingApiSearch = false;  // Trigger search on next frame after switching to API tab
    int g_pendingApiTabIndex = -1;   // Target tab index for pending API search

    // Pending match selection (deferred by one frame so horizontal scroll reset takes effect first)
    struct PendingMatch { int startLine, startCol, endLine, endCol; };
    std::optional<PendingMatch> g_pendingMatch;

    bool IsWordChar(char c) { return std::isalnum((unsigned char)c) || c == '_'; }

    bool IsWordBoundary(const std::string& s, size_t pos, size_t len)
    {
        if (pos > 0 && IsWordChar(s[pos - 1])) return false;
        size_t end = pos + len;
        if (end < s.size() && IsWordChar(s[end])) return false;
        return true;
    }

    bool MatchesAt(const std::string& haystack, size_t pos, const std::string& needle, bool caseSensitive)
    {
        if (pos + needle.size() > haystack.size()) return false;
        if (caseSensitive)
            return haystack.compare(pos, needle.size(), needle) == 0;
        for (size_t j = 0; j < needle.size(); ++j)
            if (std::tolower((unsigned char)haystack[pos + j]) != std::tolower((unsigned char)needle[j]))
                return false;
        return true;
    }

    size_t FindInString(const std::string& haystack, const std::string& needle, size_t startPos, bool caseSensitive, bool matchWord)
    {
        for (size_t pos = startPos; pos + needle.size() <= haystack.size(); ++pos)
        {
            if (MatchesAt(haystack, pos, needle, caseSensitive))
            {
                if (!matchWord || IsWordBoundary(haystack, pos, needle.size()))
                    return pos;
            }
        }
        return std::string::npos;
    }

    size_t RFindInString(const std::string& haystack, const std::string& needle, size_t endPos, bool caseSensitive, bool matchWord)
    {
        if (needle.empty()) return std::string::npos;
        size_t searchEnd = std::min(endPos, haystack.size());
        for (size_t i = searchEnd; i > 0; --i)
        {
            size_t pos = i - 1;
            if (MatchesAt(haystack, pos, needle, caseSensitive))
            {
                if (!matchWord || IsWordBoundary(haystack, pos, needle.size()))
                    return pos;
            }
        }
        return std::string::npos;
    }

    // Convert a byte offset in content to a 0-based line number
    int OffsetToLine(const std::string& content, size_t offset)
    {
        int line = 0;
        for (size_t i = 0; i < offset && i < content.size(); ++i)
            if (content[i] == '\n') ++line;
        return line;
    }

    // Convert a byte offset to a 0-based column (chars from start of line)
    int OffsetToColumn(const std::string& content, size_t offset)
    {
        int col = 0;
        for (size_t i = offset; i > 0; --i)
        {
            if (content[i - 1] == '\n') break;
            ++col;
        }
        return col;
    }

    // Convert cursor position to byte offset in content
    size_t CursorToOffset(TextEditor& editor, const std::string& content)
    {
        int curLine, curCol; editor.GetCursorPosition(curLine, curCol);
        size_t offset = 0;
        int line = 0;
        while (line < curLine && offset < content.size())
        {
            if (content[offset] == '\n') ++line;
            ++offset;
        }
        offset += curCol;
        return offset;
    }

    void GoToMatch(TextEditor& editor, const std::string& content, size_t found, size_t matchLen)
    {
        g_lastMatchOffset = found;
        int startLine = OffsetToLine(content, found);
        int startCol  = OffsetToColumn(content, found);
        int endLine   = OffsetToLine(content, found + matchLen);
        int endCol    = OffsetToColumn(content, found + matchLen);
        // Frame 1: move cursor to column 0 to reset horizontal scroll
        editor.SetCursorPosition(startLine, 0);
        editor.SetViewAtLine(startLine, TextEditor::SetViewAtLineMode::Centered);
        // Frame 2: select the match (deferred so scroll reset takes effect first)
        g_pendingMatch = PendingMatch{startLine, startCol, endLine, endCol};
    }

    // Search starting AFTER the last match (advances to next occurrence)
    void SearchNext(TextEditor& editor, const std::string& content, const char* text, bool caseSensitive, bool matchWord)
    {
        if (text[0] == '\0') return;
        std::string needle(text);
        size_t offset = (g_lastMatchOffset != std::string::npos) ? g_lastMatchOffset + 1 : CursorToOffset(editor, content);
        size_t found = FindInString(content, needle, offset, caseSensitive, matchWord);
        if (found == std::string::npos)
            found = FindInString(content, needle, 0, caseSensitive, matchWord);  // Wrap around
        if (found != std::string::npos)
            GoToMatch(editor, content, found, needle.size());
    }

    void SearchPrev(TextEditor& editor, const std::string& content, const char* text, bool caseSensitive, bool matchWord)
    {
        if (text[0] == '\0') return;
        std::string needle(text);
        // Search backward from before the last match
        size_t offset = (g_lastMatchOffset != std::string::npos && g_lastMatchOffset > 0) ? g_lastMatchOffset - 1 : CursorToOffset(editor, content);
        size_t found = RFindInString(content, needle, offset + 1, caseSensitive, matchWord);
        if (found == std::string::npos)
            found = RFindInString(content, needle, content.size(), caseSensitive, matchWord);  // Wrap around
        if (found != std::string::npos)
            GoToMatch(editor, content, found, needle.size());
    }

    // Count all matches and determine which one the cursor is on (1-based). Returns {current, total}.
    std::pair<int, int> CountMatches(const std::string& content, const char* text, bool caseSensitive, bool matchWord, size_t cursorOffset)
    {
        if (text[0] == '\0') return {0, 0};
        std::string needle(text);
        int total = 0;
        int current = 0;
        size_t pos = 0;
        while (true)
        {
            size_t found = FindInString(content, needle, pos, caseSensitive, matchWord);
            if (found == std::string::npos) break;
            ++total;
            if (found < cursorOffset)
                current = total;
            else if (current == 0)
                current = total;  // Cursor is before or at first match
            pos = found + 1;
        }
        return {current, total};
    }

    // Parse IMGUI_DEMO_MARKER("section") calls from source text, return section → 1-based line map
    std::map<std::string, int> ParseMarkers(const std::string& source)
    {
        std::map<std::string, int> markers;
        const std::string pattern = "IMGUI_DEMO_MARKER(\"";
        int lineNum = 1;
        size_t searchFrom = 0;

        while (true)
        {
            size_t found = source.find(pattern, searchFrom);
            if (found == std::string::npos) break;

            // Count newlines only between the last position and this match (one linear pass total)
            for (size_t i = searchFrom; i < found; ++i)
                if (source[i] == '\n') ++lineNum;

            // Extract marker name up to the closing quote on the same line
            size_t nameStart = found + pattern.size();
            size_t nameEnd   = source.find('"', nameStart);
            size_t lineEnd   = source.find('\n', found);
            if (nameEnd != std::string::npos && (lineEnd == std::string::npos || nameEnd < lineEnd))
                markers[source.substr(nameStart, nameEnd - nameStart)] = lineNum;

            // Advance past this line
            searchFrom = (lineEnd != std::string::npos) ? lineEnd + 1 : source.size();
            if (lineEnd != std::string::npos) ++lineNum;
        }
        return markers;
    }

    void PopulateEditor(CodeFile& cf, const std::string& content, bool isPython)
    {
        TextEditor& editor = isPython ? cf.pyEditor : cf.cppEditor;
        editor.SetText(content);
        editor.SetLanguageDefinition(isPython
            ? TextEditor::LanguageDefinitionId::Python
            : TextEditor::LanguageDefinitionId::Cpp);
        editor.SetPalette(TextEditor::PaletteId::Dark);
        editor.SetReadOnlyEnabled(true);
        editor.SetShowLineNumbersEnabled(true);
        editor.SetShowWhitespacesEnabled(false);
        if (isPython) {
            cf.pyContent = content;
            cf.pyMarkers = ParseMarkers(content);
            cf.pyState   = LoadState::Loaded;
        } else {
            cf.cppContent = content;
            cf.cppState   = LoadState::Loaded;
        }
    }

    // Desktop: reads from IMAN_DEMO_CODE_DIR/<filename> via std::ifstream.
    // Emscripten: called from OnWgetLoad after emscripten_async_wget completes.
    void LoadFile(const DemoFileInfo& fileInfo)
    {
        CodeFile& cf = g_codeFiles[fileInfo.baseName];

#ifndef __EMSCRIPTEN__
        auto loadOne = [&](const std::string& filename, LoadState& state, bool isPython)
        {
            if (state != LoadState::NotLoaded) return;
            state = LoadState::Loading;
            std::string path = std::string(IEX_DEMO_CODE_DIR) + "/" + filename;
            std::ifstream f(path);
            if (f) {
                std::string content(std::istreambuf_iterator<char>(f), {});
                PopulateEditor(cf, content, isPython);
            } else {
                state = LoadState::Failed;
            }
        };

        loadOne(fileInfo.cppDisplayName(), cf.cppState, false);
        if (fileInfo.hasPython)
            loadOne(fileInfo.pyDisplayName(), cf.pyState, true);
#endif
    }

#ifdef __EMSCRIPTEN__
    // Pending fetch map: MEMFS path ("/demo_code/foo.cpp") → {baseName, isPython}
    struct PendingFetch { std::string baseName; bool isPython; };
    std::map<std::string, PendingFetch> g_pendingFetches;

    void OnWgetDone(const char* arg, bool success)
    {
        // arg is the MEMFS local path ("/demo_code/foo.cpp") for onload,
        // or possibly the URL ("demo_code/foo.cpp") for onerror — try both.
        std::string key(arg);
        auto it = g_pendingFetches.find(key);
        if (it == g_pendingFetches.end())
            it = g_pendingFetches.find("/" + key);
        if (it == g_pendingFetches.end()) return;

        auto [baseName, isPython] = it->second;
        g_pendingFetches.erase(it);
        CodeFile& cf = g_codeFiles[baseName];
        LoadState& state = isPython ? cf.pyState : cf.cppState;

        if (!success) { state = LoadState::Failed; return; }

        // File is in MEMFS — ensure path has leading slash
        std::string path = (arg[0] == '/') ? key : ("/" + key);
        std::ifstream f(path);
        if (f) {
            std::string content(std::istreambuf_iterator<char>(f), {});
            PopulateEditor(cf, content, isPython);
        } else {
            state = LoadState::Failed;
        }
    }

    void OnWgetLoad (const char* path) { OnWgetDone(path, true);  }
    void OnWgetError(const char* path) { OnWgetDone(path, false); }

    void RequestFileLoad(const DemoFileInfo& fileInfo)
    {
        // Create /demo_code/ dir in MEMFS once (wget does not create parent dirs).
        static bool dirCreated = false;
        if (!dirCreated) { mkdir("/demo_code", 0777); dirCreated = true; }

        CodeFile& cf = g_codeFiles[fileInfo.baseName];
        auto fetchOne = [&](const std::string& url, LoadState& state, bool isPython)
        {
            if (state != LoadState::NotLoaded) return;
            state = LoadState::Loading;
            std::string localPath = "/" + url;
            g_pendingFetches[localPath] = {fileInfo.baseName, isPython};
            emscripten_async_wget(url.c_str(), localPath.c_str(), OnWgetLoad, OnWgetError);
        };
        fetchOne(fileInfo.cppFetchUrl(), cf.cppState, false);
        if (fileInfo.hasPython)
            fetchOne(fileInfo.pyFetchUrl(), cf.pyState, true);
    }
#endif  // __EMSCRIPTEN__

    int FindFileIndexInCurrentLibrary(const char* displayName)
    {
        // Match against .cpp display names in current library
        auto files = GetCurrentLibraryFiles();
        for (size_t i = 0; i < files.size(); ++i)
        {
            if (files[i].cppDisplayName() == displayName)
                return (int)i;
        }
        return -1;
    }

    void SearchInApi(const std::string& searchTerm)
    {
        // Find the API reference file that contains the search term
        auto files = GetCurrentLibraryFiles();
        int apiIdx = -1;
        int firstApiIdx = -1;
        for (size_t i = 0; i < files.size(); ++i)
        {
            if (!files[i].isApiReference) continue;
            if (firstApiIdx < 0) firstApiIdx = (int)i;

            // Check if this API file's content contains the term
            auto it = g_codeFiles.find(files[i].baseName);
            if (it != g_codeFiles.end() && !it->second.cppContent.empty())
            {
                if (it->second.cppContent.find(searchTerm) != std::string::npos)
                {
                    apiIdx = (int)i;
                    break;
                }
            }
            else
            {
                // File not loaded yet — load it now to check
#ifndef __EMSCRIPTEN__
                LoadFile(files[i]);
                auto it2 = g_codeFiles.find(files[i].baseName);
                if (it2 != g_codeFiles.end() && it2->second.cppContent.find(searchTerm) != std::string::npos)
                {
                    apiIdx = (int)i;
                    break;
                }
#endif
            }
        }
        // Fall back to first API file if term not found in any
        if (apiIdx < 0) apiIdx = firstApiIdx;
        if (apiIdx < 0) return;

        // Switch to API tab
        g_currentFileIndex = apiIdx;

        // Fill search buffer and trigger search
        snprintf(g_searchBuffer, sizeof(g_searchBuffer), "%s", searchTerm.c_str());
        g_searchBarOpen = true;
        g_lastMatchOffset = std::string::npos;  // Reset to search from beginning
        g_pendingApiTabIndex = apiIdx;
        g_pendingApiSearch = true;
    }
}

int DemoCodeViewer_GetCurrentFileIndex() { return g_currentFileIndex; }
bool DemoCodeViewer_GetShowPython() { return g_userPrefPython; }
void DemoCodeViewer_SetShowPython(bool show) { g_showPython = show; g_userPrefPython = show; }

void DemoCodeViewer_Show()
{
    // Get files for current library
    auto files = GetCurrentLibraryFiles();

    // Tabs for file selection
    if (ImGui::BeginTabBar("CodeViewerTabs"))
    {
        for (size_t i = 0; i < files.size(); ++i)
        {
            const auto& file = files[i];
            std::string displayName = (g_showPython && file.hasPython) ? file.pyDisplayName() : file.cppDisplayName();

            ImGuiTabItemFlags flags = 0;
            // If we have a pending scroll for this file, select its tab
            if (!g_pendingScrollFile.empty() && g_pendingScrollFile == file.cppDisplayName())
                flags |= ImGuiTabItemFlags_SetSelected;
            // If pending API search, select the target tab
            if (g_pendingApiSearch && (int)i == g_pendingApiTabIndex)
                flags |= ImGuiTabItemFlags_SetSelected;

            // Tinted tabs for API reference files
            int colorsPushed = 0;
            if (file.isApiReference)
            {
                ImGui::PushStyleColor(ImGuiCol_Tab, ImVec4(0.15f, 0.25f, 0.40f, 1.0f));
                ImGui::PushStyleColor(ImGuiCol_TabHovered, ImVec4(0.25f, 0.40f, 0.55f, 1.0f));
                ImGui::PushStyleColor(ImGuiCol_TabSelected, ImVec4(0.20f, 0.35f, 0.50f, 1.0f));
                colorsPushed = 3;
            }

            if (ImGui::BeginTabItem(displayName.c_str(), nullptr, flags))
            {
                g_currentFileIndex = (int)i;
                ImGui::EndTabItem();
            }

            if (colorsPushed > 0)
                ImGui::PopStyleColor(colorsPushed);
        }
        ImGui::EndTabBar();
    }

    if (files.empty())
    {
        ImGui::TextWrapped("No demo files configured");
        return;
    }

    // Clamp file index to valid range (may change when switching libraries)
    if (g_currentFileIndex >= (int)files.size())
        g_currentFileIndex = 0;

    // Display the current file's editor — load lazily on first access
    const auto& currentFile = files[g_currentFileIndex];
#ifdef __EMSCRIPTEN__
    RequestFileLoad(currentFile);  // no-op if already Loading/Loaded/Failed
#else
    LoadFile(currentFile);         // no-op if already Loading/Loaded/Failed
#endif

    CodeFile& cf = g_codeFiles[currentFile.baseName];
    // Handle pending scroll (before computing showingPython, since it may switch language)
    if (!g_pendingScrollFile.empty() && g_pendingScrollFile == currentFile.cppDisplayName() && g_pendingScrollLine > 0)
    {
        bool scrolledPython = false;
        if (g_userPrefPython && cf.pyState == LoadState::Loaded && !g_pendingScrollSection.empty())
        {
            auto it2 = cf.pyMarkers.find(g_pendingScrollSection);
            if (it2 != cf.pyMarkers.end())
            {
                int pyLine = it2->second;
                cf.pyEditor.SetViewAtLine(pyLine - 3, TextEditor::SetViewAtLineMode::FirstVisibleLine);
                cf.pyEditor.SetCursorPosition(pyLine - 1, 0);
                cf.pyEditor.SelectLine(pyLine - 1);
                scrolledPython = true;
            }
        }
        if (!scrolledPython)
        {
            cf.cppEditor.SetViewAtLine(g_pendingScrollLine - 3, TextEditor::SetViewAtLineMode::FirstVisibleLine);
            cf.cppEditor.SetCursorPosition(g_pendingScrollLine - 1, 0);
            cf.cppEditor.SelectLine(g_pendingScrollLine - 1);
        }
        // Auto-switch displayed language to match what we scrolled
        if (g_userPrefPython)
            g_showPython = scrolledPython;
        g_pendingScrollLine = -1;
        g_pendingScrollFile.clear();
        g_pendingScrollSection.clear();
    }

    bool showingPython = g_showPython && cf.pyState == LoadState::Loaded;
    LoadState activeState = showingPython ? cf.pyState : cf.cppState;
    std::string displayName = showingPython ? currentFile.pyDisplayName() : currentFile.cppDisplayName();

    if (activeState == LoadState::Loading)
    {
        ImGui::Text(ICON_FA_SPINNER " Loading %s ...", currentFile.cppDisplayName().c_str());
        return;
    }
    if (activeState == LoadState::Failed)
    {
        ImGui::TextColored(ImVec4(1.f, 0.4f, 0.4f, 1.f), "Failed to load %s", displayName.c_str());
        return;
    }

    TextEditor& editor = showingPython ? cf.pyEditor : cf.cppEditor;

    if (g_showPython && !currentFile.hasPython)
        ImGui::TextColored(ImVec4(1.f, 1.f, 0.5f, 1.f), "No Python code available for this demo");

    // Apply deferred match selection (frame 2 of GoToMatch: scroll left happened last frame)
    if (g_pendingMatch.has_value())
    {
        auto& m = g_pendingMatch.value();
        editor.SelectRegion(m.startLine, m.startCol, m.endLine, m.endCol);
        g_pendingMatch.reset();
    }

    // Top bar with line info and copy button
    {
        // Copy button
        ImGui::BeginDisabled(!editor.AnyCursorHasSelection());
        if (ImGui::Button(ICON_FA_COPY))
            editor.Copy();
        ImGui::EndDisabled();

        ImGui::SameLine();

        if (ImGui::SmallButton("View on github at this line"))
        {
            int line, column; editor.GetCursorPosition(line, column);
            const std::string& githubUrl = showingPython ? currentFile.pyGithubUrl : currentFile.cppGithubUrl;
            if (!githubUrl.empty())
                ImmApp::BrowseToUrl((githubUrl + "#L" + std::to_string(line + 1)).c_str());
        }

        ImGui::SameLine();

        // Search button
        if (ImGui::SmallButton(ICON_FA_SEARCH))
        {
            if (editor.AnyCursorHasSelection())
            {
                std::string sel = editor.GetSelectedText();
                if (!sel.empty())
                    snprintf(g_searchBuffer, sizeof(g_searchBuffer), "%s", sel.c_str());
            }
            g_searchBarOpen = true;
            g_searchBarJustOpened = true;
        }
        ImGui::SetItemTooltip("Search (Ctrl+F).\n You may also right click in the editor below.");

        ImGui::SameLine();

        // Search in API button
        ImGui::BeginDisabled(!editor.AnyCursorHasSelection());
        if (ImGui::SmallButton(ICON_FA_BOOK "##searchapi"))
        {
            std::string sel = editor.GetSelectedText();
            if (!sel.empty())
                SearchInApi(sel);
        }
        if (ImGui::IsItemHovered(ImGuiHoveredFlags_AllowWhenDisabled))
            ImGui::SetTooltip("Search selected text in API declarations (Ctrl+Shift+F)");
        ImGui::EndDisabled();

        ImGui::SameLine();

        int line, column; editor.GetCursorPosition(line, column);
        ImGui::Text("%6d / %6d  | %s", line + 1, editor.GetLineCount(), displayName.c_str());
    }

    // Content string for search operations
    const std::string& content = showingPython ? cf.pyContent : cf.cppContent;

    // Handle pending API search (triggered by SearchInApi on previous frame)
    if (g_pendingApiSearch && currentFile.isApiReference && !content.empty())
    {
        SearchNext(editor, content, g_searchBuffer, g_searchCaseSensitive, g_searchMatchWord);
        g_pendingApiSearch = false;
    }

    // Search bar (shown when g_searchBarOpen)
    if (g_searchBarOpen)
    {
        if (ImGui::SmallButton(ICON_FA_TIMES "##closesearch"))
            g_searchBarOpen = false;
        ImGui::SameLine();

        float em = HelloImGui::EmSize();
        ImGui::SetNextItemWidth(15.f * em);
        if (g_searchBarJustOpened)
        {
            ImGui::SetKeyboardFocusHere();
            g_searchBarJustOpened = false;
        }
        if (ImGui::InputText("##search", g_searchBuffer, sizeof(g_searchBuffer),
                             ImGuiInputTextFlags_EnterReturnsTrue))
        {
            SearchNext(editor, content, g_searchBuffer, g_searchCaseSensitive, g_searchMatchWord);
        }
        ImGui::SameLine();
        bool canSearch = g_searchBuffer[0] != '\0' && !content.empty();
        ImGui::BeginDisabled(!canSearch);
        ImGui::SetNextItemShortcut(ImGuiKey_F3, ImGuiInputFlags_RouteGlobal);
        if (ImGui::SmallButton(ICON_FA_ARROW_DOWN))
            SearchNext(editor, content, g_searchBuffer, g_searchCaseSensitive, g_searchMatchWord);
        ImGui::SetItemTooltip("Next match (F3)");
        ImGui::SameLine();
        ImGui::SetNextItemShortcut(ImGuiKey_F3 | ImGuiMod_Shift, ImGuiInputFlags_RouteGlobal);
        if (ImGui::SmallButton(ICON_FA_ARROW_UP))
            SearchPrev(editor, content, g_searchBuffer, g_searchCaseSensitive, g_searchMatchWord);
        ImGui::SetItemTooltip("Previous match (Shift+F3)");
        ImGui::EndDisabled();
        ImGui::SameLine();
        ImGui::SetNextItemShortcut(ImGuiKey_C | ImGuiMod_Alt, ImGuiInputFlags_RouteGlobal);
        ImGui::Checkbox("Aa##casesensitive", &g_searchCaseSensitive);
        ImGui::SetItemTooltip("Case sensitive (Alt+C)");
        ImGui::SameLine();
        ImGui::SetNextItemShortcut(ImGuiKey_W | ImGuiMod_Alt, ImGuiInputFlags_RouteGlobal);
        ImGui::Checkbox("Word##matchword", &g_searchMatchWord);
        ImGui::SetItemTooltip("Match whole word (Alt+W)");

        // Show match count: "current / total"
        if (g_searchBuffer[0] != '\0')
        {
            ImGui::SameLine();
            size_t cursorOff = CursorToOffset(editor, content);
            auto [current, total] = CountMatches(content, g_searchBuffer, g_searchCaseSensitive, g_searchMatchWord, cursorOff);
            if (total == 0)
                ImGui::TextColored(ImVec4(1.f, 0.4f, 0.4f, 1.f), "No matches");
            else
                ImGui::Text("%d / %d", current, total);
        }
    }

    // Ctrl+F shortcut: open search bar, or re-focus input if already open
    if (ImGui::IsKeyChordPressed(ImGuiMod_Ctrl | ImGuiKey_F))
    {
        g_searchBarOpen = true;
        g_searchBarJustOpened = true;
        std::string sel = editor.GetSelectedText();
        if (!sel.empty())
            snprintf(g_searchBuffer, sizeof(g_searchBuffer), "%s", sel.c_str());
    }

    // Ctrl+Shift+F shortcut to search in API declarations
    if (ImGui::IsKeyChordPressed(ImGuiMod_Ctrl | ImGuiMod_Shift | ImGuiKey_F))
    {
        std::string sel = editor.GetSelectedText();
        if (!sel.empty())
            SearchInApi(sel);
    }

    // Use code font if available
    auto codeFont = ImGuiMd::GetCodeFont();
    if (codeFont.font)
        ImGui::PushFont(codeFont.font, codeFont.size);

    // Use unique ID per file and language to keep cursor/scroll state independent
    std::string editorId = std::string("##code_") + displayName;
    editor.Render(editorId.c_str(), false, ImGui::GetContentRegionAvail());

    // Right-click context menu on the editor
    static std::string rightClickWord;
    if (ImGui::IsItemClicked(ImGuiMouseButton_Right))
    {
        std::string sel = editor.GetSelectedText();
        if (!sel.empty())
            rightClickWord = sel;
        else
        {
            rightClickWord = editor.GetWordAtScreenPos(ImGui::GetMousePos());
        }
        if (!rightClickWord.empty())
            ImGui::OpenPopup("CodeEditorContext");
    }
    if (ImGui::BeginPopup("CodeEditorContext"))
    {
        if (codeFont.font)
            ImGui::PopFont(); // restore font for menu

        std::string truncSel = rightClickWord.substr(0, 30) + (rightClickWord.size() > 30 ? "..." : "");

        std::string menuLabel = "Search \"" + truncSel + "\" in this file";
        if (ImGui::MenuItem(menuLabel.c_str()))
        {
            snprintf(g_searchBuffer, sizeof(g_searchBuffer), "%s", rightClickWord.c_str());
            g_searchBarOpen = true;
            g_lastMatchOffset = CursorToOffset(editor, content);  // Next/Prev start from here
        }

        std::string apiLabel = "Search \"" + truncSel + "\" in API";
        if (ImGui::MenuItem(apiLabel.c_str()))
            SearchInApi(rightClickWord);

        if (codeFont.font)
            ImGui::PushFont(codeFont.font, codeFont.size);

        ImGui::EndPopup();
    }

    if (codeFont.font)
        ImGui::PopFont();
}

int DemoCodeViewer_GetPythonLineForSection(const char* cppFilename, const char* section)
{
    if (!section || section[0] == '\0') return -1;
    // Find the baseName by stripping the extension from cppFilename
    std::string cpp(cppFilename);
    auto dot = cpp.rfind('.');
    if (dot == std::string::npos) return -1;
    std::string baseName = cpp.substr(0, dot);
    auto it = g_codeFiles.find(baseName);
    if (it == g_codeFiles.end() || it->second.pyState != LoadState::Loaded) return -1;
    auto it2 = it->second.pyMarkers.find(section);
    if (it2 == it->second.pyMarkers.end()) return -1;
    return it2->second;  // 1-based line number
}

void DemoCodeViewer_ShowCodeAt(const char* filename, int line, const char* section)
{
    // Store the request - will be processed on next render
    g_pendingScrollFile = filename;
    g_pendingScrollLine = line;
    g_pendingScrollSection = section ? section : "";

    // Switch to the correct tab (within current library)
    int idx = FindFileIndexInCurrentLibrary(filename);
    if (idx >= 0)
    {
        g_currentFileIndex = idx;
    }
}
