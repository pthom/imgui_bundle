// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui.h"
#include "immapp/immapp.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#include "ImGuiColorTextEdit/TextDiff.h"
#include <fplus/fplus.hpp>
#include <string>
#include <set>
#include <map>
#include <algorithm>
#include <cctype>


// ============================================================================
// Source display helper: shows the code of a demo function in a collapsible section
// ============================================================================
namespace
{
    std::string gFileContent; // loaded once

    void LoadFileContent()
    {
        if (!gFileContent.empty()) return;
#ifndef __EMSCRIPTEN__
        gFileContent = fplus::read_text_file(__FILE__)();
#else
        gFileContent = fplus::read_text_file("/demos_cpp/demo_text_edit.cpp")();
#endif
    }

    // Extract the source code of a function by searching for "void funcName()"
    // and returning everything up to the next "// ====..." separator.
    std::string ExtractFunctionSource(const std::string& funcName)
    {
        LoadFileContent();
        std::string needle = "void " + funcName + "()";
        auto pos = gFileContent.find(needle);
        if (pos == std::string::npos) return "// Source not found for " + funcName;

        // Find the preceding comment block (look backwards for "// ====")
        auto commentStart = gFileContent.rfind("// ====", pos);
        if (commentStart != std::string::npos)
            pos = commentStart;

        // Find the end: next "// ====" after the function start
        auto endPos = gFileContent.find("// ====", pos + needle.size());
        if (endPos == std::string::npos)
            endPos = gFileContent.size();

        return gFileContent.substr(pos, endPos - pos);
    }

    // Show a "Show source" checkbox. When checked, displays the function's source
    // in a read-only editor (light theme), followed by a separator before the demo.
    // Returns true so the caller can always proceed to render the demo.
    void ShowSourceToggle(const char* funcName)
    {
        static std::map<std::string, bool> showFlags;
        static std::map<std::string, TextEditor> sourceEditors;

        bool& show = showFlags[funcName];
        ImGui::Checkbox("Show source", &show);
        if (show)
        {
            ImGui::SeparatorText("Source");
            if (sourceEditors.find(funcName) == sourceEditors.end())
            {
                auto& ed = sourceEditors[funcName];
                ed.SetText(ExtractFunctionSource(funcName));
                ed.SetLanguage(TextEditor::Language::Cpp());
                ed.SetPalette(TextEditor::GetLightPalette());
                ed.SetReadOnlyEnabled(true);
            }
            auto codeFont = ImGuiMd::GetCodeFont();
            ImGui::PushFont(codeFont.font, codeFont.size);
            std::string id = std::string("##src_") + funcName;
            sourceEditors[funcName].Render(id.c_str(), ImVec2(-1, ImGui::GetTextLineHeight() * 15), false);
            ImGui::PopFont();
            ImGui::SeparatorText("Demo");
        }
    }
} // anonymous namespace


// ============================================================================
// Tab 1: Basic Editor
// Demonstrates: text loading, language selection, palette switching
// ============================================================================
void DemoBasicEditor()
{
    ShowSourceToggle("DemoBasicEditor");
    static bool initialized = false;
    static TextEditor editor;
    if (!initialized)
    {
        std::string filename = __FILE__;
#ifndef __EMSCRIPTEN__
        std::string code = fplus::read_text_file(filename)();
#else
        std::string code = fplus::read_text_file("/demos_cpp/demo_text_edit.cpp")();
#endif
        editor.SetText(code);
        editor.SetLanguage(TextEditor::Language::Cpp());
        initialized = true;
    }

    // Palette buttons
    if (ImGui::SmallButton("Dark"))
        editor.SetPalette(TextEditor::GetDarkPalette());
    ImGui::SameLine();
    if (ImGui::SmallButton("Light"))
        editor.SetPalette(TextEditor::GetLightPalette());

    // Language selection
    ImGui::SameLine();
    ImGui::SetNextItemWidth(ImGui::CalcTextSize("AngelScript__").x);
    static int langIdx = 1; // default: C++
    const char* langNames[] = { "None", "C++", "C", "Python", "GLSL", "HLSL", "Lua", "SQL", "AngelScript", "C#", "JSON", "Markdown" };
    if (ImGui::Combo("Language", &langIdx, langNames, IM_ARRAYSIZE(langNames)))
    {
        const TextEditor::Language* langs[] = {
            nullptr,
            TextEditor::Language::Cpp(), TextEditor::Language::C(),
            TextEditor::Language::Python(), TextEditor::Language::Glsl(),
            TextEditor::Language::Hlsl(), TextEditor::Language::Lua(),
            TextEditor::Language::Sql(), TextEditor::Language::AngelScript(),
            TextEditor::Language::Cs(), TextEditor::Language::Json(),
            TextEditor::Language::Markdown()
        };
        editor.SetLanguage(langs[langIdx]);
    }

    // Cursor position display
    ImGui::SameLine();
    auto pos = editor.GetMainCursorPosition();
    ImGui::Text("Line: %d  Col: %d", pos.line + 1, pos.column + 1);

    // Render editor: we shall use a monospace font
    auto codeFont = ImGuiMd::GetCodeFont();
    ImGui::PushFont(codeFont.font, codeFont.size);
    editor.Render("##basic");
    ImGui::PopFont();
}


