---
title: The ImGui Explorer, one question answered
defaults:
  over: 0.5
---
# The ImGui Explorer, one question answered

## Title

[[The title card; under it, the demo opens its plots]]
```cues
set_value("scene", "desktop")
set_value("card", "title")
set_value("card_alpha", 1.0)
click("item", "//Dear ImGui Demo/Widgets")
click("item", "//Dear ImGui Demo/**/Plotting")
wait(0.2)
```

## The question

[[The cursor goes over the animated plot: the code follows]]
```cues
animate("card_alpha", 0.0)
hover("item", "//Dear ImGui Demo/**/Lines", point=(0.2, 0.6))
hover("item", "//Dear ImGui Demo/**/Lines", point=(0.6, 0.4))
wait(0.5)
```
How is this plot made? Hover it: here is its code.

```cues
click("button", "python")
wait(1.0)
```
In C++, or in Python.

## The API

[[Hovering the function's name shows its signature; a right-click opens its card]]
```cues
hover("code_word", "plot_lines")
wait(1.3)
right_click("code_word", "plot_lines")
menu(API + "imgui.plot_lines")
wait(1.2)
```
A function? Hover it for its signature, right-click it for its documentation.

## Other libraries

[[ImPlot, ImPlot3D, ImAnim: a section opened in each, hovered (the code follows); the easings replayed]]
```cues
click("item", "**/ImPlot")
click("item", "//ImPlot Demo/**/Line Plots")
hover("item", "//ImPlot Demo/**/Line Plots", point=(0.5, 8.0))
wait(0.5)
click("item", "**/ImPlot3D")
click("item", "//ImPlot3D Demo/**/Line Plots")
hover("item", "//ImPlot3D Demo/**/Line Plots", point=(0.5, 9.0))
wait(0.5)
click("item", "**/ImAnim")
click("item", "//ImAnimDemos/**/Basic Animations")
click("item", "//ImAnimDemos/**/Easing Showcase")
click("item", "//ImAnimDemos/**/Restart")
wait(1.0)
```
The same for ImPlot, ImPlot3D and ImAnim.

## End

```cues
set_value("card", "end")
animate("card_alpha", 1.0)
wait(2.0)
```
