Here is the file structure of the tutorial:

```plaintext
.
├── CMakeLists.txt
├── _config.yml
├── _toc.yml
├── _tpl
│     ├── instantiate_tutorial_template.py
│     ├── tpl.cpp
│     ├── tpl.jpg
│     ├── tpl.py
│     └── tpl_md
├── discover
│     ├── CMakeLists.txt
│     ├── button.cpp
│     ├── button.jpg
│     ├── button.py
│     ├── hello_world.cpp
│     ├── hello_world.jpg
│     ├── hello_world.md
│     ├── hello_world.py
│     ├── layout_advices.cpp
│     ├── layout_advices.jpg
│     ├── layout_advices.md
│     ├── layout_advices.py
│     ├── whats_next.md
│     ├── widget_edit.cpp
│     ├── widget_edit.jpg
│     ├── widget_edit.md
│     └── widget_edit.py
├── discover_immediate.md
├── f.txt
├── gpt_presentation.md
├── imgui
│     └── intro.md
├── index.html
├── justfile
├── package-lock.json
├── package.json
├── resources_singlepage
│     ├── app.js
│     ├── breadcrumbs.js
│     ├── dummy_app.jpg
│     ├── page_loader.js
│     ├── pico.min.css
│     ├── resizer.js
│     ├── style.css
│     └── toc_loader.js
├── scripts
│     └── convert_toc.py
├── toc.json
└── vite.config.js
```

Here is the important files content:

