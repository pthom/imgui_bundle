"""Add IMGUI_DEMO_MARKER at the start of each Demo_ function in implot_demo.cpp.

Uses the DemoHeader label as the section name.
For Demo_Config and Demo_Help (called directly, not via DemoHeader), uses the tab name.

Usage: python add_implot_markers.py <implot_demo.cpp>
"""
import re
import sys

# Map from function name to section name (from DemoHeader calls and tab names)
FUNC_TO_SECTION = {
    # Plots tab
    "Demo_LinePlots":       "Plots/Line Plots",
    "Demo_FilledLinePlots": "Plots/Filled Line Plots",
    "Demo_ShadedPlots":     "Plots/Shaded Plots",
    "Demo_ScatterPlots":    "Plots/Scatter Plots",
    "Demo_RealtimePlots":   "Plots/Realtime Plots",
    "Demo_StairstepPlots":  "Plots/Stairstep Plots",
    "Demo_BarPlots":        "Plots/Bar Plots",
    "Demo_BarGroups":       "Plots/Bar Groups",
    "Demo_BarStacks":       "Plots/Bar Stacks",
    "Demo_ErrorBars":       "Plots/Error Bars",
    "Demo_StemPlots":       "Plots/Stem Plots",
    "Demo_InfiniteLines":   "Plots/Infinite Lines",
    "Demo_PieCharts":       "Plots/Pie Charts",
    "Demo_Heatmaps":        "Plots/Heatmaps",
    "Demo_Histogram":       "Plots/Histogram",
    "Demo_Histogram2D":     "Plots/Histogram 2D",
    "Demo_DigitalPlots":    "Plots/Digital Plots",
    "Demo_Images":          "Plots/Images",
    "Demo_MarkersAndText":  "Plots/Markers and Text",
    "Demo_NaNValues":       "Plots/NaN Values",
    # Subplots tab
    "Demo_SubplotsSizing":      "Subplots/Sizing",
    "Demo_SubplotItemSharing":  "Subplots/Item Sharing",
    "Demo_SubplotAxisLinking":  "Subplots/Axis Linking",
    "Demo_Tables":              "Subplots/Tables",
    # Axes tab
    "Demo_LogScale":            "Axes/Log Scale",
    "Demo_SymmetricLogScale":   "Axes/Symmetric Log Scale",
    "Demo_TimeScale":           "Axes/Time Scale",
    "Demo_CustomScale":         "Axes/Custom Scale",
    "Demo_MultipleAxes":        "Axes/Multiple Axes",
    "Demo_TickLabels":          "Axes/Tick Labels",
    "Demo_LinkedAxes":          "Axes/Linked Axes",
    "Demo_AxisConstraints":     "Axes/Axis Constraints",
    "Demo_EqualAxes":           "Axes/Equal Axes",
    "Demo_AutoFittingData":     "Axes/Auto-Fitting Data",
    # Tools tab
    "Demo_OffsetAndStride":     "Tools/Offset and Stride",
    "Demo_DragPoints":          "Tools/Drag Points",
    "Demo_DragLines":           "Tools/Drag Lines",
    "Demo_DragRects":           "Tools/Drag Rects",
    "Demo_Querying":            "Tools/Querying",
    "Demo_Annotations":         "Tools/Annotations",
    "Demo_Tags":                "Tools/Tags",
    "Demo_DragAndDrop":         "Tools/Drag and Drop",
    "Demo_LegendOptions":       "Tools/Legend Options",
    "Demo_LegendPopups":        "Tools/Legend Popups",
    "Demo_ColormapWidgets":     "Tools/Colormap Widgets",
    # Custom tab
    "Demo_CustomStyles":                "Custom/Custom Styles",
    "Demo_CustomDataAndGetters":        "Custom/Custom Data and Getters",
    "Demo_CustomRendering":             "Custom/Custom Rendering",
    "Demo_CustomPlottersAndTooltips":   "Custom/Custom Plotters and Tooltips",
    # Direct calls
    "Demo_Config": "Config",
    "Demo_Help":   "Help",
}

def process(lines):
    # Match: void Demo_Xxx() {  or  void Demo_Xxx()  {
    func_re = re.compile(r'^void (Demo_\w+)\(\)\s*\{?\s*$')
    result = []
    i = 0
    while i < len(lines):
        m = func_re.match(lines[i])
        if m:
            func_name = m.group(1)
            section = FUNC_TO_SECTION.get(func_name)
            if section:
                # Check if next non-blank line already has IMGUI_DEMO_MARKER
                j = i + 1
                while j < len(lines) and lines[j].strip() == '':
                    j += 1
                if j < len(lines) and 'IMGUI_DEMO_MARKER' in lines[j]:
                    # Already has a marker, skip
                    result.append(lines[i])
                    i += 1
                    continue
                # Emit function line
                result.append(lines[i])
                # If brace is on next line, emit it first
                if '{' not in lines[i] and i + 1 < len(lines) and lines[i+1].strip() == '{':
                    i += 1
                    result.append(lines[i])
                result.append(f'    IMGUI_DEMO_MARKER("{section}");\n')
                i += 1
                continue
        result.append(lines[i])
        i += 1
    return result

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file.cpp>")
        sys.exit(1)
    path = sys.argv[1]
    with open(path) as f:
        lines = f.readlines()
    out = process(lines)
    with open(path, 'w') as f:
        f.writelines(out)
    # Report
    added = len(out) - len(lines)
    print(f"Processed {path}: added {added} marker(s)")

if __name__ == '__main__':
    main()
