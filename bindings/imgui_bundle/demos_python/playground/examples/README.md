# Playground examples

The examples of the [Dear ImGui Bundle playground](https://imgui-bundle.pages.dev/playground/).

- `examples.json` lists them: label, category, and what they need (`packages`, `bundle_folders`, `hidden`; `needs`: browser features, e.g. `["jspi"]` for the test engine, whose cards are greyed in a browser without them). It also gives the order and the description of the categories.
- The playground's menu shows the **title and first paragraph** of each example's docstring. They should tell anyone what the example shows: a visitor in the menu, a reader of the file, a user of the app (many examples display their docstring). Notes for developers come after.
- The menu renders their markdown, but not math: write formulas in ASCII, e.g. `x(n+1) = r * x(n) * (1 - x(n))`.
- After changing a docstring, `examples.json` or a bundle folder, run `just playground_examples_docs`. It regenerates `examples_docs.json` (and warns when a first paragraph is missing or too long), and the `manifest.json` of each bundle folder: the files the playground downloads with the example, i.e. the folder's files that the repository ships. The deploy runs it too.
- `fiat_settings/` holds the saved state of the Fiatlight examples (values and layout), so that they start from nice values in the playground. To change it: run the example on the desktop, adjust it, then commit its `<app>.fiat_workspace.json` and `<app>.ini` (`git add -f`: `.ini` files are ignored) and run `just playground_examples_docs`.
- The menu also shows a picture of each example, from the website resources (`docs/clone_website_resources/imgui-bundle.pages.dev/resources/playground/`, its own repository). After changing an example, retake its picture with `just playground_screenshots <file stem>`, and commit it in that repository. How the pictures are made (frames, actions, crops, and the browser-only examples): `ci_scripts/playground_screenshots.py`.
