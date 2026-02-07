// Copied from imgui repo : https://github.com/pthom/imgui/blob/DemoCodeDockingSplit/imgui_demo_marker_hooks.cpp
// (pthom fork, branch DemoCodeDockingSplit)

#include "imgui.h"
#include <stdio.h>
#include <string.h>
#include "imgui_demo_marker_hooks.h"

ImGuiDemoMarkerHook             GImGuiDemoMarkerHook = NULL;

// Strip directory path from __FILE__, returning just the filename
static const char* GetFileName(const char* path)
{
    const char* f = strrchr(path, '/');
    const char* b = strrchr(path, '\\');
    const char* last = f > b ? f : b;
    return last ? last + 1 : path;
}

//-----------------------------------------------------------------------------
// [SECTION] IMGUI_DEMO_MARKER utilities
// Utilities that provide an interactive "code lookup" via the IMGUI_DEMO_MARKER macro
//-----------------------------------------------------------------------------

// Forward declarations
void                                DemoMarker_ShowGui();
bool                                DemoMarker_IsMouveHovering(int line_number);
// Global state
bool                                GDemoMarker_FlagFollowSource = true;
char                                GDemoMarker_CodeLookupInfo[1024] = {0};
void DemoMarker_HandleCallback(const char* file, int line, const char* section)
{
    if (!GImGuiDemoMarkerHook)
        return;
    if (!DemoMarker_IsMouveHovering(line))
        return;

    const char* filename = GetFileName(file);
    snprintf(GDemoMarker_CodeLookupInfo, sizeof(GDemoMarker_CodeLookupInfo),
    "%s:%d - \"%s\"", filename, line + 1, section);

    if (GDemoMarker_FlagFollowSource)
        GImGuiDemoMarkerHook(filename, line, section);
}


// [sub section] ImGuiDemoMarker_GuiToggle()
// Display a "Code Lookup" checkbox that toggles interactive code browsing
void DemoMarker_ShowShortInfo()
{
    if (GImGuiDemoMarkerHook == NULL)
        return;
    ImGui::SeparatorText("Code lookup");
    ImGui::Checkbox("Follow source", &GDemoMarker_FlagFollowSource);
    if (ImGui::IsItemHovered())
        ImGui::SetTooltip(
            "Check this box and hover any demo to pinpoint its location inside the code.\n"
            "\n"
            "(you can also press \"Ctrl-Alt-C\" at any time to toggle this mode)"
        );
    if (GDemoMarker_FlagFollowSource)
    {
        ImGui::SameLine();
        ImGui::Text("   (Press Esc to stop this mode)");
    }
    if (ImGui::IsKeyPressed(ImGuiKey_C) && ImGui::GetIO().KeyCtrl && ImGui::GetIO().KeyAlt)
        GDemoMarker_FlagFollowSource = !GDemoMarker_FlagFollowSource;
    if (GDemoMarker_FlagFollowSource && ImGui::IsKeyPressed(ImGuiKey_Escape))
        GDemoMarker_FlagFollowSource = false;

    ImGui::Text("%s", GDemoMarker_CodeLookupInfo);
    ImGui::Separator();
}

// [sub section] ImGuiDemoMarkerHighlightZone()
// `bool ImGuiDemoMarkerHighlightZone(int line_number)` is able to graphically highlight a *hovered* section
// of the demo (it keeps track of graphical location of each section).
// Each zone is identified by its source code line number, and ImGuiDemoMarkerHighlightZone will return true if
// it is currently highlighted.
#include "imgui_internal.h" //  we import GetCurrentWindow() (which is defined in imgui_internal)
namespace ImGuiDemoMarkerZoneBoundings_Impl
{
    // The DemoMarkersRegistry class stores the boundings for the different calls to the IMGUI_DEMO_MARKER macro.
    // It handles the display and handling of the "Help/Code lookup" button.
    class DemoMarkersRegistry
    {
    private:
        // A ZoneBoundings specifies a rectangular bounding for the widgets whose code is given
        // *after* a call to IMGUI_DEMO_MARKER. This bounding will extend down to the next IMGUI_DEMO_MARKER macro call.
        // It always occupies the full width of the current window.
        struct ZoneBoundings
        {
            ZoneBoundings() : SourceLineNumber(-1), MinY(-1.0f), MaxY(-1.0f), Window(NULL) {}
            int SourceLineNumber; // Source code location
            float MinY, MaxY;     // Location of this zone inside its parent window
            ImGuiWindow* Window;  // Current window when IMGUI_DEMO_MARKER was called
        };

    public:
        DemoMarkersRegistry() :
            AllZonesBoundings(),
            PreviousZoneSourceLine(-1)
        {
        }

        // Highlight starts a demo marker zone.
        // If the highlight mode is active and the demo marker zone is hovered, it will highlight it,
        // display a tooltip and return true. Otherwise it will return false.
        bool IsMouveHoveringDemoMarker(int line_number)
        {
            // This will store the bounding for the next widgets, and this bounding will extend until the next call to DemoMarker
            StoreZoneBoundings(line_number);
            ZoneBoundings& zone_boundings = GetZoneBoundingsForLine(line_number);

            // Handle mouse and keyboard actions if the zone is hovered
            bool is_mouve_hovering_zone = IsMouseHoveringZoneBoundings(zone_boundings);
            if (! is_mouve_hovering_zone)
                return false;

            // Highlight was disabled in oct 2025:
            // not really useful for the end user. Can be useful for debugging.
            // HighlightZone(zone_boundings);

            return true;
        }

