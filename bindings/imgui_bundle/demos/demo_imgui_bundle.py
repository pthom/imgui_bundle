from imgui_bundle import imgui, imgui_md, hello_imgui
from imgui_bundle.demos.demo_utils import code_str_utils, show_code_editor, show_python_vs_cpp_and_run
from imgui_bundle import immapp
from imgui_bundle import imgui_color_text_edit as text_edit
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


@immapp.static(value=0)
def demo_radio_button():
    static = demo_radio_button
    clicked, static.value = imgui.radio_button("radio a", static.value, 0)
    imgui.same_line()
    clicked, static.value = imgui.radio_button("radio b", static.value, 1)
    imgui.same_line()
    clicked, static.value = imgui.radio_button("radio c", static.value, 2)


def show_code_advices() -> None:
    cpp_code = (
            code_str_utils.unindent_code(
            """
        void DemoRadioButton()
        {
            static int value = 0;
            ImGui::RadioButton("radio a", &value, 0); ImGui::SameLine();
            ImGui::RadioButton("radio b", &value, 1); ImGui::SameLine();
            ImGui::RadioButton("radio c", &value, 2);
        }
    """,
            flag_strip_empty_lines=True,
        )
            + "\n"
    )

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
    show_python_vs_cpp_and_run(demo_radio_button, cpp_code)


# fmt: off

@immapp.static(text="")
def demo_input_text_decimal() -> None:
    static = demo_input_text_decimal
    flags:imgui.InputTextFlags = (
            imgui.InputTextFlags_.chars_uppercase.value
          | imgui.InputTextFlags_.chars_no_blank.value
        )
    changed, static.text = imgui.input_text("Upper case, no spaces", static.text, flags)

# fmt: on


def show_text_input_advice():
    cpp_code = (
            code_str_utils.unindent_code(
            """
        void DemoInputTextDecimal()
        {
            static char text[64] = "";
            ImGuiInputTextFlags flags = (
                  ImGuiInputTextFlags_CharsUppercase
                | ImGuiInputTextFlags_CharsNoBlank
            );
            bool changed = ImGui::InputText(
                                    "decimal", text, 64, 
                                    ImGuiInputTextFlags_CharsDecimal);
        }
        """,
            flag_strip_empty_lines=True,
        )
            + "\n"
    )

    md_render_unindent(
        """
        In the example below, two differences are important:
        
        ## InputText functions:
        imgui.input_text (Python) is equivalent to ImGui::InputText (C++) 
        
        * In C++, it uses two parameters for the text: the text pointer, and its length.
        * In python, you can simply pass a string, and get back its modified value in the returned tuple.
        
        ## Enums handling:

        * `ImGuiInputTextFlags_` (C++) corresponds to `imgui.InputTextFlags_` (python) and it is an _enum_ (note the trailing underscore). 
        * `ImGuiInputTextFlags` (C++) corresponds to `imgui.InputTextFlags` (python) and it is an _int_  (note: no trailing underscore)
        
        You will find many similar enums. 
        
        The dichotomy between int and enums, enables you to write flags that are a combinations of values from the enum (see example below).
        
    """
    )
    imgui.new_line()
    show_python_vs_cpp_and_run(demo_input_text_decimal, cpp_code)


def demo_add_window_size_callback():
    import imgui_bundle

    # always import glfw *after* imgui_bundle!!!
    import glfw  # type: ignore

    # Get the glfw window used by hello imgui
    window = imgui_bundle.glfw_window_hello_imgui()

    # define a callback
    def my_window_size_callback(window: glfw._GLFWwindow, w: int, h: int):
        from imgui_bundle import hello_imgui

        hello_imgui.log(hello_imgui.LogLevel.info, f"Window size changed to {w}x{h}")

    glfw.set_window_size_callback(window, my_window_size_callback)


@immapp.static(text_editor=None)
def show_glfw_callback_advice():
    static = show_glfw_callback_advice
    if static.text_editor is None:
        import inspect

        static.text_editor = text_edit.TextEditor()
        static.text_editor.set_text(inspect.getsource(demo_add_window_size_callback))

    imgui.text("Code for this demo")
    static.text_editor.render("Code", immapp.em_vec2(50., 16.5))

    md_render_unindent("""For more complex applications, you can set various callbacks, using glfw.
    *Click the button below to add a callback*""")

    if imgui.button("Add glfw callback"):
        demo_add_window_size_callback()
        hello_imgui.log(
            hello_imgui.LogLevel.warning,
            "A callback was handed to watch the window size. Change this window size and look at the logs",
        )

    hello_imgui.log_gui()


@immapp.static(is_initialized=False)
def demo_imgui_bundle() -> None:
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
            ImGui Bundle includes:
            * [imgui](https://github.com/ocornut/imgui.git) : Dear ImGui: Bloat-free Graphical User interface for C++ with minimal dependencies 
            * [implot](https://github.com/epezent/implot): Immediate Mode Plotting
            * [Hello ImGui](https://github.com/pthom/hello_imgui.git): cross-platform Gui apps with the simplicity of a "Hello World" app 
            * [ImGuizmo](https://github.com/CedricGuillemet/ImGuizmo.git): Immediate mode 3D gizmo for scene editing and other controls based on Dear Imgui 
            * [ImGuiColorTextEdit](https://github.com/BalazsJako/ImGuiColorTextEdit): Colorizing text editor for ImGui
            * [imgui-node-editor](https://github.com/thedmd/imgui-node-editor): Node Editor built using Dear ImGui 
            * [imgui-knobs](https://github.com/altschuler/imgui-knobs): Knobs widgets for ImGui
            * [ImFileDialog](https://github.com/pthom/ImFileDialog.git): A file dialog library for Dear ImGui  
            * [imgui_md](https://github.com/mekhontsev/imgui_md.git): Markdown renderer for Dear ImGui using MD4C parser
            * [imspinner](https://github.com/dalerank/imspinner): Set of nice spinners for imgui 
            * [imgui_toggle](https://github.com/cmdwtf/imgui_toggle): A toggle switch widget for Dear ImGui. [Homepage](https://cmd.wtf/projects#imgui-toggle)
            * [ImmVision](https://github.com/pthom/immvision.git): immediate image debugger and insights 
            * [imgui_tex_inspect](https://github.com/andyborrell/imgui_tex_inspect): A texture inspector tool for Dear ImGui 
            
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

        python_code = unindent(inspect.getsource(immediate_gui_example))
        # imgui.input_text_multiline("##immediate_gui_example", python_code, ImVec2(500, 150))
        show_code_editor(python_code, False)
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

    if imgui.collapsing_header("Advices"):
        show_code_advices()

    if imgui.collapsing_header("TextInput and enums"):
        show_text_input_advice()

    if imgui.collapsing_header("Advanced glfw callbacks"):
        show_glfw_callback_advice()


if __name__ == "__main__":
    from imgui_bundle import immapp

    params = immapp.RunnerParams()
    immapp.run(demo_imgui_bundle, with_markdown=True, window_size=(1000, 800))  # type: ignore
