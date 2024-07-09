from imgui_bundle import imgui, immapp, imgui_ctx, imgui_node_editor as ed


def gui():
    with imgui_ctx.begin_vertical("V"):
        ed.begin("Node editor")
        ed.begin_node(ed.NodeId(1))
        with imgui_ctx.begin_horizontal("H"):
            imgui.text("Hello")
            imgui.spring()
            imgui.text("world")

        with imgui_ctx.begin_horizontal("H2"):
            imgui.text("Hello")
            imgui.spring()
            imgui.text("world")
            imgui.text("And again")
        ed.end_node()
        ed.end()


immapp.run(gui, with_node_editor=True)
