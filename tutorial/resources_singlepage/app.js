import { initTOC, tocRoot } from "./toc_loader.js";
import { initResizer } from "./resizer.js";
import { loadPage } from "./page_loader.js";
import {registerCanvasDragEvents} from "./canvas_drag"
async function initializeAll() {
    await initTOC();
    initResizer();
    registerCanvasDragEvents();

    const rootPage = tocRoot()
    loadPage(rootPage.file + ".md");
}

document.addEventListener("DOMContentLoaded", initializeAll);
