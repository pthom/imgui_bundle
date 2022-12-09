#include "ImGuizmoPure/ImSequencerPure.h"
#include "ImGuizmoPure/Editable.h"

namespace ImSequencer
{
    void SequenceInterfaceStl::Get(int index, int** start, int** end, int* type, unsigned int* color)
    //                                           ^            ^
    //                                         ouch !       ouch ouch!
    {
        SequenceGetInfo getInfo;
        getInfo.start = start;
        getInfo.end = end;
        getInfo.type = type;
        getInfo.color = color;

        GetPure(index, &getInfo);

        // ...
        // The new external API
        //             void GetPure(int index, SequenceGetInfo* v);
        // is still not usable by python
        // ...

        throw("abandon for now.");
    }


    bool SequencerPure(SequenceInterfaceStl* sequence, SequencerInfo* sequencerInfo)
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
