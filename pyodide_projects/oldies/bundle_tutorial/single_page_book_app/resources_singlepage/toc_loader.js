import { navigate } from "./navig.js";

let gToc;

export function tocRoot() {
    return gToc.root;
}

export async function initTOC() {
    const response = await fetch("resources_singlepage/generated_toc.json");
    gToc = await response.json();
    const tocSidebar = document.getElementById("toc-sidebar");

    _buildTocList(gToc, tocSidebar);
}

function _buildTocList(toc, container) {
    const ul = document.createElement("ul");

    // Root page
    const rootLi = _createTocItem(toc.root);
    ul.appendChild(rootLi);

    // Chapters
    toc.chapters.forEach(chapter => {
        const li = _createTocItem(chapter, true); // Add `true` for collapsible chapters
        ul.appendChild(li);

        if (chapter.sections) {
            const subUl = document.createElement("ul");
            subUl.classList.add("subsections"); // Add class for styling
            subUl.style.display = "none"; // Initially hide subsections

            chapter.sections.forEach(section => {
                const subLi = _createTocItem(section);
                subUl.appendChild(subLi);
            });

            li.appendChild(subUl);

            // Attach toggle behavior and page load to links in chapters
            const chapterLink = li.querySelector("a");
            chapterLink.addEventListener("click", (e) => {
                e.preventDefault();
                _toggleSubsections(subUl, li); // Expand or collapse subsections
                navigate(chapter.file ); // Load chapter page
            });
        }
    });

    container.appendChild(ul);
}

function _createTocItem(item, isChapter = false) {
    const li = document.createElement("li");
    const link = document.createElement("a");
    link.href = "#";
    link.textContent = item.title || item.file; // Fallback if title not found
    link.classList.add(isChapter ? "chapter-link" : "section-link");
    link.addEventListener("click", (e) => {
        e.preventDefault();
        if (!isChapter) {
            navigate(item.file); // Load the page if it's a section
        }
    });
    li.appendChild(link);
    return li;
}

function _toggleSubsections(subUl, currentLi) {
    // Collapse all other subsections
    const allSubsections = document.querySelectorAll(".subsections");
    allSubsections.forEach(ul => {
        if (ul !== subUl) {
            ul.style.display = "none";
            ul.parentElement.classList.remove("expanded");
        }
    });

    // Toggle the current subsection
    const isVisible = subUl.style.display === "block";
    subUl.style.display = isVisible ? "none" : "block";
    currentLi.classList.toggle("expanded", !isVisible);
}
