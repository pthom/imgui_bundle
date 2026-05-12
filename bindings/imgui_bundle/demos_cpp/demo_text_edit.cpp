// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui.h"
#include "immapp/immapp.h"
#include "ImGuiColorTextEdit/TextEditor.h"
#include "ImGuiColorTextEdit/TextDiff.h"
#include "demo_utils/api_demos.h"
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
    std::string gCppContent;    // loaded once
    std::string gPythonContent; // loaded once

    void LoadFileContents()
    {
        if (gCppContent.empty())
            gCppContent = ReadCppCode("demo_text_edit");
        if (gPythonContent.empty())
            gPythonContent = ReadPythonCode("demo_text_edit");
    }

    // Extract source between a separator comment and the next one.
    // For C++: searches for "void funcName()" preceded by "// ===="
    // For Python: searches for "def pyFuncName(" preceded by "# ===="
    std::string ExtractFunctionSource(const std::string& content, const std::string& needle, const std::string& separator)
    {
        auto pos = content.find(needle);
        if (pos == std::string::npos) return "// Source not found for " + needle;

        auto commentStart = content.rfind(separator, pos);
        if (commentStart != std::string::npos)
            pos = commentStart;

        auto endPos = content.find(separator, pos + needle.size());
        if (endPos == std::string::npos)
            endPos = content.size();

        return content.substr(pos, endPos - pos);
    }

    // Show a "Show source" checkbox with C++/Python toggle.
    // When checked, displays the function's source in a read-only editor (light theme).
    // cppFuncName: e.g. "DemoBasicEditor", pyFuncName: e.g. "demo_basic_editor"
    void ShowSourceToggle(const char* cppFuncName, const char* pyFuncName)
    {
        static std::map<std::string, bool> showFlags;
        static std::map<std::string, int>  langFlags; // 0 = C++, 1 = Python
        static std::map<std::string, TextEditor> sourceEditors;

        std::string key(cppFuncName);
        bool& show = showFlags[key];
        int& lang = langFlags[key];

        ImGui::Checkbox("Show source", &show);
        if (show)
        {
            ImGui::SameLine();
            ImGui::RadioButton("C++", &lang, 0);
            ImGui::SameLine();
            ImGui::RadioButton("Python", &lang, 1);

            ImGui::SeparatorText("Source");
            LoadFileContents();

            // Build editor key per language to keep separate editors
            std::string editorKey = key + (lang == 0 ? "_cpp" : "_py");
            if (sourceEditors.find(editorKey) == sourceEditors.end())
            {
                auto& ed = sourceEditors[editorKey];
                if (lang == 0)
                    ed.SetText(ExtractFunctionSource(gCppContent, std::string("void ") + cppFuncName + "()", "// ===="));
                else
                    ed.SetText(ExtractFunctionSource(gPythonContent, std::string("def ") + pyFuncName + "(", "# ===="));
                ed.SetLanguage(lang == 0 ? TextEditor::Language::Cpp() : TextEditor::Language::Python());
                ed.SetPalette(TextEditor::GetLightPalette());
                ed.SetReadOnlyEnabled(true);
            }

            auto codeFont = ImGuiMd::GetCodeFont();
            ImGui::PushFont(codeFont.font, codeFont.size);
            std::string id = std::string("##src_") + editorKey;
            sourceEditors[editorKey].Render(id.c_str(), ImVec2(-1, ImGui::GetTextLineHeight() * 15), false);
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
    ShowSourceToggle("DemoBasicEditor", "demo_basic_editor");
    static bool initialized = false;
    static TextEditor editor;
    if (!initialized)
    {
        LoadFileContents();
        editor.SetText(gCppContent);
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

    // Cursor position display (doc coords: row != line once word-wrap is on)
    ImGui::SameLine();
    auto pos = editor.GetMainCursorPosition();
    ImGui::Text("Line: %zu  Col: %zu  (doc)", pos.line + 1, pos.index + 1);

    // Second row: editor view/behavior toggles
    bool wrap = editor.IsWordWrapEnabled();
    if (ImGui::Checkbox("Word Wrap", &wrap))
        editor.SetWordWrapEnabled(wrap);
    ImGui::SameLine();
    bool readOnly = editor.IsReadOnlyEnabled();
    if (ImGui::Checkbox("Read Only", &readOnly))
        editor.SetReadOnlyEnabled(readOnly);
    ImGui::SameLine();
    bool folding = editor.IsLineFoldingEnabled();
    if (ImGui::Checkbox("Line Folding", &folding))
        editor.SetLineFoldingEnabled(folding);
    ImGui::SameLine();
    ImGui::BeginDisabled(!folding);
    if (ImGui::SmallButton("Unfold All"))
        editor.UnfoldAll();
    ImGui::EndDisabled();
    ImGui::SameLine();
    bool miniMap = editor.IsShowMiniMapEnabled();
    if (ImGui::Checkbox("Show Mini Map", &miniMap))
        editor.SetShowMiniMapEnabled(miniMap);
    ImGui::TextDisabled("(folding uses brackets for C/C++, indentation for Python)");

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
    ShowSourceToggle("DemoChangeCallback", "demo_change_callback");
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
    ShowSourceToggle("DemoFilters", "demo_filters");
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
// Tab 4: Annotations & Interactivity
// Demonstrates four ways to annotate or react inside an editor:
//   - Line decorator (custom-drawn gutter): red circle on breakpoint lines
//   - Line markers (colored gutter + tooltips): error & warning markers
//   - Context menus on line numbers and on text (right-click)
//   - Hover callback in text: live popup showing the word under the cursor
// ============================================================================
void DemoDecoratorsAndContextMenus()
{
    ShowSourceToggle("DemoDecoratorsAndContextMenus", "demo_decorators_and_context_menus");
    static bool initialized = false;
    static TextEditor editor;
    static std::set<size_t> breakpoints;
    static std::string lastAction;
    // Hover callback kept here so the "Hover hints" checkbox below can
    // re-install it after a clear. Body assigned in the init block.
    static std::function<void(TextEditor::PopupData&)> textHover;

    if (!initialized)
    {
        editor.SetText(
            "#include <iostream>\n"
            "#include <vector>\n"
            "#include <map>\n"
            "\n"
            "// Compute summary statistics for a vector of numbers.\n"
            "double stats(const std::vector<double>& values) {\n"
            "    if (values.empty())\n"
            "        return 0.0;\n"
            "    double total = 0.0;\n"
            "    for (double v : values) total += v;\n"
            "    double mean = total / values.size();\n"
            "    int unused = 42;\n"
            "    return mean;\n"
            "}\n"
            "\n"
            "void greet(const std::string& name) {\n"
            "    std::cout << \"Hello \" << name << std::endl;\n"
            "}\n"
            "\n"
            "int divide(int a, int b) {\n"
            "    return a / b;\n"
            "}\n"
            "\n"
            "int main() {\n"
            "    auto data = std::vector<double>{1, 2, 3, 4, 5};\n"
            "    double m = stats(data);\n"
            "    std::cout << \"mean=\" << m << std::endl;\n"
            "    greet(\"world\");\n"
            "    std::cout << divide(10, 0) << std::endl;\n"
            "    return 0;\n"
            "}\n"
        );
        editor.SetLanguage(TextEditor::Language::Cpp());

        // Markers: persistent colored bands in the gutter / text background,
        // with built-in tooltips on hover (no callback needed for the tooltip).
        // Spread across the file so the scrollbar mini map has visible ticks.
        // Line numbers are zero-based.
        ImU32 warningColor = IM_COL32(180, 140, 0, 255);
        ImU32 warningBg    = IM_COL32(180, 140, 0, 48);
        ImU32 errorColor   = IM_COL32(220, 50, 50, 255);
        ImU32 errorBg      = IM_COL32(220, 50, 50, 56);
        editor.AddMarker(2,  warningColor, warningBg, "warning", "Included but never used: <map>");
        editor.AddMarker(11, warningColor, warningBg, "warning", "Unused variable: 'unused'");
        editor.AddMarker(20, errorColor,   errorBg,   "error",   "Unchecked division: b may be zero");
        editor.AddMarker(27, errorColor,   errorBg,   "error",   "Division by zero at runtime: divide(10, 0)");

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
        editor.SetLineNumberContextMenuCallback([](TextEditor::PopupData& data) {
            size_t line = data.pos.line;
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
        editor.SetTextContextMenuCallback([](TextEditor::PopupData& data) {
            size_t line = data.pos.line;
            size_t column = data.pos.index;
            if (ImGui::MenuItem("Go to definition"))
                lastAction = "Go to definition at " + std::to_string(line + 1) + ":" + std::to_string(column + 1);
            if (ImGui::MenuItem("Find references"))
                lastAction = "Find references at " + std::to_string(line + 1) + ":" + std::to_string(column + 1);
        });

        // Hover in text: live popup with the word under the mouse
        // (think IDE quick-info / type-on-hover).
        textHover = [](TextEditor::PopupData& data) {
            std::string word = editor.GetWordAtMousePos(ImGui::GetMousePos());
            ImGui::Text("Hovered: line %zu, col %zu", data.pos.line + 1, data.pos.index + 1);
            if (!word.empty())
            {
                ImGui::Text("Word: %s", word.c_str());
            }
        };
        editor.SetTextHoverCallback(textHover);

        initialized = true;
    }

    ImGui::TextWrapped(
        "Right-click line numbers (or F9) to toggle breakpoints. "
        "Right-click in text for a menu. Hover text for live info. "
        "Hover the colored gutter bands for marker tooltips."
    );
    if (!lastAction.empty())
        ImGui::TextColored(ImVec4(0.5f, 0.8f, 1.0f, 1.0f), "%s", lastAction.c_str());

    ImGui::BeginDisabled(!editor.HasMarkers());
    if (ImGui::SmallButton("Clear markers"))
        editor.ClearMarkers();
    ImGui::EndDisabled();
    ImGui::SameLine();
    bool miniMap = editor.IsShowMiniMapEnabled();
    if (ImGui::Checkbox("Show Mini Map", &miniMap))
        editor.SetShowMiniMapEnabled(miniMap);
    ImGui::SameLine();
    bool hoverOn = editor.HasTextHoverCallback();
    if (ImGui::Checkbox("Hover hints", &hoverOn))
    {
        if (hoverOn)
            editor.SetTextHoverCallback(textHover);
        else
            editor.ClearTextHoverCallback();
    }
    ImGui::SameLine();
    bool scrollbarMini = editor.IsShowScrollbarMiniMapEnabled();
    if (ImGui::Checkbox("Show Scrollbar Mini Map", &scrollbarMini))
        editor.SetShowScrollbarMiniMapEnabled(scrollbarMini);
    ImGui::SameLine();
    ImGui::TextDisabled("(ticks in the scrollbar at marker / selection lines)");

    ImGui::NewLine();
    ImGui::NewLine();
    auto codeFont = ImGuiMd::GetCodeFont();
    ImGui::PushFont(codeFont.font, codeFont.size);
    editor.Render("##decorators_ctx", ImVec2(-1, ImGui::GetTextLineHeight() * 20));
    ImGui::PopFont();

    // F9: toggle breakpoint on current line
    if (ImGui::Shortcut(ImGuiKey_F9))
    {
        size_t line = editor.GetMainCursorPosition().line;
        if (breakpoints.count(line))
            breakpoints.erase(line);
        else
            breakpoints.insert(line);
    }
}


// ============================================================================
// Tab 6: Text Diff
// Demonstrates: side-by-side text comparison with TextDiff
// ============================================================================
void DemoTextDiff()
{
    ShowSourceToggle("DemoTextDiff", "demo_text_diff");
    static bool initialized = false;
    static TextDiff diff;
    static bool sideBySide = false;

    if (!initialized)
    {
        // The long comment line on the second row exists so that toggling
        // the Word Wrap checkbox produces a visible effect on the diff.
        std::string left =
            "#include <iostream>\n"
            "// Module that says hello. A tiny example used in the ImGui Bundle TextDiff demo to show how line-by-line comparison works.\n"
            "\n"
            "void foo() {\n"
            "    std::cout << \"Hello\" << std::endl;\n"
            "    return 0;\n"
            "}\n";

        std::string right =
            "#include <iostream>\n"
            "// Module that says hello to anyone by name. A tiny example used in the ImGui Bundle TextDiff demo to show how line-by-line comparison and word-wrap work together.\n"
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
    ImGui::SameLine();
    bool wrap = diff.IsWordWrapEnabled();
    if (ImGui::Checkbox("Word Wrap", &wrap))
        diff.SetWordWrapEnabled(wrap);

    auto codeFont = ImGuiMd::GetCodeFont();
    ImGui::PushFont(codeFont.font, codeFont.size);
    diff.Render("##diff");
    ImGui::PopFont();
}

// ============================================================================
// Tab 7: Editor and menus
// Demonstrates how menus can be added to supplement the editor
// ============================================================================
#if __APPLE__
#define SHORTCUT "Cmd-"
#else
#define SHORTCUT "Ctrl-"
#endif
void DemoEditorWithMenus()
{
    ShowSourceToggle("DemoEditorWithMenus", "demo_editor_with_menus");

    static bool initialized = false;
    static TextEditor editor;

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
        initialized = true;
    }

    ImGui::BeginChild("editor_with_menus", ImVec2(0, 0), 0, ImGuiWindowFlags_MenuBar);

    // create menubar
	if (ImGui::BeginMenuBar()) {
		// if (ImGui::BeginMenu("File")) {
		// 	if (ImGui::MenuItem("New", SHORTCUT "N")) { newFile(); }
		// 	if (ImGui::MenuItem("Open...", SHORTCUT "O")) { openFile(); }
		// 	ImGui::Separator();
		//
		// 	if (ImGui::MenuItem("Save", SHORTCUT "S", nullptr, isSavable())) { saveFile(); }
		// 	if (ImGui::MenuItem("Save As...")) { showSaveFileAs(); }
		// 	ImGui::EndMenu();
		// }

		if (ImGui::BeginMenu("Edit")) {
			if (ImGui::MenuItem("Undo", " " SHORTCUT "Z", nullptr, editor.CanUndo())) { editor.Undo(); }
#if __APPLE__
			if (ImGui::MenuItem("Redo", "^" SHORTCUT "Z", nullptr, editor.CanRedo())) { editor.Redo(); }
#else
			if (ImGui::MenuItem("Redo", " " SHORTCUT "Y", nullptr, editor.CanRedo())) { editor.Redo(); }
#endif

			ImGui::Separator();
			if (ImGui::MenuItem("Cut", " " SHORTCUT "X", nullptr, editor.AnyCursorHasSelection())) { editor.Cut(); }
			if (ImGui::MenuItem("Copy", " " SHORTCUT "C", nullptr, editor.AnyCursorHasSelection())) { editor.Copy(); }
			if (ImGui::MenuItem("Paste", " " SHORTCUT "V", nullptr, ImGui::GetClipboardText() != nullptr)) { editor.Paste(); }

			ImGui::Separator();
			bool flag;
			flag = editor.IsInsertSpacesOnTabs(); if (ImGui::MenuItem("Insert Spaces on Tabs", nullptr, &flag)) { editor.SetInsertSpacesOnTabs(flag); };

			if (ImGui::MenuItem("Tabs To Spaces")) { editor.TabsToSpaces(); }
			if (ImGui::MenuItem("Spaces To Tabs", nullptr, nullptr, !editor.IsInsertSpacesOnTabs())) { editor.SpacesToTabs(); }
			if (ImGui::MenuItem("Strip Trailing Whitespaces")) { editor.StripTrailingWhitespaces(); }

			ImGui::EndMenu();
		}

		if (ImGui::BeginMenu("Selection")) {
			if (ImGui::MenuItem("Select All", " " SHORTCUT "A", nullptr, !editor.IsEmpty())) { editor.SelectAll(); }
			ImGui::Separator();

			if (ImGui::MenuItem("Indent Line(s)", " " SHORTCUT "]", nullptr, !editor.IsEmpty())) { editor.IndentLines(); }
			if (ImGui::MenuItem("Deindent Line(s)", " " SHORTCUT "[", nullptr, !editor.IsEmpty())) { editor.DeindentLines(); }
			if (ImGui::MenuItem("Move Line(s) Up",  "Alt-Up", nullptr, !editor.IsEmpty())) { editor.MoveUpLines(); }
			if (ImGui::MenuItem("Move Line(s) Down",  "Alt-Down", nullptr, !editor.IsEmpty())) { editor.MoveDownLines(); }
			if (ImGui::MenuItem("Toggle Comments", " " SHORTCUT "/", nullptr, editor.HasLanguage())) { editor.ToggleComments(); }
			ImGui::Separator();

			if (ImGui::MenuItem("To Uppercase", nullptr, nullptr, editor.AnyCursorHasSelection())) { editor.SelectionToUpperCase(); }
			if (ImGui::MenuItem("To Lowercase", nullptr, nullptr, editor.AnyCursorHasSelection())) { editor.SelectionToLowerCase(); }
			ImGui::Separator();

			if (ImGui::MenuItem("Add Next Occurrence", " " SHORTCUT "D", nullptr, editor.CurrentCursorHasSelection())) { editor.AddNextOccurrence(); }
			if (ImGui::MenuItem("Select All Occurrences", "^" SHORTCUT "D", nullptr, editor.CurrentCursorHasSelection())) { editor.SelectAllOccurrences(); }

			ImGui::EndMenu();
		}

		if (ImGui::BeginMenu("View")) {

			bool flag;
			flag = editor.IsShowWhitespacesEnabled(); if (ImGui::MenuItem("Show Whitespaces", nullptr, &flag)) { editor.SetShowWhitespacesEnabled(flag); };
			flag = editor.IsShowSpacesEnabled(); if (ImGui::MenuItem("Show Spaces", nullptr, &flag)) { editor.SetShowSpacesEnabled(flag); };
			flag = editor.IsShowTabsEnabled(); if (ImGui::MenuItem("Show Tabs", nullptr, &flag)) { editor.SetShowTabsEnabled(flag); };
			flag = editor.IsShowLineNumbersEnabled(); if (ImGui::MenuItem("Show Line Numbers", nullptr, &flag)) { editor.SetShowLineNumbersEnabled(flag); };
			flag = editor.IsShowingMatchingBrackets(); if (ImGui::MenuItem("Show Matching Brackets", nullptr, &flag)) { editor.SetShowMatchingBrackets(flag); };
			flag = editor.IsCompletingPairedGlyphs(); if (ImGui::MenuItem("Complete Matching Glyphs", nullptr, &flag)) { editor.SetCompletePairedGlyphs(flag); };
			flag = editor.IsShowPanScrollIndicatorEnabled(); if (ImGui::MenuItem("Show Pan/Scroll Indicator", nullptr, &flag)) { editor.SetShowPanScrollIndicatorEnabled(flag); };
			flag = editor.IsMiddleMousePanMode(); if (ImGui::MenuItem("Middle Mouse Pan Mode", nullptr, &flag)) { if (flag) editor.SetMiddleMousePanMode(); else editor.SetMiddleMouseScrollMode(); };

			ImGui::Separator();
			flag = editor.IsWordWrapEnabled(); if (ImGui::MenuItem("Word Wrap", nullptr, &flag)) { editor.SetWordWrapEnabled(flag); };
			flag = editor.IsLineFoldingEnabled(); if (ImGui::MenuItem("Line Folding", nullptr, &flag)) { editor.SetLineFoldingEnabled(flag); };
			flag = editor.IsShowMiniMapEnabled(); if (ImGui::MenuItem("Show Mini Map", nullptr, &flag)) { editor.SetShowMiniMapEnabled(flag); };
			flag = editor.IsShowScrollbarMiniMapEnabled(); if (ImGui::MenuItem("Show Scrollbar Mini Map", nullptr, &flag)) { editor.SetShowScrollbarMiniMapEnabled(flag); };

			ImGui::EndMenu();
		}

		if (ImGui::BeginMenu("Find")) {
			if (ImGui::MenuItem("Find", " " SHORTCUT "F")) { editor.OpenFindReplaceWindow(); }
			if (ImGui::MenuItem("Find Next", " " SHORTCUT "G", nullptr, editor.HasFindString())) { editor.FindNext(); }
			// if (ImGui::MenuItem("Find All", "Shift " SHORTCUT "F", nullptr, editor.HasFindString())) { editor.FindAll(); }
			ImGui::Separator();
			ImGui::EndMenu();
		}

		ImGui::EndMenuBar();
	}

    auto codeFont = ImGuiMd::GetCodeFont();
    ImGui::PushFont(codeFont.font, codeFont.size);
    editor.Render("##editor_menus");
    ImGui::PopFont();

    ImGui::EndChild();
}


// ============================================================================
// Tab 7: Multi-Cursor
// Demonstrates: multiple simultaneous cursors and selections.
//   - Alt-click (Mac) / Ctrl-click (Windows, Linux) adds a cursor
//   - Select a word, then Ctrl-D (Cmd-D on Mac) adds a cursor at the next match
// A live status panel lists every cursor (position + selected text) using
// GetNumberOfCursors / GetCursorSelection / GetCursorText.
// ============================================================================
void DemoMultiCursor()
{
    ShowSourceToggle("DemoMultiCursor", "demo_multi_cursor");
    static bool initialized = false;
    static TextEditor editor;

    if (!initialized)
    {
        editor.SetText(
            "// Multi-cursor playground.\n"
            "// - Alt-click (Mac) / Ctrl-click (Windows, Linux) to add a cursor\n"
            "//   at the click location.\n"
            "// - Hold the same modifier and drag to add a cursor and extend its selection\n"
            "// - Double-click a word to select it, then Ctrl-D (or Command-D on Mac)\n"
            "//   to add a cursor at the next occurrence of the same word.\n"
            "\n"
            "int value = 1;\n"
            "value = value + 1;\n"
            "value = value * value;\n"
            "value = value - 1;\n"
            "std::cout << value << value << value << std::endl;\n"
        );
        editor.SetLanguage(TextEditor::Language::Cpp());
        initialized = true;
    }

    // Quick-action buttons. AddNextOccurrence / SelectAllOccurrences require
    // the current cursor to have a selection (a word to match).
    {
        ImGui::BeginDisabled(!editor.CurrentCursorHasSelection());
        if (ImGui::SmallButton("Add Next Occurrence"))
            editor.AddNextOccurrence();
        ImGui::SameLine();
        if (ImGui::SmallButton("Select All Occurrences"))
            editor.SelectAllOccurrences();
        ImGui::EndDisabled();
        ImGui::SameLine();

        ImGui::BeginDisabled(editor.GetNumberOfCursors() <= 1);
        if (ImGui::SmallButton("Clear Extra Cursors"))
            editor.ClearCursors(); // leaves a single cursor at the main location
        ImGui::EndDisabled();
    }

    // Editor (constrained height so the cursor info panel below stays visible)
    {
        auto codeFont = ImGuiMd::GetCodeFont();
        ImGui::PushFont(codeFont.font, codeFont.size);
        float editorHeight = ImGui::GetTextLineHeight() * 20.0f;
        editor.Render("##multi_cursor", ImVec2(0, editorHeight));
        ImGui::PopFont();
    }

    // Live cursor status panel
    {
        size_t nCursors = editor.GetNumberOfCursors();
        ImGui::Text("Cursors: %zu", nCursors);
        for (size_t i = 0; i < nCursors; ++i)
        {
            auto sel = editor.GetCursorSelection(i);
            std::string text = editor.GetCursorText(i);
            if (text.empty())
            {
                ImGui::BulletText("[%zu] L:%zu C:%zu",
                    i, sel.start.line + 1, sel.start.index + 1);
            }
            else
            {
                ImGui::BulletText("[%zu] L:%zu C:%zu -> L:%zu C:%zu  selected: '%s'",
                    i,
                    sel.start.line + 1, sel.start.index + 1,
                    sel.end.line + 1, sel.end.index + 1,
                    text.c_str());
            }
        }
    }
}


// ============================================================================
// Main demo function
// ============================================================================
void demo_text_edit()
{
    ImGuiMd::Render(R"(
# ImGuiColorTextEdit
[ImGuiColorTextEdit](https://github.com/goossens/ImGuiColorTextEdit) is a syntax highlighting text editor for Dear ImGui (originally by BalazsJako, rewritten by Johan A. Goossens)
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
        if (ImGui::BeginTabItem("Annotations & Interactivity"))
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
        if (ImGui::BeginTabItem("Multi-Cursor"))
        {
            DemoMultiCursor();
            ImGui::EndTabItem();
        }
        if (ImGui::BeginTabItem("Editor with Menus"))
        {
            DemoEditorWithMenus();
            ImGui::EndTabItem();
        }
        ImGui::EndTabBar();
    }
}
