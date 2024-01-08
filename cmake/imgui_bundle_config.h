// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
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

//---- Define assertion handler IM_ASSERT: this is dependent on the target (C++, python, emscripten)
#define STRINGIFY(s) #s

#ifdef IMGUI_BUNDLE_BUILD_PYTHON
// With Python, we throw an exception
// Throwing an exception is important for python (in order keep the python interpreter alive)
#define IM_ASSERT(_EXPR) \
    do \
    { \
        if (!(_EXPR)) \
            throw std::runtime_error(std::string("IM_ASSERT( ") + STRINGIFY(_EXPR) + " )"      \
                + "   ---   " +  _file_short_name(__FILE__) + ":" + std::to_string(__LINE__) ); \
    } \
    while(0)
#else // #ifdef IMGUI_BUNDLE_BUILD_PYTHON
    #ifdef __EMSCRIPTEN__
    // With emscripten, IM_ASSERT terminates, since emscripten does not support exceptions by default
    #define IM_ASSERT(_EXPR) \
        do \
        { \
            if (!(_EXPR)) \
            { \
                fprintf(stderr, "%s\n", (std::string("IM_ASSERT( ") + STRINGIFY(_EXPR) + " )"      \
                    + "   ---   " +  _file_short_name(__FILE__) + ":" + std::to_string(__LINE__) ).c_str() ) ; \
                std::terminate(); \
            } \
        } \
        while(0)
    #else // __EMSCRIPTEN__
        // For standard C++, this could be changed to assert. At this time, we also terminate()
        #define IM_ASSERT(_EXPR) \
            do \
            { \
                if (!(_EXPR)) \
                { \
                    fprintf(stderr, "%s\n", (std::string("IM_ASSERT( ") + STRINGIFY(_EXPR) + " )"      \
                        + "   ---   " +  _file_short_name(__FILE__) + ":" + std::to_string(__LINE__) ).c_str() ) ; \
                    /*assert(false);*/                                                                 \
                    std::terminate(); \
                } \
            } \
            while(0)
    #endif // __EMSCRIPTEN__
#endif // IMGUI_BUNDLE_BUILD_PYTHON

// #define IMGUI_USE_WCHAR32 (already defined by the use of Freetype in HelloImGui)

// Enable 32 bits ImDrawIdx for ImPlot
#define ImDrawIdx unsigned int
