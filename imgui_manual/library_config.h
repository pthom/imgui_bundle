#pragma once
#include <vector>
#include <string>
#include <functional>

// Information about a single demo file
struct DemoFileInfo {
    std::string baseName;    // e.g., "im_anim_demo_basics" (without extension)
    bool hasPython = false;  // true if .py exists alongside .cpp

    // Derived names for display and asset loading
    std::string cppDisplayName() const { return baseName + ".cpp"; }
    std::string pyDisplayName() const { return baseName + ".py"; }
    std::string cppAssetName() const { return baseName + ".cpp.txt"; }
    std::string pyAssetName() const { return baseName + ".py.txt"; }
};

// Configuration for a library (ImGui, ImPlot, ImPlot3D, ImAnim)
struct LibraryConfig {
    std::string name;                           // "ImAnim", "ImGui", etc.
    std::vector<DemoFileInfo> files;            // Demo files for this library
    std::function<void()> frameSetup;           // Called each frame (e.g., iam_update_begin_frame)
    std::function<void()> showDemoWindow;        // Shows the demo content
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
