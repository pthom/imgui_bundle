---
title: The ImGui Explorer, a montage
defaults:
  over: 0.5
---
# The ImGui Explorer, a montage

[[How to read this file. It is the script of a 30-second video of the ImGui Explorer. A small Python player, "narrator", plays it over the real explorer, which runs in Dear ImGui Bundle's Python bindings.]]

[[Each "##" heading is a scene. A plain paragraph is a subtitle: shown at the bottom of the frame for its reading time. A line in double brackets, like this one, is a note for the reader: the player ignores it.]]

[[A "cues" block is Python, run once when the script loads: each call records an event on the timeline. set_value and animate are keyframes of the program's parameters (the scene, a card, a veil). The other calls are gestures: the Dear ImGui Test Engine moves the mouse, clicks and types, as a user would.]]

[[A gesture's target is a Test Engine reference, like "//Dear ImGui Demo/**/Button" (the "**/" searches the window's items), or a name that the program turns into a rectangle on screen: "code", "code_word", "button". A subtitle stays on screen until its gestures end.]]

[[The video: python imgui_explorer_tour.py cut_montage.md --video out.mp4. The window is 960 x 540 points, 1920 x 1080 pixels on a Retina screen. The Test Engine's fixed delta time makes each frame last 1/30 s of video, however long it takes to draw. Each frame is read before the swap and piped to ffmpeg. The subtitles are drawn by Dear ImGui too, in the foreground draw list. A 30-second video takes about 10 seconds to record.]]

## Title

[[The title card: a dark veil and two lines of text, drawn over the explorer. Under it, unseen, the demo opens its color picker. "fast=True" plays a gesture at the Test Engine's fast speed: a setup the viewer does not see.]]
```cues
set_value("scene", "desktop")
set_value("card", "title")
set_value("card_alpha", 1.0)
click("item", "//Dear ImGui Demo/Widgets", fast=True)
click("item", "//Dear ImGui Demo/**/Color\\/Picker Widgets", fast=True)
hover("item", "//Dear ImGui Demo/**/MyColor##4/sv", point=(0.3, 0.3), fast=True)
wait(1.0)
```

## Features

[[The card fades out in half a second. The cursor moves over the color picker's square and hue bar. The explorer's "Follow source" shows the code of the hovered widget: the demo marks its sections with IMGUI_DEMO_MARKER, and the explorer jumps to the marker of the section under the mouse.]]
```cues
animate("card_alpha", 0.0)
hover("item", "//Dear ImGui Demo/**/MyColor##4/sv", point=(0.7, 0.4))
hover("item", "//Dear ImGui Demo/**/MyColor##4/hue", point=(0.5, 0.6))
hover("item", "//Dear ImGui Demo/**/MyColor##4/sv", point=(0.5, 0.75))
wait(0.3)
```
Hover any demo: here is its code.

[[ImPlot. The "Search the demos" field, at the top of the demo pane, opens the demo's outline with a search, over the field like a dropdown. "color" lists the colorful plots. A click on Colorful Bubbles opens that section in the demo, and shows its code.]]
```cues
click("item", "**/ImPlot")
click("item", "**/###search_demos")
type_keys("color")
wait(0.5)
click("item", "**/Colorful Bubbles##Colorful Bubbles")
wait(0.8)
```
How do I plot with colors?

[[One wheel step down the code, then the mouse rests on PlotBubbles: a tooltip shows its signature. A right-click, then "API: ImPlot::PlotBubbles": its card, in the API tab. The word's place on screen comes from the explorer itself (GetImGuiExplorerCodeTextRect, a function for tours and tests).]]
```cues
wheel("code", lines=-1, point=(0.85, 0.5))
wait(0.3)
hover("code_word", "PlotBubbles")
wait(1.2)
right_click("code_word", "PlotBubbles")
menu(API + "ImPlot::PlotBubbles")
wait(1.0)
```
A function? Its signature, and its documentation.

[[The API tab searches the whole API, by its C++ or Python names. A card shows the signature, the doc, and links to the online doc and to the declaration in the header. The index behind it is generated from the bindings' stubs.]]
```cues
click("item", "**/##apifilter")
type_keys("SampleColormap")
wait(0.3)
click("item", "**/ImPlot::SampleColormap##hit0")
wait(0.8)
```
The whole API, searchable.

[[The Python logo: the same card in Python, with the C++ name under it. The code view would show the same section in Python too: the bundle's demos have a Python port, section by section.]]
```cues
click("button", "python")
wait(1.2)
```
In C++, or in Python.

## In 3D

[[ImPlot3D: the same search, "surf". The cursor goes to the section's entry in the demo, away from the field (its tooltip would show when the popup closes), then Enter takes the first match. The demo opens the section. Then 3 wheel steps show the whole surface: a number tuned for this window's size.]]
```cues
click("item", "**/ImPlot3D")
click("item", "**/###search_demos")
type_keys("surf")
wait(0.3)
hover("item", "//ImPlot3D Demo/**/Surface Plots")
press("enter")
wait(0.3)
wheel("item", "//ImPlot3D Demo/**/Custom range", lines=-3)
wait(1.2)
```
And in 3D?

## Phone

[[A veil fades to black, the scene becomes the phone, and the veil fades back. The phone is the same explorer, drawn in a child window of a phone's size, with its own zoom (style.FontScaleMain). The explorer sees a narrow window and shows one pane at a time, as on a real phone. The program draws the bezel, the status bar and the finger.]]

[[Under the veil, unseen: the explorer shows the Dear ImGui manual alone, and its Basic widgets open. Then a finger ticks the checkbox and drags a slider. Its tap on "Code" is fast: a finger lifts, it does not slide over the demo, where the code would follow every widget it crossed.]]

[[On a phone, the code view drops its line numbers, uses a smaller font than the rest, and scrolls past the indentation that the lines in view share.]]
```cues
animate("veil", 1.0, over=0.25)
set_value("scene", "phone", at=0.25)
wait(0.3)
click("item", "//Dear ImGui Demo/**/Basic", fast=True)
hover("item", "//Dear ImGui Demo/**/checkbox", fast=True)
animate("veil", 0.0, over=0.3, at=1.0)
wait(0.5)
click("item", "//Dear ImGui Demo/**/checkbox")
drag("item", "//Dear ImGui Demo/**/slider float", start=(0.15, 0.5), end=(0.85, 0.5))
click("button", "switch", point=(0.75, 0.5), fast=True)
wait(1.0)
```

## End

[[The end card fades in, and the video ends a second and a half later.]]
```cues
set_value("card", "end")
animate("card_alpha", 1.0)
wait(1.5)
```
