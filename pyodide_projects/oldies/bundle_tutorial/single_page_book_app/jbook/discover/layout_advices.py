from imgui_bundle import imgui, hello_imgui, imgui_ctx


class AppState:
    """Our application state"""
    name: str = ""
    first_name: str = ""
    city: str = ""
    age: int = 0


def input_text_aligned(label: str, value: str, width_pixel: float) -> tuple[bool, str]:
    """A helper function to create a label and an input text field in the same row,
    where the label is placed to the left, and the input field is right-aligned.
    It returns a tuple of (changed: bool, value: str), following the pattern of imgui.input_text.
    """
    # We will use a horizontal layout to place the label and the input field in the same row
    # (by default, imgui places widgets vertically)
    with imgui_ctx.begin_horizontal(label):
        # Display the label on the left side
        imgui.text(label)
        # Add a spring, which will occupy all remaining space:
        # this will push the input field to the right
        imgui.spring()
        imgui.set_next_item_width(width_pixel)
        # Note: by default, imgui.input_text will place the label to the right of the input field.
        # We do not want that, so we will use "##" to hide the label. We still need to make it unique,
        # so we append the user provided label to it (which will not be displayed).
        changed, value = imgui.input_text("##" + label, value)
    return changed, value


def gui(app_state: AppState):
    # Set the width of the widgets: we will use 10 em for most widgets
    widgets_width = hello_imgui.em_size(10)

    # Add some spacing at the top: we will skip 1 line of text
    imgui.dummy(hello_imgui.em_to_vec2(0, 1))

    # Enclose the widgets in a vertical layout: this is important, so that
    # the inner horizontal layouts use their parent's layout width.
    with imgui_ctx.begin_vertical("main"):
        imgui.separator_text("Personal information")
        imgui.dummy(hello_imgui.em_to_vec2(20, 0))
        _, app_state.name = input_text_aligned("Name", app_state.name, widgets_width)
        _, app_state.first_name = input_text_aligned("First name", app_state.first_name, widgets_width)
        _, app_state.city = input_text_aligned("City", app_state.city, widgets_width)

        # Add a slider to input the age: we enclose it in a horizontal layout
        with imgui_ctx.begin_horizontal("Age"):
            imgui.text("Age")
            # Add a spring to push the slider to the right
            imgui.spring()
            # Set the width of the slider to 10 em (by default, it would be the full width of the window)
            imgui.set_next_item_width(widgets_width)
            # use imgui.slider_int with a hidden label, and a range from 0 to 120
            _, app_state.age = imgui.slider_int("##Age", app_state.age, 0, 120)


def main():
    app_state = AppState()
    hello_imgui.run(lambda: gui(app_state), window_size=(400, 200))


if __name__ == "__main__":
    main()