// ============================================================================
// Tab 2: Change Callback
// Demonstrates: detecting edits via SetChangeCallback
// ============================================================================
void DemoChangeCallback()
{
    ShowSourceToggle("DemoChangeCallback");
    static bool initialized = false;
    static TextEditor editor;
    static int changeCount = 0;
    static std::string lastChangeTime;

    if (!initialized)
    {
        editor.SetText("Edit this text to see the change callback in action.\n\nTry typing, deleting, or pasting.\n");
        editor.SetLanguage(TextEditor::Language::Cpp());
        editor.SetChangeCallback([&]()
        {
            changeCount++;
            lastChangeTime = "just now";
        }, 200); // 200ms debounce
        initialized = true;
    }

    ImGui::Text("Change count: %d", changeCount);
    if (!lastChangeTime.empty())
    {
        ImGui::SameLine();
        ImGui::Text("  (last change: %s)", lastChangeTime.c_str());
    }

    auto codeFont = ImGuiMd::GetCodeFont();
    ImGui::PushFont(codeFont.font, codeFont.size);
    editor.Render("##changes");
    ImGui::PopFont();
}


// ============================================================================
// Tab 3: Filters
// Demonstrates: FilterSelections to transform selected text
// ============================================================================
void DemoFilters()
{
    ShowSourceToggle("DemoFilters");
    static bool initialized = false;
    static TextEditor editor;

    if (!initialized)
    {
        editor.SetText(
            "Select some text below, then click a filter button.\n"
            "\n"
            "Hello World\n"
            "the quick brown fox jumps over the lazy dog\n"
            "SOME UPPERCASE TEXT\n"
            "mixed Case Text Here\n"
        );
        initialized = true;
    }

    ImGui::Text("Select text, then apply a filter:");
    ImGui::SameLine();

    if (ImGui::SmallButton("UPPER"))
    {
        editor.FilterSelections([](std::string_view text) -> std::string {
            std::string result(text);
            std::transform(result.begin(), result.end(), result.begin(), ::toupper);
            return result;
        });
    }
    ImGui::SameLine();
    if (ImGui::SmallButton("lower"))
    {
        editor.FilterSelections([](std::string_view text) -> std::string {
            std::string result(text);
            std::transform(result.begin(), result.end(), result.begin(), ::tolower);
            return result;
        });
    }
    ImGui::SameLine();
    if (ImGui::SmallButton("Strip trailing spaces"))
        editor.StripTrailingWhitespaces();

    auto codeFont = ImGuiMd::GetCodeFont();
    ImGui::PushFont(codeFont.font, codeFont.size);
    editor.Render("##filters");
    ImGui::PopFont();
}


