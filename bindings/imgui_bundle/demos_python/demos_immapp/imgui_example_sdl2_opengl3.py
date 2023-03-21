# imgui_bundle can be used to run imgui with an almost line by line translation from C++ to python
#
# This file a direct adaptation of an imgui example (imgui/examples/example_sdl2_opengl3/main.cpp)
# (see https://github.com/ocornut/imgui/blob/master/examples/example_sdl2_opengl3/main.cpp)


import os.path
import sys
import platform
import OpenGL.GL as GL  # type: ignore
from imgui_bundle import imgui

# Always import sdl *after* imgui_bundle
# (since imgui_bundle will set the correct path where to look for the correct version of the SDL dynamic library)
import sdl2  # type: ignore # if this fails, you need to: pip install PySDL2


def main():
    # Setup window
    if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_TIMER | sdl2.SDL_INIT_GAMECONTROLLER) != 0:
        print(f"Error: {sdl2.SDL_GetError()}")

    # Decide GL+GLSL versions
    if platform.system() == "Darwin":
        glsl_version = "#version 150"
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_FLAGS, sdl2.SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG) # Always required on Mac
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_PROFILE_MASK, sdl2.SDL_GL_CONTEXT_PROFILE_CORE)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MAJOR_VERSION, 3)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MINOR_VERSION, 2)
    else:
        # GL 3.0 + GLSL 130
        glsl_version = "#version 130"
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_FLAGS, 0)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_PROFILE_MASK, sdl2.SDL_GL_CONTEXT_PROFILE_CORE)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MAJOR_VERSION, 3)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MINOR_VERSION, 0)

    # From 2.0.18: Enable native IME.
    sdl2.SDL_SetHint(sdl2.SDL_HINT_IME_SHOW_UI, b"1")

    # Create window with graphics context
    sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_DOUBLEBUFFER, 1)
    sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_DEPTH_SIZE, 24)
    sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_STENCIL_SIZE, 8)
    window_flags = sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_RESIZABLE | sdl2.SDL_WINDOW_ALLOW_HIGHDPI
    window = sdl2.SDL_CreateWindow(b"Dear ImGui SDL2+OpenGL3 example", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, 1280, 720, window_flags)
    gl_context = sdl2.SDL_GL_CreateContext(window)
    sdl2.SDL_GL_MakeCurrent(window, gl_context)
    sdl2.SDL_GL_SetSwapInterval(1) # Enable vsync

    # Setup Dear ImGui context
    # IMGUI_CHECKVERSION();
    imgui.create_context()
    io = imgui.get_io()
    io.config_flags |= imgui.ConfigFlags_.nav_enable_keyboard  # Enable Keyboard Controls
    # io.config_flags |= imgui.ConfigFlags_.nav_enable_gamepad # Enable Gamepad Controls
    io.config_flags |= imgui.ConfigFlags_.docking_enable  # Enable docking
    # io.config_flags |= imgui.ConfigFlags_.viewports_enable # Enable Multi-Viewport / Platform Windows
    # io.config_viewports_no_auto_merge = True
    # io.config_viewports_no_task_bar_icon = True

    # Setup Dear ImGui style
    imgui.style_colors_dark()
    # imgui.style_colors_classic()

    # When viewports are enabled we tweak WindowRounding/WindowBg so platform windows can look identical to regular ones.
    style = imgui.get_style()
    if io.config_flags & imgui.ConfigFlags_.viewports_enable:
        style.window_rounding = 0.0
        window_bg_color = style.color_(imgui.Col_.window_bg)
        window_bg_color.w = 1.0
        style.set_color_(imgui.Col_.window_bg, window_bg_color)

    # Setup Platform/Renderer backends
    import ctypes

    # You need to transfer the window address to imgui.backends.sdl2_init_for_opengl
    # proceed as shown below to get it.
    window_address = ctypes.cast(window, ctypes.c_void_p).value
    gl_context_address = ctypes.cast(gl_context, ctypes.c_void_p).value
    imgui.backends.sdl2_init_for_opengl(window_address, gl_context_address)

    imgui.backends.opengl3_init(glsl_version)

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

    # Load font example, with a merged font for icons
    # ------------------------------------------------
    # i. Load default font
    font_atlas = imgui.get_io().fonts
    font_atlas.add_font_default()
    this_dir = os.path.dirname(__file__)
    font_size_pixel = 48.0
    # i. Load another font...
    font_filename = this_dir + "/../../demos_assets/fonts/Akronim-Regular.ttf"
    font_atlas = imgui.get_io().fonts
    glyph_range = font_atlas.get_glyph_ranges_default()
    custom_font = font_atlas.add_font_from_file_ttf(
        filename=font_filename,
        size_pixels=font_size_pixel,
        glyph_ranges_as_int_list=glyph_range,
    )
    # ii. ... And merge icons into the previous font
    from imgui_bundle import icons_fontawesome

    font_filename = this_dir + "/../../demos_assets/fonts/fontawesome-webfont.ttf"
    font_config = imgui.ImFontConfig()
    font_config.merge_mode = True
    icons_range = [icons_fontawesome.ICON_MIN_FA, icons_fontawesome.ICON_MAX_FA, 0]
    custom_font = font_atlas.add_font_from_file_ttf(
        filename=font_filename,
        size_pixels=font_size_pixel,
        glyph_ranges_as_int_list=icons_range,
        font_cfg=font_config,
    )

    # Our state
    show_demo_window = True
    show_another_window = False
    clear_color = [0.45, 0.55, 0.60, 1.00]
    f = 0.0
    counter = 0

    # Main loop
    done = False
    while not done:

        # // Poll and handle events (inputs, window resize, etc.)
        # // You can read the io.WantCaptureMouse, io.WantCaptureKeyboard flags to tell if dear imgui wants to use your inputs.
        # // - When io.WantCaptureMouse is true, do not dispatch mouse input data to your main application, or clear/overwrite your copy of the mouse data.
        # // - When io.WantCaptureKeyboard is true, do not dispatch keyboard input data to your main application, or clear/overwrite your copy of the keyboard data.
        # // Generally you may always pass all inputs to dear imgui, and hide them from your application based on those two flags.
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(event):
            # event_address = ctypes.cast(event, ctypes.c_void_p).value
            event_address = ctypes.addressof(event)
            imgui.backends.sdl2_process_event(event_address)
            if event.type == sdl2.SDL_QUIT:
                done = True
            if (event.type == sdl2.SDL_WINDOWEVENT and event.window.event == sdl2.SDL_WINDOWEVENT_CLOSE and event.window.windowID == sdl2.SDL_GetWindowID(window)):
                done = True


        # Start the Dear ImGui frame
        imgui.backends.opengl3_new_frame()
        imgui.backends.sdl2_new_frame()
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

            # Demo custom font
            _id = id(custom_font)
            imgui.push_font(custom_font)
            imgui.text("Hello " + icons_fontawesome.ICON_FA_SMILE)
            imgui.pop_font()

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
        GL.glViewport(0, 0, int(imgui.get_io().display_size.x), int(imgui.get_io().display_size.y))
        GL.glClearColor(
            clear_color[0] * clear_color[3],
            clear_color[1] * clear_color[3],
            clear_color[2] * clear_color[3],
            clear_color[3],
        )
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        imgui.backends.opengl3_render_draw_data(imgui.get_draw_data())

        # Update and Render additional Platform Windows
        # (Platform functions may change the current OpenGL context, so we save/restore it to make it easier to paste this code elsewhere.
        #  For this specific demo app we could also call SDL_GL_MakeCurrent(window, gl_context) directly)
        if io.config_flags & imgui.ConfigFlags_.viewports_enable > 0:
            backup_current_window = sdl2.SDL_GL_GetCurrentWindow()
            backup_current_context = sdl2.SDL_GL_GetCurrentContext()
            imgui.update_platform_windows()
            imgui.render_platform_windows_default()
            sdl2.SDL_GL_MakeCurrent(backup_current_window, backup_current_context)

        sdl2.SDL_GL_SwapWindow(window)

    # Cleanup
    imgui.backends.opengl3_shutdown()
    imgui.backends.sdl2_shutdown()
    imgui.destroy_context()

    sdl2.SDL_GL_DeleteContext(gl_context)
    sdl2.SDL_DestroyWindow(window);
    sdl2.SDL_Quit();


if __name__ == "__main__":
    main()
