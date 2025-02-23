"""Patch the immapp and hello_imgui runners for Jupyter notebook.
- Will display a screenshot of the final app state in the notebook output.
- Will use a white theme for the GUI.
- Will make the window autosize by default.
- Will patch hello_imgui.run and immapp.run
"""

def is_in_notebook() -> bool:
    try:
        import sys
        return 'ipykernel' in sys.modules and 'IPython' in sys.modules
    except ImportError:
        return False


def notebook_do_patch_runners_if_needed() -> None:
    if not is_in_notebook():
        return

    from imgui_bundle import immapp, hello_imgui
    from imgui_bundle.immapp.immapp_notebook import _run_app_function_and_display_image_in_notebook

    def patch_runner(run_backup):
        def patched_run(*args, **kwargs):
            # Are we using hello_imgui.RunnerParams, or are we using raw parameters (i.e. a gui_function + other parameters)?
            use_gui_function = (len(args) >= 1 and callable(args[0])) or "gui_function" in kwargs

            # Set window_size_auto to True if not set, to make the window smaller and reduce the size of the screenshot
            if use_gui_function and "window_size" not in kwargs and "window_size_auto" not in kwargs:
                kwargs["window_size_auto"] = True

            # If using a gui function, patch it so that it uses a white theme
            if use_gui_function:
                gui_function = args[0] if len(args) >= 1 else kwargs.get("gui_function", None)
                if gui_function:
                    from imgui_bundle.immapp.immapp_notebook import _make_gui_with_light_theme
                    gui_function_with_light_theme = _make_gui_with_light_theme(gui_function)
                    if "gui_function" in kwargs:
                        kwargs["gui_function"] = gui_function_with_light_theme
                    else:
                        args = (gui_function_with_light_theme, *args[1:])

            # define a function that will run the full app, then run this function
            # via _run_app_function_and_display_image_in_notebook
            def app_function():
                run_backup(*args, **kwargs)
            _run_app_function_and_display_image_in_notebook(app_function)
        return patched_run

    immapp.run_original = immapp.run
    immapp.run = patch_runner(immapp.run_original)  # noqa

    hello_imgui.run_original = hello_imgui.run
    hello_imgui.run = patch_runner(hello_imgui.run_original)  # noqa
