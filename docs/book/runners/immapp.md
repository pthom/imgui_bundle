# ImmApp - Immediate App

ImGui Bundle includes a library named ImmApp (which stands for Immediate App). ImmApp is a thin extension of HelloImGui that enables to easily initialize the ImGuiBundle addons that require additional setup at startup

## API

* [C++ API](https://github.com/pthom/imgui_bundle/tree/main/external/immapp/immapp/runner.h)-
* [Python API](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/immapp/immapp_cpp.pyi)

## How to start an application with addons

Some libraries included by ImGui Bundle require an initialization at startup. ImmApp makes this easy via AddOnParams.

The example program below demonstrates how to run an application which will use implot (which requires a context to be created at startup), and imgui_md (which requires additional fonts to be loaded at startup).

::::{tab-set}
:::{tab-item} Python
```python
import numpy as np
# imgui_bundle is a package that provides several imgui-related submodules
from imgui_bundle import (imgui,       # first we import ImGui
                          implot,      # ImPlot provides advanced real-time plotting
                          imgui_md,    # imgui_md: markdown rendering for imgui
                          hello_imgui, # hello_imgui: starter pack for imgui apps
                          immapp,      # helper to activate addons (like implot, markdown, etc.)
                          )

def gui():
    # Render some markdown text
    imgui_md.render_unindented("""
    # Render an animated plot with ImPlot
    This example shows how to use `ImPlot` to render an animated plot,
    and how to use `imgui_md` to render markdown text (*this text!*).
    """)

    # Render an animated plot
    if implot.begin_plot(
            title_id="Plot",
            # size in em units (1em = height of a character)
            size=hello_imgui.em_to_vec2(40, 20)):
        x = np.arange(0, np.pi * 4, 0.01)
        y = np.cos(x + imgui.get_time())
        implot.plot_line("y1", x, y)
        implot.end_plot()

    if imgui.button("Exit"):
        hello_imgui.get_runner_params().app_shall_exit = True


def main():
    # This call is specific to the ImGui Bundle interactive manual.
    from imgui_bundle.demos_python import demo_utils
    demo_utils.set_hello_imgui_demo_assets_folder()

    # Run the app with ImPlot and markdown support
    immapp.run(gui,
               with_implot=True,
               with_markdown=True,
               window_size=(700, 500))


if __name__ == "__main__":
    main()
```
:::

:::{tab-item} C++
```cpp
#include "immapp/immapp.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "implot/implot.h"
#include "demo_utils/api_demos.h"
#include <vector>
#include <cmath>


int main(int, char**)
{
    constexpr double pi = 3.1415926535897932384626433;
    std::vector<double> x, y1, y2;
    for (double _x = 0; _x < 4 * pi; _x += 0.01)
    {
        x.push_back(_x);
        y1.push_back(std::cos(_x));
        y2.push_back(std::sin(_x));
    }

    auto gui = [x,y1,y2]()
    {
        ImGuiMd::Render("# This is the plot of _cosinus_ and *sinus*");  // Markdown
        if (ImPlot::BeginPlot("Plot"))
        {
            ImPlot::PlotLine("y1", x.data(), y1.data(), x.size());
            ImPlot::PlotLine("y2", x.data(), y2.data(), x.size());
            ImPlot::EndPlot();
        }
    };

    HelloImGui::SimpleRunnerParams runnerParams { .guiFunction = gui, .windowSize = {600, 400} };
    ImmApp::AddOnsParams addons { .withImplot = true, .withMarkdown = true };
    ImmApp::Run(runnerParams, addons);

    return 0;
}
```
:::
::::
