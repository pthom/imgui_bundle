# Playground examples

The examples of the [Dear ImGui Bundle playground](https://imgui-bundle.pages.dev/playground/).

- `examples.json` lists them: label, category, and what they need (`packages`, `bundle_folders`, `hidden`). It also gives the order and the description of the categories.
- The playground's menu shows the **title and first paragraph** of each example's docstring. They should tell anyone what the example shows: a visitor in the menu, a reader of the file, a user of the app (many examples display their docstring). Notes for developers come after.
- The menu renders their markdown, but not math: write formulas in ASCII, e.g. `x(n+1) = r * x(n) * (1 - x(n))`.
- After changing a docstring or `examples.json`, run `just playground_examples_docs`. It regenerates `examples_docs.json`, and warns when a first paragraph is missing or too long. The deploy runs it too.
- The menu also shows a picture of each example, from the website resources (`docs/clone_website_resources/imgui-bundle.pages.dev/resources/playground/`, its own repository). After changing an example, retake its picture with `just playground_screenshots <file stem>`, and commit it in that repository. How the pictures are made (frames, actions, crops, and the browser-only examples): `ci_scripts/playground_screenshots.py`.
