import { initTOC, tocRoot } from "./toc_loader.js";
import { loadPage } from "./page_loader.js";
import { initializeCodeMirrorEditors } from "./code_editor"
import {registerCanvasDragEvents} from "./canvas_drag"
import { registerSidebarToggle } from "./toggle_sidebars.js";

async function initializeAll() {
    await initTOC();
    registerCanvasDragEvents();
    registerSidebarToggle();
    initializeCodeMirrorEditors();

    const rootPage = tocRoot()
    loadPage(rootPage.file + ".md");
}

document.addEventListener("DOMContentLoaded", initializeAll);
