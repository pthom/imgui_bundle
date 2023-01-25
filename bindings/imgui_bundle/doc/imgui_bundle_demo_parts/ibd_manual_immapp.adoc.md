# ImmApp - Immediate App

ImGui Bundle includes a library named ImmApp (which stands for Immediate App). ImmApp is a thin extension of HelloImGui that enables to easily initialize the ImGuiBundle addons that require additional setup at startup

## API

[C++ API](https://github.com/pthom/imgui_bundle/tree/doc/external/immapp/immapp/runner.h)

[Python bindings](https://github.com/pthom/imgui_bundle/tree/doc/bindings/imgui_bundle/immapp/immapp_cpp.pyi)

## How to start an application with addons

Some libraries included by ImGui Bundle require an initialization at startup. ImmApp makes this easy via AddOnParams.

The example program below demonstrates how to run an application which will use implot (which requires a context to be created at startup), and imgui_md (which requires additional fonts to be loaded at startup).

C++

``` cpp
#include "immapp/immapp.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"
#include "implot/implot.h"
#include "demo_utils/api_demos.h"
#include <vector>
#include <cmath>


int main(int, char**)
{
    // This call is specific to the ImGui Bundle interactive manual. In a standard application, you could write:
    //         HelloImGui::SetAssetsFolder("my_assets"); // (By default, HelloImGui will search inside "assets")
    ChdirBesideAssetsFolder();

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

Python:

``` python
import numpy as np
from imgui_bundle import implot, imgui_md, immapp
from imgui_bundle.demos_python import demo_utils


def main():
    # This call is specific to the ImGui Bundle interactive manual. In a standard application, you could write:
    #         hello_imgui.set_assets_folder("my_assets"); # (By default, HelloImGui will search inside "assets")
    demo_utils.set_hello_imgui_demo_assets_folder()

    x = np.arange(0, np.pi * 4, 0.01)
    y1 = np.cos(x)
    y2 = np.sin(x)

    def gui():
        imgui_md.render("# This is the plot of _cosinus_ and *sinus*")  # Markdown
        if implot.begin_plot("Plot"):
            implot.plot_line("y1", x, y1)
            implot.plot_line("y2", x, y2)
            implot.end_plot()

    immapp.run(gui, with_implot=True, with_markdown=True, window_size=(600, 400))


if __name__ == "__main__":
    main()
```
