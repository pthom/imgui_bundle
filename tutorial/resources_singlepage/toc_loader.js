import { loadPage } from "./page_loader.js";

export async function initTOC() {
    const response = await fetch("toc.json");
    const toc = await response.json();
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
    buildTocList(toc, tocSidebar);
}

function buildTocList(toc, container) {
    const ul = document.createElement("ul");

    // root page
    const rootLi = createTocItem(toc.root);
    ul.appendChild(rootLi);

    // chapters
    toc.chapters.forEach(chapter => {
        const li = createTocItem(chapter.file);
        ul.appendChild(li);

        if (chapter.sections) {
            const subUl = document.createElement("ul");
            chapter.sections.forEach(section => {
                const subLi = createTocItem(section.file);
                subUl.appendChild(subLi);
            });
            li.appendChild(subUl);
        }
    });

    container.appendChild(ul);
}

function createTocItem(mdPath) {
    const li = document.createElement("li");
    const link = document.createElement("a");
    link.href = "#"; // no real nav, just a link
    link.textContent = mdPath;
    link.addEventListener("click", (e) => {
        e.preventDefault();
        loadPage(mdPath + ".md");
    });
    li.appendChild(link);
    return li;
}
