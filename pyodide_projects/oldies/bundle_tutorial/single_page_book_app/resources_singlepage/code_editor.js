import { EditorState } from "@codemirror/state";
import { EditorView, lineNumbers, highlightSpecialChars, drawSelection, dropCursor, rectangularSelection, highlightActiveLine } from "@codemirror/view";
import { defaultHighlightStyle, syntaxHighlighting } from "@codemirror/language";
import { oneDark, oneDarkHighlightStyle } from "@codemirror/theme-one-dark";
import { python } from "@codemirror/lang-python";
import { cpp } from "@codemirror/lang-cpp";
import { marked } from "marked";
import { runPythonCode } from "./pyodide_helper.js";


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
                // console.log("Found codes_include directive:", match[1]); // Log matched directive
                const baseName = match[1].trim();

                // Generate HTML as a string
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
                // console.log("Generated HTML for tabs:", tabsHtml); // Debug log
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

function _createEditorRunPythonCodeButton(editorView) {
    const runButton = document.createElement("button");
    runButton.textContent = "Run Python Code";
    runButton.classList.add("run-python-button");

    runButton.addEventListener("click", () => {
        const currentCode = editorView.state.doc.toString();
        runPythonCode(currentCode);
    });
    return runButton;
}

async function _initializeCodeMirrorEditors(baseUrlPath) {
    const containers = document.querySelectorAll(".code-editor-tab-container");

    for (const container of containers) {
        const tabPanes = container.querySelectorAll(".code-editor-tab-pane");

        for (const tabPane of tabPanes) {
            const filePath = tabPane.dataset.file;
            const language = tabPane.dataset.language.toLowerCase();

            try {
                // Combine baseUrlPath + filePath properly
                let fullPath = new URL(filePath, `${window.location.origin}/${baseUrlPath}/`).toString();
                const fileResponse = await fetch(fullPath);
                if (!fileResponse.ok) {
                    console.warn(`File not found: ${fullPath}`);
                    continue;
                }

                const codeContent = await fileResponse.text();

                // Create a wrapper for CodeMirror so we can set resize/height on it
                const wrapper = document.createElement("div");
                wrapper.classList.add("codemirror-wrapper");

                // Append this wrapper to the pane’s placeholder
                const cmPlaceholder = tabPane.querySelector(".codemirror-placeholder");
                cmPlaceholder.appendChild(wrapper);

                const isDarkMode = document.body.classList.contains("dark-mode");

                // Build up CodeMirror extensions
                const extensions = [
                    lineNumbers(),
                    highlightSpecialChars(),
                    drawSelection(),
                    dropCursor(),
                    rectangularSelection(),
                    highlightActiveLine(),
                    isDarkMode
                        ? syntaxHighlighting(oneDarkHighlightStyle)
                        : syntaxHighlighting(defaultHighlightStyle),
                ];

                if (language === "python") {
                    extensions.push(python());
                } else if ((language === "cpp") || (language === "c++")){
                    extensions.push(cpp());
                }

                // Detect if dark mode is active
                if (isDarkMode) {
                    extensions.push(oneDark);
                }

                // Create the editor in the wrapper
                const editorView = new EditorView({
                    state: EditorState.create({
                        doc: codeContent,
                        extensions,
                    }),
                    parent: wrapper, // set the parent as our new wrapper
                });

                // *** Adjust initial height based on line count ***
                const lineCount = codeContent.split("\n").length;
                const maxLines = 20; // limit to 20 lines
                const chosenLines = Math.min(lineCount, maxLines);

                // We'll assume ~1.4em line height. Adjust as needed or measure programmatically
                const lineHeightPx = 22; // approx
                const initialHeightPx = chosenLines * lineHeightPx;

                // Now style the wrapper
                wrapper.style.resize = "vertical";
                wrapper.style.overflow = "auto";
                wrapper.style.maxHeight = "600px"; // some overall maximum if you like
                wrapper.style.height = `${initialHeightPx}px`; // initial size

                // If it's a Python editor, add a run button
                if (language === "python") {
                    const runButton = _createEditorRunPythonCodeButton(editorView);
                    tabPane.appendChild(runButton);
                }

            } catch (error) {
                console.error(`Failed to fetch file: ${filePath}`, error);
                tabPane.innerHTML = `<div class="code-editor-tab-error">Error loading file: ${filePath}</div>`;
            }
        }
    }

    _setupCodeEditorTabs(containers);
}

function _setupCodeEditorTabs(containers) {
    containers.forEach((container) => {
        const buttons = container.querySelectorAll(".code-editor-tab-button");
        const panes = container.querySelectorAll(".code-editor-tab-pane");

        buttons.forEach((button) => {
            // console.log(`Attaching click event to button: ${button.dataset.tab}`); // Debugging log
            button.addEventListener("click", () => {
                const targetTab = button.dataset.tab;
                // console.log(`Tab clicked: ${targetTab}`); // Debugging log

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


export async function renderMarkdownAndCodeEditors(mdText, baseUrlPath) {
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
    // console.log("Final Rendered HTML:", renderedHtml);

    // Update the content area with the rendered HTML
    const contentArea = document.getElementById("content-area");
    contentArea.innerHTML = renderedHtml;

    // Scroll to the top of the content area
    const wrapper = document.getElementById("content-area-wrapper");
    wrapper.scrollTo({ top: 0 });

    // Initialize CodeMirror editors for the placeholders
    //await _initializeCodeMirrorEditors(baseUrlPath);
    await _initializeCodeMirrorEditors("jbook");
}
