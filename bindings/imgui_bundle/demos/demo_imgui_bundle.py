from imgui_bundle import imgui, imgui_md, static, ImVec2, hello_imgui, imgui_color_text_edit
from imgui_bundle.demos import code_str_utils
import inspect


def unindent(s: str):
    r = code_str_utils.unindent_code(s, flag_strip_empty_lines=True)
    return r


def md_render_unindent(md: str):
    u = code_str_utils.unindent_code(md, flag_strip_empty_lines=True, is_markdown=True)
    imgui_md.render(u)


class AppState:
    counter = 0
    name = ""


def show_python_vs_cpp_code_advice(python_gui_function, cpp_code: str):
    import inspect

    imgui.push_id(str(id(python_gui_function)))

    python_code = inspect.getsource(python_gui_function)

    code_size = ImVec2(500, 150)

    imgui.begin_group()
    imgui.text("C++ code")
    imgui.input_text_multiline("##C++", unindent(cpp_code), code_size)
    imgui.end_group()

    imgui.same_line()

    imgui.begin_group()
    imgui.text("Python code")
    imgui.input_text_multiline("##Python", unindent(python_code), code_size)
    imgui.end_group()

    python_gui_function()
    imgui.pop_id()


@static(value=0)
def demo_radio_button():
    static = demo_radio_button
    clicked, static.value = imgui.radio_button("radio a", static.value, 0)
    imgui.same_line()
    clicked, static.value = imgui.radio_button("radio b", static.value, 1)
    imgui.same_line()
    clicked, static.value = imgui.radio_button("radio c", static.value, 2)


def show_basic_code_advices():
    cpp_code = """
        void DemoRadioButton()
        {
            static int value = 0;
            ImGui::RadioButton("radio a", &value, 0); ImGui::SameLine();
            ImGui::RadioButton("radio b", &value, 1); ImGui::SameLine();
            ImGui::RadioButton("radio c", &value, 2);
        }
    """

    md_render_unindent(
        """
    ImGui is a C++ library that was ported to Python. In order to work with it you will often refer to its [demo](https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html), which shows example code in C++.

    In order to translate from C++ to Python:
     1. change the function names and parameters' names from `CamelCase` to `snake_case`
     2. change the way the output are handled
        a. in C++ `ImGui::RadioButton` modifies its second parameter (which is passed by address) and returns true if the user clicked the radio button
        b. In python, the (possibly modified) value is transmitted via the return: ìmgui.radio_button` returns a `Tuple[bool, str]` which contains (user_clicked, new_value)
    3. if porting some code that uses static variables, use the @static decorator
       In this case, this decorator simply adds a variable "value" at the function scope. It is is preserved between calls.
       Normally, this variable should be accessed via "demo_radio_button.value", however the first line of the function
       adds a synonym named static for more clarity.
       Do not overuse them! Static variable suffer from almost the same shortcomings as global variables, so you should prefer to modify an application state.
    """
    )
    imgui.new_line()
    show_python_vs_cpp_code_advice(demo_radio_button, cpp_code)


@static(text="")
def demo_input_text_decimal():
    static = demo_input_text_decimal
    changed, static.text = imgui.input_text("decimal", static.text, imgui.ImGuiInputTextFlags_.chars_decimal)


def show_text_input_advice():
    cpp_code = """
        void DemoInputTextDecimal()
        {
            static char text[64] = "";
            bool changed = ImGui::InputText(
                                            "decimal", text, 64, 
                                            ImGuiInputTextFlags_CharsDecimal);
        }
        """
    md_render_unindent(
        """
        In the example below, two differences are important:
        
        * ImGui::InputText aka imgui.input_text
        
           * In C++, it uses two parameters for the text: the text pointer, and its length.
           * In python, you can simply pass a string, and get back its modified value in the returned tuple.
        
        * ImGuiInputTextFlags_ is an enum in python (note the trailing underscore). You will find many similar enums.
    """
    )
    imgui.new_line()
    show_python_vs_cpp_code_advice(demo_input_text_decimal, cpp_code)


def demo_add_window_size_callback():
    import imgui_bundle
    import glfw # always import glfw *after* imgui_bundle!!!
    # Get the glfw window used by hello imgui
    window = imgui_bundle.glfw_window_hello_imgui()

    # define a callback
    def my_window_size_callback(window: glfw._GLFWwindow, w:int, h:int):
        from imgui_bundle import hello_imgui
        hello_imgui.log(hello_imgui.LogLevel.info, f"Window size changed to {w}x{h}")

    glfw.set_window_size_callback(window, my_window_size_callback)

