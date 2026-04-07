# Dev tools

Internal helpers for local development. Not shipped in any wheel or release.

## `dev_screenshot.py` + `dev_screenshot.h`

Programmatically capture a screenshot of an ImGui Bundle GUI for visual
validation. Lets developers (and AI assistants) verify a UI change without
launching a window manually and eyeballing it.

### Python helper

```python
import sys
sys.path.insert(0, "ci_scripts/dev_tools")
from dev_screenshot import take_screenshot

def my_gui():
    imgui.text("Hello")

png_path = take_screenshot(
    my_gui,
    "/tmp/out.png",
    window_size=(600, 400),
    with_latex=True,           # any immapp.run kwarg works
)
```

The function wraps `my_gui` in a frame counter, runs it for
`exit_after_frames` frames (default `8`), then sets `app_shall_exit`,
fetches `hello_imgui.final_app_window_screenshot()`, and saves it as PNG
via Pillow.

### C++ helper

`dev_screenshot.h` is a header-only equivalent. Drop a temporary
`.cpp` file into `bindings/imgui_bundle/demos_cpp/sandbox/` and the
existing `ibd_add_this_folder_auto_demos` glob will discover it on the
next `cmake .` reconfigure:

```cpp
// bindings/imgui_bundle/demos_cpp/sandbox/sandbox_shoot_xxx.cpp
#include "dev_screenshot.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"

int main()
{
    DevScreenshot::Options opts;
    opts.outputPath = "/tmp/out.png";
    opts.windowSize = ImVec2(900, 950);
    opts.withLatex  = true;

    return DevScreenshot::RunAndSave(
        [](){
            ImGuiMd::Render("Inline math: $E = mc^2$");
        },
        opts
    ) ? 0 : 1;
}
```

Then:
```bash
cmake builds/claude_python_bindings   # rediscover sandbox files
cmake --build builds/claude_python_bindings --target sandbox_shoot_xxx
./builds/claude_python_bindings/bin/sandbox_shoot_xxx.app/Contents/MacOS/sandbox_shoot_xxx
# delete the temp .cpp when done
```

### Why this exists

Until you can see the rendering, "the build succeeded" only proves the
code compiles, not that the UI is correct. With these helpers you can
take a screenshot, look at it, and be confident before pushing.

For Claude Code: see `.claude/skills/screenshot-imgui-bundle/SKILL.md`.
