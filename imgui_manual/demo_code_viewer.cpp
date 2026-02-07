#include "demo_code_viewer.h"
#include "imgui.h"
#include "hello_imgui/hello_imgui.h"
#include "hello_imgui/icons_font_awesome_4.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include <string>
#include <map>
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
#elif defined(TARGET_OS_MAC)
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

    // Files we want to display (display name -> asset filename)
    struct FileInfo {
        const char* displayName;  // Shown in tabs and used for marker matching
        const char* assetName;    // Actual filename in assets (with .txt extension for macOS bundling)
    };
    const FileInfo g_files[] = {
        {"im_anim_demo_basics.cpp", "im_anim_demo_basics.cpp.txt"},
        {"im_anim_demo.cpp", "im_anim_demo.cpp.txt"},
        {"im_anim_doc.cpp", "im_anim_doc.cpp.txt"},
        {"im_anim_usecase.cpp", "im_anim_usecase.cpp.txt"},
    };
    constexpr int g_fileCount = sizeof(g_files) / sizeof(g_files[0]);

    std::map<std::string, CodeFile> g_codeFiles;  // Keyed by displayName
    int g_currentFileIndex = 0;
    int g_pendingScrollLine = -1;
    std::string g_pendingScrollFile;

    void LoadFile(const FileInfo& fileInfo)
    {
        std::string assetPath = std::string("demo_code/") + fileInfo.assetName;
        auto assetData = HelloImGui::LoadAssetFileData(assetPath.c_str());

        if (assetData.data != nullptr && assetData.dataSize > 0)
        {
            CodeFile& cf = g_codeFiles[fileInfo.displayName];
            cf.content = std::string((const char*)assetData.data, assetData.dataSize);
            cf.editor.SetText(cf.content);
            cf.editor.SetLanguageDefinition(TextEditor::LanguageDefinitionId::Cpp);
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
        for (int i = 0; i < g_fileCount; ++i)
        {
            if (strcmp(g_files[i].displayName, displayName) == 0)
                return i;
        }
        return -1;
    }
}

void DemoCodeViewer_Init()
{
    for (int i = 0; i < g_fileCount; ++i)
    {
        LoadFile(g_files[i]);
    }
}

void DemoCodeViewer_Show()
{
    // Tabs for file selection
    if (ImGui::BeginTabBar("CodeViewerTabs"))
    {
        for (int i = 0; i < g_fileCount; ++i)
        {
            ImGuiTabItemFlags flags = 0;
            // If we have a pending scroll for this file, select its tab
            if (!g_pendingScrollFile.empty() && g_pendingScrollFile == g_files[i].displayName)
            {
                flags |= ImGuiTabItemFlags_SetSelected;
            }

            if (ImGui::BeginTabItem(g_files[i].displayName, nullptr, flags))
            {
                g_currentFileIndex = i;
                ImGui::EndTabItem();
            }
        }
        ImGui::EndTabBar();
    }

    // Display the current file's editor
    const char* currentDisplayName = g_files[g_currentFileIndex].displayName;
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
                printf("To be implemented: open github link for %s at line %d\n", currentDisplayName, line + 1);
                //use OpenUrl
            }

            ImGui::SameLine();

            int line, column; cf.editor.GetCursorPosition(line, column);
            ImGui::Text("%6d / %6d  | %s", line + 1, cf.editor.GetLineCount(), currentDisplayName);

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
        ImGui::TextWrapped("Failed to load %s", currentDisplayName);
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
