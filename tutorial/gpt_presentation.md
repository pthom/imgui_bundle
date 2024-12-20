I'm working on creating a complete tutorial for ImGui Bundle and Hello ImGui.
It will be web-based, and it will use pyodide to run the code examples, since
I now have a very efficient way to run imgui python apps in the browser.

In order to simplify my process, I created the tutorial files in a manner which is compatible with jupyter-book: this way, I can  build the tutorial as a jupyter-book, and then convert it to a web-based tutorial. However, in this web-based tutorial, the code cannot be run.

I did explore ways to hack into sphinx, in order to make the code renewable inside a Jupiter book: it is a dead-end.
The reason for that is that jupyter-book reloads the whole HTML at each new page, and pyodide is way too slow to reload at each page.
Another reason is that sphinx + jupyter-book is too complex for me to handle.

So I would like to explore with you the possibility to display the tutorial with a Single Page Web application:
We would have to write code to parse the toc, display markdown, and then to run pyodide code.

We will take it slowly as it is a complex endeavor. Please let's work step by step, and first discuss together
about the possible directions we can take before exploring them.

In my opinion, the first step is too check whether it is possible to display the md files in a single page web application, while respecting the toc, and displaying it in a nice way. We will work on running the code much later (and I do have solutions for that).

I will want you to help me to get very organized code:
- separate concerns in different files and functions
- Do not nest to much calls in javascript
- Use existing js libraries when possible, and provide a way to load them in the html file


Here is the list of files I have at the moment:
```
.
.
├── _config.yml
├── _toc.yml
├── discover/
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
```

