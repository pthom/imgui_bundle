# Using Dear ImGui Bundle with jupyter notebook

ImmApp adds support for integration inside jupyter notebook: the application will be run in an external window, and a screenshot will be placed on the notebook after execution.

This requires a window server, and will not run on google collab.

Below is a screenshot, that you can test by running `jupyter notebook` inside `bindings/imgui_bundle/demos_python/notebooks`

![immapp notebook example](images/immapp_notebook_example.jpg)

[40 seconds demo video on Youtube](https://www.youtube.com/watch?v=QQIC7lpHono)

## API:

[immapp/immapp_notebook.py](https://github.com/pthom/imgui_bundle/tree/doc/bindings/imgui_bundle/immapp/immapp_notebook.py)
