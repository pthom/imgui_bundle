#include "patch_imgui.h"
#include "imgui.h"

#include <string>
#include <vector>


namespace PatchImGui
{
    // ImGuiIO::IniFilename & LogFilename
    // Those are bare pointers with no storage for a string.
    //
    // Let's hack a storage
    static std::string gIniFilename, gLogFilename;

    void set_imgui_io_filename(const std::string& filename)
    {
        gIniFilename = filename;
        ImGui::GetIO().IniFilename = gIniFilename.c_str();
    }

    void set_imgui_log_filename(const std::string& filename)
    {
        gLogFilename = filename;
        ImGui::GetIO().LogFilename = gLogFilename.c_str();
    }

} // namespace PatchImGui
