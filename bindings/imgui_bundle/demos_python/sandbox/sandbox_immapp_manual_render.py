from imgui_bundle import immapp, hello_imgui, rich_md, imgui


def gui():
    rich_md.render("""
        # Sandbox

        Lorem ipsum dolor sit amet, consectetur adipiscing elit
    """)
    if imgui.button("Save"):
        # Save something
        pass
    imgui.same_line()
    if imgui.button("Load"):
        # Load something
        pass


def main():
    immapp.manual_render.setup_from_gui_function(gui)
    while not hello_imgui.get_runner_params().app_shall_exit:
        immapp.manual_render.render()
    immapp.manual_render.tear_down()


if __name__ == "__main__":
    main()
    main()
    main()
