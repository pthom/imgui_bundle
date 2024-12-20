import { marked } from "marked";
import { baseUrl } from "marked-base-url";
import { updateBreadcrumbs } from "./breadcrumbs.js";

export async function loadPage(mdPath) {
    const baseUrlPath = mdPath.substring(0, mdPath.lastIndexOf('/') + 1);
    marked.use(baseUrl(baseUrlPath));

    const response = await fetch(mdPath);
    const mdText = await response.text();
    const html = marked.parse(mdText);

    const contentArea = document.getElementById("content-area");
    contentArea.innerHTML = html;

    updateBreadcrumbs(); // after content is loaded
}
