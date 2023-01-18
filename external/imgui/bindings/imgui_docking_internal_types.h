// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui.h"
#include "imgui_internal.h"

////////////////////////////////////////////////////////////
// Copy paste of Docking Internal Types from imgui.cpp
//
// needed for the compilation on docking branch
////////////////////////////////////////////////////////////

//-----------------------------------------------------------------------------
// Docking: Internal Types
//-----------------------------------------------------------------------------
// - ImGuiDockRequestType
// - ImGuiDockRequest
// - ImGuiDockPreviewData
// - ImGuiDockNodeSettings
// - ImGuiDockContext
//-----------------------------------------------------------------------------

enum ImGuiDockRequestType
{
    ImGuiDockRequestType_None = 0,
    ImGuiDockRequestType_Dock,
    ImGuiDockRequestType_Undock,
    ImGuiDockRequestType_Split                  // Split is the same as Dock but without a DockPayload
};

struct ImGuiDockRequest
{
    ImGuiDockRequestType    Type;
    ImGuiWindow*            DockTargetWindow;   // Destination/Target Window to dock into (may be a loose window or a DockNode, might be NULL in which case DockTargetNode cannot be NULL)
    ImGuiDockNode*          DockTargetNode;     // Destination/Target Node to dock into
    ImGuiWindow*            DockPayload;        // Source/Payload window to dock (may be a loose window or a DockNode), [Optional]
    ImGuiDir                DockSplitDir;
    float                   DockSplitRatio;
    bool                    DockSplitOuter;
    ImGuiWindow*            UndockTargetWindow;
    ImGuiDockNode*          UndockTargetNode;

    ImGuiDockRequest()
    {
        Type = ImGuiDockRequestType_None;
        DockTargetWindow = DockPayload = UndockTargetWindow = NULL;
        DockTargetNode = UndockTargetNode = NULL;
        DockSplitDir = ImGuiDir_None;
        DockSplitRatio = 0.5f;
        DockSplitOuter = false;
    }
};

struct ImGuiDockPreviewData
{
    ImGuiDockNode   FutureNode;
    bool            IsDropAllowed;
    bool            IsCenterAvailable;
    bool            IsSidesAvailable;           // Hold your breath, grammar freaks..
    bool            IsSplitDirExplicit;         // Set when hovered the drop rect (vs. implicit SplitDir==None when hovered the window)
    ImGuiDockNode*  SplitNode;
    ImGuiDir        SplitDir;
    float           SplitRatio;
    ImRect          DropRectsDraw[ImGuiDir_COUNT + 1];  // May be slightly different from hit-testing drop rects used in DockNodeCalcDropRects()

    ImGuiDockPreviewData() : FutureNode(0) { IsDropAllowed = IsCenterAvailable = IsSidesAvailable = IsSplitDirExplicit = false; SplitNode = NULL; SplitDir = ImGuiDir_None; SplitRatio = 0.f; for (int n = 0; n < IM_ARRAYSIZE(DropRectsDraw); n++) DropRectsDraw[n] = ImRect(+FLT_MAX, +FLT_MAX, -FLT_MAX, -FLT_MAX); }
};

// Persistent Settings data, stored contiguously in SettingsNodes (sizeof() ~32 bytes)
struct ImGuiDockNodeSettings
{
    ImGuiID             ID;
    ImGuiID             ParentNodeId;
    ImGuiID             ParentWindowId;
    ImGuiID             SelectedTabId;
    signed char         SplitAxis;
    char                Depth;
    ImGuiDockNodeFlags  Flags;                  // NB: We save individual flags one by one in ascii format (ImGuiDockNodeFlags_SavedFlagsMask_)
    ImVec2ih            Pos;
    ImVec2ih            Size;
    ImVec2ih            SizeRef;
    ImGuiDockNodeSettings() { memset(this, 0, sizeof(*this)); SplitAxis = ImGuiAxis_None; }
};
