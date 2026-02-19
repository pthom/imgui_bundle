#pragma once
#include <vector>
#include <string>
#include <functional>

// Information about a single demo file or API reference file
struct DemoFileInfo {
    std::string baseName;    // e.g., "im_anim_demo_basics" (without extension)
    bool hasPython = false;  // true if .py/.pyi exists alongside .cpp/.h
    bool isApiReference = false;  // true for header/stub files (vs demo files)
    std::string cppGithubUrl;  // Full URL without #L suffix
    std::string pyGithubUrl;   // Same for Python file (empty if no Python)

    // Derived names for display and asset loading
    std::string cppDisplayName() const { return baseName + (isApiReference ? ".h" : ".cpp"); }
    std::string pyDisplayName() const { return baseName + (isApiReference ? ".pyi" : ".py"); }
    std::string cppAssetName() const { return baseName + (isApiReference ? ".h.txt" : ".cpp.txt"); }
    std::string pyAssetName() const { return baseName + (isApiReference ? ".pyi.txt" : ".py.txt"); }
};

// Configuration for a library (ImGui, ImPlot, ImPlot3D, ImAnim)
struct LibraryConfig {
    std::string name;                           // "ImAnim", "ImGui", etc.
    std::vector<DemoFileInfo> files;            // Demo files for this library
    std::function<void()> frameSetup;           // Called each frame (e.g., iam_update_begin_frame)
    std::function<void()> showDemoWindow;        // Shows the demo content
    std::string mdIntro;                         // Markdown text with intro & links for the library, show in the top toolbar
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

