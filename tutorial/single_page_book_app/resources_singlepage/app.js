import { initTOC, tocRoot } from "./toc_loader.js";
import { loadPage } from "./page_loader.js";
import {registerCanvasDragEvents} from "./canvas_drag"
import { registerSidebarToggle } from "./toggle_sidebars.js";
import { initializePyodideHelper, runPythonCode } from "./pyodide_helper.js";

async function initializeAll() {
    await initTOC();
    registerCanvasDragEvents();
    registerSidebarToggle();
    const rootPage = tocRoot()
    loadPage(rootPage.file + ".md");

    await initializePyodideHelper();

    // Test Python code
    await runPythonCode(`
import sys
print(sys.version)
print("Hello from Python!")

from imgui_bundle import imgui, hello_imgui
def gui():
    imgui.text("Hello, world!")
    imgui.show_demo_window()

hello_imgui.run(gui)
`);


}

document.addEventListener("DOMContentLoaded", initializeAll);
