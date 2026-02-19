from imgui_bundle import imgui, imgui_manual, immapp, hello_imgui
from imgui_bundle.demos_python import demo_utils
demo_utils.set_hello_imgui_demo_assets_folder()

#hello_imgui.set_assets_folder("/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/imgui_bundle/external/imgui_manual/imgui_manual/assets")

def gui():
    # imgui_manual.show_imgui_manual_gui(imgui_manual.ImGuiManualLibrary.implot, True)
    imgui_manual.show_imgui_manual_gui()


immapp.run(gui, with_markdown=True, with_implot=True, with_implot3d=True, with_im_anim=True)
