import { EditorState } from "@codemirror/state";
import { EditorView, lineNumbers, highlightSpecialChars, drawSelection, dropCursor, rectangularSelection, highlightActiveLine } from "@codemirror/view";
import { defaultHighlightStyle, syntaxHighlighting } from "@codemirror/language";
import { python } from "@codemirror/lang-python";
import { cpp } from "@codemirror/lang-cpp";
import { marked } from "marked";

// _ stands for private function to this module. Let's adopt this convention!

// Process `{codes_include}` directives in the raw Markdown
// Should this be public and called from page_loader.js????
async function _processCodesIncludeInMarkdown(mdText, baseUrlPath) {
    const lines = mdText.split("\n");
    const processedLines = [];
    let insideCodesIncludeBlock = false;

    for (const line of lines) {
        if (line.trim().startsWith("```{codes_include}")) {
            const match = line.match(/```{codes_include}\s+(.*)/);
            if (match) {
                console.log("Found codes_include directive:", match[1]); // Log matched directive
                const baseName = match[1].trim();

                // Generate HTML as a string
//                 const tabsHtml = `
// <div class="code-editor-tab-container" data-base-name="${baseName}">
//     <div class="code-editor-tab-buttons">
//         <button class="code-editor-tab-button active" data-tab="Python">Python</button>
//         <button class="code-editor-tab-button" data-tab="C++">C++</button>
//     </div>
//     <div class="code-editor-tab-content">
//         <div class="code-editor-tab-pane" data-language="Python" data-file="${baseName}.py">
//             <div class="codemirror-placeholder" data-language="python"></div>
//         </div>
//         <div class="code-editor-tab-pane hidden" data-language="C++" data-file="${baseName}.cpp">
//             <div class="codemirror-placeholder" data-language="cpp"></div>
//         </div>
//     </div>
// </div>`;
                const tabsHtml = `
<div class="code-editor-tab-container" data-base-name="${baseName}">
    <div class="code-editor-tab-buttons">
        <button class="code-editor-tab-button active" data-tab="Python">Python</button>
        <button class="code-editor-tab-button" data-tab="C++">C++</button>
    </div>
    <div class="code-editor-tab-content">
        <div class="code-editor-tab-pane" data-language="Python" data-file="${baseName}.py">
            <div class="codemirror-placeholder" data-language="python"></div>
        </div>
        <div class="code-editor-tab-pane hidden" data-language="C++" data-file="${baseName}.cpp">
            <div class="codemirror-placeholder" data-language="cpp"></div>
        </div>
    </div>
</div>`;


                console.log("Generated HTML for tabs:", tabsHtml); // Debug log
                processedLines.push(tabsHtml);
            }
            insideCodesIncludeBlock = true;
        } else if (insideCodesIncludeBlock && line.trim() === "```") {
            insideCodesIncludeBlock = false;
        } else if (!insideCodesIncludeBlock) {
            processedLines.push(line); // Keep other lines unchanged
        }
    }

    return processedLines.join("\n");
}

async function _initializeCodeMirrorEditors(baseUrlPath) {
    const containers = document.querySelectorAll(".code-editor-tab-container");

    console.log("Found Code Editor Containers:", containers.length); // Debug log

    for (const container of containers) {
        const tabPanes = container.querySelectorAll(".code-editor-tab-pane");

        console.log("Found Tab Panes:", tabPanes.length); // Debug log

        for (const tabPane of tabPanes) {
            const filePath = tabPane.dataset.file;
            const language = tabPane.dataset.language.toLowerCase();

            console.log(`Initializing CodeMirror for file: ${filePath}, language: ${language}`); // Debug log

            try {
                const fileResponse = await fetch(`${baseUrlPath}${filePath}`);
                if (!fileResponse.ok) {
                    console.warn(`File not found: ${baseUrlPath}${filePath}`);
                    continue;
                }

                const codeContent = await fileResponse.text();
                console.log(`Fetched Code Content for ${filePath}:\n`, codeContent); // Debug log

                const cmPlaceholder = tabPane.querySelector(".codemirror-placeholder");

                const extensions = [
                    lineNumbers(),
                    syntaxHighlighting(defaultHighlightStyle),
                    highlightSpecialChars(),
                    drawSelection(),
                    dropCursor(),
                    rectangularSelection(),
                    highlightActiveLine(),
                ];

                if (language === "python") {
                    extensions.push(python());
                } else if (language === "cpp") {
                    extensions.push(cpp());
                }

                new EditorView({
                    state: EditorState.create({
                        doc: codeContent,
                        extensions,
                    }),
                    parent: cmPlaceholder,
                });
            } catch (error) {
                console.error(`Failed to fetch file: ${filePath}`, error);
                tabPane.innerHTML = `<div class="code-editor-tab-error">Error loading file: ${filePath}</div>`;
            }
        }
    }

    _setupCodeEditorTabs(containers); // Ensure tab setup is called
}

function _setupCodeEditorTabs(containers) {
    containers.forEach((container) => {
        const buttons = container.querySelectorAll(".code-editor-tab-button");
        const panes = container.querySelectorAll(".code-editor-tab-pane");

        buttons.forEach((button) => {
            console.log(`Attaching click event to button: ${button.dataset.tab}`); // Debugging log
            button.addEventListener("click", () => {
                const targetTab = button.dataset.tab;
                console.log(`Tab clicked: ${targetTab}`); // Debugging log

                // Deactivate all buttons and panes
                buttons.forEach((btn) => btn.classList.remove("active"));
                panes.forEach((pane) => pane.classList.add("hidden"));

                // Activate the clicked button and its corresponding pane
                button.classList.add("active");
                const activePane = [...panes].find((pane) => pane.dataset.language === targetTab);
                if (activePane) activePane.classList.remove("hidden");
            });
        });
    });
}


function _addCodeEditorTabEventListeners(container) {
    const buttons = container.querySelectorAll(".code-editor-tab-button");
    const panes = container.querySelectorAll(".code-editor-tab-pane");

    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            const targetTab = button.dataset.tab;

            // Deactivate all buttons and panes
            buttons.forEach(btn => btn.classList.remove("active"));
            panes.forEach(pane => pane.classList.add("hidden"));

            // Activate the clicked button and its corresponding pane
            button.classList.add("active");
            const activePane = [...panes].find(pane => pane.dataset.language === targetTab);
            if (activePane) activePane.classList.remove("hidden");
        });
    });
}


export async function prepareCodeEditors(mdText, baseUrlPath) {
    // Process `{codes_include}` blocks into editor placeholders
    const processedMdText = await _processCodesIncludeInMarkdown(mdText, baseUrlPath);

    // Configure `marked` options
    marked.setOptions({
        gfm: true,
        breaks: true,
        mangle: false,
        headerIds: false,
    });

    // Render the processed Markdown into HTML
    const renderedHtml = marked(processedMdText);

    // Debug log: Final rendered HTML
    console.log("Final Rendered HTML:", renderedHtml);

    // Update the content area with the rendered HTML
    const contentArea = document.getElementById("content-area");
    contentArea.innerHTML = renderedHtml;

    // Initialize CodeMirror editors for the placeholders
    await _initializeCodeMirrorEditors(baseUrlPath);
}
