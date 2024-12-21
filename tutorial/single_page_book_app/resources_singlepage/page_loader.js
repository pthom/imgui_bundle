import { marked } from "marked";
import { baseUrl } from "marked-base-url";
import { initializeCodeMirrorEditors, processLiteralIncludesInMarkdown } from "./code_editor.js";
import { updateBreadcrumbs } from "./breadcrumbs.js";

// Custom renderer to preserve `{literalinclude}` directives
const renderer = new marked.Renderer();

renderer.code = (code, lang, escaped) => {
    // Return the code block as-is with a `literalinclude` class
    return `<pre><code class="literalinclude">${code}</code></pre>`;
};

export async function loadPage(mdPath) {
    mdPath = "jbook/" + mdPath;
    const baseUrlPath = mdPath.substring(0, mdPath.lastIndexOf('/') + 1);

    // Fetch the Markdown file
    const response = await fetch(mdPath);
    let mdText = await response.text();

    // Process `{literalinclude}` before parsing Markdown
    mdText = await processLiteralIncludesInMarkdown(mdText, baseUrlPath);

    // Parse the Markdown into HTML
    marked.use(baseUrl(baseUrlPath));
    const html = marked.parse(mdText);

    // Update the content area
    const contentArea = document.getElementById("content-area");
    contentArea.innerHTML = html;

    initializeCodeMirrorEditors();

    updateBreadcrumbs(); // after content is loaded
}

