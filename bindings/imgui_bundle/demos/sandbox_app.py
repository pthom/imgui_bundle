import imgui_bundle
from imgui_bundle import imgui, hello_imgui, ImVec2



def make_gui_closure():
    texture_id = None

    def gui():
        nonlocal texture_id
        if texture_id is None:
            texture_id = hello_imgui.im_texture_id_from_asset("images/world.jpg")

        imgui.text("Hello")
        imgui.get_foreground_draw_list().add_image_rounded(
            texture_id,
            p_min = ImVec2(50, 50),
            p_max= ImVec2(300, 300),
            uv_min = ImVec2(0, 0),
            uv_max = ImVec2(1, 1),
            col = 0xffffffff,
            rounding = 50.0)
        if imgui.button("text"):
            settings = imgui.save_ini_settings_to_memory()
            print(settings)

    return gui


def main():
    gui = make_gui_closure()
    imgui_bundle.run(gui, window_size=(1000, 800))


if __name__ == "__main__":
    main()
