export function registerSidebarToggle() {
    const toggleButton = document.getElementById("toggle-sidebar");
    const sidebar = document.getElementById("toc-sidebar");
    const layoutContainer = document.querySelector(".layout-container");

    if (!toggleButton || !sidebar || !layoutContainer) {
        console.warn("Sidebar toggle elements are missing.");
        return;
    }

    // Handle toggle button click
    toggleButton.addEventListener("click", () => {
        sidebar.classList.toggle("hidden");
        layoutContainer.classList.toggle("sidebar-hidden");
    });
}
