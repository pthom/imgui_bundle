from copy_imgui_bindings import copy_imgui_bindings
from generate_hello_imgui import autogenerate_hello_imgui
from generate_implot import autogenerate_implot


def main():
    copy_imgui_bindings()
    autogenerate_hello_imgui()
    autogenerate_implot()


if __name__ == "__main__":
    main()
