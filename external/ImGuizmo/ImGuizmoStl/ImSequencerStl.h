#pragma once

#include "ImGuizmo/ImSequencer.h"

namespace ImSequencer
{
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

        void Get_V2(int index, SequenceGetInfo* v);
    };


    struct SequencerInfo
    {
        int currentFrame = 0;
        bool expanded = true;
        int selectedEntry = 0;
        int firstFrame = 0;

        int sequenceOptions = 0;
    };
    bool Sequencer_V2(SequenceInterfaceStl* sequence, SequencerInfo* sequencerInfo);

}
