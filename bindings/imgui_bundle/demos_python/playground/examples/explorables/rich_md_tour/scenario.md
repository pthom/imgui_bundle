---
title: Rich Markdown
voice: en-US-AndrewMultilingualNeural
defaults:
  over: 1
  delay_after_interaction: 8
---
# Rich Markdown

## Markdown, drawn by Dear ImGui

[[The finished page alone, as a teaser]]
```cues
reset_page()
set_value("theme", "dark")
set_value("page_width", 1.0)
set_value("view", "page")
set_value("source", FULL)
```
This page is markdown. A table, formulas, code, a diagram: Dear ImGui draws all of it, with no browser and no web view.

[[Its source appears on the left]]
```cues
set_value("view", "split", at="Here is")
highlight("source", at="Here is")
```
Here is its source. When the source changes, the page follows at once.

The library is called Rich Markdown. It runs wherever Dear ImGui runs: on the desktop, on a phone, and in this web page. Let us write the page again, from the start.

## Writing

```cues
reset_page()
set_value("view", "split")
set_value("source", "")
animate("source", upto("title"), over=1.5, at="A hash")
```
A hash sign makes a heading.

```cues
animate("source", upto("intro"), over=6)
```
A paragraph is plain text. Stars make a word italic or bold; two tildes strike it through.

```cues
animate("source", upto("list"), over=5)
```
A dash starts a list. The page wraps the long lines, and the bullets follow.

```cues
animate("source", upto("quote"), over=4)
```
A quote starts with a greater-than sign.

```cues
animate("source", upto("link"), over=3)
```
A link is its text in brackets, then its address.

## Tables

```cues
reset_page()
set_value("view", "split")
set_value("source", upto("link"))
animate("source", upto("table"), over=4)
```
A table is drawn with pipes and dashes. The colons on the second line align a column to the right.

```cues
animate("source", upto("rows_inner"), over=4)
animate("source", upto("rows_outer"), over=4, at="the outer ones")
```
One line per row: the inner planets, then the outer ones, with their distance to the Sun and the length of their year.

```cues
animate("source", upto("au"), over=3)
```
The farther the planet, the longer its year.

## Math and code

```cues
reset_page()
set_value("view", "split")
set_value("source", upto("au"))
animate("source", upto("kepler"), over=8)
```
Formulas are written in LaTeX. Between single dollars, a formula sits in the text: here, Kepler's law. The square of the year grows as the cube of the distance.

```cues
animate("source", upto("newton"), over=3)
```
Between double dollars, a formula stands on its own, centered. MicroTeX draws it, inside Dear ImGui.

```cues
animate("source", upto("code"), over=6)
```
Code goes between three backquotes, with its language. Here, the year of Mars in Python, colored by a code editor.

## Diagrams

```cues
reset_page()
set_value("view", "split")
set_value("source", upto("code"))
animate("source", upto("families"), over=5)
```
A link can lead to a section of the page: its address is the heading's name, after a hash sign. A diagram is code too: a block of language Mermaid, with the type of the diagram on its first line.

[[Each line appears whole: typed letter by letter, a line would not parse until its end, and the diagram would flash an error]]
```cues
set_value("source", upto("fam_sun"), at="Each line")
set_value("source", upto("fam_gas"), at="The diagram")
set_value("source", upto("fam_ice"), at="its colors")
set_value("source", upto("fam_examples"), at="No web view")
```
Each line adds a node or an arrow. The diagram lays itself out again, and its colors are those of the ImGui style. No web view, no JavaScript: it is drawn with the draw list of Dear ImGui.

## Callouts and tasks

```cues
reset_page()
set_value("view", "split")
set_value("source", upto("families_end"))
animate("source", upto("note"), over=4)
```
GitHub's callouts are quotes that start with a tag: note, tip, important, warning or caution.

```cues
animate("source", upto("tasks"), over=4)
```
A task list is a list with boxes, checked or not.

```cues
animate("source", upto("dwarfs"), over=5)
```
And an HTML details tag folds a passage away, until a click opens it.

## A document

```cues
reset_page()
set_value("view", "page")
set_value("source", FULL)
```
The page is long now: it needs a map. On the left, the table of contents lists its headings. It marks the section on screen, and follows the scroll.

