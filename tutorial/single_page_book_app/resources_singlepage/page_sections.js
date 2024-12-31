export function updatePageSections() {
    const contentArea = document.getElementById("content-area");
    const h2Elements = contentArea.querySelectorAll("h2");
    const sectionsContainer = document.querySelector(".sections-sidebar");

    // Clear previous breadcrumbs
    sectionsContainer.innerHTML = "";

    // Create a list of H2 headings as vertical links
    h2Elements.forEach((h2) => {
        if (!h2.id) {
            // Create a slug from the text if no ID exists
            const slug = h2.textContent.toLowerCase().replace(/\s+/g, '-');
            h2.id = slug;
        }

        const link = document.createElement("a");
        link.href = `#${h2.id}`;
        link.textContent = h2.textContent;
        sectionsContainer.appendChild(link);
    });
}
