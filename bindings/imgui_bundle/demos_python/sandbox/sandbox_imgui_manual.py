from imgui_bundle import imgui, imgui_explorer, immapp, hello_imgui

#hello_imgui.set_assets_folder("/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/imgui_bundle/external/imgui_explorer/imgui_explorer/assets")

def gui():
    # imgui_explorer.show_imgui_explorer_gui(imgui_explorer.ImGuiExplorerLibrary.implot, True)
    imgui_explorer.show_imgui_explorer_gui()


immapp.run(gui, with_markdown=True, with_implot=True, with_implot3d=True, with_im_anim=True)
