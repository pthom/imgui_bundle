from imgui_bundle import immapp, hello_imgui, imgui
from imgui_bundle.demos_python import demo_utils


def make_gui():
    def gui():
        demo_utils.render_md_unindented(
            """
        # Notebook integration
        ImmApp adds support for integration inside jupyter notebook: the application will be run in an external window, and a screenshot will be placed on the notebook after execution.

        This requires a window server, and will not run on google collab.
        
        Below is a screenshot, that you can test by running `jupyter notebook` inside `bindings/imgui_bundle/demos_python/notebooks`
        
                """
        )

        hello_imgui.image_from_asset("images/immapp_notebook_screenshot.jpg", (0, immapp.em_size(30)))
    return gui


@immapp.static(gui=None)
def demo_launch():
    statics = demo_launch
    if statics.gui is None:
        statics.gui = make_gui()
    statics.gui()


if __name__ == "__main__":
    immapp.run(demo_launch, window_size=(1000, 800), with_markdown=True)
