#pragma once

#include "imgui.h"
#include <optional>
#include <vector>
#include <string>


// Specific patches for python bindings, where ImWChar* cannot be bound to python

namespace PatchImGui
{
    void set_imgui_io_filename(const std::string& filename);
    void set_imgui_log_filename(const std::string& filename);
}
