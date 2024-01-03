from imgui_bundle import imgui, immapp, hello_imgui


def gui():
    imgui.text("Here is an image that was loaded from the assets: ")
    image_size = hello_imgui.em_to_vec2(26, 0.0)
    hello_imgui.image_from_asset("images/world.png", image_size)


def set_assets_folder_if_macos_bundle():
    import os
    this_dir = str(os.path.dirname(os.path.realpath(__file__)))
    if this_dir.endswith("Contents/Frameworks"):
        assets_folder = this_dir + "/../Resources/assets"
        hello_imgui.set_assets_folder(assets_folder)
        print(f"Changed assets folder to: {assets_folder}")


def main():
    set_assets_folder_if_macos_bundle()
    immapp.run(gui, window_size_auto=True, window_title="Assets test")


if __name__ == "__main__":
    main()
