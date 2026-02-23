#pragma once
#include <vector>
#include <string>
#include <utility>
#include <functional>
#include "imgui.h"

// Information about a single demo file or API reference file
struct DemoFileInfo {
    std::string baseName;    // e.g., "im_anim_demo_basics" (without extension)
    bool hasPython = false;  // true if .py/.pyi exists alongside .cpp/.h
    bool isApiReference = false;  // true for header/stub files (vs demo files)
    std::string cppGithubUrl;  // Full URL without #L suffix
    std::string pyGithubUrl;   // Same for Python file (empty if no Python)

    // Display names
    std::string cppDisplayName() const { return baseName + (isApiReference ? ".h" : ".cpp"); }
    std::string pyDisplayName() const { return baseName + (isApiReference ? ".pyi" : ".py"); }

    // Fetch URL for emscripten_async_wget (e.g. "demo_code/imgui_demo.cpp")
    // Desktop reads via std::ifstream(IMAN_DEMO_CODE_DIR + "/" + cppDisplayName())
    std::string cppFetchUrl() const { return "demo_code/" + baseName + (isApiReference ? ".h" : ".cpp"); }
    std::string pyFetchUrl()  const { return "demo_code/" + baseName + (isApiReference ? ".pyi" : ".py"); }
};

// Configuration for a library (ImGui, ImPlot, ImPlot3D, ImAnim)
struct LibraryConfig {
    std::string name;                           // "ImAnim", "ImGui", etc.
    std::vector<DemoFileInfo> files;            // Demo files for this library
    std::function<void()> frameSetup;           // Called each frame (e.g., iam_update_begin_frame)
    std::function<void(ImVec2 windowPos, ImVec2 windowSize)> showDemoWindow; // Shows the demo content
    std::string introText;                                       // Plain text intro for the library (e.g. "Dear ImGui")
    std::vector<std::pair<std::string, std::string>> links;      // {label, url} pairs shown in the top toolbar
};

// Get all library configurations
const std::vector<LibraryConfig>& GetAllLibraryConfigs();

// Get all demo files across all libraries (for code viewer)
std::vector<DemoFileInfo> GetAllDemoFiles();

// Current library selection
int GetCurrentLibraryIndex();
void SetCurrentLibraryIndex(int index);
const LibraryConfig& GetCurrentLibrary();

// Get demo files for current library only
std::vector<DemoFileInfo> GetCurrentLibraryFiles();

// Single-library mode: when launched with --lib <name> (desktop) or ?lib=<name> (emscripten),
// only one library is shown and the library selection toolbar is simplified.
bool IsSingleLibraryMode();
void SetSingleLibraryMode(std::string libname);
void SetMultipleLibraryMode();

