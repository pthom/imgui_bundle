import { marked } from "marked";
import { baseUrl } from "marked-base-url";
import { updateBreadcrumbs } from "./breadcrumbs.js";

// Add CodeMirror imports
import { EditorState } from "@codemirror/state";
import { EditorView } from "@codemirror/view";
import { python } from "@codemirror/lang-python";
import { cpp } from "@codemirror/lang-cpp";
import { basicSetup } from "codemirror"; // Import basicSetup from codemirror

export async function loadPage(mdPath) {
    mdPath = "jbook/" + mdPath;
    const baseUrlPath = mdPath.substring(0, mdPath.lastIndexOf('/') + 1);
    marked.use(baseUrl(baseUrlPath));

    const response = await fetch(mdPath);
    const mdText = await response.text();

    // Parse the Markdown into HTML
    let html = marked.parse(mdText);

    // Process `{literalinclude}` directives
    html = await processLiteralIncludes(html, baseUrlPath);

    const contentArea = document.getElementById("content-area");
    contentArea.innerHTML = html;

    // After loading, initialize CodeMirror for imported blocks
    initializeCodeMirrorEditors();

    updateBreadcrumbs(); // after content is loaded
}

async function processLiteralIncludes(html, baseUrlPath) {
    // Use a DOM parser to work with the HTML
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, "text/html");

    // Find all `{literalinclude}` directives in the HTML
    const codeBlocks = doc.querySelectorAll("code");

    for (const codeBlock of codeBlocks) {
        const textContent = codeBlock.textContent;

        // Check if the block contains a `{literalinclude}` directive
        const match = textContent.match(/\{literalinclude\}\s+(.*)/);
        if (match) {
            const filePath = match[1].trim(); // Extract the file path

            // Fetch the file content
            try {
                const fileResponse = await fetch(baseUrlPath + filePath);
                const fileContent = await fileResponse.text();

                // Replace the `{literalinclude}` directive with the actual code
                const preElement = document.createElement("pre");
                const newCodeBlock = document.createElement("code");
                newCodeBlock.textContent = fileContent;

                // Add classes for syntax highlighting
                if (filePath.endsWith(".py")) {
                    newCodeBlock.classList.add("language-python");
                } else if (filePath.endsWith(".cpp")) {
                    newCodeBlock.classList.add("language-cpp");
                }

                preElement.appendChild(newCodeBlock);
                codeBlock.replaceWith(preElement);
            } catch (error) {
                console.error(`Failed to fetch ${filePath}:`, error);
            }
        }
    }

    return doc.body.innerHTML; // Return the updated HTML
}

export async function initializeCodeMirrorEditors() {
    const codeBlocks = document.querySelectorAll("pre code");

    for (const codeBlock of codeBlocks) {
        const mode = codeBlock.classList.contains("language-python")
            ? python()
            : codeBlock.classList.contains("language-cpp")
                ? cpp()
                : null;

        if (mode) {
            // Replace the `<code>` block with a CodeMirror editor
            const parent = codeBlock.parentNode;
            const editor = new EditorView({
                state: EditorState.create({
                    doc: codeBlock.textContent,
                    extensions: [basicSetup, mode], // Use `basicSetup` from codemirror
                }),
                parent, // Attach the editor to the parent element
            });

            parent.replaceChild(editor.dom, codeBlock);
        }
    }
}