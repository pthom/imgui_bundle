"""# Deploy to the Web: Minimal HTML Example

Dear ImGui Bundle apps can run entirely in the browser using [Pyodide](https://pyodide.org). The HTML file below is a **complete, self-contained app** in about 80 lines - no server, no build step.

You can copy this HTML, save it as a `.html` file, and open it in any browser. Edit the Python code inside to make it your own.

* **Try it live:** [Open the minimal example](https://traineq.org/imgui_bundle_online/projects/min_bundle_pyodide_app/demo_heart.html)
* **View its source:** [minimal example source](https://traineq.org/imgui_bundle_online/projects/min_bundle_pyodide_app/demo_heart.source.txt)

**How it works:**
1. Loads Pyodide (Python runtime for the browser) from a CDN
2. Installs `imgui-bundle` via micropip
3. Runs the embedded Python code, which creates a full ImGui app with a canvas

**Links:**
- [Pyodide deployment docs](https://pthom.github.io/imgui_bundle/python/python-pyodide/)
"""
from imgui_bundle import (
    imgui, immapp,
    imgui_color_text_edit as ed, imgui_md,
)


class AppState:
    def __init__(self):
        self.editor = ed.TextEditor()
        # Download the minimal HTML example source
        html_bytes = immapp.download_url_bytes("https://traineq.org/imgui_bundle_online/projects/min_bundle_pyodide_app/demo_heart.html")
        if len(html_bytes) > 0:
            self.editor.set_text(html_bytes.decode("utf-8"))
        else:
            self.editor.set_text("<!-- Failed to download HTML source -->")
        self.editor.set_read_only_enabled(True)
        self.editor.set_show_whitespaces_enabled(False)


def gui(state: AppState) -> None:
    # Documentation panel
    immapp.render_markdown_doc_panel(__doc__, height_em=16)

    # Copy button
    # if imgui.button("Copy HTML to clipboard"):
    #     imgui.set_clipboard_text(state.editor.get_text())
    # imgui.same_line()
    # imgui.text_disabled(
    #     "(save as .html and open in a browser)")

    # HTML source viewer with code font
    code_font = imgui_md.get_code_font()
    imgui.push_font(code_font.font, code_font.size)
    avail = imgui.get_content_region_avail()
    state.editor.render("##html_viewer", avail, False)
    imgui.pop_font()


def main():
    state = AppState()
    immapp.run(
        lambda: gui(state),
        window_size=(1000, 700),
        window_title="Minimal HTML Example",
        with_markdown=True,
        ini_disable=True)


if __name__ == "__main__":
    main()
