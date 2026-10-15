#pragma once
#include "imgui_explorer.h"
#include <string>

// Render the code viewer window (call from a dockable window's GuiFunction)
void DemoCodeViewer_Show();

// Get/set whether to show Python code (when available)
bool DemoCodeViewer_GetShowPython();
void DemoCodeViewer_SetShowPython(bool show);

// Get the index of the currently displayed file tab
int DemoCodeViewer_GetCurrentFileIndex();

// Scroll to a specific line in a specific file
// filename: just the filename (e.g., "im_anim_demo.cpp"), not the full path
// line: 1-based line number
// section: the IMGUI_DEMO_MARKER section name (used to find the corresponding Python line)
void DemoCodeViewer_ShowCodeAt(const char* filename, int line, const char* section);

// Starts loading the current library's demo source (both languages), before the code is shown: the line labels and the
// first jump to the code then need no wait. A no-op once it is loading or loaded.
void DemoCodeViewer_PreloadDemoFile();

// Look up the Python line (1-based) for a IMGUI_DEMO_MARKER section in a given file.
// cppFilename: e.g. "imgui_demo.cpp". Returns -1 if not found or no Python available.
int DemoCodeViewer_GetPythonLineForSection(const char* cppFilename, const char* section);

// The demo's marker callback asks whether its section is the one "Show demo" reveals: true at its first few frames,
// then the caller scrolls the demo window to it
bool DemoCodeViewer_TakeRevealTarget(const char* section);
// Whether this section is being revealed (a query: unlike DemoCodeViewer_TakeRevealTarget, it does not count a frame)
bool DemoCodeViewer_IsRevealTarget(const char* section);
// True once after "Show demo" (the breadcrumb's button, the code's menu): a narrow layout shows the demo pane
bool DemoCodeViewer_TakeShowDemoRequest();
// The demo's marker callback reports a section whose zone is in view: "Show demo" is then disabled for it
void DemoCodeViewer_NoteSectionInView(const char* section);
// The explorer reports each frame when it shows the demo: beside the code, or in the other pane of a narrow layout
void DemoCodeViewer_NoteDemoShown();
// The explorer reports each frame whether it shows one pane at a time (a phone): the code then has no line numbers,
// and a jump scrolls it sideways past its indentation
void DemoCodeViewer_NoteNarrowLayout(bool narrow);
// The explorer gives the demo's pane each frame: a window of the demo's menus that a search just opened goes there
void DemoCodeViewer_PlaceMenuWindow(ImVec2 pos, ImVec2 size);
// The screen rectangle of a text in the code shown at the last frame: its first occurrence on screen
ImGuiExplorerCodeTextRect DemoCodeViewer_TextRectOnScreen(const std::string& text);
// The search of the demo's sections, drawn as a text field ("Search the demos", shorter when narrow) of a width
// (-FLT_MIN: all the width): a click opens the popup over it. A result opens in the demo when it is shown, in the
// code otherwise. True when the code pane should be shown (one pane at a time: a result the demo cannot open)
bool DemoCodeViewer_SearchField(float width, bool demoShown);
// Links to a section, for the standalone explorer (call once, before the first frame): opens demoRequest (a
// section's path, e.g. "Plots/Line Plots", or words of it, as in the search; empty for none), and on the web keeps
// the address bar on the section shown (?lib=implot&demo=...). "Copy link" items appear in the menus
void DemoCodeViewer_EnableLinks(const std::string& demoRequest);
// Each frame, after DemoCodeViewer_PreloadDemoFile(): opens the requested section, updates the address bar
void DemoCodeViewer_UpdateLinks();
// The "..." menu's item: copies a link to the section shown (when links are enabled). True when clicked
bool DemoCodeViewer_CopyLinkMenuItem();
// Returns true when in Python-only mode (PyPI install).
// In this mode, C++ source files are not available and only Python code is shown.
bool DemoCodeViewer_IsPythonOnlyMode();

// Configure Python-only mode: sets the demo code directory and stub aliases
// based on the imgui_bundle package root path.
void DemoCodeViewer_SetupPythonMode(const std::string& pythonPackagePath);
