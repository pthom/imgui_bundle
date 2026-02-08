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

    // Parse IMGUI_DEMO_MARKER("section") calls from source text, return section → 1-based line map
    std::map<std::string, int> ParseMarkers(const std::string& source)
    {
        std::map<std::string, int> markers;
        const std::string pattern = "IMGUI_DEMO_MARKER(\"";
        int lineNum = 1;
        size_t pos = 0;
        while (pos < source.size())
        {
            size_t eol = source.find('\n', pos);
            if (eol == std::string::npos) eol = source.size();
            // Search for pattern in this line
            size_t found = source.find(pattern, pos);
            if (found != std::string::npos && found < eol)
            {
                size_t start = found + pattern.size();
                size_t end = source.find('"', start);
                if (end != std::string::npos && end < eol)
                {
                    std::string section = source.substr(start, end - start);
                    markers[section] = lineNum;
                }
            }
            lineNum++;
            pos = eol + 1;
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
}

bool DemoCodeViewer_GetShowPython() { return g_showPython; }
void DemoCodeViewer_SetShowPython(bool show) { g_showPython = show; }

void DemoCodeViewer_Init()
{
    // Load all files from all libraries (for fast switching between libraries)
    auto allFiles = GetAllDemoFiles();
    for (const auto& file : allFiles)
    {
        LoadFile(file);
    }
}

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
            {
                flags |= ImGuiTabItemFlags_SetSelected;
            }

            if (ImGui::BeginTabItem(displayName.c_str(), nullptr, flags))
            {
                g_currentFileIndex = (int)i;
                ImGui::EndTabItem();
            }
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

    // Display the current file's editor
    const auto& currentFile = files[g_currentFileIndex];
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

        int line, column; editor.GetCursorPosition(line, column);
        ImGui::Text("%6d / %6d  | %s", line + 1, editor.GetLineCount(), displayName.c_str());
    }

    // Use code font if available
    auto codeFont = ImGuiMd::GetCodeFont();
    if (codeFont.font)
        ImGui::PushFont(codeFont.font, codeFont.size);

    // Use unique ID per file and language to keep cursor/scroll state independent
    std::string editorId = std::string("##code_") + displayName;
    editor.Render(editorId.c_str(), false, ImGui::GetContentRegionAvail());

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
