#include "ImGuizmoStl/ImSequencerStl.h"

namespace ImSequencer
{
    void SequenceInterfaceStl::Get(int index, int** start, int** end, int* type, unsigned int* color)
    //                                           ^            ^
    //                                         ouch !       ouch ouch!
    {
        // Let's juggle with the heap memory, and hope for the best

        SequenceGetInfo getInfo;
        getInfo.start = start;
        getInfo.end = end;
        getInfo.type = type;
        getInfo.color = color;

        Get_V2(index, &getInfo);

        // ...
        // The new external API
        //             void Get_V2(int index, SequenceGetInfo* v);
        // is still not usable by python
        // ...

        throw("I give up.");
    }


    bool Sequencer_V2(SequenceInterfaceStl* sequence, SequencerInfo* sequencerInfo)
    {
        bool result = Sequencer(
            sequence,
            &sequencerInfo->currentFrame,
            &sequencerInfo->expanded,
            &sequencerInfo->selectedEntry,
            &sequencerInfo->firstFrame,
            sequencerInfo->sequenceOptions
        );
        return result;
    }

}
