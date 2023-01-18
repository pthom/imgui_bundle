# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from imgui_bundle import immapp, hello_imgui, imgui_md
from imgui_bundle.demos_python import demo_utils


def demo_gui():
    imgui_md.render_unindented(
        """
    # Notebook integration
    ImmApp adds support for integration inside jupyter notebook: the application will be run in an external window, and a screenshot will be placed on the notebook after execution.

    This requires a window server, and will not run on google collab.
    
    Below is a screenshot, that you can test by running `jupyter notebook` inside `bindings/imgui_bundle/demos_python/notebooks`
    
            """
    )

    hello_imgui.image_from_asset("images/immapp_notebook_screenshot.jpg", (0, immapp.em_size(30)))


if __name__ == "__main__":
    hello_imgui.set_assets_folder(demo_utils.demos_assets_folder())
    immapp.run(demo_gui, window_size=(1000, 800), with_markdown=True)
