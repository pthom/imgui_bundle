// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
#pragma once
// Helpers shared by the wrapper and its backends. Not part of the public API.
#include <string>

namespace RichMd { namespace Internal
{
    // Removes the common indentation (that of the first non-empty line) and the leading / trailing
    // empty lines. Code: trailing spaces are trimmed; markdown: they are kept (two are a hard line break).
    std::string Unindent(const std::string& text, bool isCode);
}}