===========================================================================
File discover/hello_world.md
===========================================================================
```
# Discover Immediate Mode GUIs

We'll start by creating a simple applications, where we will demonstrate several aspects of ImGui and Hello ImGui.

## Hello, World!

We will start by running a simple Hello World application, which displays:
![](hello_world.jpg)

We will follow the steps below:
1. We define a gui function that will be called by Hello ImGui at every frame: It will display the GUI of our application *and* handle user events.
2. We use the `imgui.text()` (Python) or `ImGui::Text` (C++) function to display a text in the window.
3. We call `hello_imgui.run()` (Python) or `HelloImGui::Run()` (C++) to start the application, optionally specifying the window title and size, or if we want it to set its size automatically.


**Python**
```{literalinclude} hello_world.py
```


**C++**
```{literalinclude} hello_world.cpp
```


## Handling button events

We will now create an application which handles clicks on a button, and updates a counter each time the button is clicked:

![](button.jpg)

We will follow the steps below:
1. Add an AppState class to store the state of the application. This is a recommended best practice, as it allows to separate the GUI code from the business logic.
2. Add a counter to the AppState. This counter will be incremented each time a button is clicked.
3. Let the gui function take an AppState as an argument (and possibly modify it).
4. Add a button to the GUI, with `imgui.button()`, and increment the counter when the button is clicked.
5. Add a tooltip to the button, to display a message when the user hovers over it.
6. Add a button to exit the application (see note below).
7. Create a main() function to run the application, where we create an AppState object
8. Create a lambda function to call the gui function with the AppState object as an argument.
9. Call `hello_imgui.run()` with the lambda function as an argument.

*Note: In the case of a web application, such as in this tutorial, the "exit" button will not have any effect. In the case of a desktop application, it will close the window.*


**Python**
```{literalinclude} button.py
```


**C++**
```{literalinclude} button.cpp
```
```
===========================================================================
File discover/hello_world.py
===========================================================================
```
from imgui_bundle import imgui, hello_imgui


def gui():                                                                  # 1.
imgui.text("Hello, World!")                                             # 2.


hello_imgui.run(gui, window_title="Hello, World!", window_size_auto=True)   # 3.
```
===========================================================================
File _config.yml
===========================================================================
```
# Book settings
# Learn more at https://jupyterbook.org/customize/config.html

#
# Main book settings
# -----------------------------------------------------------
title: "Immediate GUI Tutorial"
author: Pascal Thomet
#logo: ../assets/logo/logo.jpg
copyright: "2025"

#
# Notebook execution during book build
# See https://jupyterbook.org/content/execute.html
# -----------------------------------------------------------
# Never execute notebooks during the build process
# (to preserve our nice fiatlight execution thumbnails)
execute:
execute_notebooks: off

# Information about where the book exists on the web
# -----------------------------------------------------------
#repository:
#  url: https://github.com/pthom/fiatlight  # Online location of your book
#  path_to_book: src/python/fiatlight/doc  # Optional path to your book, relative to the repository root
#  branch: master  # Which branch of the repository should be used when creating links (optional)
#
##launch_buttons:
##  notebook_interface: "jupyterlab"  # or "classic"
##  binderhub_url: "https://mybinder.org"  # The URL for your BinderHub (e.g., https://mybinder.org)
#
## Add GitHub buttons to your book
## See https://jupyterbook.org/customize/config.html#add-a-link-to-your-repository
#html:
#  use_issues_button: true
#  use_repository_button: true
#
## Misc
## -----------------------------------------------------------
## Define the name of the latex output file for PDF builds
#latex:
#  latex_documents:
#    targetname: book.tex


```
===========================================================================
File _toc.yml
===========================================================================
```
# Syntax inspired from jupyter-book
format: jb-book
root: discover_immediate

chapters:
- file: discover/hello_world
  sections:
    - file: discover/widget_edit
    - file: discover/layout_advices
    - file: discover/whats_next
- file: imgui/intro
# Possibly some sections here
```
===========================================================================
File toc.json
===========================================================================
```
{
"format": "jb-book",
"root": {
"file": "discover_immediate",
"title": "Intro"
},
"chapters": [
{
"file": "discover/hello_world",
"sections": [
{
"file": "discover/widget_edit",
"title": "Edit value with widgets"
},
{
"file": "discover/layout_advices",
"title": "Advices to layout your GUI"
},
{
"file": "discover/whats_next",
"title": "What's next?"
}
],
"title": "Discover Immediate Mode GUIs"
},
{
"file": "imgui/intro",
"title": "Discover ImGui"
}
]
}```
===========================================================================
File index.html
===========================================================================
```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Immediate GUI Tutorial</title>
    <link rel="stylesheet" href="resources_singlepage/pico.min.css" />
    <link rel="stylesheet" href="resources_singlepage/style.css" />
</head>
<body>
<header>
    <h1>Immediate GUI Tutorial</h1>
</header>
<div class="layout-container">
    <nav id="toc-sidebar">
        <!-- TOC content generated by app.js -->
    </nav>
    <main id="content-area-wrapper">
        <div id="breadcrumb-container" style="margin-bottom:1em;"></div>
        <div id="content-area"></div>
    </main>
    <div id="resizer"></div>
    <aside id="code-panel">
        <!-- Dummy code execution panel -->
        <img src="resources_singlepage/dummy_app.jpg" alt="Code panel placeholder" style="max-width:100%;">
    </aside>
</div>
<script type="module" src="resources_singlepage/app.js"></script>
</body>
</html>
```
===========================================================================
File resources_singlepage/app.js
===========================================================================
```
import { initTOC, tocRoot } from "./toc_loader.js";
import { initResizer } from "./resizer.js";
import { loadPage } from "./page_loader.js";

async function initializeAll() {
    await initTOC();
    initResizer();

    const rootPage = tocRoot()
    loadPage(rootPage.file + ".md");
    // loadPage("discover/hello_world.md")
}

document.addEventListener("DOMContentLoaded", initializeAll);
```
===========================================================================
File resources_singlepage/breadcrumbs.js
===========================================================================
```
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
```
===========================================================================
File resources_singlepage/page_loader.js
===========================================================================
```
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
```
===========================================================================
File resources_singlepage/resizer.js
===========================================================================
```
let isResizing = false;
let startX = 0;
let startContentWidth = 0;

function _onResizerMouseDown(e)
{
    const layout = document.querySelector('.layout-container');
    isResizing = true;
    startX = e.clientX;
    // Get current width of content area (second column)
    // We assume something like: [TOC:200px] [content:auto] [handle:5px] [code:33%]
    // We'll convert the content column to a fixed width during resizing
    const computedStyle = window.getComputedStyle(layout);
    const columns = computedStyle.getPropertyValue('grid-template-columns').split(' ');
    // columns[1] is the content area width
    startContentWidth = parseFloat(columns[1]);
    // If it's 'auto', we might need to set a default width or measure #content-area’s offsetWidth
    if (isNaN(startContentWidth)) {
        const contentArea = document.getElementById('content-area');
        startContentWidth = contentArea.offsetWidth;
    }
    document.body.style.userSelect = 'none'; // Prevent text selection
}

function _onResizerMouseMove(e)
{
    const layout = document.querySelector('.layout-container');

    if (!isResizing) return;
    const dx = e.clientX - startX;
    const newContentWidth = startContentWidth + dx;
    if (newContentWidth > 100) { // A minimum width for content area
        layout.style.gridTemplateColumns = `200px ${newContentWidth}px 5px auto`;
    }
}

function _onResizerMouseUp()
{
    isResizing = false;
    document.body.style.userSelect = 'auto';
}

export function initResizer()
{
    const resizer = document.getElementById('resizer');
    resizer.addEventListener('mousedown', _onResizerMouseDown);
    document.addEventListener('mousemove', _onResizerMouseMove);
    document.addEventListener('mouseup', _onResizerMouseUp);
}
```
===========================================================================
File resources_singlepage/style.css
===========================================================================
```
body {
    font-size: 14px;
}

.layout-container {
    display: grid;
    grid-template-columns: 400px auto 5px 33% /* TOC | content | handle | code */;
    height: 100vh;
    overflow: hidden;
}

#toc-sidebar {
    border-right: 1px solid #ccc;
    padding: 1rem;
    overflow-y: auto;
}

#content-area {
    padding: 1rem;
    overflow-y: auto;
}

#resizer {
    background: #ccc;
    cursor: col-resize;
    width: 5px; /* Matches the grid template size */
    height: 100%;
}

#code-panel {
    border-left: 1px solid #ccc;
    padding: 1rem;
    overflow-y: auto;
}```
===========================================================================
File resources_singlepage/toc_loader.js
===========================================================================
```
import { loadPage } from "./page_loader.js";


// The global `gToc` variable will store the TOC data (from toc.json)
let gToc;

export function tocRoot() {
return gToc.root;
}

export async function initTOC() {
const response = await fetch("resources_singlepage/toc.json");
gToc = await response.json();
const tocSidebar = document.getElementById("toc-sidebar");

    // Build a simple TOC list from toc's `chapters`
    // toc format example:
    // {
    //   "format": "jb-book",
    //   "root": "discover_immediate",
    //   "chapters": [
    //     { "file": "discover/hello_world", "sections": [...] }
    //   ]
    // }
    _buildTocList(gToc, tocSidebar);
}

function _buildTocList(toc, container) {
const ul = document.createElement("ul");

    // root page
    const rootLi = _createTocItem(toc.root);
    ul.appendChild(rootLi);

    // chapters
    toc.chapters.forEach(chapter => {
        const li = _createTocItem(chapter);
        ul.appendChild(li);

        if (chapter.sections) {
            const subUl = document.createElement("ul");
            chapter.sections.forEach(section => {
                const subLi = _createTocItem(section.file);
                subUl.appendChild(subLi);
            });
            li.appendChild(subUl);
        }
    });

    container.appendChild(ul);
}

function _createTocItem(item) {
const li = document.createElement("li");
const link = document.createElement("a");
link.href = "#";
link.textContent = item.title || item.file; // fallback if title not found
link.addEventListener("click", (e) => {
e.preventDefault();
loadPage(item.file + ".md");
});
li.appendChild(link);
return li;
}
```
===========================================================================

