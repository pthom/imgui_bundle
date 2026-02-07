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
        std::string content;
        TextEditor editor;
        bool loaded = false;
    };

    // Cached file list from config
    std::vector<DemoFileInfo> g_files;

    std::map<std::string, CodeFile> g_codeFiles;  // Keyed by displayName (e.g., "im_anim_demo.cpp")
    int g_currentFileIndex = 0;
    int g_pendingScrollLine = -1;
    std::string g_pendingScrollFile;

    void LoadFile(const std::string& displayName, const std::string& assetName, TextEditor::LanguageDefinitionId lang)
    {
        std::string assetPath = std::string("demo_code/") + assetName;
        auto assetData = HelloImGui::LoadAssetFileData(assetPath.c_str());

        if (assetData.data != nullptr && assetData.dataSize > 0)
        {
            CodeFile& cf = g_codeFiles[displayName];
            cf.content = std::string((const char*)assetData.data, assetData.dataSize);
            cf.editor.SetText(cf.content);
            cf.editor.SetLanguageDefinition(lang);
            cf.editor.SetPalette(TextEditor::PaletteId::Dark);
            cf.editor.SetReadOnlyEnabled(true);
            cf.editor.SetShowLineNumbersEnabled(true);
            cf.editor.SetShowWhitespacesEnabled(false);
            cf.loaded = true;
            HelloImGui::FreeAssetFileData(&assetData);
        }
    }

    int FindFileIndex(const char* displayName)
    {
        for (size_t i = 0; i < g_files.size(); ++i)
        {
            if (g_files[i].cppDisplayName() == displayName)
                return (int)i;
        }
        return -1;
    }
}

void DemoCodeViewer_Init()
{
    // Get file list from config
    g_files = GetAllDemoFiles();

    // Load all C++ files
    for (const auto& file : g_files)
    {
        LoadFile(file.cppDisplayName(), file.cppAssetName(), TextEditor::LanguageDefinitionId::Cpp);
    }
}

void DemoCodeViewer_Show()
{
    // Tabs for file selection
    if (ImGui::BeginTabBar("CodeViewerTabs"))
    {
        for (size_t i = 0; i < g_files.size(); ++i)
        {
            const auto& file = g_files[i];
            std::string displayName = file.cppDisplayName();

            ImGuiTabItemFlags flags = 0;
            // If we have a pending scroll for this file, select its tab
            if (!g_pendingScrollFile.empty() && g_pendingScrollFile == displayName)
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

    if (g_files.empty())
    {
        ImGui::TextWrapped("No demo files configured");
        return;
    }

    // Display the current file's editor
    std::string currentDisplayName = g_files[g_currentFileIndex].cppDisplayName();
    auto it = g_codeFiles.find(currentDisplayName);
    if (it != g_codeFiles.end() && it->second.loaded)
    {
        CodeFile& cf = it->second;

        // Handle pending scroll
        if (!g_pendingScrollFile.empty() && g_pendingScrollFile == currentDisplayName && g_pendingScrollLine > 0)
        {
            cf.editor.SetViewAtLine(g_pendingScrollLine - 3, TextEditor::SetViewAtLineMode::FirstVisibleLine);
            cf.editor.SetCursorPosition(g_pendingScrollLine - 1, 0);
            cf.editor.SelectLine(g_pendingScrollLine - 1);
            g_pendingScrollLine = -1;
            g_pendingScrollFile.clear();
        }

        // Top bar with line info and copy button
        {
            // Copy button
            ImGui::BeginDisabled(!cf.editor.AnyCursorHasSelection());
            if (ImGui::Button(ICON_FA_COPY))
                cf.editor.Copy();
            ImGui::EndDisabled();

            ImGui::SameLine();

            if (ImGui::SmallButton("View on github at this line"))
            {
                int line, column; cf.editor.GetCursorPosition(line, column);
                printf("To be implemented: open github link for %s at line %d\n", currentDisplayName.c_str(), line + 1);
                //use OpenUrl
            }

            ImGui::SameLine();

            int line, column; cf.editor.GetCursorPosition(line, column);
            ImGui::Text("%6d / %6d  | %s", line + 1, cf.editor.GetLineCount(), currentDisplayName.c_str());

        }

        // Use code font if available
        auto codeFont = ImGuiMd::GetCodeFont();
        if (codeFont.font)
            ImGui::PushFont(codeFont.font, codeFont.size);

        // Use unique ID per file to keep cursor/scroll state independent
        std::string editorId = std::string("##code_") + currentDisplayName;
        cf.editor.Render(editorId.c_str(), false, ImGui::GetContentRegionAvail());

        if (codeFont.font)
            ImGui::PopFont();
    }
    else
    {
        ImGui::TextWrapped("Failed to load %s", currentDisplayName.c_str());
    }
}

void DemoCodeViewer_ShowCodeAt(const char* filename, int line)
{
    // Store the request - will be processed on next render
    g_pendingScrollFile = filename;
    g_pendingScrollLine = line;

    // Switch to the correct tab
    int idx = FindFileIndex(filename);
    if (idx >= 0)
    {
        g_currentFileIndex = idx;
    }
}
