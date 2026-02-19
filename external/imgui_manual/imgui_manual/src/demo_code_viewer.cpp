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
#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif


void OpenUrl(const std::string &url)
{
    bool isAbsoluteUrl = url.find("http") == 0;
    if (!isAbsoluteUrl)
        return;
#if defined(__EMSCRIPTEN__)
    std::string js_command = "window.open(\"" + url + "\");";
    emscripten_run_script(js_command.c_str());
#elif defined(_WIN32)
    ShellExecuteA( NULL, "open", url.c_str(), NULL, NULL, SW_SHOWNORMAL );
#elif defined(__APPLE__)
    std::string cmd = std::string("open ") + url.c_str();
    system(cmd.c_str());
#endif
}

namespace
{
    struct CodeFile
    {
        std::string cppContent;
        std::string pyContent;
        TextEditor cppEditor;
        TextEditor pyEditor;
        bool cppLoaded = false;
        bool pyLoaded = false;
        std::map<std::string, int> pyMarkers;  // section_name → 1-based line number
    };

    std::map<std::string, CodeFile> g_codeFiles;  // Keyed by baseName (all files loaded)
    int g_currentFileIndex = 0;
    int g_pendingScrollLine = -1;
    std::string g_pendingScrollFile;
    std::string g_pendingScrollSection;  // section name from IMGUI_DEMO_MARKER
    bool g_showPython = false;  // Global toggle for C++/Python view

    // Search state
    bool g_searchBarOpen = false;
    bool g_searchBarJustOpened = false;  // To auto-focus the input
    char g_searchBuffer[256] = "";
    bool g_searchCaseSensitive = false;
    bool g_searchMatchWord = false;
    size_t g_lastMatchOffset = std::string::npos;  // Byte offset of last match found

    bool g_pendingApiSearch = false;  // Trigger search on next frame after switching to API tab

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

    void GoToMatch(TextEditor& editor, const std::string& content, size_t found)
    {
        g_lastMatchOffset = found;
        int foundLine = OffsetToLine(content, found);
        editor.SetCursorPosition(foundLine, 0);
        editor.SelectLine(foundLine);
        editor.SetViewAtLine(foundLine, TextEditor::SetViewAtLineMode::Centered);
    }

    void SearchNext(TextEditor& editor, const std::string& content, const char* text, bool caseSensitive, bool matchWord)
    {
        if (text[0] == '\0') return;
        std::string needle(text);
        // Start after the last match to advance forward
        size_t offset = (g_lastMatchOffset != std::string::npos) ? g_lastMatchOffset + 1 : CursorToOffset(editor, content);
        size_t found = FindInString(content, needle, offset, caseSensitive, matchWord);
        if (found == std::string::npos)
            found = FindInString(content, needle, 0, caseSensitive, matchWord);  // Wrap around
        if (found != std::string::npos)
            GoToMatch(editor, content, found);
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
            GoToMatch(editor, content, found);
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

    void LoadFile(const DemoFileInfo& fileInfo)
    {
        CodeFile& cf = g_codeFiles[fileInfo.baseName];

        // Load C++ file
        {
            std::string assetPath = std::string("demo_code/") + fileInfo.cppAssetName();
            auto assetData = HelloImGui::LoadAssetFileData(assetPath.c_str());
            if (assetData.data != nullptr && assetData.dataSize > 0)
            {
                cf.cppContent = std::string((const char*)assetData.data, assetData.dataSize);
                cf.cppEditor.SetText(cf.cppContent);
                cf.cppEditor.SetLanguageDefinition(TextEditor::LanguageDefinitionId::Cpp);
                cf.cppEditor.SetPalette(TextEditor::PaletteId::Dark);
                cf.cppEditor.SetReadOnlyEnabled(true);
                cf.cppEditor.SetShowLineNumbersEnabled(true);
                cf.cppEditor.SetShowWhitespacesEnabled(false);
                cf.cppLoaded = true;
                HelloImGui::FreeAssetFileData(&assetData);
            }
        }

        // Load Python file if it exists
        if (fileInfo.hasPython)
        {
            std::string assetPath = std::string("demo_code/") + fileInfo.pyAssetName();
            auto assetData = HelloImGui::LoadAssetFileData(assetPath.c_str());
            if (assetData.data != nullptr && assetData.dataSize > 0)
            {
                cf.pyContent = std::string((const char*)assetData.data, assetData.dataSize);
                cf.pyEditor.SetText(cf.pyContent);
                cf.pyEditor.SetLanguageDefinition(TextEditor::LanguageDefinitionId::Python);
                cf.pyEditor.SetPalette(TextEditor::PaletteId::Dark);
                cf.pyEditor.SetReadOnlyEnabled(true);
                cf.pyEditor.SetShowLineNumbersEnabled(true);
                cf.pyEditor.SetShowWhitespacesEnabled(false);
                cf.pyLoaded = true;
                cf.pyMarkers = ParseMarkers(cf.pyContent);
                HelloImGui::FreeAssetFileData(&assetData);
            }
        }
    }

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
        // Find the API reference file index in current library
        auto files = GetCurrentLibraryFiles();
        int apiIdx = -1;
        for (size_t i = 0; i < files.size(); ++i)
        {
            if (files[i].isApiReference) { apiIdx = (int)i; break; }
        }
        if (apiIdx < 0) return;

        // Switch to API tab
        g_currentFileIndex = apiIdx;

        // Fill search buffer and trigger search
        snprintf(g_searchBuffer, sizeof(g_searchBuffer), "%s", searchTerm.c_str());
        g_searchBarOpen = true;
        g_lastMatchOffset = std::string::npos;  // Reset to search from beginning
        g_pendingApiSearch = true;
    }
}

