// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "../imgui-command-palette/imcmd_command_palette.h"


namespace ImCmd
{
    // Workaround for ImCmd::Context, since pybind11 stubbornly fails on perfect encapsulation
    // ImCmd::Context is perfectly encapsulated, since it is only defined privately in a C++ file, and not in a header.
    // See https://github.com/pybind/pybind11/issues/2770

    struct ContextWrapper
    {
        inline ContextWrapper() { ptr = ImCmd::CreateContext(); }
        inline ~ContextWrapper() { ImCmd::DestroyContext(ptr); }
        inline void SetAsCurrentContext(ContextWrapper *context) { ImCmd::SetCurrentContext(ptr); }
    private:
        ImCmd::Context *ptr;
    };
}
