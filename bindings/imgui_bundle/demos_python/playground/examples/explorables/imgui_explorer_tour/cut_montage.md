---
title: The ImGui Explorer, a montage
defaults:
  over: 0.5
---
# The ImGui Explorer, a montage

## Title

[[The title card; under it, the demo opens its color picker (fast: unseen)]]
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

[[The cursor plays with the color picker: the code follows]]
```cues
animate("card_alpha", 0.0)
hover("item", "//Dear ImGui Demo/**/MyColor##4/sv", point=(0.7, 0.4))
hover("item", "//Dear ImGui Demo/**/MyColor##4/hue", point=(0.5, 0.6))
hover("item", "//Dear ImGui Demo/**/MyColor##4/sv", point=(0.5, 0.75))
wait(0.3)
```
Hover any demo: here is its code.

[[ImPlot; the outline's search: the colorful plots; the bubbles open, in the demo and in the code]]
```cues
click("item", "**/ImPlot")
click("crumb")
type_keys("color")
wait(0.5)
click("item", "//$FOCUSED/Colorful Bubbles##Colorful Bubbles")
wait(0.8)
```
How do I plot with colors?

[[A function of the code: its signature on hover, its card on a right-click]]
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

[[The API tab's search: a name, its card]]
```cues
click("item", "**/##apifilter")
type_keys("SampleColormap")
wait(0.3)
click("item", "**/ImPlot::SampleColormap##hit0")
wait(0.8)
```
The whole API, searchable.

```cues
click("button", "python")
wait(1.2)
```
In C++, or in Python.

## In 3D

[[ImPlot3D; the outline's search: the surfaces; the demo scrolls to the surface]]
```cues
click("item", "**/ImPlot3D")
click("crumb")
type_keys("surf")
wait(0.3)
press("enter")
wait(0.6)
wheel("item", "//ImPlot3D Demo/**/Custom range", lines=-10)
wait(0.6)
```
And in 3D?

## Phone

[[A fade to the phone, Dear ImGui's manual; under the veil, its Basic widgets open (fast). A finger ticks the checkbox, drags a slider, taps "Code" (fast: a finger lifts, it does not slide over the demo): the slider's code, scrolled past its indentation]]
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
wait(0.4)
wheel("code", lines=0, columns=-2, point=(0.5, 0.45))
wait(0.6)
```

## End

```cues
set_value("card", "end")
animate("card_alpha", 1.0)
wait(1.5)
```
