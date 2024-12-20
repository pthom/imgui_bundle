export function updateBreadcrumbs() {
    const contentArea = document.getElementById("content-area");
    const h2Elements = contentArea.querySelectorAll("h2");
    const breadcrumbContainer = document.getElementById("breadcrumb-container");

    // Clear previous breadcrumbs
    breadcrumbContainer.innerHTML = "";

    // Create a simple list of H2 headings as links
    // Each H2 can have an id (if not, we add one)
    h2Elements.forEach((h2, index) => {
        if (!h2.id) {
            // create a slug from the text
            const slug = h2.textContent.toLowerCase().replace(/\s+/g, '-');
            h2.id = slug;
        }

        const link = document.createElement('a');
        link.href = `#${h2.id}`;
        link.textContent = h2.textContent;
        breadcrumbContainer.appendChild(link);
        breadcrumbContainer.appendChild(document.createTextNode(" | "));
    });

    if (breadcrumbContainer.lastChild) {
        breadcrumbContainer.removeChild(breadcrumbContainer.lastChild); // remove trailing separator
    }
}
