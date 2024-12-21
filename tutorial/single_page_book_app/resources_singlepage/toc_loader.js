import { loadPage } from "./page_loader.js";


// The global `gToc` variable will store the TOC data (from generated_toc.json)
let gToc;

export function tocRoot() {
    return gToc.root;
}

export async function initTOC() {
    const response = await fetch("resources_singlepage/generated_toc.json");
    gToc = await response.json();
    const tocSidebar = document.getElementById("toc-sidebar");

    // Build a simple TOC list from toc's `chapters`
    // toc format example:
    // {
    //   "format": "jb-book",
    //   "root": "discover_immediate",
    //   "chapters": [
    //     { "file": "discover/hello_world", "sections": [...] }
    //   ]
    // }
    _buildTocList(gToc, tocSidebar);
}

function _buildTocList(toc, container) {
    const ul = document.createElement("ul");

    // root page
    const rootLi = _createTocItem(toc.root);
    ul.appendChild(rootLi);

    // chapters
    toc.chapters.forEach(chapter => {
        const li = _createTocItem(chapter);
        ul.appendChild(li);

        if (chapter.sections) {
            const subUl = document.createElement("ul");
            chapter.sections.forEach(section => {
                const subLi = _createTocItem(section.file);
                subUl.appendChild(subLi);
            });
            li.appendChild(subUl);
        }
    });

    container.appendChild(ul);
}

function _createTocItem(item) {
    const li = document.createElement("li");
    const link = document.createElement("a");
    link.href = "#";
    link.textContent = item.title || item.file; // fallback if title not found
    link.addEventListener("click", (e) => {
        e.preventDefault();
        loadPage(item.file + ".md");
    });
    li.appendChild(link);
    return li;
}