bool DemoCodeViewer_GetShowPython() { return g_showPython; }
void DemoCodeViewer_SetShowPython(bool show) { g_showPython = show; }

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
            bool hasPy = file.hasPython && g_codeFiles.count(file.baseName) && g_codeFiles[file.baseName].pyLoaded;
            std::string displayName = (g_showPython && hasPy) ? file.pyDisplayName() : file.cppDisplayName();

            ImGuiTabItemFlags flags = 0;
            // If we have a pending scroll for this file, select its tab
            if (!g_pendingScrollFile.empty() && g_pendingScrollFile == file.cppDisplayName())
                flags |= ImGuiTabItemFlags_SetSelected;
            // If pending API search, select the API tab
            if (g_pendingApiSearch && file.isApiReference)
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
    if (g_codeFiles.find(currentFile.baseName) == g_codeFiles.end())
        LoadFile(currentFile);
    auto it = g_codeFiles.find(currentFile.baseName);
    if (it == g_codeFiles.end())
    {
        ImGui::TextWrapped("File not found: %s", currentFile.baseName.c_str());
        return;
    }

    CodeFile& cf = it->second;
    bool showingPython = g_showPython && cf.pyLoaded;
    TextEditor& editor = showingPython ? cf.pyEditor : cf.cppEditor;
    bool loaded = showingPython ? cf.pyLoaded : cf.cppLoaded;
    std::string displayName = showingPython ? currentFile.pyDisplayName() : currentFile.cppDisplayName();

    if (!loaded)
    {
        ImGui::TextWrapped("Failed to load %s", displayName.c_str());
        return;
    }

    if (g_showPython && !cf.pyLoaded)
        ImGui::TextColored(ImVec4(1.f, 1.f, 0.5f, 1.f), "No Python code available for this demo");

    // Handle pending scroll
    if (!g_pendingScrollFile.empty() && g_pendingScrollFile == currentFile.cppDisplayName() && g_pendingScrollLine > 0)
    {
        bool scrolledPython = false;
        // If viewing Python and we have a section match, scroll Python editor
        if (g_showPython && cf.pyLoaded && !g_pendingScrollSection.empty())
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
        // Otherwise scroll C++ editor (without changing the user's language preference)
        if (!scrolledPython)
        {
            cf.cppEditor.SetViewAtLine(g_pendingScrollLine - 3, TextEditor::SetViewAtLineMode::FirstVisibleLine);
            cf.cppEditor.SetCursorPosition(g_pendingScrollLine - 1, 0);
            cf.cppEditor.SelectLine(g_pendingScrollLine - 1);
        }
        g_pendingScrollLine = -1;
        g_pendingScrollFile.clear();
        g_pendingScrollSection.clear();
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
                OpenUrl(githubUrl + "#L" + std::to_string(line + 1));
        }

        ImGui::SameLine();

        // Search button
        if (ImGui::SmallButton(ICON_FA_SEARCH))
        {
            std::string sel = editor.GetSelectedText();
            if (!sel.empty())
                snprintf(g_searchBuffer, sizeof(g_searchBuffer), "%s", sel.c_str());
            g_searchBarOpen = true;
            g_searchBarJustOpened = true;
        }

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
    if (g_pendingApiSearch && currentFile.isApiReference)
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
        if (ImGui::SmallButton("Next"))
            SearchNext(editor, content, g_searchBuffer, g_searchCaseSensitive, g_searchMatchWord);
        ImGui::SameLine();
        if (ImGui::SmallButton("Prev"))
            SearchPrev(editor, content, g_searchBuffer, g_searchCaseSensitive, g_searchMatchWord);
        ImGui::SameLine();
        ImGui::Checkbox("Aa##casesensitive", &g_searchCaseSensitive);
        ImGui::SameLine();
        ImGui::Checkbox("Word##matchword", &g_searchMatchWord);

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

    // Ctrl+F shortcut to toggle search bar
    if (ImGui::IsKeyChordPressed(ImGuiMod_Ctrl | ImGuiKey_F))
    {
        g_searchBarOpen = !g_searchBarOpen;
        if (g_searchBarOpen)
        {
            g_searchBarJustOpened = true;
            std::string sel = editor.GetSelectedText();
            if (!sel.empty())
                snprintf(g_searchBuffer, sizeof(g_searchBuffer), "%s", sel.c_str());
        }
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
    ImGui::OpenPopupOnItemClick("CodeEditorContext", ImGuiPopupFlags_MouseButtonRight);
    if (ImGui::BeginPopup("CodeEditorContext"))
    {
        if (codeFont.font)
            ImGui::PopFont(); // restore font for menu

        std::string sel = editor.GetSelectedText();
        if (!sel.empty())
        {
            std::string truncSel = sel.substr(0, 30) + (sel.size() > 30 ? "..." : "");

            std::string menuLabel = "Search \"" + truncSel + "\" in this file";
            if (ImGui::MenuItem(menuLabel.c_str()))
            {
                snprintf(g_searchBuffer, sizeof(g_searchBuffer), "%s", sel.c_str());
                g_searchBarOpen = true;
                SearchNext(editor, content, g_searchBuffer, g_searchCaseSensitive, g_searchMatchWord);
            }

            std::string apiLabel = "Search \"" + truncSel + "\" in API";
            if (ImGui::MenuItem(apiLabel.c_str()))
                SearchInApi(sel);
        }

        if (codeFont.font)
            ImGui::PushFont(codeFont.font, codeFont.size);
        
        ImGui::EndPopup();
    }

    if (codeFont.font)
        ImGui::PopFont();
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
