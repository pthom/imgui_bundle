"""all_imgui_manual_py_demos.py: shows all imgui_manual Python demos in one tabbed window,
to check that they all work together and to compare them with the C++ versions"""

from imgui_bundle import imgui, immapp, imgui_manual, imgui_ctx
from imgui_bundle.demos_python.demos_imgui_manual import imgui_demo, implot_demo, implot3d_demo, im_anim_demo_basics


def gui():
    imgui.text("All imgui_manual Python demos in one tabbed window")
    with imgui_ctx.begin_tab_bar("Tabs"):
        with imgui_ctx.begin_tab_item("imgui_demo.py") as tab_item:
            if tab_item:
                 imgui_demo.show_demo_window_maybe_docked(False)
        with imgui_ctx.begin_tab_item("imgui_demo.cpp") as tab_item:
            if tab_item:
                imgui_manual.show_imgui_manual_gui(imgui_manual.ImGuiManualLibrary.imgui, imgui_manual.ImGuiManualCppOrPython.python, False)

        with imgui_ctx.begin_tab_item("implot_demo.py") as tab_item:
            if tab_item:
                implot_demo.show_demo_window_maybe_docked(False)
        with imgui_ctx.begin_tab_item("implot_demo.cpp") as tab_item:
            if tab_item:
                imgui_manual.show_imgui_manual_gui(imgui_manual.ImGuiManualLibrary.implot, imgui_manual.ImGuiManualCppOrPython.python, False)

        with imgui_ctx.begin_tab_item("implot3d_demo.py") as tab_item:
            if tab_item:
                implot3d_demo.show_demo_window_maybe_docked(False)
        with imgui_ctx.begin_tab_item("implot3d_demo.cpp") as tab_item:
            if tab_item:
                imgui_manual.show_imgui_manual_gui(imgui_manual.ImGuiManualLibrary.implot3_d, imgui_manual.ImGuiManualCppOrPython.python, False)

        with imgui_ctx.begin_tab_item("im_anim_demo_basics.py") as tab_item:
            if tab_item:
                im_anim_demo_basics.im_anim_demo_basics_window(False)
        with imgui_ctx.begin_tab_item("im_anim_demo_basics.cpp") as tab_item:
            if tab_item:
                imgui_manual.show_imgui_manual_gui(imgui_manual.ImGuiManualLibrary.im_anim, imgui_manual.ImGuiManualCppOrPython.python, False)


def main():
    immapp.run(gui, with_markdown=True, with_implot=True, with_implot3d=True, with_im_anim=True, window_size=(1200, 900))



if __name__ == "__main__":
    main()