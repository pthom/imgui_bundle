// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#pragma once
//
// Several utilities to help the use of the Immediate Gui paradigm in the context of pure functions
// (i.e. one input, one output, no modifiable parameter)
//


// Editable: a simple structure to extend ImGui's policy of "returning true when changed",
// by adding with a modified return value to the functions output
template<typename T>
struct Editable
{
    Editable(const T& value, bool edited = false) : Value(value), Edited(edited) {}

    // Invoke this operator to check for user modification
    operator bool() const { return Edited; }

    // (this version is adapted for relatively lightweight objects, since it does copy the values.
    //  however, anything less than 1KB should be OK, since copying 1KB per frame at 200FPS should be
    //  unnoticeable)
    T Value;
    bool Edited = false;
};