```cues
click("toc", "The families", at="A click")
click("line", "The families", point=(0.03, 0.5), at="A link")
```
A click on an entry scrolls the page there. A link to a section does the same: here, back to the table.

```cues
click("toc_hide", at="The arrow")
click("toc_show", at="The other arrow")
```
The arrow at the top hides the table of contents. A line above the page then gives the current section, with the whole table as a menu. The other arrow shows it again.

## Search

```cues
reset_page()
set_value("view", "page")
set_value("source", FULL)
click("page", point=(0.75, 0.2))
press("ctrl+f", at="Control F")
type_keys("Mars", at="Let us look")
```
Control F opens the search, or Command F on a Mac. Let us look for Mars.

```cues
press("enter", at="Enter goes")
```
Every match is highlighted. Enter goes to the next one.

```cues
press("shift+enter", at="Shift Enter")
press("shift+enter", at="past the first")
```
The search also looks into the code, and into the folded passages. Shift Enter goes back, and past the first match, to the last one: in the passage on the dwarf planets, which opens.

The table of contents counts the matches of each section, and the scroll bar marks where they are.

```cues
press("escape", at="Escape")
```
Escape closes the search.

## Folds

```cues
reset_page()
set_value("view", "page")
set_value("source", FULL)
hover("heading", "The planets", at="Each heading")
click("fold", "The planets", at="a click")
```
Each heading folds. Under the mouse, an arrow appears at its left: a click hides its section.

```cues
right_click("page", point=(0.75, 0.3), at="A right click")
menu("Fold All", at="fold all the headings")
```
A right click opens a menu. It can fold all the headings at once: the page becomes its own outline.

```cues
right_click("page", point=(0.75, 0.3), at="The same menu")
menu("Unfold All", at="unfolds them")
```
The same menu unfolds them all.

## Select and copy

```cues
reset_page()
set_value("view", "page")
set_value("source", FULL)
click("toc", "Kepler's law")
double_click("line", "Kepler's law", point=(0.12, 0.5), at="A double click")
drag("line", "Kepler's law", start=(0.0, 0.5), end=(0.85, 0.5), at="a drag")
```
The text can be selected, as on a web page. A double click selects a word, and a drag a passage.

```cues
right_click("line", "Kepler's law", point=(0.5, 0.5), at="A right click")
menu("Copy as Markdown", at="as markdown")
```
A right click copies it, as plain text or as markdown.

```cues
set_value("view", "split", at="Let us paste")
click("editor", point=(0.5, 0.9), at="Let us paste")
press("ctrl+end", at="at the end")
press("enter", at="at the end")
press("ctrl+v", at="at the end")
```
Let us paste it at the end of the source. The formula came back as LaTeX.

## Any screen, any theme

```cues
reset_page()
set_value("view", "page")
set_value("source", FULL)
set_value("page_width", 1.0)
click("toc", "The families")
animate("page_width", 0.4, over=3, at="On a narrow")
```
On a narrow screen, as a phone's, the table of contents becomes a menu, in the line above the page, with a magnifier for the search.

```cues
set_value("theme", "light", at="In a light")
```
The page follows the style of Dear ImGui. In a light theme, the diagram and the code turn light too.

```cues
set_value("theme", "dark")
animate("page_width", 1.0, over=2)
```
Everything here is drawn by the GPU, every frame, as the rest of the interface.

## In your code

```cues
set_value("view", "split")
set_value("source", FULL)
```
In your program, one function draws a markdown text; another draws a document, with its table of contents and its search. Their code is under Code, below.

```cues
highlight("source", at="The source")
```
The source on the left is yours now. Edit it, and watch the page.

[[The learner acts: a row for Pluto in the table]]
```cues
challenge("Your turn: in the source, add a row for Pluto to the table. It orbits at 39.5 AU, in 90,560 days.", until="'| Pluto' in source", hint="A row is a line of cells between pipes, under the row of Neptune: | Pluto | 39.5 | 90,560 |", hint_after=40)
```
There it is. Pluto has its row in the table again, if not its title of planet.

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
