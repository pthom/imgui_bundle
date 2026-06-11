import { marked } from "marked";
import { renderMarkdownAndCodeEditors } from "./code_editor.js";
import { updatePageSections } from "./page_sections.js";

// Custom renderer to preserve `{literalinclude}` directives
const renderer = new marked.Renderer();

renderer.code = (code, _lang, _escaped) => {
    // Return the code block as-is with a `literalinclude` class
    return `<pre><code class="literalinclude">${code}</code></pre>`;
};

export async function loadPage(mdPath) {
    mdPath = "jbook/" + mdPath;
    const baseUrlPath = mdPath.substring(0, mdPath.lastIndexOf('/') + 1);

    // Fetch the Markdown file
    const response = await fetch(mdPath);
    let mdText = await response.text();

    // Process and render Markdown with Code Editors
    await renderMarkdownAndCodeEditors(mdText, baseUrlPath);

    // Update breadcrumbs after the content is loaded
    updatePageSections();
}
