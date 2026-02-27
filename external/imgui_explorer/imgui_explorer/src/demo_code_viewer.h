#pragma once

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

// Look up the Python line (1-based) for a IMGUI_DEMO_MARKER section in a given file.
// cppFilename: e.g. "imgui_demo.cpp". Returns -1 if not found or no Python available.
int DemoCodeViewer_GetPythonLineForSection(const char* cppFilename, const char* section);
