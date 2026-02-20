# Todo: Refactor imgui_manual for multiple Libraries, and integrate it into imgui_bundle

This is a to-do list which contains tasks inspired by from the plan.
The items here are used in the short term: this file changes quickly.

## Triage
<!-- Dump new ideas and discoveries here before classifying them. -->
- pyodide wheels: remove demo_assets, demo_cpp, demos_python

## Todo
<!-- Notation: [ ] pending, [~] in progress, [x] done, [N] won't do -->

- [ ] immvision disabled in emscripten demo! It seems that the emscripten compil does not include OpenCV anymore by default (see ems_builmd.sh).
- [ ] Update bundle book and documentation
- [ ] Add doc for ImAnim in the bundle book (compare C++ and Python API, esp enum usage)

- [x] Add imgui/implot[3d]/imanim manual in bundle interactive manual:
- [x] specify default python or C++ for ShowImGuiManualGui
- [x] add python demos
- [x] add full python demos also (for implot, implot3d, and imanim)
- [x] fix imgui_demo.py :
- [x] add menu bars to all demos py
- [x] "Code for this demo": only on selected demos
- [x] Add link to imgui_manual in imgui_manual for imgui
- [x] Fix choice lib in emscripten
- [x] Can't switch between C++ and Python!
- [x] "Code for this demo" => fail in emscripten
- [x] publish imgui_bundle_demo
- [x] fix CI errors