    private:
        void StoreZoneBoundings(int line_number)
        {
            // Store info about marker
            ZoneBoundings current_zone_boundings;
            {
                if (HasZoneBoundingsForLine(line_number))
                    current_zone_boundings = GetZoneBoundingsForLine(line_number);
                else
                    current_zone_boundings.SourceLineNumber = line_number;
            }

            // Store MinY position for current marker
            current_zone_boundings.Window = ImGui::GetCurrentWindow();
            current_zone_boundings.MinY = ImGui::GetCursorScreenPos().y;

            // Store current marker in list
            SetZoneBoundingsForLine(line_number, current_zone_boundings);

            // Store Max position for previous marker
            if (HasZoneBoundingsForLine(PreviousZoneSourceLine))
            {
                ZoneBoundings& previous_zone_boundings = GetZoneBoundingsForLine(PreviousZoneSourceLine);
                if (previous_zone_boundings.Window == ImGui::GetCurrentWindow())
                    previous_zone_boundings.MaxY = ImGui::GetCursorScreenPos().y;
            }

            PreviousZoneSourceLine = line_number;
        }

        bool IsMouseHoveringZoneBoundings(const ZoneBoundings& zone_boundings)
        {
            if (!ImGui::IsWindowHovered(ImGuiHoveredFlags_AllowWhenBlockedByActiveItem | ImGuiHoveredFlags_RootAndChildWindows | ImGuiHoveredFlags_NoPopupHierarchy))
                return false;
            float y_mouse = ImGui::GetMousePos().y;
            float x_mouse = ImGui::GetMousePos().x;
            return (
                (y_mouse >= zone_boundings.MinY)
                && ( (y_mouse < zone_boundings.MaxY) || (zone_boundings.MaxY < 0.f) )
                && ( (x_mouse >= ImGui::GetWindowPos().x) && ( x_mouse < ImGui::GetWindowPos().x + ImGui::GetWindowSize().x ))
            );
        }

        void HighlightZone(const ZoneBoundings zone_boundings)
        {
            // tl_dim / br_dim : top_left and bottom_right corners of the dimmed zone.
            ImVec2 tl_dim = ImGui::GetWindowPos();
            ImVec2 br_dim(ImGui::GetWindowPos().x + ImGui::GetWindowSize().x, ImGui::GetWindowPos().y + ImGui::GetWindowSize().y);

            // tl_zone / br_zone: top_left and bottom_right corner of the highlighted zone
            float minY = zone_boundings.MinY < ImGui::GetWindowPos().y ? ImGui::GetWindowPos().y : zone_boundings.MinY;
            ImVec2 tl_zone(ImGui::GetWindowPos().x, minY);
            float maxY = zone_boundings.MaxY > 0.f ? zone_boundings.MaxY : ImGui::GetWindowPos().y + ImGui::GetWindowHeight();
            ImVec2 br_zone(ImGui::GetWindowPos().x + ImGui::GetWindowWidth(), maxY);

            ImDrawList* draw_list = ImGui::GetForegroundDrawList();
            ImU32 dim_color = IM_COL32(127, 127, 127, 100);

            draw_list->AddRectFilled(tl_dim, ImVec2(br_dim.x, tl_zone.y), dim_color);

            draw_list->AddRectFilled(ImVec2(tl_dim.x, tl_zone.y), ImVec2(tl_zone.x, br_zone.y), dim_color);
            draw_list->AddRectFilled(ImVec2(br_zone.x, tl_zone.y), ImVec2(br_dim.x, br_zone.y), dim_color);

            draw_list->AddRectFilled(ImVec2(tl_dim.x, br_zone.y), ImVec2(br_dim.x, br_dim.y), dim_color);
        }

        bool HasZoneBoundingsForLine(int line_number)
        {
            for (int i = 0; i < AllZonesBoundings.size(); ++i)
                if (AllZonesBoundings[i].SourceLineNumber == line_number)
                    return true;
            return false;
        }

        ZoneBoundings& GetZoneBoundingsForLine(int line_number)
        {
            IM_ASSERT(HasZoneBoundingsForLine(line_number)); // Please call HasZoneBoundingsForLine before!
            for (int i = 0; i < AllZonesBoundings.size(); ++i)
            {
                ZoneBoundings& zone = AllZonesBoundings[i];
                if (zone.SourceLineNumber == line_number)
                    return zone;
            }

            IM_ASSERT(false);       // We should never get there!
            static ZoneBoundings dummy; return dummy; // Make the compiler happy
        }

        void SetZoneBoundingsForLine(int line_number, const ZoneBoundings& zone_boundings)
        {
            if (HasZoneBoundingsForLine(line_number))
            {
                ZoneBoundings& old_boundings = GetZoneBoundingsForLine(line_number);
                old_boundings = zone_boundings;
            }
            else
            {
                AllZonesBoundings.push_back(zone_boundings);
            }
        }

        // Members
        ImVector<ZoneBoundings> AllZonesBoundings;    // All boundings for all the calls to DEMO_MARKERS
        int PreviousZoneSourceLine;                   // Location of the previous call to DEMO_MARKERS (used to end the previous bounding)
    };
    static DemoMarkersRegistry GDemoMarkersRegistry;  // Global instance used by the IMGUI_DEMO_MARKER macro
} // namespace ImGuiDemoMarkerHighlight_Impl
bool DemoMarker_IsMouveHovering(int line_number)
{
    return ImGuiDemoMarkerZoneBoundings_Impl::GDemoMarkersRegistry.IsMouveHoveringDemoMarker(line_number);
}

// End of Demo code
