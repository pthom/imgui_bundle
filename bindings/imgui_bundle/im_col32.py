# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
ImU32 = int

IM_COL32_R_SHIFT = 0
IM_COL32_G_SHIFT = 8
IM_COL32_B_SHIFT = 16
IM_COL32_A_SHIFT = 24


def IM_COL32(r: ImU32, g: ImU32, b: ImU32, a: ImU32) -> ImU32:
    r = (
        (a << IM_COL32_A_SHIFT)
        | (b << IM_COL32_B_SHIFT)
        | (g << IM_COL32_G_SHIFT)
        | (r << IM_COL32_R_SHIFT)
    )
    return r
