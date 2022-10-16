from generate_hello_imgui import autogenerate_hello_imgui
from generate_im_file_dialog import autogenerate_im_file_dialog
from generate_imgui import autogenerate_imgui
from generate_imgui_color_text_edit import autogenerate_imgui_color_text_edit
from generate_imgui_knobs import autogenerate_imgui_knobs
from generate_imgui_node_editor import autogenerate_imgui_node_editor
from generate_implot import autogenerate_implot


def main():
    autogenerate_hello_imgui()
    autogenerate_im_file_dialog()
    autogenerate_imgui()
    autogenerate_imgui_color_text_edit()
    autogenerate_imgui_knobs()
    autogenerate_imgui_node_editor()
    autogenerate_implot()


if __name__ == "__main__":
    main()
