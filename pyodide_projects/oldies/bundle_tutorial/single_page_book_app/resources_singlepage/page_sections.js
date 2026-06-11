// Toggle contents panel logic
const pageSectionsBtn = document.getElementById("page-sections-btn");
const pageSectionsPanel = document.getElementById("page-sections-panel");
let pageSectionsPanelVisible = false;

export function registerPageSectionEvents() {
    pageSectionsBtn.addEventListener("click", (e) => {
        pageSectionsPanelVisible = !pageSectionsPanelVisible;
        pageSectionsPanel.classList.toggle("active", pageSectionsPanelVisible);
        e.stopPropagation();
    });

    // Close the panel when clicking outside
    document.addEventListener("click", (e) => {
        if (pageSectionsPanelVisible && !pageSectionsPanel.contains(e.target) && e.target !== pageSectionsBtn) {
            pageSectionsPanelVisible = false;
            pageSectionsPanel.classList.remove("active");
        }
    });
}


export function updatePageSections() {
    const contentArea       = document.getElementById("content-area");
    const h2Elements        = contentArea.querySelectorAll("h2");
    const sectionsContainer = document.getElementById("page-sections-panel");

    /* remember where the user was */
    const prevScrollTop = sectionsContainer.scrollTop;

    /* rebuild the list */
    sectionsContainer.innerHTML = "";
    const frag = document.createDocumentFragment();

    h2Elements.forEach((h2) => {
        if (!h2.id) {
            h2.id = h2.textContent
                .toLowerCase()
                .replace(/\s+/g, "-");
        }
        const link   = document.createElement("a");
        link.href    = `#${h2.id}`;
        link.textContent = h2.textContent;
        frag.appendChild(link);

        // Add event listener to scroll to the section
        // (the default browser behavior does not work here: it scrolls past the link,
        //  because of the main-header position:sticky flag)
        link.addEventListener("click", (ev) => {
            ev.preventDefault();                 // ← stop default hash jump

            const id          = link.getAttribute("href").slice(1);
            const target      = document.getElementById(id);
            const wrapper     = document.getElementById("content-area-wrapper");

            if (target) {
                /* distance from top of wrapper to heading, minus header height */
                const y = target.getBoundingClientRect().top
                    - wrapper.getBoundingClientRect().top
                    + wrapper.scrollTop;

                wrapper.scrollTo({ top: y, behavior: "smooth" });
            }
        });
    });

    sectionsContainer.appendChild(frag);

    /* restore scroll position so the list doesn’t jump */
    sectionsContainer.scrollTop = prevScrollTop;


}
