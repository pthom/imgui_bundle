"""Narrated explorables: the idea, in one page

A page that presents two ideas: narrative programming (a program that contains its own document), and narrated
explorables (interactive lessons with a voice, written as markdown with cues, played by Dear ImGui Bundle in the
browser). The page is itself a narrative program: its text lives in this file, next to the code it quotes.
"""

# This file is rendered by rich_md.render_this_file("Pitch") (see gui() at the bottom): the ::md sections below are
# the page, and the page quotes the code of this file through transclusions (![[#Clock#code]]).

from imgui_bundle import hello_imgui, imgui, immapp, rich_md

r"""::md Pitch
# Narrated explorables

> *A notebook is a document containing a program. A narrative program is a program containing a document.*
> *A narrated explorable is a narrative program that talks.*

# Part 1. Narrative programming

A source file can contain its own narrative. Selected strings or comments hold markdown, in named sections, next to the
code they explain. The file stays a normal program: it runs, it is type-checked, it is tested, it is versioned. But it
can also be rendered as a document, which quotes the code in the order of an explanation rather than the order of a
program.

## The syntax

It is small. A section is a string whose first line is `r'''::md Clock` (its name is `Clock`). A line `::code` at
its end says that the code that follows, up to a comment `# ::endcode`, belongs to the section. A document includes
the section's prose with `![[#Clock]]`, and its code with `![[#Clock#code]]`. A document can also include a section
of another file (`![[physics.py#Equations]]`), or a whole file.

This page is itself a narrative program. A section named `Clock` is defined further down in this very file, next
to a three-line function, and here it is, transcluded live, prose then code:

![[#Clock]]
![[#Clock#code]]

The source of the page is at the bottom (the last section, *The source of this page*): the `Clock` section is near
its end. Edit the file while it runs: the document follows.

## The document places the widgets

The markdown is not only text. A code block of the language `widget` holds a call to a Python function of the
program, a plain GUI function with sliders, pictures, plots; the document draws whatever it renders, at that place.
The story decides where the reader plays.

The [Julia map](https://imgui-bundle.pages.dev/playground/?demo=explorables/julia_map/julia_map.py) is written this way.
Its story, a `::md Story` section, says where its two pictures go:

````markdown
**Click anywhere on the left picture to choose $c$**: the Julia set on the right is the one for that $c$.

```widget
gui_julia_map()   # draws the two pictures, interactive: click, zoom, drag
```

## Iterations
Set the maximum number of iterations, and watch the fine details of the boundary appear:

```widget
gui_iterations()   # a slider for the iteration budget of both pictures
```
````

And the program renders the story. This one line draws the whole GUI of the app:

```python
def gui() -> None:
    rich_md.render_this_file("Story")
```

![The Julia map](https://imgui-bundle.pages.dev/resources/playground/julia_map.jpg)

The ground for all this is [Dear ImGui Bundle](https://imgui-bundle.pages.dev), a toolkit for Python and C++ that
runs the same code on the desktop and in the browser (through Pyodide), and its rich markdown: text, LaTeX, images,
code, diagrams, inside the GUI. Demo: [rich markdown](https://imgui-bundle.pages.dev/playground/?demo=demo_imgui_md.py).
The [playground](https://imgui-bundle.pages.dev/playground/) edits and runs a program in the browser; this page is one
of its hidden demos.

## The bundle, for scientists who want to be on the web

Most interactive explanations on the web are written by web developers, in JavaScript, HTML and CSS, with a build
chain and often a server. The bundle takes the other road, so that the person who understands the science can write
the explanation alone:

- **One language.** The whole application, interface included, is Python (or C++). No JavaScript, no HTML, no CSS,
  no framework. The same file runs on the desktop and in the browser.
- **No server.** The site is static files. The computation runs on the reader's machine: numpy, the plots, the
  simulation, all of it in the browser through Pyodide. Nothing to host, nothing to scale, nothing that stops working
  when a service closes.
- **Fast on the screen.** Immediate-mode rendering redraws everything each frame, at 60 frames per second even with
  live data: a simulation, a training run, an image pipeline. Plots, images and LaTeX are part of the toolkit.
- **Fast to change.** Edit the code, run, see: a few seconds in the playground. On the desktop, the narrative follows
  a save while the program runs.
- **Light.** An explorable is a Python file of a few hundred lines, and its data. No dependency to keep up to date,
  no build.

## Lineage

The idea has ancestors. Donald Knuth's
[literate programming](https://www-cs-faculty.stanford.edu/~knuth/lp.html) (1984) wrote a program as an essay, in the
order of the explanation, and a tool extracted the compilable code from it. Notebooks went the other way: a document
whose cells run; [Jupyter Book](https://jupyterbook.org) turns them into books, such as the
[Python Data Science Handbook](https://jakevdp.github.io/PythonDataScienceHandbook/) or
[Quantitative Economics with Python](https://python.quantecon.org). Bret Victor's
[explorable explanations](https://worrydream.com/ExplorableExplanations/) (2011) put live widgets into a text, so
that the reader can play with what the text says. Narrative programming takes one thing from each: the prose beside the code, the live
rendering, the widgets placed by the text. What it keeps from none of them: the program stays a program, as every
tool sees it; the document is a view of it.

# Part 2. Narrated explorables

## The idea in three sentences

An **explorable** is an interactive explanation: a simulation you can touch, next to the text that explains it.
A **narrated explorable** adds a voice and a timeline: the lesson speaks, and while it speaks, the widgets move by
themselves; you may interrupt at any moment, play with them, and the story goes on.
It is written as a **markdown document with cues**, and it runs **in the browser, on a phone, with no server**.

![Simple harmonic motion, an explorable of the playground](https://imgui-bundle.pages.dev/resources/playground/lesson_harmonic_motion.jpg)

Andy Matuschak named the medium in 2018, after Ben Eater and Grant Sanderson's *Visualizing quaternions*. What it
adds, in his words: to an interactive alone, an invested speaker; to a text with figures, the sentence and the picture
happening together; to a video, active learning, since the learner asks and answers questions of the representation.
A recent example: David Louapre's lesson on the
[Navier-Stokes equations](https://huggingface.co/spaces/dlouapre/tangible-navier-stokes), made with his framework
Tangible.

## What exists today

- **Explorables**, already written with the bundle: the
  [Julia map](https://imgui-bundle.pages.dev/playground/?demo=explorables/julia_map/julia_map.py),
  [simple harmonic motion](https://imgui-bundle.pages.dev/playground/?demo=explorables/lesson_harmonic_motion.py),
  [a tiny neural network that learns two spirals](https://imgui-bundle.pages.dev/playground/?demo=explorables/neural_spiral/neural_spiral.py),
  [the logistic map](https://imgui-bundle.pages.dev/playground/?demo=explorables/logistic_map.py).
- **Narrative programming**, above: the text of an explorable lives in its source file, and places its widgets.

What is missing is the voice and the timeline: a player, and a format for the lessons. That is the project.

## The example: grokking

The first narrated explorable will tell the story of **grokking**, a strange phenomenon of neural networks
(Power et al., OpenAI, 2022; explained by Nanda et al., 2023; a minimal version by David Louapre, 2023).

A small network learns addition modulo 53. It is shown half of the 53 x 53 table of sums, and tested on the other
half. In a few hundred steps it knows the half it has seen by heart, and fails on the other: it has memorized, not
understood. Then, long after, with nothing changed, the test accuracy jumps to 100 %. The network has found the rule.

![Accuracy during training: memorization, then grokking (numpy, 7 seconds on a laptop)](https://imgui-bundle.pages.dev/resources/nex/grok_accuracy.png)

What did it find? Looking inside, at how it represents the 53 numbers, one sees circles: the network built clocks,
and adds by turning hands. The lesson will let the reader watch the table fill in, scrub through the training, and
look at the circles forming.

![The representation of the 53 numbers after grokking](https://imgui-bundle.pages.dev/resources/nex/grok_pca.png)

Everything above runs in numpy, in seconds, on the reader's own device: no GPU, no server. The lesson ships as a text
file, about a megabyte of precomputed data, and a few minutes of cached audio.

## A lesson, in pseudocode

The lesson is a markdown document. Chapters are headings. The narration is ordinary paragraphs, read sentence by
sentence by the voice. What happens on the stage is written apart, in small `cues` blocks placed before the paragraph
they drive; they are Python, run once when the lesson loads, and they record what will happen and when.

````markdown
## Learning by heart

```cues
reset_training()
set_value("weight_decay", 1.0)
```
We train the network on the pairs it is allowed to see.

```cues
animate("step", 300, over=4, at="almost at once")
highlight("train_accuracy", at="hundred percent")
```
The accuracy on these pairs reaches one hundred percent almost at once.
But on the pairs it has never seen... nothing. It learned the table by heart.

### More: overfitting
A model that fits its training data, but not new data, is said to overfit.

## Grokking

```cues
animate("step", 1900, over=8, at="Keep training")
```
Keep training, long after the loss seems to have nothing left to learn. And then, suddenly, the hidden half of the
table turns right, cell by cell.

```cues
pause("Set the weight decay to zero, and train again. Does it still happen?")
```
````

On the program's side, the explorable stays a normal app with its own state and widgets. A few lines tell the lesson
what it may touch:

```python
lesson = narrator.Lesson.from_this_file(section="Lesson")
lesson.param(name="step", owner=app_state, range=(0, 2600))
lesson.param(name="weight_decay", owner=app_state, range=(0.0, 1.0))
lesson.action(name="reset_training", function=app_state.reset)
```

The voice reads the paragraphs; each word's time is known, so a cue lands on its word. When the reader turns a knob
during the narration, the story goes on, and the script takes the knob back at its next cue. Seeking anywhere is
exact, because the narrated values are a function of time.

## Why it may matter

- **For learning**: the medium combines what videos, interactives and texts each do well, and few people have built
  it: Matuschak's article still lists three examples.
- **For understanding AI**: the first lessons are about what neural networks learn and how one can look inside
  (grokking, then the geometry of features), a field whose best work is made of interactive figures.
- **For frugality**: a lesson is a text file and a megabyte of data; the computation is a few seconds of numpy on
  the reader's device; the whole thing is served as static files. No model behind, no server, no account.

## References

Narrative programming:
- Donald Knuth, [Literate Programming](http://www.literateprogramming.com/knuthweb.pdf), The Computer Journal (1984),
  and [his page on the book](https://www-cs-faculty.stanford.edu/~knuth/lp.html);
  [Wikipedia's article](https://en.wikipedia.org/wiki/Literate_programming) lists the tools that followed.
- [Jupyter Book](https://jupyterbook.org) and its [gallery](https://executablebooks.org/en/latest/gallery/) of books
  made of notebooks.
- Bret Victor, [Explorable Explanations](https://worrydream.com/ExplorableExplanations/) (2011).
- Matthew Conlen and Jeffrey Heer, [Idyll](https://idyll-lang.org): a markup language for interactive articles (2018).
- Pascal Thomet, [imgui_rich_md](https://github.com/pthom/imgui_rich_md) and the
  [narrative programming](https://github.com/pthom/imgui_rich_md/blob/main/docs/narrative_programming/narrative_programming.md)
  presentation and specification.

Narrated explorables:
- Andy Matuschak, [Narrated explorables: three mental models](https://medium.com/khan-academy-early-product-development/narrated-explorables-three-mental-models-e16e0d80e4c1) (2018).
- Ben Eater and Grant Sanderson, [Visualizing quaternions](https://eater.net/quaternions).
- David Louapre, [Tangible](https://github.com/scienceetonnante/tangible), a framework for narrated lessons on the web;
  his lessons on [the Navier-Stokes equations](https://huggingface.co/spaces/dlouapre/tangible-navier-stokes) and
  [optimizers](https://huggingface.co/spaces/dlouapre/tangible-optimizers); his
  [grokking notebook](https://github.com/scienceetonnante/grokking) and [article](https://scienceetonnante.substack.com/p/grokking-les-modeles-dia-sont-ils).
- Power, Burda, Edwards, Babuschkin, Misra, [Grokking: generalization beyond overfitting on small algorithmic datasets](https://arxiv.org/abs/2201.02177) (2022).
- Nanda, Chan, Liberum, Smith, Steinhardt, [Progress measures for grokking via mechanistic interpretability](https://arxiv.org/abs/2301.05217) (2023).
- Pascal Thomet, [Dear ImGui Bundle](https://imgui-bundle.pages.dev), the toolkit under all this.
"""


r"""::md Clock
### Addition on a clock
Two numbers are added, then wrapped around $p$: $(a + b) \bmod p$. With $p = 12$, $9 + 5 = 2$, as on a clock.
This is the task the grokking network learns, with $p = 53$.
::code
"""
def add_mod(a: int, b: int, p: int) -> int:
    return (a + b) % p
# ::endcode


def gui() -> None:
    rich_md.render_this_file("Pitch")
    if imgui.collapsing_header("The source of this page"):
        rich_md.render_this_file("")  # the whole file, as code


def main() -> None:
    params = hello_imgui.RunnerParams()
    params.app_window_params.window_title = "Narrated explorables"
    params.app_window_params.window_geometry.size = (1000, 900)
    params.imgui_window_params.tweaked_theme.theme = hello_imgui.ImGuiTheme_.white_is_white  # a page, not a tool
    params.callbacks.show_gui = gui
    immapp.run(params, immapp.AddOnsParams(with_markdown=True, with_latex=True))


if __name__ == "__main__":
    main()
