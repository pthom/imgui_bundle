#pragma once

#include "ImGuizmo/ImSequencer.h"

namespace ImSequencer
{
    // Effort to adapt ImSequencer to python. Abandoned for now

    struct SequenceGetInfo
    {
        int **start;
        int **end;
        int *type;
        unsigned int *color;
    };


    struct SequenceInterfaceStl: public SequenceInterface
    {
        void Get(int index, int** start, int** end, int* type, unsigned int* color) override;

        void GetPure(int index, SequenceGetInfo* v);
    };


    struct SequencerInfo
    {
        int currentFrame = 0;
        bool expanded = true;
        int selectedEntry = 0;
        int firstFrame = 0;

        int sequenceOptions = 0;
    };
    bool SequencerPure(SequenceInterfaceStl* sequence, SequencerInfo* sequencerInfo);

}
