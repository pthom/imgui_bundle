from generate_hello_imgui import autogenerate_hello_imgui
from generate_imgui import autogenerate_imgui
from generate_implot import autogenerate_implot
from generate_imgui_color_text_edit import autogenerate_imgui_color_text_edit
from generate_imgui_node_editor import autogenerate_imgui_node_editor


def main():
    autogenerate_imgui()
    autogenerate_hello_imgui()
    autogenerate_implot()
    autogenerate_imgui_color_text_edit()
    autogenerate_imgui_node_editor()


if __name__ == "__main__":
    main()