Below is an extract of their content:
==========================================

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
```
===========================================================================


Can we discuss together about the possible directions we can take before exploring them?
First, we'll concentrate on displaying the md files in a single page web application, while respecting the toc, and displaying it in a nice way. We will work on running the code much later (and I do have solutions for that).

Please ask question if you feel you need more details, or information about the project or files.





===========================================================================

Clarifications asked by GPT:

> Project Goal: You want a single-page web application that:
> Displays the content from these markdown files in a structured way.
> ...

=> Correct. Please note that in the end, I will want to add a resizable canvas on the right of the page, where the code will be executed (probably with a splitter).

> Environment Assumptions:

We are going to run on a web server. The file structure will be known.
So the JavaScript code can query the markdown and images files.
Concerning the translation from Markdown to HTML, I think this should be done via javascript.

> Would you like to use a known JS library to handle markdown rendering (e.g., marked.js)?
Yes


> Desired Implementation Details:
> You mentioned separation of concerns and using existing JS libraries. For instance, using marked.js or markdown-it for rendering markdown would simplify code. Is that acceptable?

Yes!

> For the TOC: The _toc.yml can be parsed into a JS object. From this, we can build a navigation sidebar that, when a user clicks on a section, fetches and displays the corresponding markdown. Is this approach what you envision?

Yes. It would be desirable to also parse the md file for H2 titles, and display them in a breadcrumbs specific to the page.
(H1 would be the title of the page, there will be only one per page).


> Technical Constraints:
> Are there any constraints on which frameworks/libraries can be used? For example, can we use a framework like React or Vue, or do you prefer a vanilla JS solution plus small libraries?

I'd very much prefer a vanilla JS solution plus small libraries. I'm not familiar with React or Vue, and I'd like to keep the project as simple as possible.

> How important is it to maintain a pure static structure (no build steps) versus a solution that could involve a small build pipeline (like a one-time preprocessing step that converts .md to .html or .json)?

We could envision a small build pipeline, preferably in Python, in which I am proficient.

> Do you have preferences for the layout and styling? For instance, would a standard "sidebar on the left, main content on the right" layout be acceptable?

I would like something beautiful and modern.
For the toc, a sidebar on the left is the way to go.
As for the inner page navigation, I would like to save space on the right since we will have a canvas there.
So I thought about a breadcrumb on top of the page, or any other solution that would save space on the right.
(knowing that the number of H2 titles in a page will be limited to <= 6).

> Will styling be handled by a CSS framework (like Bootstrap or Tailwind) or custom CSS?

I don't know. I will rely on your advices.

> Future Steps:
> Eventually, we’ll integrate code execution with pyodide. Will the code blocks appear as runnable code cells in the final UI, or just as static code blocks until triggered?

The code blocks will appear as editable code blocks, with syntax highlighting, and a run button.
Once the run button is clicked, the code will be executed and the app will be displayed in the canvas on the right.
If there are errors, a dedicated panel should appear.
If there is stdout output to be displayed, I have not decided yet. Maybe we should envision two displays below the code.

> Are we aiming for an experience similar to a Jupyter Book but all contained in one page, with dynamic navigation?
That is the idea.
- Each code cell will start an app from scratch (using hello_imgu.run() for instance)
- the canvas will be refreshed at each run
- However the python runtime will not be restarted at each run

Do you have other questions or can we start exploring possible alternatives?

===========================================================================

> Questions for you:
> Would you be comfortable adding a minimal build step to convert _toc.yml to JSON using Python? This would simplify the JavaScript code.
Absolutely. We would need to create a scripts/ folder, and store it there. Then I have a justfile that helps me remember the commands to run; we will populate it with the command to run the build step.

> Are you open to using a minimal CSS framework like Pico.css to speed up styling?

Absolutely. I would ask that we add a recipe in the justfile if needed to simplify the process.

> For the layout, do you prefer starting simple (just TOC on left, content in center), and later add the canvas panel on the right once we handle code execution?

Actually I would like to have a feeling of the final look. So we will put a dummy code execution panel, with an dummy app image.
In terms of size, I think the execution panel should initially occupy 1/3 of the screen, and the code panel 2/3 (not taking into account the TOC). The user will resize the panels as needed (and later, it may be initially hidden and appear once the code is run).

I do not know the answer to your question "Two columns or three columns ... Or a two-column layout (TOC on the left, main content in the middle), and a draggable splitter to open a right panel overlay for code output. We need to consider vertical/horizontal splits and what feels natural." Please explain what the difference might be.

Let's now try to work on implementing this. Once again, please let's work with organized code, and separate concerns in different files and functions.

===========================================================================

> With this setup, you have a three-column layout: TOC on the left, content in the center, and a dummy code panel on the right. Once the basic structure is in place, we can refine functionality, add the resizing splitter, integrate the breadcrumbs, and prepare for code execution steps.
> Does this direction seem good to you?

Yes, it does!

The script convert_toc works, and I now have a toc.json file.
I changed the files structure a bit (I do not want to pollute the root of the jupyter-book).
See:
.
├── CMakeLists.txt
├── _config.yml
├── _toc.yml
├── discover/
│     ├── hello_world.cpp
│     ├── hello_world.jpg
│     ├── hello_world.md
│     ├── hello_world.py
│     ├── layout_advices.cpp
│     ├── ...
├── discover_immediate.md
├── index_singlepage.html
├── justfile
├── resources_singlepage
│     ├── app.js
│     └── style.css
├── scripts
│     └── convert_toc.py
└── toc.json

I'll want the canvas to be resizable in a later step, and to apply some styling to the page.
I guess this is the next step. Do you agree?

===========================================================================

The resizer work well, and the columns width seem ok.

In your proposed css, there is no more #toc-sidebar, is that normal?
At the moment, I kept it as before.

As far as the separation of concerns, I'm afraid that app.js will quickly get huge and difficult to navigate.
I started to split it:

```bash
ls -1 resources_singlepage
app.js
resizer.js     # Contains the resizer code you provided (and referenced in html)
style.css
```
We will continue to split it in several files as needed: I suspect that the navigation handling will deserve its own file.

Also, please note that I refactored resizer.js like this, which is more readable:
```javascript
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

function initResizer()
{
  const resizer = document.getElementById('resizer');
  resizer.addEventListener('mousedown', _onResizerMouseDown);
  document.addEventListener('mousemove', _onResizerMouseMove);
  document.addEventListener('mouseup', _onResizerMouseUp);
}

document.addEventListener('DOMContentLoaded', initResizer);
```
I do not like to use long anonymous functions, it makes the code difficult to read.

Also, note that once we will have added pyodide, we will need to be extremely precise about the order of operations:
pyodide is loaded in async mode, and python code is also executed in async mode.
Thus, we cannot rely on using document.addEventListener('DOMContentLoaded') in too many places; because it makes the initialization sequence of the code difficult to follow. The app is ought to become complex, and we need to be organized.
I'd like us to work towards having an `initializeAll()` function in app.js, which will call every js file initialization function in the right order.

===========================================================================

OK, it works.

Notes:
1. I had to refactor a bit:

app.js
```
// Initialize all parts of the app
async function initializeAll() {
    await loadToc();
    initResizer();
    // In the future, initTOC(), initMarkdownLoading(), etc.
    loadPage("discover/hello_world.md");
}