@static(text_editor = None)
def show_glfw_callback_advice():
    static = show_glfw_callback_advice
    if static.text_editor is None:
        import inspect
        static.text_editor = imgui_color_text_edit.TextEditor()
        static.text_editor.set_text(inspect.getsource(demo_add_window_size_callback))

    md_render_unindent("For more complex applications, you can set various callbacks, using glfw.")
    if imgui.button("Add glfw callback"):
        demo_add_window_size_callback()
        hello_imgui.log(hello_imgui.LogLevel.warning,
            "A callback was handed to watch the window size. Change this window size and look at the logs")

    imgui.text("Code for this demo")
    static.text_editor.render("Code", ImVec2(500, 150))

    hello_imgui.log_gui()


def show_callback_avice():
    imgui.new_line()
    show_python_vs_cpp_code_advice()


@static(is_initialized=False)
def demo_imgui_bundle():
    static = demo_imgui_bundle

    if not static.is_initialized:
        static.app_state = AppState()
        static.is_initialized = True

    app_state: AppState = static.app_state

    md_render_unindent(
        """
        # ImGui Bundle
        [ImGui Bundle](https://github.com/pthom/imgui_bundle) is a collection of python bindings for [Dear ImGui](https://github.com/ocornut/imgui.git), and various libraries from its ecosystem.
        The bindings were autogenerated from the original C++ code, so that they are easier to keep up to date, and the python API closely matches the C++ api.
        """
    )
    imgui.separator()

    if imgui.collapsing_header("About"):
        md_render_unindent(
            """
            ### Batteries included
            ImGui Bundle include:
            * [imgui](https://github.com/ocornut/imgui.git) : Immediate Gui library
            * [hello imgui](https://github.com/pthom/hello_imgui.git): multiplatform backend provider for imgui
            * [implot](https://github.com/epezent/implot): plotting library based on ImGui
            * [ImGuiColorTextEdit](https://github.com/BalazsJako/ImGuiColorTextEdit): Colorizing text editor
            * [imgui-node-editor](https://github.com/thedmd/imgui-node-editor): Node editor
            * [imgui-knobs](https://github.com/altschuler/imgui-knobs): Knobs for ImGui
            * [ImFileDialog](https://github.com/pthom/ImFileDialog.git): File dialogs 
            * [imgui_md](https://github.com/mekhontsev/imgui_md.git): Markdown for ImGui
            * [imspinner](https://github.com/dalerank/imspinner): Spinners 
            
            ### Philosophy
            * Mirror the original API of ImGui and other libraries
            * Original code documentation is consciously kept inside the python stubs. See for example the documentation for:
                * [imgui](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui.pyi)
                * [implot](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/implot.pyi)
                * [hello imgui](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/hello_imgui.pyi)
            * Fully typed bindings, so that code completion works like a (Py) charm
            
            ### About Dear ImGui
            [Dear ImGui](https://github.com/ocornut/imgui.git) is one possible implementation of an idea generally described as the IMGUI (Immediate Mode GUI) paradigm.
         """
        )

    if imgui.collapsing_header("Immediate mode gui"):
        md_render_unindent("""An example is often worth a thousand words. The following code:""")

        def immediate_gui_example():
            # Display a text
            imgui.text(f"Counter = {app_state.counter}")
            imgui.same_line()  # by default ImGui starts a new line at each widget

            # The following line displays a button
            if imgui.button("increment counter"):
                # And returns true if it was clicked: you can *immediately* handle the click
                app_state.counter += 1

        imgui.input_text_multiline(
            "##immediate_gui_example", unindent(inspect.getsource(immediate_gui_example)), ImVec2(500, 150)
        )
        imgui.text("Displays this:")
        immediate_gui_example()
        imgui.separator()

    if imgui.collapsing_header("Consult the ImGui interactive manual!"):
        md_render_unindent(
            """
        Dear ImGui comes with a complete demo. It demonstrates all of the widgets, together with an example code on how to use them.

        [ImGui Manual](https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html) is an easy way to consult this demo, and to see the corresponding code. The demo code is in C++, but read the part "Code advices" below for advices on how to translate from C++ to python.
        """
        )
        if imgui.button("Open imgui manual"):
            import webbrowser

            webbrowser.open("https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html")

    if imgui.collapsing_header("Basic code advices"):
        show_basic_code_advices()

    if imgui.collapsing_header("TextInput and enums"):
        show_text_input_advice()

    if imgui.collapsing_header("Advanced callbacks"):
        show_glfw_callback_advice()


if __name__ == "__main__":
    import imgui_bundle

    imgui_bundle.run(demo_imgui_bundle, with_markdown=True, window_size=(1000, 800))
