//-----------------------------------------------------------------------------
// COMPILE-TIME OPTIONS FOR DEAR IMGUI
// Runtime options (clipboard callbacks, enabling various features, etc.) can generally be set via the ImGuiIO structure.
// You can use ImGui::SetAllocatorFunctions() before calling ImGui::CreateContext() to rewire memory allocation functions.
//-----------------------------------------------------------------------------
// A) You may edit imconfig.h (and not overwrite it when updating Dear ImGui, or maintain a patch/rebased branch with your modifications to it)
// B) or '#define IMGUI_USER_CONFIG "my_imgui_config.h"' in your project and then add directives in your own file without touching this template.
//-----------------------------------------------------------------------------
// You need to make sure that configuration settings are defined consistently _everywhere_ Dear ImGui is used, which include the imgui*.cpp
// files but also _any_ of your code that uses Dear ImGui. This is because some compile-time options have an affect on data structures.
// Defining those options in imconfig.h will ensure every compilation unit gets to see the same data structure layouts.
// Call IMGUI_CHECKVERSION() from your .cpp files to verify that the data structures your files are using are matching the ones imgui.cpp is using.
//-----------------------------------------------------------------------------

#pragma once

#include <stdexcept>
#include <string>

inline std::string _file_short_name(const std::string& filename)
{
    auto pos = filename.rfind("/");
    if (pos != std::string::npos)
        return filename.substr(pos + 1);

    pos = filename.rfind("\\");
    if (pos != std::string::npos)
        return filename.substr(pos + 1);

    return filename;
}

//---- Define assertion handler. Defaults to calling assert().
// If your macro uses multiple statements, make sure is enclosed in a 'do { .. } while (0)' block so it can be used as a single statement.
#define STRINGIFY(s) #s
#define IM_ASSERT(_EXPR) \
    do \
    { \
        if (!(_EXPR)) \
            throw std::runtime_error(std::string("IM_ASSERT( ") + STRINGIFY(_EXPR) + " )"      \
                + "   ---   " +  _file_short_name(__FILE__) + ":" + std::to_string(__LINE__) ); \
    } \
    while(0)

//---- Define attributes of all API symbols declarations, e.g. for DLL under Windows
// Using Dear ImGui via a shared library is not recommended, because of function call overhead and because we don't guarantee backward nor forward ABI compatibility.
// DLL users: heaps and globals are not shared across DLL boundaries! You will need to call SetCurrentContext() + SetAllocatorFunctions()
// for each static/DLL boundary you are calling from. Read "Context and Memory Allocators" section of imgui.cpp for more details.
#ifdef _WIN32
#define IMGUI_API __declspec( dllexport )
#define IMPLOT_API __declspec( dllexport )
#endif

#define IMGUI_USE_WCHAR32
