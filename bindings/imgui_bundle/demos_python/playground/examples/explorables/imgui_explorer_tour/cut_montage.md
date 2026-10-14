---
title: The ImGui Explorer, a montage
defaults:
  over: 0.5
---
# The ImGui Explorer, a montage

## Title

[[The title card; under it, the demo opens Widgets > Basic]]
```cues
set_value("scene", "desktop")
set_value("card", "title")
set_value("card_alpha", 1.0)
click("item", "//Dear ImGui Demo/Widgets")
click("item", "//Dear ImGui Demo/**/Basic")
wait(0.3)
```

## Features

[[Hover: the code follows]]
```cues
animate("card_alpha", 0.0)
hover("item", "//Dear ImGui Demo/**/Button")
wait(0.4)
hover("item", "//Dear ImGui Demo/**/checkbox")
wait(0.3)
```
Every demo, beside its code.

[[The breadcrumb opens the outline; its search finds the plots; Enter: the code and the demo go there]]
```cues
click("crumb")
type_keys("plot")
wait(0.3)
press("enter")
wait(0.4)
hover("item", "//Dear ImGui Demo/**/Lines", point=(0.5, 0.6))
wait(0.4)
```
Search a section: the code and the demo go there.

[[The API tab: a search, a card]]
```cues
click("item", API_TAB)
click("item", "**/##apifilter")
type_keys("slider")
wait(0.3)
click("item", "**/ImGui::SliderFloat##hit0")
wait(1.0)
```
The whole API, searchable.

```cues
click("button", "python")
wait(1.2)
```
In C++, or in Python.

## Other libraries

[[ImPlot, ImPlot3D, ImAnim: a section opened in each, hovered]]
```cues
click("item", "**/ImPlot")
click("item", "//ImPlot Demo/**/Line Plots")
hover("item", "//ImPlot Demo/**/Line Plots", point=(0.5, 8.0))
wait(0.3)
click("item", "**/ImPlot3D")
click("item", "//ImPlot3D Demo/**/Line Plots")
hover("item", "//ImPlot3D Demo/**/Line Plots", point=(0.5, 9.0))
wait(0.3)
click("item", "**/ImAnim")
click("item", "//ImAnimDemos/**/Basic Animations")
click("item", "//ImAnimDemos/**/Easing Showcase")
click("item", "//ImAnimDemos/**/Restart")
wait(0.6)
```
ImPlot, ImPlot3D and ImAnim too.

## Phone

[[A fade to the phone; a tap on "Code"]]
```cues
animate("veil", 1.0, over=0.3)
set_value("scene", "phone", at=0.3)
animate("veil", 0.0, over=0.3, at=0.3)
wait(0.6)
click("button", "switch", point=(0.75, 0.5))
wait(1.2)
```

## End

```cues
set_value("card", "end")
animate("card_alpha", 1.0)
wait(2.0)
```
