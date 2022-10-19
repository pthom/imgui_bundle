from imgui_bundle import imgui


def demo_imgui():
    imgui.text("""Dear ImGui https://github.com/ocornut/imgui.git
    This is the main demo from ImGui. Its code is in C++ but it is the most useful reference for ImGui.    
    You can browse the code corresponding to each widget via ImGui Manual.""")
    if imgui.button("Open ImGui manual"):
        import webbrowser
        webbrowser.open("https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html")

    imgui.show_demo_window()
