#include "demo_code_viewer.h"
#include "library_config.h"
#include "api_index.h"
#include "imgui.h"
#include "hello_imgui/hello_imgui.h"
#include "hello_imgui/icons_font_awesome_4.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#include "imgui_rich_md/rich_md.h"
#include <string>
#include <map>
#include <vector>
#include <algorithm>
#include <cctype>
#include <cstring>
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

    // Editor display preferences (apply to whichever editor is currently shown)
    bool g_wordWrap = false;
    bool g_showMinimap = true;

    // The API tab (after the files' tabs): the entry shown, or the candidates of an ambiguous lookup
    ApiRef g_apiCurrent;
    std::vector<ApiRef> g_apiCandidates;
    bool g_pendingApiTabSelect = false;  // select the API tab on the next tab bar
    char g_apiFilter[128] = "";
    bool g_pendingScrollPython = false;  // the pending scroll targets a line of the Python file itself
    bool g_apiTooltips = true;  // a tooltip with the API of the identifier under the mouse
    ApiRef g_pendingDeclRef;    // a "Go to declaration" waiting for its file (the web loads them asynchronously)
    bool g_pendingDeclPython = false;

    // Python-only mode state
    bool g_pythonOnlyMode = false;
    std::string g_pythonPackageRoot;  // root of the imgui_bundle Python package
    std::string g_pyDemoCodeDir;     // pythonPackageRoot + "/demos_python/demos_imgui_explorer"

    std::string GetDemoCodeDir()
    {
        if (g_pythonOnlyMode)
            return g_pyDemoCodeDir;
#ifdef IEX_DEMO_CODE_DIR
        return IEX_DEMO_CODE_DIR;
#else
        return {};
#endif
    }

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
        auto pos = editor.GetMainCursorPosition();
        size_t offset = 0;
        size_t line = 0;
        while (line < pos.line && offset < content.size())
        {
            if (content[offset] == '\n') ++line;
            ++offset;
        }
        offset += pos.index;
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
        editor.SetCursor(TextEditor::DocPos(startLine, 0));
        editor.ScrollToLine(startLine, TextEditor::Scroll::alignMiddle);
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

    // Shows a line: the cursor on it, scrolled near the top, highlighted by a line marker (not a selection: a selection
    // would feed the copy button and the search)
    void ShowLine(CodeFile& cf, bool python, int line)
    {
        TextEditor& editor = python ? cf.pyEditor : cf.cppEditor;
        cf.cppEditor.ClearMarkers();
        cf.pyEditor.ClearMarkers();
        editor.AddMarker((size_t)line, IM_COL32(255, 220, 100, 110), IM_COL32(255, 220, 100, 36), "", "");
        editor.SetCursor(TextEditor::DocPos(line, 0));
        editor.ScrollToLine(line - 2, TextEditor::Scroll::alignTop);
    }

    void PopulateEditor(CodeFile& cf, const std::string& content, bool isPython)
    {
        TextEditor& editor = isPython ? cf.pyEditor : cf.cppEditor;
        editor.SetText(content);
        editor.SetLanguage(isPython
            ? TextEditor::Language::Python()
            : TextEditor::Language::Cpp());
        editor.SetPalette(TextEditor::GetDarkPalette());
        editor.SetReadOnlyEnabled(true);
        editor.SetShowLineNumbersEnabled(true);
        editor.SetShowWhitespacesEnabled(false);
        editor.SetLineFoldingEnabled(true);
        if (isPython) {
            cf.pyContent = content;
            cf.pyMarkers = ParseMarkers(content);
            cf.pyState   = LoadState::Loaded;
        } else {
            cf.cppContent = content;
            cf.cppState   = LoadState::Loaded;
        }
    }

    // Resolve the file path for a Python file, using pyPackageRelativePath if
    // in Python-only mode and the field is set, otherwise flat lookup in demo code dir.
    std::string ResolvePyFilePath(const DemoFileInfo& fileInfo)
    {
        if (g_pythonOnlyMode && !fileInfo.pyPackageRelativePath.empty())
            return g_pythonPackageRoot + "/" + fileInfo.pyPackageRelativePath;
        std::string dir = GetDemoCodeDir();
        if (!dir.empty())
            return dir + "/" + fileInfo.pyDisplayName();
        return {};
    }

    // Desktop: reads from demo code dir via std::ifstream.
    // Emscripten: called from OnWgetLoad after emscripten_async_wget completes.
    void LoadFile(const DemoFileInfo& fileInfo)
    {
        CodeFile& cf = g_codeFiles[fileInfo.baseName];

#ifndef __EMSCRIPTEN__
        auto loadOne = [&](const std::string& path, LoadState& state, bool isPython)
        {
            if (state != LoadState::NotLoaded) return;
            state = LoadState::Loading;

            if (!path.empty()) {
                std::ifstream f(path);
                if (f) {
                    std::string content(std::istreambuf_iterator<char>(f), {});
                    PopulateEditor(cf, content, isPython);
                    return;
                }
            }
            state = LoadState::Failed;
        };

        {
            std::string dir = GetDemoCodeDir();
            std::string cppPath = dir.empty() ? "" : dir + "/" + fileInfo.cppDisplayName();
            loadOne(cppPath, cf.cppState, false);
        }
        if (fileInfo.hasPython)
            loadOne(ResolvePyFilePath(fileInfo), cf.pyState, true);
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


    // -----------------------------------------------------------------------------------------------------------------
    // The API tab: the card of an entry of the index (api_index.h), the list of all the entries, a filter
    // -----------------------------------------------------------------------------------------------------------------

    std::string IdentifierAtCursor(const TextEditor& editor)
    {
        auto pos = editor.GetMainCursorPosition();
        return ApiIndex_IdentifierAt(editor.GetLineText(pos.line), pos.index);
    }

    std::string BareCppName(const std::string& cppName)
    {
        size_t pos = cppName.rfind("::");
        return pos == std::string::npos ? cppName : cppName.substr(pos + 2);
    }

    // The first declarations file of the library, in the shown language: "imgui.h", or "imgui.pyi"
    std::string FirstApiFileName(bool python)
    {
        for (const auto& file : GetCurrentLibraryFiles())
            if (file.isApiReference)
                return python ? file.pyDisplayName() : file.cppDisplayName();
        return "the declarations";
    }

    // The name of an entry in a list: without the module in Python (button, ImDrawList.add_line), as typed in C++
    std::string ListLabel(const ApiRef& ref, bool python)
    {
        if (!python)
            return ref.CppName();
        return ref.owner ? ref.owner->name + "." + ref.entry->name : ref.entry->name;
    }

    // Shows the hits of a lookup in the API tab: the entry when there is one, a choice otherwise
    void OpenApi(const std::vector<ApiRef>& hits)
    {
        if (hits.empty())
            return;
        if (hits.size() == 1)
        {
            g_apiCurrent = hits[0];
            g_apiCandidates.clear();
        }
        else
        {
            g_apiCurrent = ApiRef();
            g_apiCandidates = hits;
        }
        g_apiFilter[0] = '\0';
        g_currentFileIndex = (int)GetCurrentLibraryFiles().size();
        g_pendingApiTabSelect = true;
    }

    void ShowCode(const std::string& text, bool muted, float wrapWidth = 0.f)
    {
        auto codeFont = RichMd::GetCodeFont();
        if (codeFont.font)
            ImGui::PushFont(codeFont.font, codeFont.size);
        if (muted)
            ImGui::PushStyleColor(ImGuiCol_Text, ImGui::GetStyleColorVec4(ImGuiCol_TextDisabled));
        if (wrapWidth > 0.f)
            ImGui::PushTextWrapPos(ImGui::GetCursorPosX() + wrapWidth);
        ImGui::TextWrapped("%s", text.c_str());
        if (wrapWidth > 0.f)
            ImGui::PopTextWrapPos();
        if (muted)
            ImGui::PopStyleColor();
        if (codeFont.font)
            ImGui::PopFont();
    }

    // The hover tooltip: the signature in the shown language, the name in the other, the first sentence of the doc
    void ShowApiTooltip(const ApiRef& ref, bool python, size_t hitCount)
    {
        const ApiEntry& e = *ref.entry;
        float wrap = ImGui::GetFontSize() * 45.f;
        const std::string& signature = python ? e.py : e.cpp;
        ShowCode(signature.empty() ? (python ? ref.PyName() : ref.CppName()) : signature, false, wrap);
        ImGui::PushTextWrapPos(ImGui::GetCursorPosX() + wrap);
        ImGui::TextDisabled("%s: %s", python ? "C++" : "Python", python ? ref.CppName().c_str() : ref.PyName().c_str());
        std::string sentence = ApiIndex_FirstSentence(e.doc.empty() ? e.note : e.doc);
        if (!sentence.empty())
            ImGui::TextUnformatted(sentence.c_str());
        if (hitCount > 1)
            ImGui::TextDisabled("%zu entries have this name: the API button lists them", hitCount);
        ImGui::PopTextWrapPos();
    }

    struct DemoUse
    {
        int line;             // 1-based
        std::string section;  // the IMGUI_DEMO_MARKER section above it
        std::string text;     // the line, trimmed
    };

    // The lines of a demo file that use an entry (a call for a function, the name for the others), each with the demo
    // section it belongs to. Comment lines are skipped
    std::vector<DemoUse> FindDemoUses(const std::string& content, const ApiRef& ref, bool python)
    {
        auto isIdent = [](char c) { return std::isalnum((unsigned char)c) || c == '_'; };
        std::string name = python ? ref.entry->name : BareCppName(ref.CppName());
        bool isCall = ref.entry->kind == "function" || ref.entry->kind == "method";
        const std::string markerPattern = "IMGUI_DEMO_MARKER(\"";
        std::vector<DemoUse> uses;
        std::string section;
        int lineNum = 1;
        size_t pos = 0;
        while (pos < content.size() && uses.size() < 60)
        {
            size_t eol = content.find('\n', pos);
            if (eol == std::string::npos)
                eol = content.size();
            std::string line = content.substr(pos, eol - pos);
            pos = eol + 1;
            size_t first = line.find_first_not_of(" \t");
            std::string trimmed = first == std::string::npos ? "" : line.substr(first);
            int thisLine = lineNum++;
            if (trimmed.empty() || trimmed.rfind("//", 0) == 0 || trimmed.rfind("#", 0) == 0)
                continue;
            size_t m = line.find(markerPattern);
            if (m != std::string::npos)
            {
                size_t s = m + markerPattern.size();
                size_t e = line.find('"', s);
                if (e != std::string::npos)
                    section = line.substr(s, e - s);
                continue;
            }
            size_t f = 0;
            while ((f = line.find(name, f)) != std::string::npos)
            {
                size_t after = f + name.size();
                bool wordStart = f == 0 || !isIdent(line[f - 1]);
                bool wordEnd = after >= line.size() || !isIdent(line[after]);
                if (wordStart && wordEnd)
                {
                    bool ok = true;
                    if (isCall)
                    {
                        size_t k = after;
                        while (k < line.size() && line[k] == ' ')
                            ++k;
                        ok = k < line.size() && line[k] == '(';
                    }
                    if (ok)
                    {
                        uses.push_back({thisLine, section, trimmed});
                        break;
                    }
                }
                f = after;
            }
        }
        return uses;
    }

    // "In the demo": a framed block with the lines of the library's demo file that use the entry, counted; a click
    // scrolls the code there
    void ShowDemoUses(const ApiRef& ref, bool python)
    {
        auto files = GetCurrentLibraryFiles();
        int demoIndex = -1;
        for (size_t i = 0; i < files.size(); ++i)
            if (!files[i].isApiReference && (!python || files[i].hasPython))
            {
                demoIndex = (int)i;
                break;
            }
        if (demoIndex < 0)
            return;
        const DemoFileInfo& file = files[demoIndex];
#ifdef __EMSCRIPTEN__
        RequestFileLoad(file);
#else
        LoadFile(file);
#endif
        CodeFile& cf = g_codeFiles[file.baseName];
        const std::string& content = python ? cf.pyContent : cf.cppContent;
        std::string displayName = python ? file.pyDisplayName() : file.cppDisplayName();

        // The uses, found once per entry, file and language
        static const ApiEntry* cachedEntry = nullptr;
        static std::string cachedFile;
        static std::vector<DemoUse> cachedUses;
        if (!content.empty() && (cachedEntry != ref.entry || cachedFile != displayName))
        {
            cachedEntry = ref.entry;
            cachedFile = displayName;
            cachedUses = FindDemoUses(content, ref, python);
        }

        ImGui::Dummy(ImVec2(0.f, ImGui::GetFontSize() * 0.8f));
        ImGui::PushStyleColor(ImGuiCol_ChildBg, ImVec4(0.5f, 0.5f, 0.5f, 0.10f));
        ImGui::BeginChild("api_uses", ImVec2(0.f, 0.f),
                          ImGuiChildFlags_Borders | ImGuiChildFlags_AutoResizeY | ImGuiChildFlags_AlwaysUseWindowPadding);
        std::string name = python ? ref.PyName() : ref.CppName();
        if (content.empty())
            ImGui::TextDisabled(ICON_FA_SPINNER " In the demo: loading %s ...", displayName.c_str());
        else if (cachedUses.empty())
            ImGui::TextDisabled("In the demo: %s is not used in %s", name.c_str(), displayName.c_str());
        else
        {
            ImGui::Text("In the demo: %zu use%s of %s", cachedUses.size(), cachedUses.size() > 1 ? "s" : "", name.c_str());
            ImGui::SameLine();
            ImGui::TextDisabled("(%s, a click shows the line)", displayName.c_str());
            ImGui::Spacing();
            auto codeFont = RichMd::GetCodeFont();
            for (size_t i = 0; i < cachedUses.size() && i < 40; ++i)
            {
                const DemoUse& use = cachedUses[i];
                std::string label = (use.section.empty() ? std::string("(top of file)") : use.section)
                                    + "  line " + std::to_string(use.line) + "##use" + std::to_string(i);
                if (ImGui::Selectable(label.c_str()))
                {
                    g_pendingScrollFile = file.cppDisplayName();
                    g_pendingScrollLine = use.line;
                    g_pendingScrollSection.clear();
                    g_pendingScrollPython = python;
                    g_currentFileIndex = demoIndex;
                }
                ImGui::Indent();
                if (codeFont.font)
                    ImGui::PushFont(codeFont.font, codeFont.size * 0.9f);
                ImGui::TextDisabled("%s", use.text.substr(0, 110).c_str());
                if (codeFont.font)
                    ImGui::PopFont();
                ImGui::Unindent();
            }
            if (cachedUses.size() > 40)
                ImGui::TextDisabled("... and %zu more", cachedUses.size() - 40);
        }
        ImGui::EndChild();
        ImGui::PopStyleColor();
    }

    // -----------------------------------------------------------------------------------------------------------------
    // "Go to declaration": the line of an entry in the header (C++) or in the stub (Python)
    // -----------------------------------------------------------------------------------------------------------------

    std::vector<std::string> SplitLines(const std::string& content)
    {
        std::vector<std::string> lines;
        size_t pos = 0;
        while (pos <= content.size())
        {
            size_t eol = content.find('\n', pos);
            if (eol == std::string::npos)
                eol = content.size();
            lines.push_back(content.substr(pos, eol - pos));
            pos = eol + 1;
        }
        return lines;
    }

    std::string NormalizeSpaces(const std::string& text)
    {
        std::string out;
        bool pendingSpace = false;
        for (char c : text)
        {
            if (std::isspace((unsigned char)c))
            {
                pendingSpace = true;
                continue;
            }
            if (pendingSpace && !out.empty())
                out += ' ';
            pendingSpace = false;
            out += c;
        }
        return out;
    }

    bool IsWordAt(const std::string& line, size_t pos, size_t len)
    {
        auto ident = [](char c) { return std::isalnum((unsigned char)c) || c == '_'; };
        bool start = pos == 0 || !ident(line[pos - 1]);
        bool end = pos + len >= line.size() || !ident(line[pos + len]);
        return start && end;
    }

    std::string Trimmed(const std::string& line)
    {
        size_t first = line.find_first_not_of(" \t");
        return first == std::string::npos ? "" : line.substr(first);
    }

    // The 1-based line of a declaration in a header: a function by its signature (spaces collapsed), else by a
    // call-like "Name("; a struct or an enum by its head ("struct Name", not a forward declaration "struct Name;");
    // a member or an attribute by its name, inside its owner. -1 when not found
    int FindCppDeclaration(const std::vector<std::string>& lines, const ApiRef& ref)
    {
        const ApiEntry& e = *ref.entry;
        std::string bare = BareCppName(ref.CppName());
        size_t from = 0;
        if (ref.owner)
        {
            int ownerLine = FindCppDeclaration(lines, ApiRef{ref.module, ref.owner, nullptr});
            if (ownerLine > 0)
                from = (size_t)ownerLine;
        }
        auto isComment = [](const std::string& trimmed) { return trimmed.rfind("//", 0) == 0; };
        if (e.kind == "function" || e.kind == "method")
        {
            std::string signature = NormalizeSpaces(e.cpp.substr(0, e.cpp.find('\n')));
            if (!signature.empty())
                for (size_t i = from; i < lines.size(); ++i)
                    if (NormalizeSpaces(lines[i]).find(signature) != std::string::npos)
                        return (int)i + 1;
            for (size_t i = from; i < lines.size(); ++i)
            {
                const std::string& line = lines[i];
                if (isComment(Trimmed(line)))
                    continue;
                size_t pos = 0;
                while ((pos = line.find(bare, pos)) != std::string::npos)
                {
                    size_t k = pos + bare.size();
                    while (k < line.size() && line[k] == ' ')
                        ++k;
                    if (IsWordAt(line, pos, bare.size()) && k < line.size() && line[k] == '(')
                        return (int)i + 1;
                    pos += bare.size();
                }
            }
        }
        else if (e.kind == "class" || e.kind == "enum")
        {
            for (size_t i = from; i < lines.size(); ++i)
            {
                std::string trimmed = Trimmed(lines[i]);
                for (const char* prefix : {"struct ", "class ", "enum class ", "enum "})
                {
                    std::string head = std::string(prefix) + bare;
                    if (trimmed.rfind(head, 0) != 0 || !IsWordAt(trimmed, strlen(prefix), bare.size()))
                        continue;
                    std::string rest = Trimmed(trimmed.substr(head.size()));
                    if (rest.empty() || rest[0] != ';')  // not a forward declaration
                        return (int)i + 1;
                }
            }
        }
        else
        {
            for (size_t i = from; i < lines.size(); ++i)
            {
                const std::string& line = lines[i];
                if (isComment(Trimmed(line)))
                    continue;
                size_t pos = 0;
                while ((pos = line.find(bare, pos)) != std::string::npos)
                {
                    if (IsWordAt(line, pos, bare.size()))
                        return (int)i + 1;
                    pos += bare.size();
                }
            }
        }
        return -1;
    }

    // The 1-based line of a declaration in a stub: "def name(" or "class Name" at the top level, or inside the owner's
    // class for a method, an attribute ("name:") or a member ("name ="). -1 when not found
    int FindPyDeclaration(const std::vector<std::string>& lines, const ApiRef& ref)
    {
        const ApiEntry& e = *ref.entry;
        bool nested = ref.owner != nullptr;
        size_t from = 0;
        if (nested)
        {
            int ownerLine = FindPyDeclaration(lines, ApiRef{ref.module, ref.owner, nullptr});
            if (ownerLine > 0)
                from = (size_t)ownerLine;
        }
        for (size_t i = from; i < lines.size(); ++i)
        {
            const std::string& line = lines[i];
            size_t indent = line.find_first_not_of(' ');
            if (indent == std::string::npos || line[indent] == '#')
                continue;
            if (nested && indent == 0)
                break;  // the owner's block ended
            if (!nested && indent != 0)
                continue;
            std::string trimmed = line.substr(indent);
            bool found = false;
            if (e.kind == "function" || e.kind == "method")
                found = trimmed.rfind("def " + e.name + "(", 0) == 0;
            else if (e.kind == "class" || e.kind == "enum")
                found = trimmed.rfind("class " + e.name, 0) == 0 && IsWordAt(trimmed, 6, e.name.size());
            else
                found = trimmed.rfind(e.name + ":", 0) == 0 || trimmed.rfind(e.name + " =", 0) == 0
                        || trimmed.rfind(e.name + " :", 0) == 0;
            if (found)
                return (int)i + 1;
        }
        return -1;
    }

    // Shows the declaration of an entry in the header's tab (C++) or the stub's (Python). Returns false when the
    // file is not loaded yet: the request waits (the web loads the files asynchronously)
    bool GoToDeclaration(const ApiRef& ref, bool python)
    {
        const ApiEntry& located = ref.owner ? *ref.owner : *ref.entry;
        auto files = GetCurrentLibraryFiles();
        int index = -1;
        for (size_t i = 0; i < files.size(); ++i)
            if (files[i].isApiReference && files[i].cppDisplayName() == located.header)
                index = (int)i;
        if (index < 0)
            for (size_t i = 0; i < files.size() && index < 0; ++i)
                if (files[i].isApiReference)
                    index = (int)i;
        if (index < 0)
            return true;
        const DemoFileInfo& file = files[index];
        if (python && !file.hasPython)
            python = false;
#ifdef __EMSCRIPTEN__
        RequestFileLoad(file);
#else
        LoadFile(file);
#endif
        CodeFile& cf = g_codeFiles[file.baseName];
        LoadState state = python ? cf.pyState : cf.cppState;
        if (state == LoadState::NotLoaded || state == LoadState::Loading)
            return false;
        const std::string& content = python ? cf.pyContent : cf.cppContent;
        if (content.empty())
            return true;
        auto lines = SplitLines(content);
        int line = python ? FindPyDeclaration(lines, ref) : FindCppDeclaration(lines, ref);
        if (line < 0)
        {
            SearchInApi(python ? ref.entry->name : BareCppName(ref.CppName()));  // the text search, as a fallback
            return true;
        }
        g_pendingScrollFile = file.cppDisplayName();
        g_pendingScrollLine = line;
        g_pendingScrollSection.clear();
        g_pendingScrollPython = python;
        g_currentFileIndex = index;
        return true;
    }

    void RequestGoToDeclaration(const ApiRef& ref, bool python)
    {
        g_pendingDeclRef = GoToDeclaration(ref, python) ? ApiRef() : ref;
        g_pendingDeclPython = python;
    }

    void ResolvePendingDeclaration()
    {
        if (g_pendingDeclRef.entry != nullptr && GoToDeclaration(g_pendingDeclRef, g_pendingDeclPython))
            g_pendingDeclRef = ApiRef();
    }

    // The card of an entry: its names, its signatures in both languages, its doc, its members, the links to its pages
    void ShowApiCard(const ApiRef& ref, bool python)
    {
        const ApiEntry& e = *ref.entry;
        float em = ImGui::GetFontSize();

        // The title: the name in the shown language, the kind; the name in the other language under it
        ImGui::PushFont(nullptr, em * 1.35f);
        ImGui::TextUnformatted(python ? ref.PyName().c_str() : ref.CppName().c_str());
        ImGui::PopFont();
        ImGui::SameLine();
        ImGui::TextDisabled("%s", e.kind.c_str());
        ImGui::TextDisabled("%s: %s", python ? "C++" : "Python", python ? ref.CppName().c_str() : ref.PyName().c_str());

        // Where it is declared: the owner, the header, the section
        const ApiEntry& located = ref.owner ? *ref.owner : e;
        if (ref.owner)
        {
            ImGui::TextDisabled("Member of");
            ImGui::SameLine();
            if (ImGui::SmallButton(ListLabel(ApiRef{ref.module, ref.owner, nullptr}, python).c_str()))
            {
                g_apiCurrent = ApiRef{ref.module, ref.owner, nullptr};
                return;
            }
        }
        std::string where = located.header;
        const std::string& place = located.section.empty() ? located.part : located.section;
        if (!place.empty())
            where += (where.empty() ? "" : ", ") + place;
        if (!where.empty())
            ImGui::TextDisabled("%s", where.c_str());

        // Online doc (the module's page, its C++ view), find in the header or the stub (the text search), copy
        ImGui::AlignTextToFramePadding();
        ImGui::TextDisabled("Online doc:");
        ImGui::SameLine();
        if (ImGui::Button(ICON_FA_EXTERNAL_LINK_ALT " Python"))
            ImmApp::BrowseToUrl(ref.Url().c_str());
        ImGui::SetItemTooltip("%s", ref.Url().c_str());
        std::string cppUrl = ref.CppUrl();
        if (!cppUrl.empty())
        {
            ImGui::SameLine();
            if (ImGui::Button(ICON_FA_EXTERNAL_LINK_ALT " C++"))
                ImmApp::BrowseToUrl(cppUrl.c_str());
            ImGui::SetItemTooltip("%s", cppUrl.c_str());
        }
        ImGui::SameLine(0.f, em * 1.5f);
        std::string apiFile = located.header;  // the header, or its stub ("imgui.h" -> "imgui.pyi")
        if (python && apiFile.size() > 2 && apiFile.compare(apiFile.size() - 2, 2, ".h") == 0)
            apiFile = apiFile.substr(0, apiFile.size() - 2) + ".pyi";
        if (ImGui::Button("Go to declaration"))
            RequestGoToDeclaration(ref, python);
        ImGui::SetItemTooltip("The line that declares it, in %s", (apiFile.empty() ? FirstApiFileName(python) : apiFile).c_str());
        ImGui::SameLine();
        if (ImGui::Button(("Find in " + (apiFile.empty() ? FirstApiFileName(python) : apiFile)).c_str()))
            SearchInApi(python ? e.name : BareCppName(ref.CppName()));
        ImGui::SetItemTooltip("The text search in the declarations");
        const std::string& signature = python ? e.py : e.cpp;
        if (!signature.empty())
        {
            ImGui::SameLine();
            if (ImGui::Button(ICON_FA_COPY " Copy signature"))
                ImGui::SetClipboardText(signature.c_str());
        }

        // The signatures: the shown language first, the other muted
        ImGui::Separator();
        const std::string& other = python ? e.cpp : e.py;
        if (!signature.empty())
            ShowCode(signature, false);
        if (!other.empty())
            ShowCode(other, true);
        if (!e.value.empty())
            ImGui::Text("= %s", e.value.c_str());

        // The doc: the header's lines, as they are
        if (!e.doc.empty() || !e.note.empty())
        {
            ImGui::Spacing();
            ImGui::PushTextWrapPos(0.f);
            if (!e.doc.empty())
                ImGui::TextUnformatted(e.doc.c_str());
            if (!e.note.empty())
                ImGui::TextUnformatted(e.note.c_str());
            ImGui::PopTextWrapPos();
        }
        if (python && !e.bindingsNote.empty())
        {
            ImGui::Spacing();
            ImGui::PushTextWrapPos(0.f);
            ImGui::TextDisabled("%s", e.bindingsNote.c_str());
            ImGui::PopTextWrapPos();
        }

        // The members of a class or an enum
        if (!e.children.empty())
        {
            ImGui::SeparatorText(e.kind == "enum" ? "Values" : "Members");
            auto codeFont = RichMd::GetCodeFont();
            for (size_t i = 0; i < e.children.size(); ++i)
            {
                const ApiEntry& c = e.children[i];
                ApiRef childRef{ref.module, &c, &e};
                std::string label = python ? c.name : (c.cppName.empty() ? c.name : BareCppName(c.cppName));
                if (c.kind == "member" && !c.value.empty())
                    label += " = " + c.value;
                else if (c.kind == "attribute")
                    label = python ? c.py : c.cpp;
                if (codeFont.font)
                    ImGui::PushFont(codeFont.font, codeFont.size);
                bool clicked = ImGui::Selectable((label + "##child" + std::to_string(i)).c_str());
                if (codeFont.font)
                    ImGui::PopFont();
                if (clicked)
                {
                    g_apiCurrent = childRef;
                    return;
                }
                std::string hint = ApiIndex_FirstSentence(c.doc.empty() ? c.note : c.doc);
                if (!hint.empty())
                {
                    ImGui::SameLine();
                    ImGui::TextDisabled("%s", hint.c_str());
                }
            }
        }

        ShowDemoUses(ref, python);
    }

    // The entries matching the filter, in both languages (a substring, case insensitive)
    void ShowApiFilterResults(const std::vector<const ApiModule*>& modules, bool python)
    {
        std::string needle = g_apiFilter;
        std::transform(needle.begin(), needle.end(), needle.begin(), [](unsigned char c) { return std::tolower(c); });
        auto matches = [&](const std::string& text)
        {
            std::string lower = text;
            std::transform(lower.begin(), lower.end(), lower.begin(), [](unsigned char c) { return std::tolower(c); });
            return lower.find(needle) != std::string::npos;
        };
        // The entries whose name is the filter first, then the others that contain it
        std::vector<ApiRef> exact, partial;
        auto collect = [&](const ApiRef& ref)
        {
            if (partial.size() >= 200)
                return;
            std::string py = ref.PyName(), cpp = ref.CppName();
            if (!matches(py) && !matches(cpp))
                return;
            std::string name = ref.entry->name, bare = BareCppName(cpp);
            std::transform(name.begin(), name.end(), name.begin(), [](unsigned char c) { return std::tolower(c); });
            std::transform(bare.begin(), bare.end(), bare.begin(), [](unsigned char c) { return std::tolower(c); });
            (name == needle || bare == needle ? exact : partial).push_back(ref);
        };
        for (const ApiModule* m : modules)
            for (const auto& entry : m->entries)
            {
                collect(ApiRef{m, &entry, nullptr});
                for (const auto& child : entry.children)
                    collect(ApiRef{m, &child, &entry});
            }
        int shown = 0;
        for (const auto* hits : {&exact, &partial})
            for (const ApiRef& ref : *hits)
            {
                std::string label = ListLabel(ref, python) + "##hit" + std::to_string(shown++);
                if (ImGui::Selectable(label.c_str()))
                {
                    g_apiCurrent = ref;
                    g_apiCandidates.clear();
                    g_apiFilter[0] = '\0';
                }
                ImGui::SameLine();
                ImGui::TextDisabled("%s", python ? ref.CppName().c_str() : ListLabel(ref, true).c_str());
            }
        if (shown == 0)
            ImGui::TextDisabled("No entry matches");
        else if (partial.size() >= 200)
            ImGui::TextDisabled("(the first 200)");
    }

    // All the entries, under their parts and sections (the headers' own)
    void ShowApiBrowser(const std::vector<const ApiModule*>& modules, bool python)
    {
        for (const ApiModule* m : modules)
        {
            ImGui::PushID(m->module.c_str());  // two modules may share a part's name (implot and implot.internal)
            // The module's title: its name in Python, its first header in C++
            std::string title = m->module;
            if (!python)
                for (const auto& e : m->entries)
                    if (!e.header.empty())
                    {
                        title = e.header;
                        break;
                    }
            ImGui::SeparatorText(title.c_str());
            std::string part, section;
            bool partOpen = true, sectionOpen = true;
            for (size_t i = 0; i < m->entries.size(); ++i)
            {
                const ApiEntry& e = m->entries[i];
                if (e.part != part)
                {
                    if (sectionOpen && !section.empty())
                        ImGui::TreePop();
                    if (partOpen && !part.empty())
                        ImGui::TreePop();
                    part = e.part;
                    section.clear();
                    sectionOpen = true;
                    partOpen = part.empty() || ImGui::TreeNodeEx(part.c_str(), ImGuiTreeNodeFlags_SpanAvailWidth);
                }
                if (!partOpen)
                    continue;
                if (e.section != section)
                {
                    if (sectionOpen && !section.empty())
                        ImGui::TreePop();
                    section = e.section;
                    sectionOpen = section.empty() || ImGui::TreeNodeEx(section.c_str(), ImGuiTreeNodeFlags_SpanAvailWidth);
                }
                if (!sectionOpen)
                    continue;
                ApiRef ref{m, &e, nullptr};
                std::string label = ListLabel(ref, python) + "##entry" + std::to_string(i);
                if (ImGui::Selectable(label.c_str()))
                {
                    g_apiCurrent = ref;
                    g_apiCandidates.clear();
                }
                std::string hint = ApiIndex_FirstSentence(e.doc);
                if (!hint.empty())
                {
                    ImGui::SameLine();
                    ImGui::TextDisabled("%s", hint.c_str());
                }
            }
            if (sectionOpen && !section.empty())
                ImGui::TreePop();
            if (partOpen && !part.empty())
                ImGui::TreePop();
            ImGui::PopID();
        }
    }

    void ShowApiTab()
    {
        // The entry, the candidates and the filter belong to a library: a switch starts from the list
        static int lastLibrary = -1;
        if (GetCurrentLibraryIndex() != lastLibrary)
        {
            lastLibrary = GetCurrentLibraryIndex();
            g_apiCurrent = ApiRef();
            g_apiCandidates.clear();
            g_apiFilter[0] = '\0';
        }
        const std::vector<std::string>& moduleNames = GetCurrentLibrary().apiModules;
        ApiIndexState state = ApiIndex_Load(GetDemoCodeDir(), moduleNames);
        auto modules = ApiIndex_Modules(moduleNames);
        if (modules.empty())
        {
            if (state == ApiIndexState::Loading)
                ImGui::Text(ICON_FA_SPINNER " Loading the API index ...");
            else
            {
                ImGui::TextWrapped("The API index is not available here. The API pages are online:");
                RichMd::RenderTextAsLink("imgui-bundle.pages.dev/doc/api", "https://imgui-bundle.pages.dev/doc/api/");
            }
            return;
        }
        bool python = g_showPython;

        // The toolbar: the filter, back to the list, the pages
        float em = ImGui::GetFontSize();
        ImGui::SetNextItemWidth(18.f * em);
        ImGui::InputTextWithHint("##apifilter", ICON_FA_SEARCH " a name, Python or C++", g_apiFilter, sizeof(g_apiFilter));
        ImGui::SameLine();
        bool listing = g_apiFilter[0] == '\0' && g_apiCurrent.entry == nullptr && g_apiCandidates.empty();
        ImGui::BeginDisabled(listing);
        if (ImGui::SmallButton(ICON_FA_LIST " All"))
        {
            g_apiCurrent = ApiRef();
            g_apiCandidates.clear();
            g_apiFilter[0] = '\0';
        }
        ImGui::EndDisabled();
        ImGui::SameLine();
        ImGui::TextDisabled("|");
        ImGui::SameLine();
        RichMd::RenderTextAsLink("API pages", modules[0]->url.c_str());
        ImGui::SetItemTooltip("The reference of the module, on the web (every entry, searchable)");

        ImGui::BeginChild("api_body", ImVec2(0, 0), ImGuiChildFlags_None, ImGuiWindowFlags_None);
        if (g_apiFilter[0] != '\0')
            ShowApiFilterResults(modules, python);
        else if (!g_apiCandidates.empty())
        {
            ImGui::TextWrapped("Several entries have this name:");
            for (size_t i = 0; i < g_apiCandidates.size(); ++i)
            {
                const ApiRef& ref = g_apiCandidates[i];
                if (ImGui::Selectable((ListLabel(ref, python) + "##cand" + std::to_string(i)).c_str()))
                {
                    g_apiCurrent = ref;
                    g_apiCandidates.clear();
                    break;
                }
                ImGui::SameLine();
                ImGui::TextDisabled("%s", python ? ref.CppName().c_str() : ListLabel(ref, true).c_str());
            }
        }
        else if (g_apiCurrent.entry != nullptr)
            ShowApiCard(g_apiCurrent, python);
        else
            ShowApiBrowser(modules, python);
        ImGui::EndChild();
    }
}

