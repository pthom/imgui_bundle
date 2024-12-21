import { EditorState } from "@codemirror/state";
import { EditorView, keymap, highlightSpecialChars, drawSelection, dropCursor, rectangularSelection, highlightActiveLine, lineNumbers } from "@codemirror/view";
import { defaultHighlightStyle, syntaxHighlighting, indentOnInput, bracketMatching, foldGutter } from "@codemirror/language";
import { history, historyKeymap } from "@codemirror/commands";
import { python } from "@codemirror/lang-python";
import { cpp } from "@codemirror/lang-cpp";


// Process `{literalinclude}` directives in the raw Markdown
export async function processLiteralIncludesInMarkdown(mdText, baseUrlPath) {
    const lines = mdText.split("\n");
    const processedLines = [];

    for (const line of lines) {
        const match = line.match(/```{literalinclude}\s+(.*)/);
        if (match) {
            const filePath = match[1].trim(); // Extract file path

            try {
                const fileResponse = await fetch(baseUrlPath + filePath);
                const fileContent = await fileResponse.text();

                // Replace `{literalinclude}` with a placeholder div for CodeMirror
                const language = filePath.endsWith(".py") ? "python" : filePath.endsWith(".cpp") ? "cpp" : "plaintext";
                processedLines.push(`<div class="codemirror-placeholder" data-language="${language}" data-code="${encodeURIComponent(fileContent)}"></div>`);
            } catch (error) {
                console.error(`Failed to fetch ${filePath}:`, error);
                processedLines.push(`**Error loading file: ${filePath}**`);
            }
        } else {
            processedLines.push(line); // Keep other lines unchanged
        }
    }

    return processedLines.join("\n");
}

export function initializeCodeMirrorEditors() {
    const codeBlocks = document.querySelectorAll(".codemirror-placeholder");

    for (const block of codeBlocks) {
        const code = decodeURIComponent(block.dataset.code || "");
        const language = block.dataset.language;

        const extensions = [
            lineNumbers(),
            syntaxHighlighting(defaultHighlightStyle),
        ];

        if (language === "python") {
            extensions.push(python());
        } else if (language === "cpp") {
            extensions.push(cpp());
        }

        // Attach CodeMirror to the block
        new EditorView({
            state: EditorState.create({
                doc: code,
                extensions,
            }),
            parent: block,
        });
    }
}
