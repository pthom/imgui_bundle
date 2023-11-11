# Adapted from
# https://github.com/thedmd/imgui-node-editor/blob/master/examples/basic-interaction-example/basic-interaction-example.cpp
from __future__ import annotations
from typing import List
from dataclasses import dataclass
from imgui_bundle import (
    imgui,
    imgui_node_editor as ed,
)
from imgui_bundle.immapp import static, run_anon_block


class IdProvider:
    """A simple utility to obtain unique ids, and to be able to restore them at each frame"""

    _next_id: int = 1

    def next_id(self):
        """Gets a new unique id"""
        r = self._next_id
        self._next_id += 1
        return r

    def reset(self):
        """Resets the counter (called at each frame)"""
        self._next_id = 1


ID = IdProvider()


class ImGuiEx:
    """Some additional tools for ImGui. Provide columns via begin/end_group"""

    @staticmethod
    def begin_column():
        imgui.begin_group()

    @staticmethod
    def next_column():
        imgui.end_group()
        imgui.same_line()
        imgui.begin_group()

    @staticmethod
    def end_column():
        imgui.end_group()


@dataclass
class LinkInfo:
    id: ed.LinkId
    input_id: ed.PinId
    output_id: ed.PinId


class DemoNodeEditor:
    # Struct to hold basic information about connection between
    # pins. Note that connection (aka. link) has its own ID.
    # This is useful later with dealing with selections, deletion
    # or other operations.

    # Flag set for first frame only, some action need to be executed once.
    is_first_frame: bool = True
    # List of live links. It is dynamic unless you want to create read-only view over nodes.
    links: List[LinkInfo]
    # Counter to help generate link ids. In real application this will probably
    # be based on pointers to user data structure.
    next_link_id: int = 100

    def __init__(self):
        self.links = []

    def on_frame(self):
        ID.reset()
        # io = imgui.get_io()
        # imgui.text(f"FPS: {io.framerate}FPS")

        imgui.separator()

        # Start interaction with editor.
        ed.begin("My Editor", imgui.ImVec2(0.0, 0.0))

        #######################################################################
        # 1) Commit known data to editor
        #######################################################################
        # Submit Node A
        node_a_id = ed.NodeId(ID.next_id())
        node_a_input_pin_id = ed.PinId(ID.next_id())
        node_a_output_pin_id = ed.PinId(ID.next_id())

        if self.is_first_frame:
            ed.set_node_position(node_a_id, imgui.ImVec2(200, -300))

        ed.begin_node(node_a_id)

        @run_anon_block
        def _fill_node_a():  # This function emulates an anonymous block and
            imgui.text("Node A")  # will be evaluated right after its definition
            ed.begin_pin(node_a_input_pin_id, ed.PinKind.input)
            imgui.text("-> In")
            ed.end_pin()
            imgui.same_line()
            ed.begin_pin(node_a_output_pin_id, ed.PinKind.output)
            imgui.text("Out ->")
            ed.end_pin()

        ed.end_node()

        # Submit Node B
        node_b_id = ed.NodeId(ID.next_id())
        node_b_input_pin_id1 = ed.PinId(ID.next_id())
        node_b_input_pin_id2 = ed.PinId(ID.next_id())
        node_b_output_pin_id = ed.PinId(ID.next_id())

        if self.is_first_frame:
            ed.set_node_position(node_b_id, imgui.ImVec2(210, 60))

        ed.begin_node(node_b_id)

        @run_anon_block
        def _fill_node_b():  # This function emulates an anonymous block and
            imgui.text("Node B")  # will be evaluated right after its definition
            ImGuiEx.begin_column()
            ed.begin_pin(node_b_input_pin_id1, ed.PinKind.input)
            imgui.text("-> In1")
            ed.end_pin()
            ed.begin_pin(node_b_input_pin_id2, ed.PinKind.input)
            imgui.text("-> In2")
            ed.end_pin()
            ImGuiEx.next_column()
            ed.begin_pin(node_b_output_pin_id, ed.PinKind.output)
            imgui.text("Out ->")
            ed.end_pin()
            ImGuiEx.end_column()

        ed.end_node()

        # Submit Links
        for linkInfo in self.links:
            ed.link(linkInfo.id, linkInfo.input_id, linkInfo.output_id)

        #######################################################################
        # 2) Handle interactions
        #######################################################################
        # Handle creation action, returns true if editor want to create new object (node or link)
        if ed.begin_create():

            input_pin_id = ed.PinId()
            output_pin_id = ed.PinId()

            if ed.query_new_link(input_pin_id, output_pin_id):
                # QueryNewLink returns true if editor want to create new link between pins.
                #
                # Link can be created only for two valid pins, it is up to you to
                # validate if connection make sense. Editor is happy to make any.
                #
                # Link always goes from input to output. User may choose to drag
                # link from output pin or input pin. This determines which pin ids
                # are valid and which are not:
                #   * input valid, output invalid - user started to drag new link from input pin
                #   * input invalid, output valid - user started to drag new link from output pin
                #   * input valid, output valid   - user dragged link over other pin, can be validated

                if input_pin_id and output_pin_id:  # both are valid, let's accept link
                    # ed.AcceptNewItem(): return true when user release mouse button.
                    if ed.accept_new_item():
                        # Since we accepted new link, lets add one to our list of links.
                        link_info = LinkInfo(
                            ed.LinkId(self.next_link_id), input_pin_id, output_pin_id
                        )
                        self.next_link_id += 1
                        self.links.append(link_info)

                        # Draw new link.
                        ed.link(
                            self.links[-1].id,
                            self.links[-1].input_id,
                            self.links[-1].output_id,
                        )

                    # You may choose to reject connection between these nodes
                    # by calling ed.RejectNewItem():. This will allow editor to give
                    # visual feedback by changing link thickness and color.

            ed.end_create()  # Wraps up object creation action handling.

        # Handle deletion action
        if ed.begin_delete():

            # There may be many links marked for deletion, let's loop over them.
            deleted_link_id = ed.LinkId()
            while ed.query_deleted_link(deleted_link_id):
                # If you agree that link can be deleted, accept deletion.
                if ed.accept_deleted_item():
                    # Then remove link from your data.
                    for link in self.links:
                        if link.id == deleted_link_id:
                            self.links.remove(link)
                            break
                # You may reject link deletion by calling:
                # ed.reject_deleted_item()

            ed.end_delete()  # Wrap up deletion action

        # End of interaction with editor.
        ed.end()

        if self.is_first_frame:
            ed.navigate_to_content(0.0)

        self.is_first_frame = False

        # imgui.show_metrics_window()


@static(demo_node_editor=None)
def demo_gui():
    statics = demo_gui
    if statics.demo_node_editor is None:
        statics.demo_node_editor = DemoNodeEditor()
    statics.demo_node_editor.on_frame()


def main():
    import os

    this_dir = os.path.dirname(__file__)
    config = ed.Config()
    config.settings_file = this_dir + "/demo_node_editor_basic.json"
    from imgui_bundle import immapp

    immapp.run(
        demo_gui,
        with_node_editor_config=config,
        with_markdown=True,
        window_size=(800, 600),
    )


if __name__ == "__main__":
    main()
