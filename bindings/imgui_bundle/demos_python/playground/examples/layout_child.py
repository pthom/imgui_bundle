"""# Resizable Layouts with begin_child

ImGui's `begin_child` creates scrollable, nestable sub-regions.
With `ChildFlags_.resize_x` or `resize_y`, the user can **drag dividers** to resize panels.

**Key pattern:**
```python
imgui.begin_child("left", size=(width, 0),  child_flags=imgui.ChildFlags_.resize_x)
# ... left content ...
imgui.end_child()
imgui.same_line()
imgui.begin_child("right")
# ... right content ...
imgui.end_child()
```
"""
from imgui_bundle import imgui, immapp, ImVec4


# Sample content for each panel
def sidebar_content():
    imgui.text("Sidebar")
    imgui.separator()
    items = ["Home", "Dashboard", "Settings", "Users", "Reports", "Help"]
    for i, item in enumerate(items):
        # Selectable: a clickable text item
        imgui.selectable(item, i == 0)


def main_content():
    imgui.text("Main Area")
    imgui.separator()
    imgui.text_wrapped("This is the main content area. It fills the remaining space after the sidebar. Drag the left border "
        "to resize the sidebar.")
    imgui.spacing()
    # Some sample widgets
    imgui.button("Action 1")
    imgui.same_line()
    imgui.button("Action 2")
    imgui.same_line()
    imgui.button("Action 3")
    imgui.spacing()
    # A simple table
    if imgui.begin_table("##data", 3,
            imgui.TableFlags_.borders| imgui.TableFlags_.row_bg):
        imgui.table_setup_column("Name")
        imgui.table_setup_column("Value")
        imgui.table_setup_column("Status")
        imgui.table_headers_row()
        for row in range(5):
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text(f"Item {row + 1}")
            imgui.table_next_column()
            imgui.text(f"{(row + 1) * 42}")
            imgui.table_next_column()
            ok = row % 3 != 2
            color = ImVec4(0.3, 0.8, 0.3, 1) if ok else ImVec4(0.8, 0.3, 0.3, 1)
            imgui.text_colored(color, "OK" if ok else "Error")
        imgui.end_table()


def bottom_content():
    imgui.text("Bottom Panel")
    imgui.separator()
    imgui.text_disabled(
        "Drag the top border to resize this panel.")
    # Simulate a log output
    for i in range(8):
        level = ["INFO", "DEBUG", "WARN"][i % 3]
        imgui.text_disabled(f"[{level}] Log message {i + 1}...")


def gui():
    # Documentation panel
    immapp.render_markdown_doc_panel(__doc__, height_em=18)

    em = imgui.get_font_size()

    # This demo builds a classic app layout using only `begin_child`:
    # ```
    # ┌────────────┬──────────────────┐
    # │  Sidebar   │                  │
    # │ (resize_x) │   Main area      │
    # │            │                  │
    # ├────────────┴──────────────────┤
    # │  Bottom panel (resize_y)      │
    # └───────────────────────────────┘
    # ```

    # --- Top row: sidebar + main (resizable height) ---
    # resize_y on this child makes its bottom border draggable.
    # The bottom panel fills the remaining space below.
    # Use 65% of available height for the top row
    avail = imgui.get_content_region_avail()
    top_h = avail.y * 0.65
    imgui.begin_child("##top_row", (0, top_h),
        child_flags=imgui.ChildFlags_.resize_y)

    # Sidebar (resizable width)
    sidebar_w = em * 10  # initial width
    imgui.begin_child(
        "##sidebar", size=(sidebar_w, 0),
        child_flags=(imgui.ChildFlags_.borders | imgui.ChildFlags_.resize_x))
    sidebar_content()
    imgui.end_child()

    # Main area (fills remaining width)
    imgui.same_line()
    imgui.begin_child("##main", child_flags=imgui.ChildFlags_.borders)
    main_content()
    imgui.end_child()

    imgui.end_child()  # top_row

    # --- Bottom panel (fills remaining space) ---
    imgui.begin_child("##bottom", child_flags=imgui.ChildFlags_.borders)
    bottom_content()
    imgui.end_child()


def main():
    immapp.run(
        gui,
        window_size=(1000, 700),
        window_title="Resizable Layouts",
        with_markdown=True,
        ini_disable=True)


if __name__ == "__main__":
    main()
