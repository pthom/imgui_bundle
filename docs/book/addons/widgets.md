# Widgets

Dear ImGui Bundle includes a variety of additional widgets beyond the standard ImGui set.

## Full Demo

::::{card}
:link: https://traineq.org/ImGuiBundle/emscripten/bin/demo_widgets.html
```{figure} ../images/demo_widgets.webp
:width: 350
Widgets demo showcasing knobs, toggles, spinners, coolbar, and more.
```
::::

[Try online](https://traineq.org/ImGuiBundle/emscripten/bin/demo_widgets.html) | [Python](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demo_widgets.py) | [C++](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demo_widgets.cpp)


## imgui-knobs - Rotary Knobs

### Introduction

[imgui-knobs](https://github.com/altschuler/imgui-knobs) adds rotary knob widgets similar to those found in audio software.

::::{card}
:link: https://github.com/altschuler/imgui-knobs
```{figure} https://user-images.githubusercontent.com/956928/164050142-96a8dde4-7d2e-43e4-9afe-14ab48eac243.png
:width: 350
imgui-knobs: rotary knobs with multiple visual styles.
```
::::

**Knob variants:** `tick`, `dot`, `wiper`, `wiper_only`, `stepped`

### Quick Example

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import imgui_knobs, immapp

value = 50.0

def gui():
    global value
    changed, value = imgui_knobs.knob("Volume", value, 0.0, 100.0)

immapp.run(gui)
```
:::

:::{tab-item} C++
```cpp
#include "immapp/immapp.h"
#include "imgui-knobs/imgui-knobs.h"

float value = 50.0f;

void gui() {
    ImGuiKnobs::Knob("Volume", &value, 0.0f, 100.0f);
}

int main() {
    ImmApp::Run(gui, "Knobs Demo", {400, 300});
    return 0;
}
```
:::

::::

### Documented APIs

- **Python:** [imgui_knobs.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui_knobs.pyi)
- **C++:** [imgui-knobs.h](https://github.com/altschuler/imgui-knobs/blob/main/imgui-knobs.h)


## imgui_toggle - Toggle Switches

### Introduction

[imgui_toggle](https://github.com/cmdwtf/imgui_toggle) provides iOS-style toggle switches.

::::{card}
:link: https://github.com/cmdwtf/imgui_toggle
```{figure} https://github.com/cmdwtf/imgui_toggle/raw/main/.meta/imgui_toggle_example.gif
:width: 350
imgui_toggle: iOS-style toggle switches with animations.
```
::::

### Quick Example

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import imgui_toggle, immapp

enabled = False

def gui():
    global enabled
    changed, enabled = imgui_toggle.toggle("Enable feature", enabled)

immapp.run(gui)
```
:::

:::{tab-item} C++
```cpp
#include "immapp/immapp.h"
#include "imgui_toggle/imgui_toggle.h"

bool enabled = false;

void gui() {
    ImGui::Toggle("Enable feature", &enabled);
}

int main() {
    ImmApp::Run(gui, "Toggle Demo", {400, 300});
    return 0;
}
```
:::

::::

### Documented APIs

- **Python:** [imgui_toggle.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui_toggle.pyi)
- **C++:** [imgui_toggle.h](https://github.com/cmdwtf/imgui_toggle/blob/main/imgui_toggle.h)


## imspinner - Loading Spinners

### Introduction

[imspinner](https://github.com/dalerank/imspinner) provides a large collection of animated loading spinners.


:::{tip}
Call `imspinner.demo_spinners()` (Python) or `ImSpinner::demoSpinners()` (C++) to see all available spinner types.
:::

### Quick Example

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import imspinner, imgui, immapp

def gui():
    imspinner.spinner_ang_triple(
        "spinner",
        radius1=16, radius2=13, radius3=10,
        thickness=3,
        c1=imgui.ImColor(255, 255, 255),
        c2=imgui.ImColor(255, 100, 100),
        c3=imgui.ImColor(100, 100, 255)
    )

immapp.run(gui)
```
:::

:::{tab-item} C++
```cpp
#include "immapp/immapp.h"
#include "imspinner/imspinner.h"

void gui() {
    ImSpinner::SpinnerAngTriple(
        "spinner",
        16, 13, 10,  // radii
        3,           // thickness
        ImColor(255, 255, 255),
        ImColor(255, 100, 100),
        ImColor(100, 100, 255)
    );
}

int main() {
    ImmApp::Run(gui, "Spinner Demo", {400, 300});
    return 0;
}
```
:::

::::

### Documented APIs

- **Python:** [imspinner.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imspinner.pyi)
- **C++:** [imspinner.h](https://github.com/dalerank/imspinner/blob/master/imspinner.h)


## ImCoolBar - macOS-style Dock Bar

### Introduction

[ImCoolBar](https://github.com/aiekick/ImCoolBar) creates a macOS-style dock bar with magnification effect on hover.

::::{card}
:link: https://github.com/aiekick/ImCoolBar
```{figure} https://github.com/aiekick/ImCoolBar/raw/DemoApp/doc/DemoApp.gif
:width: 350
ImCoolBar: macOS-style dock bar with magnification effect.
```
::::

### Documented APIs

- **Python:** [im_cool_bar.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/im_cool_bar.pyi)
- **C++:** [ImCoolbar.h](https://github.com/aiekick/ImCoolBar/blob/master/ImCoolbar.h)


## imgui-command-palette - VSCode-style Command Palette

### Introduction

[imgui-command-palette](https://github.com/hnOsmium0001/imgui-command-palette) adds a Sublime Text / VSCode style command palette.

::::{card}
:link: https://github.com/hnOsmium0001/imgui-command-palette
```{figure} https://user-images.githubusercontent.com/36975818/146656302-646eccfd-6bf4-4ad0-80e0-239c7766210a.png
:width: 350
imgui-command-palette: VSCode-style command palette.
```
::::

### Full Demo

[Try online](https://traineq.org/ImGuiBundle/emscripten/bin/demo_command_palette.html) | [Python](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_python/demos_immapp/demo_command_palette.py) | [C++](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/demos_cpp/demos_immapp/demo_command_palette.cpp)

### Documented APIs

- **Python:** [imgui_command_palette.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui_command_palette.pyi)
- **C++:** [imcmd_command_palette.h](https://github.com/hnOsmium0001/imgui-command-palette/blob/master/imcmd_command_palette.h)


## File Dialogs

Dear ImGui Bundle provides two file dialog libraries.

### portable-file-dialogs

[portable-file-dialogs](https://github.com/samhocevar/portable-file-dialogs) uses native OS dialogs for file selection, notifications, and messages.

::::{card}
:link: https://github.com/samhocevar/portable-file-dialogs
```{figure} https://user-images.githubusercontent.com/245089/47155865-0f8cd900-d2e6-11e8-8041-1e20b6f77dee.png
:width: 350
portable-file-dialogs: native OS dialogs on all platforms.
```
::::

:::{note}
On **Emscripten/Web**, only message dialogs (with an OK button and icon) are supported since native file dialogs are unavailable. On **Windows, Linux, and macOS**, all features work fully.
:::

#### Quick Example

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import portable_file_dialogs as pfd

# Open file dialog (native OS)
selection = pfd.open_file("Select a file", ".", ["Image Files", "*.png *.jpg"])

# Message box
pfd.message("Title", "Message content", pfd.choice.ok, pfd.icon.info)
```
:::

:::{tab-item} C++
```cpp
#include "portable-file-dialogs/portable-file-dialogs.h"

// Open file dialog (native OS)
auto selection = pfd::open_file("Select a file", ".",
    {"Image Files", "*.png *.jpg"}).result();

// Message box
pfd::message("Title", "Message content", pfd::choice::ok, pfd::icon::info);
```
:::

::::

#### Documented APIs

- **Python:** [portable_file_dialogs.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/portable_file_dialogs.pyi)
- **C++:** [portable-file-dialogs.h](https://github.com/samhocevar/portable-file-dialogs/blob/master/portable-file-dialogs.h)



### ImFileDialog

[ImFileDialog](https://github.com/dfranx/ImFileDialog) is a file dialog library with a modern look.

::::{card}
:link: https://github.com/dfranx/ImFileDialog
```{figure} https://user-images.githubusercontent.com/30801537/107225799-8e5b3200-6a19-11eb-9847-ca2606205402.png
:width: 350
ImFileDialog: modern file dialog with preview support.
```
::::

:::{warning}
Consider using **portable-file-dialogs** instead, which provides native OS dialogs on each platform plus notifications and messages.

**Known limitations of ImFileDialog:**
- Not adapted for High DPI resolution under Windows
- No support for multi-selection
- Will not work under Python with a pure Python backend (requires `immapp.run()`)
:::

#### Quick Example

::::{tab-set}

:::{tab-item} Python
```python
from imgui_bundle import im_file_dialog as ifd, imgui, immapp

def gui():
    if imgui.button("Open File"):
        ifd.FileDialog.instance().open(
            "OpenFile", "Open a file", "Image files (*.png;*.jpg){.png,.jpg},.*"
        )

    if ifd.FileDialog.instance().is_done("OpenFile"):
        if ifd.FileDialog.instance().has_result():
            result = ifd.FileDialog.instance().get_result()
            print(f"Selected: {result}")
        ifd.FileDialog.instance().close()

immapp.run(gui)
```
:::

:::{tab-item} C++
```cpp
#include "immapp/immapp.h"
#include "ImFileDialog/ImFileDialog.h"

void gui() {
    if (ImGui::Button("Open File")) {
        ifd::FileDialog::Instance().Open(
            "OpenFile", "Open a file", "Image files (*.png;*.jpg){.png,.jpg},.*"
        );
    }

    if (ifd::FileDialog::Instance().IsDone("OpenFile")) {
        if (ifd::FileDialog::Instance().HasResult()) {
            auto result = ifd::FileDialog::Instance().GetResult();
            printf("Selected: %s\n", result.string().c_str());
        }
        ifd::FileDialog::Instance().Close();
    }
}

int main() {
    ImmApp::Run(gui, "File Dialog", {800, 600});
    return 0;
}
```
:::

::::

#### Documented APIs

- **Python:** [im_file_dialog.pyi](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/im_file_dialog.pyi)
- **C++:** [ImFileDialog.h](https://github.com/pthom/ImFileDialog/blob/imgui_bundle/ImFileDialog.h)


