#pragma once

// Initialize the code viewer - loads source files from assets
void DemoCodeViewer_Init();

// Render the code viewer window (call from a dockable window's GuiFunction)
void DemoCodeViewer_Show();

// Scroll to a specific line in a specific file
// filename: just the filename (e.g., "im_anim_demo.cpp"), not the full path
// line: 1-based line number
void DemoCodeViewer_ShowCodeAt(const char* filename, int line);
