# Spec: Refactor imgui_manual for multiple Libraries, and integrate it into imgui_bundle

## Goal

ImGui manual is a standalone project which gives an interactive manual for only dear ImGui: As soon as you look at a widget's demonstration, you can see its code in the code editor to the right.

The goal is to refactor this manual so that it can give an interactive manual for multiple libraries: imgui, implot, implot3d, imanim.
After careful evaluation it was decided to integrate this manual into the imgui_bundle repository, so that it can be easily maintained and updated together with the libraries.

This manual will be available:
- as a standalone manual: a replacement for the current imgui_manual (will replace the [current manual for ImGui] https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html)
- as a standalone manual for each library: implot, implot3d, imanim
- as a composed manual for all libraries: a single manual that includes all libraries, with a navigation system to switch between them.
- as a part of the imgui_bundle interactive manual: integrated into interactive manual of imgui_bundle, with tabs that show specific parts of the standalone manuals.

## Context

The existing manual is located at:
https://github.com/pthom/imgui_manual
https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html

It is a quite useful, and some user do visit regularly. Approx 40000 visits per year. 
I do have a counter with goatcounter. We might want to move it to the new manual someday.

## Requirements
<!-- What must be true when this is done? -->
-
-

## Non-goals
...

## Open questions
None at the moment.