document.addEventListener("DOMContentLoaded", initializeAll);
```

2. When using export/import, I get errors:
```
export function initResizer()
{
...
}
```
==> Uncaught SyntaxError: export declarations may only appear at top level of a module
==> Uncaught SyntaxError: import declarations may only appear at top level of a module

At the moment, I removed those keywords, and it works. I'm not proficient with this. I don't know if it is important.
If it is complex, maybe we can keep that for a later time.

3. I see issues in the java console:
```
The resource at “https://unpkg.com/@picocss/pico@latest/css/pico.min.css” was blocked due to its Cross-Origin-Resource-Policy header (or lack thereof). See https://developer.mozilla.org/docs/Web/HTTP/Cross-Origin_Resource_Policy_(CORP)# index_singlepage.html

==> I'm using a local webserver where I activated CORS. I do not know why this error appears.
    Anyhow, let's download the css file and put it in the resources_singlepage folder. Please provide me with the link to download it.


GET
   http://localhost:8005/favicon.ico
   [HTTP/1 404 File not found 1ms]
   ==> not important

GET
http://localhost:8005/hello_world.jpg
[HTTP/1 404 File not found 1ms]
GET
http://localhost:8005/button.jpg
[HTTP/1 404 File not found 2ms]

==> We have to account for the fact that they are inside the discover folder. There will be other folders in the future, so we have to be careful about that. Image paths are to be considered relative to the md file.

(I did add a dummy image of the app and it works)
```

Let's fix the issues, and then move on to the next step.

===========================================================================

discover/hello_world.jpg does exist.

However, loadPage() is executed in the top folder:
we probably need to scan for relative paths in the markdown file, and adjust them accordingly.
```
async function loadPage(mdPath) {
  console.log("loadPage " + mdPath); // will receive discover/hello_world.md
  const response = await fetch(mdPath);
  const mdText = await response.text();
  const html = marked.parse(mdText);
  const contentArea = document.getElementById("content-area");
  contentArea.innerHTML = html;
  buildBreadcrumbs();
}
```

I downloaded pico.css, and the style is now better. The default font size is too big. I have to display the page at 70% to have a good view.

Let's correct these issues, and move to the next step. Is it navigation and breadcrumbs?

===========================================================================

I solved the issues on my side. Here is what I did:

* Switched to npm + modules
Here is my package.json:
  {
  "name": "tutorial",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
  "dev": "vite",
  "build": "vite build",
  "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "description": "",
  "dependencies": {
  "marked": "^15.0.4",
  "marked-base-url": "^1.1.6"
  },
  "devDependencies": {
  "vite": "^6.0.5"
  }
  }

* use of marked-base-url to handle relative paths in markdown files
* now, we have:
app.js
```js
import { marked } from "marked";
import { baseUrl } from "marked-base-url";

async function loadToc() {
    const response = await fetch("toc.json");
    const toc = await response.json();
    // Build sidebar navigation from toc
}

async function loadPage(mdPath) {
    console.log("loadPage " + mdPath);

    const baseUrlPath = mdPath.substring(0, mdPath.lastIndexOf('/') + 1);

    marked.use(baseUrl(baseUrlPath));

    // Fetch and parse the Markdown
    const response = await fetch(mdPath);
    const mdText = await response.text();
    const html = marked.parse(mdText);

    // Update the content area
    const contentArea = document.getElementById("content-area");
    contentArea.innerHTML = html;

    buildBreadcrumbs();
}
function buildBreadcrumbs() {
    // scan content for h2 headings
}

// Initialize all parts of the app
async function initializeAll() {
    await loadToc();
    initResizer();
    // In the future, initTOC(), initMarkdownLoading(), etc.
    loadPage("discover/hello_world.md");
}

document.addEventListener("DOMContentLoaded", initializeAll);
```
* I now run a server with npm run dev, and it works well.


Note: app.js might grow quickly. It should only be an orchestrator. We will need to place the navigation and breadcrumbs logic in their own file(s).


