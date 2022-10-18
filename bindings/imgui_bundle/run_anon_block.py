from typing import Callable


def run_anon_block(function: Callable[[None], None]):
    """Decorator for anonymous block

    This enables you to emulate CC++ anonymous blocks.
    In the example below, _win_code() is an anonymous block which is evaluated right after its definition.
    Its presence makes it possible to indent parts of the code (for example, the code responsible for the widgets
     inside a window)

        imgui.begin("My window")
        @run_anon_block
        def _win_code():
            imgui.text("What is your name")
            changed_f, first_name = imgui.input_text("First name")
            changed_l, last_name = imgui.input_text("Last name")
            # ...
        imgui.end()

    """
    function()  # type: ignore
