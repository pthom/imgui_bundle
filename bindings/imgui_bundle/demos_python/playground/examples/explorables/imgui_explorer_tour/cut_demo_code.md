---
title: The ImGui Explorer, demo and code
defaults:
  over: 0.5
---
# The ImGui Explorer, demo and code

## Title

[[The title card; under it, the demo opens Widgets > Basic]]
```cues
set_value("scene", "desktop")
set_value("card", "title")
set_value("card_alpha", 1.0)
click("item", "//Dear ImGui Demo/Widgets")
click("item", "//Dear ImGui Demo/**/Basic")
wait(1.0)
```

## Hover

[[The card fades; the cursor hovers widgets: the code follows]]
```cues
animate("card_alpha", 0.0)
hover("item", "//Dear ImGui Demo/**/Button")
wait(0.7)
hover("item", "//Dear ImGui Demo/**/checkbox")
wait(0.5)
hover("item", "//Dear ImGui Demo/**/radio b")
wait(0.7)
```
Hover a widget in the demo: its code shows at the right.

## The breadcrumb

[[The wheel scrolls the code down to the Color section; the cursor rests on the breadcrumb, which follows]]
```cues
wheel("code", lines=-54, point=(0.85, 0.5))
hover("crumb", point=(1.4, 0.5))
wait(0.6)
```
Reading the code? The bar above it says where you are.

[["Show in the demo" opens the section in the demo; a color widget there, hovered]]
```cues
click("show_in_demo")
wait(0.8)
hover("item", "//Dear ImGui Demo/**/MyColor##1/##X")
wait(0.6)
```
One click, and the demo opens there.

## Python

```cues
click("button", "python")
wait(1.6)
```
C++ or Python: the same section, in either language.

## Phone

[[A fade to the phone; a finger on the color widget, then a tap on "Code": its code]]
```cues
animate("veil", 1.0, over=0.3)
set_value("scene", "phone", at=0.3)
animate("veil", 0.0, over=0.3, at=0.3)
wait(0.5)
hover("item", "//Dear ImGui Demo/**/MyColor##1/##X")
wait(0.3)
click("button", "switch", point=(0.75, 0.5))
wait(1.6)
```

## End

```cues
set_value("card", "end")
animate("card_alpha", 1.0)
wait(2.5)
```
