"""Add IMGUI_DEMO_MARKER to implot3d_demo.cpp.

1. Adds the #ifndef IMGUI_DEMO_MARKER guard near the top
2. Adds IMGUI_DEMO_MARKER("Tab/Label") at the start of each Demo function

Usage: python add_implot3d_markers.py <implot3d_demo.cpp>
"""
import re
import sys

# Map from function name to section name (from DemoHeader calls)
FUNC_TO_SECTION = {
    # Plots tab - Plot Types
    "DemoLinePlots":        "Plots/Line Plots",
    "DemoScatterPlots":     "Plots/Scatter Plots",
    "DemoTrianglePlots":    "Plots/Triangle Plots",
    "DemoQuadPlots":        "Plots/Quad Plots",
    "DemoSurfacePlots":     "Plots/Surface Plots",
    "DemoMeshPlots":        "Plots/Mesh Plots",
    "DemoRealtimePlots":    "Plots/Realtime Plots",
    "DemoImagePlots":       "Plots/Image Plots",
    # Plots tab - Plot Options
    "DemoPlotFlags":        "Plots/Plot Flags",
    "DemoOffsetAndStride":  "Plots/Offset and Stride",
    "DemoLegendOptions":    "Plots/Legend Options",
    "DemoMarkersAndText":   "Plots/Markers and Text",
    "DemoNaNValues":        "Plots/NaN Values",
    # Axes tab
    "DemoBoxScale":         "Axes/Box Scale",
    "DemoBoxRotation":      "Axes/Box Rotation",
    "Demo_LogScale":        "Axes/Log Scale",
    "Demo_SymmetricLogScale": "Axes/Symmetric Log Scale",
    "DemoTickLabels":       "Axes/Tick Labels",
    "DemoAxisConstraints":  "Axes/Axis Constraints",
    "DemoEqualAxes":        "Axes/Equal Axes",
    "DemoAutoFittingData":  "Axes/Auto-Fitting Data",
    # Tools tab
    "DemoMousePicking":     "Tools/Mouse Picking",
    # Custom tab
    "DemoCustomStyles":         "Custom/Custom Styles",
    "DemoCustomRendering":      "Custom/Custom Rendering",
    "DemoCustomOverlay":        "Custom/Custom Overlay",
    "DemoCustomPerPointStyle":  "Custom/Custom Per-Point Style",
    # Direct calls
    "DemoConfig": "Config",
    "DemoHelp":   "Help",
}

MARKER_GUARD = """\
// IMGUI_DEMO_MARKER can be used to mark sections of the demo and link them to an interactive code browser.
// In order to use it, define it to an actual macro via force-include.
#ifndef IMGUI_DEMO_MARKER
#define IMGUI_DEMO_MARKER(section)  // Called everywhere in the code to mark interesting sections for the reader.
#endif

"""


def process(lines):
    func_re = re.compile(r'^void (Demo\w+)\(\)\s*\{?\s*$')
    result = []
    guard_added = False
    i = 0
    while i < len(lines):
        # Add marker guard after the last #include line
        if not guard_added and lines[i].startswith('#include') and (i + 1 >= len(lines) or not lines[i+1].startswith('#include')):
            result.append(lines[i])
            result.append('\n')
            result.append(MARKER_GUARD)
            guard_added = True
            i += 1
            continue

        m = func_re.match(lines[i])
        if m:
            func_name = m.group(1)
            section = FUNC_TO_SECTION.get(func_name)
            if section:
                # Check if already has marker
                j = i + 1
                while j < len(lines) and lines[j].strip() == '':
                    j += 1
                if j < len(lines) and 'IMGUI_DEMO_MARKER' in lines[j]:
                    result.append(lines[i])
                    i += 1
                    continue
                # Emit function line
                result.append(lines[i])
                # Handle Allman braces
                if '{' not in lines[i] and i + 1 < len(lines) and lines[i+1].strip() == '{':
                    i += 1
                    result.append(lines[i])
                result.append(f'    IMGUI_DEMO_MARKER("{section}");\n')
                i += 1
                continue
        result.append(lines[i])
        i += 1

    if not guard_added:
        print("WARNING: Could not find insertion point for IMGUI_DEMO_MARKER guard")

    return result


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <implot3d_demo.cpp>")
        sys.exit(1)
    path = sys.argv[1]
    with open(path) as f:
        lines = f.readlines()
    out = process(lines)
    with open(path, 'w') as f:
        f.writelines(out)
    added = len(out) - len(lines)
    print(f"Processed {path}: added {added} line(s)")


if __name__ == '__main__':
    main()