int DemoCodeViewer_GetCurrentFileIndex() { return g_currentFileIndex; }
bool DemoCodeViewer_GetShowPython() { return g_userPrefPython; }
void DemoCodeViewer_SetShowPython(bool show) { g_showPython = show; g_userPrefPython = show; }

void DemoCodeViewer_Show()
{
    bool pythonOnly = DemoCodeViewer_IsPythonOnlyMode();

    // In Python-only mode, force Python display
    if (pythonOnly)
    {
        g_showPython = true;
        g_userPrefPython = true;
    }

    // Get files for current library
    auto files = GetCurrentLibraryFiles();

    // Tabs for file selection
    std::string tabBarId = "CodeViewerTabs_" + GetCurrentLibrary().name;
    if (ImGui::BeginTabBar(tabBarId.c_str()))
    {
        for (size_t i = 0; i < files.size(); ++i)
        {
            const auto& file = files[i];

            // In Python-only mode, skip files that have no Python equivalent
            if (pythonOnly && !file.hasPython)
                continue;

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

        // The API tab: the index of the library's modules (the card of an entry, the list of all)
        {
            ImGuiTabItemFlags flags = g_pendingApiTabSelect ? ImGuiTabItemFlags_SetSelected : 0;
            ImGui::PushStyleColor(ImGuiCol_Tab, ImVec4(0.15f, 0.35f, 0.25f, 1.0f));
            ImGui::PushStyleColor(ImGuiCol_TabHovered, ImVec4(0.25f, 0.50f, 0.38f, 1.0f));
            ImGui::PushStyleColor(ImGuiCol_TabSelected, ImVec4(0.20f, 0.45f, 0.32f, 1.0f));
            if (ImGui::BeginTabItem(ICON_FA_BOOK " API", nullptr, flags))
            {
                g_currentFileIndex = (int)files.size();
                ImGui::EndTabItem();
            }
            ImGui::PopStyleColor(3);
            g_pendingApiTabSelect = false;
        }
        ImGui::EndTabBar();
    }

    if (files.empty())
    {
        ImGui::TextWrapped("No demo files configured");
        return;
    }

    // Clamp file index to valid range (may change when switching libraries); the API tab is files.size()
    if (g_currentFileIndex > (int)files.size())
        g_currentFileIndex = 0;

    // The index loads once per library (asynchronously on the web); the lookups below need it
    const std::vector<std::string>& apiModules = GetCurrentLibrary().apiModules;
    ApiIndex_Load(GetDemoCodeDir(), apiModules);
    ResolvePendingDeclaration();

    if (g_currentFileIndex == (int)files.size())
    {
        ShowApiTab();
        return;
    }

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
        if (g_pendingScrollPython && cf.pyState == LoadState::Loaded)
        {
            ShowLine(cf, true, g_pendingScrollLine - 1);
            scrolledPython = true;
        }
        else if (g_userPrefPython && cf.pyState == LoadState::Loaded && !g_pendingScrollSection.empty())
        {
            auto it2 = cf.pyMarkers.find(g_pendingScrollSection);
            if (it2 != cf.pyMarkers.end())
            {
                ShowLine(cf, true, it2->second - 1);
                scrolledPython = true;
            }
        }
        if (!scrolledPython)
        {
            ShowLine(cf, false, g_pendingScrollLine - 1);
        }
        // Auto-switch displayed language to match what we scrolled
        if (g_userPrefPython || g_pendingScrollPython)
            g_showPython = scrolledPython;
        g_pendingScrollLine = -1;
        g_pendingScrollFile.clear();
        g_pendingScrollSection.clear();
        g_pendingScrollPython = false;
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
        const std::string& githubUrl = showingPython ? currentFile.pyGithubUrl : currentFile.cppGithubUrl;
        if (!githubUrl.empty())
        {
            ImGui::TextColored(ImVec4(1.f, 1.f, 0.5f, 1.f), "%s is not available locally.", displayName.c_str());
            if (ImGui::SmallButton(("View " + displayName + " on GitHub").c_str()))
                ImmApp::BrowseToUrl(githubUrl.c_str());
        }
        else
        {
            ImGui::TextColored(ImVec4(1.f, 0.4f, 0.4f, 1.f), "Failed to load %s", displayName.c_str());
        }
        return;
    }

    TextEditor& editor = showingPython ? cf.pyEditor : cf.cppEditor;

    if (g_showPython && !currentFile.hasPython)
        ImGui::TextColored(ImVec4(1.f, 1.f, 0.5f, 1.f), "No Python code available for this demo");

    // Apply deferred match selection (frame 2 of GoToMatch: scroll left happened last frame)
    if (g_pendingMatch.has_value())
    {
        auto& m = g_pendingMatch.value();
        editor.SelectRegion(TextEditor::DocPos(m.startLine, m.startCol), TextEditor::DocPos(m.endLine, m.endCol));
        g_pendingMatch.reset();
    }

    // The identifier at the text cursor and its entries, for the API button and Ctrl+Shift+F. Never the selection:
    // the explorer selects the demo's marker line when the demo is hovered
    std::string apiWord = IdentifierAtCursor(editor);
    std::vector<ApiRef> apiHits = apiWord.empty() ? std::vector<ApiRef>{} : ApiIndex_Lookup(apiModules, apiWord);

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
            auto pos = editor.GetMainCursorPosition();
            const std::string& githubUrl = showingPython ? currentFile.pyGithubUrl : currentFile.cppGithubUrl;
            if (!githubUrl.empty())
                ImmApp::BrowseToUrl((githubUrl + "#L" + std::to_string(pos.line + 1)).c_str());
        }

        ImGui::SameLine();

        // Search button
        if (ImGui::SmallButton(ICON_FA_SEARCH))
        {
            if (editor.AnyCursorHasSelection())
            {
                std::string sel = editor.GetCursorText(0);
                if (!sel.empty())
                    snprintf(g_searchBuffer, sizeof(g_searchBuffer), "%s", sel.c_str());
            }
            g_searchBarOpen = true;
            g_searchBarJustOpened = true;
        }
        ImGui::SetItemTooltip("Search (Ctrl+F).\n You may also right click in the editor below.");

        ImGui::SameLine();

        // The API button: the entry of the identifier at the cursor, in the API tab; its label names the entry, so
        // that the user knows what a click will open
        std::string apiLabel = ICON_FA_BOOK;
        if (!apiHits.empty())
            apiLabel += " " + (showingPython ? apiHits[0].PyName() : apiHits[0].CppName()) + (apiHits.size() > 1 ? " ..." : "");
        ImGui::BeginDisabled(apiHits.empty());
        if (ImGui::SmallButton((apiLabel + "###searchapi").c_str()))
            OpenApi(apiHits);
        if (ImGui::IsItemHovered(ImGuiHoveredFlags_AllowWhenDisabled))
            ImGui::SetTooltip("The API of the identifier at the cursor (Ctrl+Shift+F): click a name in the code, "
                              "then here.\nIts signatures in Python and C++, its doc, where the demo uses it.");
        ImGui::EndDisabled();

        ImGui::SameLine();

        auto pos = editor.GetMainCursorPosition();
        ImGui::Text("%6zu / %6zu  | %s", pos.line + 1, editor.GetLineCount(), displayName.c_str());

        ImGui::SameLine();
        ImGui::Checkbox("Wrap", &g_wordWrap);
        ImGui::SetItemTooltip("Wrap long lines to the editor width");
        ImGui::SameLine();
        ImGui::Checkbox("Minimap", &g_showMinimap);
        ImGui::SetItemTooltip("Show minimap on the right side of the editor");
        ImGui::SameLine();
        ImGui::Checkbox("API tooltips", &g_apiTooltips);
        ImGui::SetItemTooltip("A tooltip with the API of the identifier under the mouse");
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
        std::string sel = editor.GetCursorText(0);
        if (!sel.empty())
            snprintf(g_searchBuffer, sizeof(g_searchBuffer), "%s", sel.c_str());
    }

    // Ctrl+Shift+F shortcut: the API of the identifier at the cursor (as the book button)
    if (ImGui::IsKeyChordPressed(ImGuiMod_Ctrl | ImGuiMod_Shift | ImGuiKey_F) && !apiHits.empty())
        OpenApi(apiHits);

    // Use code font if available
    auto codeFont = RichMd::GetCodeFont();
    if (codeFont.font)
        ImGui::PushFont(codeFont.font, codeFont.size);

    // Apply user display preferences to the active editor
    editor.SetWordWrapEnabled(g_wordWrap);
    editor.SetShowMiniMapEnabled(g_showMinimap);

    // Use unique ID per file and language to keep cursor/scroll state independent
    std::string editorId = std::string("##code_") + displayName;
    ImVec2 editorSize = ImGui::GetContentRegionAvail();
    editor.Render(editorId.c_str(), editorSize, false);

    // Hover: a tooltip with the API of the identifier under the mouse (the desktop's complement of the API button)
    if (g_apiTooltips && ImGui::IsItemHovered(ImGuiHoveredFlags_DelayNormal | ImGuiHoveredFlags_Stationary)
        && !ImGui::IsPopupOpen("CodeEditorContext") && editor.IsMousePosOverGlyph(ImGui::GetMousePos()))
    {
        auto pos = editor.GetDocPosAtMousePos(ImGui::GetMousePos());
        std::string identifier = ApiIndex_IdentifierAt(editor.GetLineText(pos.line), pos.index);
        std::vector<ApiRef> hits = identifier.empty() ? std::vector<ApiRef>{} : ApiIndex_Lookup(apiModules, identifier);
        // A bare name is not an attribute: "size", "flags" or "min_x" in the code name a variable, not a struct's field
        bool qualified = identifier.find('.') != std::string::npos || identifier.find("::") != std::string::npos;
        if (!qualified)
            hits.erase(std::remove_if(hits.begin(), hits.end(),
                                      [](const ApiRef& r) { return r.entry->kind == "attribute"; }), hits.end());
        if (!hits.empty())
        {
            if (codeFont.font)
                ImGui::PopFont();
            ImGui::BeginTooltip();
            ShowApiTooltip(hits[0], showingPython, hits.size());
            ImGui::EndTooltip();
            if (codeFont.font)
                ImGui::PushFont(codeFont.font, codeFont.size);
        }
    }

    // Right-click context menu on the editor
    static std::string rightClickWord;
    static std::vector<ApiRef> rightClickHits;
    if (ImGui::IsItemClicked(ImGuiMouseButton_Right))
    {
        // The API item: the identifier under the mouse (never the selection). The find items: the selection, else the word
        std::string sel = editor.GetCursorText(0);
        rightClickWord = !sel.empty() ? sel : editor.GetWordAtMousePos(ImGui::GetMousePos());
        auto pos = editor.GetDocPosAtMousePos(ImGui::GetMousePos());
        std::string identifier = ApiIndex_IdentifierAt(editor.GetLineText(pos.line), pos.index);
        rightClickHits = identifier.empty() ? std::vector<ApiRef>{} : ApiIndex_Lookup(apiModules, identifier);
        if (!rightClickWord.empty() || !rightClickHits.empty())
            ImGui::OpenPopup("CodeEditorContext");
    }
    if (ImGui::BeginPopup("CodeEditorContext"))
    {
        if (codeFont.font)
            ImGui::PopFont(); // restore font for menu

        std::string truncSel = rightClickWord.substr(0, 30) + (rightClickWord.size() > 30 ? "..." : "");

        if (!rightClickHits.empty())
        {
            std::string name = showingPython ? rightClickHits[0].PyName() : rightClickHits[0].CppName();
            std::string label = std::string(ICON_FA_BOOK " API: ") + name + (rightClickHits.size() > 1 ? " ..." : "");
            if (ImGui::MenuItem(label.c_str()))
                OpenApi(rightClickHits);
            ImGui::Separator();
        }

        if (!rightClickWord.empty())
        {
            std::string menuLabel = "Find \"" + truncSel + "\" in this file";
            if (ImGui::MenuItem(menuLabel.c_str()))
            {
                snprintf(g_searchBuffer, sizeof(g_searchBuffer), "%s", rightClickWord.c_str());
                g_searchBarOpen = true;
                g_lastMatchOffset = CursorToOffset(editor, content);  // Next/Prev start from here
            }

            std::string findLabel = "Find \"" + truncSel + "\" in " + FirstApiFileName(showingPython);
            if (ImGui::MenuItem(findLabel.c_str()))
                SearchInApi(rightClickWord);
        }

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

bool DemoCodeViewer_IsPythonOnlyMode()
{
    return g_pythonOnlyMode;
}

void DemoCodeViewer_SetupPythonMode(const std::string& pythonPackagePath)
{
    if (pythonPackagePath.empty() || g_pythonOnlyMode) return;
    g_pythonOnlyMode = true;
    g_pythonPackageRoot = pythonPackagePath;
    g_pyDemoCodeDir = pythonPackagePath + "/demos_python/demos_imgui_explorer";
}
