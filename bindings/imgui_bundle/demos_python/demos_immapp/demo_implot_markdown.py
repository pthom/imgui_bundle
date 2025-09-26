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