// ============================================================================
// Tab 4: Decorators & Context Menus
// Demonstrates: line decorators + context menus working together
//   - Right-click a line number to toggle a breakpoint
//   - Right-click in the text for "Go to definition" / "Find references"
//   - Breakpoints are shown as red circles via a line decorator
// ============================================================================
void DemoDecoratorsAndContextMenus()
{
    ShowSourceToggle("DemoDecoratorsAndContextMenus");
    static bool initialized = false;
    static TextEditor editor;
    static std::set<int> breakpoints;
    static std::string lastAction;

    if (!initialized)
    {
        editor.SetText(
            "#include <iostream>\n"
            "\n"
            "void foo() {\n"
            "    std::cout << \"Hello\" << std::endl;\n"
            "    int x = 42;\n"
            "    float pi = 3.14159f;\n"
            "    return x;\n"
            "}\n"
        );
        editor.SetLanguage(TextEditor::Language::Cpp());

        // Decorator: draw a red circle on lines that have a breakpoint
        editor.SetLineDecorator(-2.0f, [](TextEditor::Decorator& decorator) {
            if (breakpoints.count(decorator.line))
            {
                auto cursorPos = ImGui::GetCursorScreenPos();
                ImVec2 center(
                    cursorPos.x + decorator.glyphSize.x * 0.5f,
                    cursorPos.y + decorator.glyphSize.y * 0.5f
                );
                float radius = decorator.glyphSize.y * 0.35f;
                ImGui::GetWindowDrawList()->AddCircleFilled(center, radius, IM_COL32(255, 60, 60, 255));
            }
        });

        // Right-click on line numbers: toggle breakpoint
        editor.SetLineNumberContextMenuCallback([](int line) {
            bool has = breakpoints.count(line) > 0;
            std::string label = (has ? "Remove breakpoint" : "Set breakpoint");
            label += " (line " + std::to_string(line + 1) + ")";
            if (ImGui::MenuItem(label.c_str()))
            {
                if (has)
                    breakpoints.erase(line);
                else
                    breakpoints.insert(line);
            }
        });

        // Right-click in the text: different context menu
        editor.SetTextContextMenuCallback([](int line, int column) {
            if (ImGui::MenuItem("Go to definition"))
                lastAction = "Go to definition at " + std::to_string(line + 1) + ":" + std::to_string(column + 1);
            if (ImGui::MenuItem("Find references"))
                lastAction = "Find references at " + std::to_string(line + 1) + ":" + std::to_string(column + 1);
        });

        initialized = true;
    }

    ImGui::Text("Right-click line numbers to toggle breakpoints, right-click text for other actions.");
    if (!lastAction.empty())
    {
        ImGui::SameLine();
        ImGui::TextColored(ImVec4(0.5f, 0.8f, 1.0f, 1.0f), "  %s", lastAction.c_str());
    }

    auto codeFont = ImGuiMd::GetCodeFont();
    ImGui::PushFont(codeFont.font, codeFont.size);
    editor.Render("##decorators_ctx");
    ImGui::PopFont();
}


// ============================================================================
// Tab 6: Text Diff
// Demonstrates: side-by-side text comparison with TextDiff
// ============================================================================
void DemoTextDiff()
{
    ShowSourceToggle("DemoTextDiff");
    static bool initialized = false;
    static TextDiff diff;
    static bool sideBySide = false;

    if (!initialized)
    {
        std::string left =
            "#include <iostream>\n"
            "\n"
            "void foo() {\n"
            "    std::cout << \"Hello\" << std::endl;\n"
            "    return 0;\n"
            "}\n";

        std::string right =
            "#include <iostream>\n"
            "#include <string>\n"
            "\n"
            "void foo() {\n"
            "    std::string name = \"World\";\n"
            "    std::cout << \"Hello, \" << name << std::endl;\n"
            "    return 0;\n"
            "}\n";

        diff.SetText(left, right);
        diff.SetLanguage(TextEditor::Language::Cpp());
        initialized = true;
    }

    if (ImGui::Checkbox("Side by side", &sideBySide))
        diff.SetSideBySideMode(sideBySide);

    auto codeFont = ImGuiMd::GetCodeFont();
    ImGui::PushFont(codeFont.font, codeFont.size);
    diff.Render("##diff");
    ImGui::PopFont();
}


// ============================================================================
// Main demo function
// ============================================================================
void demo_text_edit()
{
    ImGuiMd::Render(R"(
# ImGuiColorTextEdit
[ImGuiColorTextEdit](https://github.com/goossens/ImGuiColorTextEdit) is a syntax highlighting text editor for ImGui (originally by BalazsJako, rewritten by Johan A. Goossens)
    )");

    if (ImGui::BeginTabBar("##TextEditorDemos"))
    {
        if (ImGui::BeginTabItem("Basic Editor"))
        {
            DemoBasicEditor();
            ImGui::EndTabItem();
        }
        if (ImGui::BeginTabItem("Change Callback"))
        {
            DemoChangeCallback();
            ImGui::EndTabItem();
        }
        if (ImGui::BeginTabItem("Decorators & Menus"))
        {
            DemoDecoratorsAndContextMenus();
            ImGui::EndTabItem();
        }
        if (ImGui::BeginTabItem("Filters"))
        {
            DemoFilters();
            ImGui::EndTabItem();
        }
        if (ImGui::BeginTabItem("Text Diff"))
        {
            DemoTextDiff();
            ImGui::EndTabItem();
        }
        ImGui::EndTabBar();
    }
}
