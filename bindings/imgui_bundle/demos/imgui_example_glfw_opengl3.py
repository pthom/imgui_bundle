"""This is a direct adaptation of imgui example: imgui/examples/example_glfw_opengl3/main.cpp

imgui_bundle can be used without hello imgui, and you can configure and run imgui, opengl and glfw (or sdl, etc.) manually,
as shown here.
"""

import sys
import platform
import OpenGL.GL as GL
from imgui_bundle import imgui, imgui_backends
# Always import glfw *after* imgui_bundle
# (since imgui_bundle will set the correct path where to look for
#  the correct version of the glfw dynamic library)
import glfw


def glfw_error_callback(error: int, description: str):
    sys.stderr.write(f"Glfw Error {error}: {description}\n")


def main():
    # Setup window
    glfw.set_error_callback(glfw_error_callback)
    if not glfw.init():
        sys.exit(1)

    # Decide GL+GLSL versions
    # #if defined(IMGUI_IMPL_OPENGL_ES2)
    # // GL ES 2.0 + GLSL 100
    # const char* glsl_version = "#version 100";
    # glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 2);
    # glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
    # glfwWindowHint(GLFW_CLIENT_API, GLFW_OPENGL_ES_API);
    if platform.system() == "Darwin":
        glsl_version = "#version 150"
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)  # // 3.2+ only
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
    else:
        # GL 3.0 + GLSL 130
        glsl_version = "#version 130"
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
        # glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE) # // 3.2+ only
        # glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    # Create window with graphics context
    window = glfw.create_window(1280, 720, "Dear ImGui GLFW+OpenGL3 example", None, None)
    if window is None:
        sys.exit(1)
    glfw.make_context_current(window)
    glfw.swap_interval(1)  # // Enable vsync

    # Setup Dear ImGui context
    # IMGUI_CHECKVERSION();
    imgui.create_context()
    io = imgui.get_io()
    io.config_flags |= imgui.ImGuiConfigFlags_.nav_enable_keyboard  # Enable Keyboard Controls
    # io.config_flags |= imgui.ImGuiConfigFlags_.nav_enable_gamepad # Enable Gamepad Controls
    io.config_flags |= imgui.ImGuiConfigFlags_.docking_enable # Enable docking
    # io.config_flags |= imgui.ImGuiConfigFlags_.viewports_enable # Enable Multi-Viewport / Platform Windows
    # io.ConfigViewportsNoAutoMerge = true;
    # io.ConfigViewportsNoTaskBarIcon = true;

    # Setup Dear ImGui style
    imgui.style_colors_dark()
    # imgui.style_colors_classic()

    # When viewports are enabled we tweak WindowRounding/WindowBg so platform windows can look identical to regular ones.
    style = imgui.get_style()
    if io.config_flags & imgui.ImGuiConfigFlags_.viewports_enable:
        style.window_rounding = 0.0
        # style.Colors[ImGuiCol_WindowBg].w = 1.0f;  # unsettable from python!!!!

    # Setup Platform/Renderer backends
    import ctypes
    # You need to transfer the window address to imgui_backends.glfw_init_for_open_gl
    # proceed as shown below to get it.
    window_address = ctypes.cast(window, ctypes.c_void_p).value
    imgui_backends.glfw_init_for_open_gl(window_address, True)

    imgui_backends.open_gl3_init(glsl_version)

    # // Load Fonts
    # // - If no fonts are loaded, dear imgui will use the default font. You can also load multiple fonts and use imgui.PushFont()/PopFont() to select them.
    # // - AddFontFromFileTTF() will return the ImFont* so you can store it if you need to select the font among multiple.
    # // - If the file cannot be loaded, the function will return NULL. Please handle those errors in your application (e.g. use an assertion, or display an error and quit).
    # // - The fonts will be rasterized at a given size (w/ oversampling) and stored into a texture when calling ImFontAtlas::Build()/GetTexDataAsXXXX(), which ImGui_ImplXXXX_NewFrame below will call.
    # // - Read 'docs/FONTS.md' for more instructions and details.
    #     // - Remember that in C/C++ if you want to include a backslash \ in a string literal you need to write a double backslash \\ !
    # //io.Fonts->AddFontDefault();
    # //io.Fonts->AddFontFromFileTTF("../../misc/fonts/Roboto-Medium.ttf", 16.0f);
    # //io.Fonts->AddFontFromFileTTF("../../misc/fonts/Cousine-Regular.ttf", 15.0f);
    # //io.Fonts->AddFontFromFileTTF("../../misc/fonts/DroidSans.ttf", 16.0f);
    # //io.Fonts->AddFontFromFileTTF("../../misc/fonts/ProggyTiny.ttf", 10.0f);
    # //ImFont* font = io.Fonts->AddFontFromFileTTF("c:\\Windows\\Fonts\\ArialUni.ttf", 18.0f, NULL, io.Fonts->GetGlyphRangesJapanese());
    # //IM_ASSERT(font != NULL);

    # Our state
    show_demo_window = True
    show_another_window = False
    clear_color = [0.45, 0.55, 0.60, 1.00]
    f = 0.0
    counter = 0

    # Main loop
    while not glfw.window_should_close(window):

        # // Poll and handle events (inputs, window resize, etc.)
        # // You can read the io.WantCaptureMouse, io.WantCaptureKeyboard flags to tell if dear imgui wants to use your inputs.
        # // - When io.WantCaptureMouse is true, do not dispatch mouse input data to your main application, or clear/overwrite your copy of the mouse data.
        # // - When io.WantCaptureKeyboard is true, do not dispatch keyboard input data to your main application, or clear/overwrite your copy of the keyboard data.
        # // Generally you may always pass all inputs to dear imgui, and hide them from your application based on those two flags.
        glfw.poll_events()

        # Start the Dear ImGui frame
        imgui_backends.open_gl3_new_frame()
        imgui_backends.glfw_new_frame()
        imgui.new_frame()

        # 1. Show the big demo window (Most of the sample code is in imgui.ShowDemoWindow()! You can browse its code to learn more about Dear ImGui!).
        if show_demo_window:
            show_demo_window = imgui.show_demo_window(show_demo_window)

        # 2. Show a simple window that we create ourselves. We use a Begin/End pair to created a named window.
        def show_simple_window():
            nonlocal show_demo_window, show_another_window, clear_color, counter, f
            # static float f = 0.0f;
            # static int counter = 0;
            imgui.begin("Hello, world!")  # Create a window called "Hello, world!" and append into it.

            imgui.text("This is some useful text.")  # Display some text (you can use a format strings too)
            _, show_demo_window = imgui.checkbox(
                "Demo Window", show_demo_window
            )  # Edit bools storing our window open/close state
            _, show_another_window = imgui.checkbox("Another Window", show_another_window)

            _, f = imgui.slider_float("float", f, 0.0, 1.0)  # Edit 1 float using a slider from 0.0f to 1.0f
            _, clear_color = imgui.color_edit4("clear color", clear_color)  # Edit 4 floats representing a color

            if imgui.button(
                "Button"
            ):  # Buttons return true when clicked (most widgets return true when edited/activated)
                counter += 1

            imgui.same_line()
            imgui.text(f"counter = {counter}")

            imgui.text(
                f"Application average {1000.0 / imgui.get_io().framerate} ms/frame ({imgui.get_io().framerate:.1f} FPS)"
            )
            imgui.end()

        show_simple_window()

        # 3. Show another simple window.
        def gui_another_window():
            nonlocal show_another_window
            if show_another_window:
                imgui.begin(
                    "Another Window", show_another_window
                )  # Pass a pointer to our bool variable (the window will have a closing button that will clear the bool when clicked)
                imgui.text("Hello from another window!")
                if imgui.button("Close Me"):
                    show_another_window = False
                imgui.end()

        gui_another_window()

        # Rendering
        imgui.render()
        display_w, display_h = glfw.get_framebuffer_size(window)
        GL.glViewport(0, 0, display_w, display_h)
        GL.glClearColor(
            clear_color[0] * clear_color[3],
            clear_color[1] * clear_color[3],
            clear_color[2] * clear_color[3],
            clear_color[3],
        )
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        imgui_backends.open_gl3_render_draw_data(imgui.get_draw_data())

        # Update and Render additional Platform Windows
        # (Platform functions may change the current OpenGL context, so we save/restore it to make it easier to paste this code elsewhere.
        #  For this specific demo app we could also call glfwMakeContextCurrent(window) directly)
        if io.config_flags & imgui.ImGuiConfigFlags_.viewports_enable > 0:
            backup_current_context = glfw.get_current_context()
            imgui.update_platform_windows()
            imgui.render_platform_windows_default(glfw.make_context_current(backup_current_context))

        glfw.swap_buffers(window)

    # Cleanup
    imgui_backends.open_gl3_shutdown()
    imgui_backends.glfw_shutdown()
    imgui.destroy_context()

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
