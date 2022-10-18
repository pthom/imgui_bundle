# Adapted from https://github.com/thedmd/imgui-node-editor/blob/master/examples/basic-interaction-example/basic-interaction-example.cpp
from __future__ import annotations
from typing import List
from imgui_bundle import hello_imgui, imgui, imgui_node_editor

ed = imgui_node_editor


def unique_id():
    # Add a static variable to the function
    if not hasattr(unique_id, "last_id"):
        unique_id.last_id = 1

    r = unique_id.last_id
    unique_id.last_id += 1
    return r


class Example:
    # Struct to hold basic information about connection between
    # pins. Note that connection (aka. link) has its own ID.
    # This is useful later with dealing with selections, deletion
    # or other operations.

    m_Context: ed.EditorContext = None  # Editor context, required to trace a editor state.
    m_FirstFrame: bool = True  # Flag set for first frame only, some action need to be executed once.
    m_Links: List[LinkInfo]  # List of live links. It is dynamic unless you want to create read-only view over nodes.
    m_NextLinkId: int = 100  # Counter to help generate link ids. In real application this will probably based on pointer to user data structure.

    def __init__(self):
        self.m_Links = []

    class LinkInfo:
        Id: ed.LinkId
        InputId: ed.PinId
        OutputId: ed.PinId

    def OnStart(self):
        config = ed.Config()
        # config.settings_file = "BasicInteraction.json"    # const char * !!!!
        self.m_Context = ed.create_editor(config)

    def OnStop(self):
        ed.destroy_editor(self.m_Context)

    def ImGuiEx_BeginColumn(self):
        imgui.begin_group()

    def ImGuiEx_NextColumn(self):
        imgui.end_group()
        imgui.same_line()
        imgui.begin_group()

    def ImGuiEx_EndColumn(self):
        imgui.end_group()

    def OnFrame(self):
        io = imgui.get_io()
        imgui.text(f"FPS: {io.framerate}FPS")

        imgui.separator()

        ed.set_current_editor(self.m_Context)

        # Start interaction with editor.
        ed.begin("My Editor", imgui.ImVec2(0.0, 0.0))

        #
        # 1) Commit known data to editor
        #

        # Submit Node A
        nodeA_Id = ed.NodeId(unique_id())
        nodeA_InputPinId = ed.PinId(unique_id())
        nodeA_OutputPinId = ed.PinId(unique_id())

        if self.m_FirstFrame:
            ed.set_node_position(nodeA_Id, imgui.ImVec2(200, -300))
        ed.begin_node(nodeA_Id)
        imgui.text("Node A")
        ed.begin_pin(nodeA_InputPinId, ed.PinKind.input)
        imgui.text("-> In")
        ed.end_pin()
        imgui.same_line()
        ed.begin_pin(nodeA_OutputPinId, ed.PinKind.output)
        imgui.text("Out ->")
        ed.end_pin()
        ed.end_node()

        # Submit Node B
        nodeB_Id = ed.NodeId(unique_id())
        nodeB_InputPinId1 = ed.PinId(unique_id())
        nodeB_InputPinId2 = ed.PinId(unique_id())
        nodeB_OutputPinId = ed.PinId(unique_id())

        if self.m_FirstFrame:
            ed.set_node_position(nodeB_Id, imgui.ImVec2(210, 60))
        ed.begin_node(nodeB_Id)
        imgui.text("Node B")
        self.ImGuiEx_BeginColumn()
        ed.begin_pin(nodeB_InputPinId1, ed.PinKind.input)
        imgui.text("-> In1")
        ed.end_pin()
        ed.begin_pin(nodeB_InputPinId2, ed.PinKind.input)
        imgui.text("-> In2")
        ed.end_pin()
        self.ImGuiEx_NextColumn()
        ed.begin_pin(nodeB_OutputPinId, ed.PinKind.output)
        imgui.text("Out ->")
        ed.end_pin()
        self.ImGuiEx_EndColumn()
        ed.end_node()

        # Submit Links
        for linkInfo in self.m_Links:
            ed.link(linkInfo.Id, linkInfo.InputId, linkInfo.OutputId)

        #
        # 2) Handle interactions
        #
        # Handle creation action, returns true if editor want to create new object (node or link)
        if ed.begin_create():

            inputPinId = ed.PinId()
            outputPinId = ed.PinId()

            if ed.query_new_link(inputPinId, outputPinId):
                # QueryNewLink returns true if editor want to create new link between pins.
                #
                # Link can be created only for two valid pins, it is up to you to
                # validate if connection make sense. Editor is happy to make any.
                #
                # Link always goes from input to output. User may choose to drag
                # link from output pin or input pin. This determine which pin ids
                # are valid and which are not:
                #   * input valid, output invalid - user started to drag new ling from input pin
                #   * input invalid, output valid - user started to drag new ling from output pin
                #   * input valid, output valid   - user dragged link over other pin, can be validated

                if inputPinId and outputPinId:  # both are valid, let's accept link
                    # ed.AcceptNewItem(): return true when user release mouse button.
                    if ed.accept_new_item():
                        # Since we accepted new link, lets add one to our list of links.
                        self.m_Links.append(ed.LinkId(self.m_NextLinkId), inputPinId, outputPinId)
                        self.m_NextLinkId += 1

                        # Draw new link.
                        ed.link(self.m_Links[-1].Id, self.m_Links[-1].InputId, self.m_Links[-1].OutputId)

                    # You may choose to reject connection between these nodes
                    # by calling ed.RejectNewItem():. This will allow editor to give
                    # visual feedback by changing link thickness and color.

        ed.end_create()  # Wraps up object creation action handling.

        # Handle deletion action
        if ed.begin_delete():

            # There may be many links marked for deletion, let's loop over them.
            deletedLinkId: ed.LinkId
            while ed.query_deleted_link(deletedLinkId):
                # If you agree that link can be deleted, accept deletion.
                if ed.accept_deleted_item():
                    # Then remove link from your data.
                    for link in self.m_Links:
                        if link.Id == deletedLinkId:
                            self.m_Links.remove(link)
                            break
                # You may reject link deletion by calling:
                # ed.reject_deleted_item()

        ed.end_delete()  # Wrap up deletion action

        # End of interaction with editor.
        ed.end()

        if self.m_FirstFrame:
            ed.navigate_to_content(0.0)

        ed.set_current_editor(None)

        self.m_FirstFrame = False

        # imgui.show_metrics_window()


def main():
    example = Example()
    runner_params = hello_imgui.RunnerParams()
    runner_params.callbacks.show_gui = lambda: example.OnFrame()
    runner_params.callbacks.post_init = lambda: example.OnStart()
    runner_params.callbacks.before_exit = lambda: example.OnStop()
    runner_params.app_window_params.window_size = imgui.ImVec2(1200.0, 800.0)
    hello_imgui.run(runner_params)

    example.OnStop()


if __name__ == "__main__":
    main()
