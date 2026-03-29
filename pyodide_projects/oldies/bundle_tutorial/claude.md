# ImGui Bundle Tutorial

## Aim of this project

This project is intended to create a complete interactive web tutorial for the python bindings of Dear ImGui, Hello ImGui and Dear ImGui Bundle. I am the author of Hello ImGui and Dear ImGui Bundle, and I am also the maintainer of the python bindings of Dear ImGui, inside Dear ImGui Bundle.

Recently I was able to port ImGui Bundle the Python Bindings to pyodide (no public release yet).

## Build/Run Commands

- Prepare tutorial: `just tutorial_prepare`
- Generate JSON TOC: `just tutorial_json_toc`
- Run dev server: `just srv_dev` or `cd single_page_book_app && npm run dev`
- Build production: `cd single_page_book_app && npm run build`
- Build Jupyter book: `just tutorial_book`
- Build PDF version: `just tutorial_book_pdf`

## Code Style Guidelines

- **Python**: Clear type hints, 4-space indentation, descriptive naming
- **Class Structure**: Group related functionality into classes (e.g., `AppState`)
- **ImGui Pattern**: Use function-based UI rendering with state passed as parameters
- **JS**: ES6 modules, async/await for asynchronous operations
- **Error Handling**: Use assertions for preconditions and proper error propagation
- **File Structure**: Keep Python examples self-contained and focused on a single concept

## Structure of this project

When run, this project will look like a Jupyter book website, but it will actually be a single page web app which will load a pyodide environment and display the pages in the browser. Each python code block, containing and ImGui app, can be run and show, in the browser!

```
.
├── README.md
├── _brainstorm/  # old conversations with GPT
│     ├── gpt4.md
│     └── gpt_presentation.md
├── claude.md  # this file
├── jbook/                  # A jupyter book which contains the tutorial, and will be converted to a SPA
│     ├── CMakeLists.txt
│     ├── __pycache__
│     ├── _build
│     │     └── html
│     ├── _config.yml
│     ├── _toc.yml
│     ├── discover/                 # The tutorial
│     │     ├── CMakeLists.txt
│     │     ├── button.cpp
│     │     ├── button.jpg
│     │     ├── button.py
│     │     ├── hello_world.cpp
│     │     ├── hello_world.jpg
│     │     ├── hello_world.md
│     │     ├── hello_world.py
│     │     ├── layout_advices.cpp
│     │     ├── layout_advices.jpg
│     │     ├── layout_advices.md
│     │     ├── layout_advices.py
│     │     ├── whats_next.md
│     │     ├── widget_edit.cpp
│     │     ├── widget_edit.jpg
│     │     ├── widget_edit.md
│     │     └── widget_edit.py
│     ├── discover_immediate.md
│     ├── imgui
│     │     └── intro.md
│     └── sphinx_ext_imgui
│         ├── __pycache__
│         └── sphinx_codes_include.py
├── justfile
├── scripts
│     └── convert_toc.py    # a script to convert the jbook toc to a json file
└── single_page_book_app/   # The single page web app
    ├── dist
    │     └── styles.css
    ├── index.html
    ├── jbook -> ../jbook
    ├── node_modules
    │     ├── @codemirror
    │     ├── ...
    ├── package-lock.json
    ├── package.json
    ├── pyodide_dist -> ../../imgui_bundle/bindings/pyodide_web_demo/pyodide_dist
    ├── resources_singlepage/  # the js code of the single page app
    │     ├── app.js
    │     ├── canvas_drag.js
    │     ├── code_editor.js
    │     ├── dummy_app.jpg
    │     ├── generated_toc.json  # converted jbook toc
    │     ├── page_loader.js
    │     ├── page_sections.js
    │     ├── pyodide_helper.js
    │     ├── style.css
    │     └── toc_loader.js
    └── vite.config.js
```
