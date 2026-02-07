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
    };

    std::map<std::string, CodeFile> g_codeFiles;  // Keyed by baseName (all files loaded)
    int g_currentFileIndex = 0;
    int g_pendingScrollLine = -1;
    std::string g_pendingScrollFile;
    bool g_showPython = false;  // Global toggle for C++/Python view

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

    // Language toggle (only show if any file has Python)
    bool anyHasPython = false;
    for (const auto& f : files)
        if (f.hasPython) { anyHasPython = true; break; }

    if (anyHasPython)
    {
        if (ImGui::RadioButton("C++", !g_showPython))
            g_showPython = false;
        ImGui::SameLine();
        if (ImGui::RadioButton("Python", g_showPython))
            g_showPython = true;
        ImGui::SameLine();
        ImGui::Spacing();
        ImGui::SameLine();
    }

    // Tabs for file selection
    if (ImGui::BeginTabBar("CodeViewerTabs"))
    {
        for (size_t i = 0; i < files.size(); ++i)
        {
            const auto& file = files[i];
            std::string displayName = g_showPython ? file.pyDisplayName() : file.cppDisplayName();

            // Skip if showing Python but file doesn't have Python
            if (g_showPython && !file.hasPython)
                continue;

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

    // Handle pending scroll (only for C++ since markers come from C++)
    if (!g_pendingScrollFile.empty() && g_pendingScrollFile == currentFile.cppDisplayName() && g_pendingScrollLine > 0)
    {
        // If showing Python, switch to C++ to show the marker location
        if (g_showPython)
        {
            g_showPython = false;
        }
        cf.cppEditor.SetViewAtLine(g_pendingScrollLine - 3, TextEditor::SetViewAtLineMode::FirstVisibleLine);
        cf.cppEditor.SetCursorPosition(g_pendingScrollLine - 1, 0);
        cf.cppEditor.SelectLine(g_pendingScrollLine - 1);
        g_pendingScrollLine = -1;
        g_pendingScrollFile.clear();
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
            printf("To be implemented: open github link for %s at line %d\n", displayName.c_str(), line + 1);
            //use OpenUrl
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

void DemoCodeViewer_ShowCodeAt(const char* filename, int line)
{
    // Store the request - will be processed on next render
    g_pendingScrollFile = filename;
    g_pendingScrollLine = line;

    // Switch to the correct tab (within current library)
    int idx = FindFileIndexInCurrentLibrary(filename);
    if (idx >= 0)
    {
        g_currentFileIndex = idx;
    }
}
