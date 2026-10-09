---
title: Rich Markdown
voice: en-US-AndrewMultilingualNeural
defaults:
  over: 1
  delay_after_interaction: 8
---
# Rich Markdown

## Markdown, live

[[The finished page alone, as a teaser; then an empty page beside an empty source]]
```cues
reset_page()
set_value("theme", "dark")
set_value("page_width", 1.0)
set_value("view", "page")
set_value("source", FULL)
set_value("view", "split", at="Let me start")
set_value("source", "", at="Let me start")
```
This whole page is markdown, drawn live by Dear ImGui: no browser, no web view. Let me start again, from an empty page.

[[The cursor of the test engine clicks in the editor and types: the page follows each key]]
```cues
click("editor", point=(0.5, 0.2))
type_keys(part("title"))
```
A hash sign, and a title.

```cues
type_keys(part("intro"))
```
Stars for italic and bold, two tildes to strike Pluto out. There is no preview button: the page follows every key.

```cues
paste(part("table"), at="A table")
```
A table? Paste it. The colons under the header align the numbers to the right.

## Math and code

```cues
reset_page()
set_value("view", "split")
set_value("source", upto("table"))
click("editor", point=(0.5, 0.9))
press("ctrl+end")
type_keys(part("kepler"))
```
Formulas are LaTeX. Watch Kepler's law: it becomes a formula as soon as its second dollar sign closes it.

```cues
paste(part("newton"), at="Between double")
paste(part("code"), at="And code")
```
Between double dollars, a formula stands on its own line. And code gets its colors from a real code editor.

## A diagram that grows

[[Each line is pasted whole: typed letter by letter, a line would not parse until its end, and the diagram would flash an error]]
```cues
reset_page()
set_value("view", "split")
set_value("source", upto("code"))
click("editor", point=(0.5, 0.9))
press("ctrl+end")
paste(part("families") + part("families_end"))
press("up")
paste(part("fam_sun"), at="Each line")
paste(part("fam_gas"), at="a node")
paste(part("fam_ice"), at="an arrow")
paste(part("fam_examples"), at="lays itself")
```
A Mermaid block is a diagram. Each line adds a node, or an arrow, and the diagram lays itself out again. No JavaScript here: it is drawn with the draw list of Dear ImGui.

## Find anything

```cues
reset_page()
set_value("view", "page")
set_value("source", FULL)
click("toc", "The planets", at="a click")
```
Here is the whole page, as a document. On the left, its table of contents: a click, and the page scrolls there.

```cues
press("ctrl+f", at="Control F")
type_keys("Mars", at="Let us find")
```
Control F searches it, or Command F on a Mac. Let us find Mars.

```cues
press("enter", at="Enter jumps")
```
Every match lights up. The table of contents counts them, the scroll bar marks them, and Enter jumps to the next one.

```cues
press("shift+enter", at="Shift Enter")
press("shift+enter", at="past the first")
```
Shift Enter goes back, past the first match, to the last one: inside a folded passage, which opens by itself.

```cues
press("escape", at="Escape")
```
Escape, and the search is gone.

## Fold, select, copy

```cues
reset_page()
set_value("view", "page")
set_value("source", FULL)
right_click("heading", "The planets", point=(0.3, 0.5), at="A right click")
menu("Fold All", at="every section")
```
A right click folds every section: the page becomes its own outline.

```cues
right_click("heading", "The planets", point=(0.3, 0.5), at="Unfold")
menu("Unfold All", at="Unfold")
click("toc", "Kepler's law", at="Unfold")
drag("line", "Kepler's law", start=(0.0, 0.5), end=(0.9, 0.5), at="select a line")
```
Unfold it, and select a line, as on a web page.

```cues
right_click("line", "Kepler's law", at="Copy it")
menu("Copy as Markdown", at="Copy it")
set_value("view", "split", at="paste it")
click("editor", point=(0.5, 0.9), at="paste it")
press("ctrl+end", at="paste it")
press("enter", at="paste it")
press("ctrl+v", at="paste it")
```
Copy it as markdown, and paste it at the end of the source: the formula comes back as LaTeX.

## Anywhere, and yours

```cues
reset_page()
set_value("view", "page")
set_value("source", FULL)
set_value("page_width", 1.0)
click("toc", "The families")
animate("page_width", 0.4, over=3, at="On a phone")
set_value("theme", "light", at="In a light")
```
On a phone, the table of contents folds into a menu above the page. In a light theme, the diagram and the code follow.

```cues
set_value("theme", "dark", at="In your program")
set_value("page_width", 1.0, at="In your program")
set_value("view", "split", at="In your program")
```
In your program, it is one function call: the code is below, under Code. And now, the source is yours.

[[The learner acts: a row for Pluto in the table]]
```cues
challenge("Your turn: add a row for Pluto to the table, in the source. It orbits at 39.5 AU, in 90,560 days.", until="'| Pluto' in source", hint="A row is a line of cells between pipes, under the row of Neptune: | Pluto | 39.5 | 90,560 |", hint_after=40)
```
There it is. Pluto is back in the table, if not among the planets.

### Code
```python
from imgui_bundle import imgui, immapp, rich_md

def gui():
    rich_md.render(r"Some *markdown*, and a formula: $e^{i\pi} + 1 = 0$")  # in the flow of the window
    rich_md.render_document("doc", MY_LONG_TEXT)  # a document: table of contents, search, folds

immapp.run(gui, with_markdown=True, with_latex=True)
```

### References
- [imgui_rich_md](https://github.com/pthom/imgui_rich_md): the library, standalone, for any Dear ImGui app.
- [The Markdown tour](https://imgui-bundle.pages.dev/playground/?demo=demo_imgui_md.py) of Dear ImGui Bundle: every feature, with its source.
