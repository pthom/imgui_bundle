*Note: You can find a more complete version of this document in the
[official documentation site](https://pthom.github.io/imgui_bundle) for
Dear ImGui Bundle.*

[![abc](https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/demos_assets/images/logo_imgui_bundle_512.png)](https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html)

Dear ImGui Bundle: easily create ImGui applications in Python and C++.
Batteries included!

Click on the logo for a complete interactive demonstration!

[![sources](https://github.com/pthom/imgui_bundle/raw/main/bindings/imgui_bundle/doc/doc_images/badge_view_sources.png)](https://github.com/pthom/imgui_bundle/)
[![doc](https://github.com/pthom/imgui_bundle/raw/main/bindings/imgui_bundle/doc/doc_images/badge_view_docs.png)](https://pthom.github.io/imgui_bundle)
[![manual](https://github.com/pthom/imgui_bundle/raw/main/bindings/imgui_bundle/doc/doc_images/badge_interactive_manual.png)](https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html)

# Introduction

## About Dear ImGui Bundle

[Dear ImGui Bundle](https://github.com/pthom/imgui_bundle) is a bundle
for [Dear ImGui](https://github.com/ocornut/imgui), including various
powerful libraries from its ecosystem. It enables to easily create ImGui
applications in C++ and Python, under Windows, macOS, and Linux. It is
aimed at application developers, researchers, and beginner developers
who want to quickly get started.

## Interactive manual & demo in one click!

Click on the animated demonstration below to launch the fully
interactive demonstration.

<figure id="truc">
<img src="https://traineq.org/imgui_bundle_doc/demo_bundle8.gif"
alt="Demo" />
<figcaption>Dear ImGui Bundle interactive demo</figcaption>
</figure>

This demonstration is also an interactive manual, similar to the online
[ImGui
Manual](https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html)

## Batteries included

Dear ImGui Bundle includes the following libraries, which are available
in C++ *and* in Python:

<table>
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup>
<tbody>
<tr class="odd">
<td style="text-align: left;"><p><a
href="https://github.com/ocornut/imgui.git">Dear ImGui</a> : Bloat-free
Graphical User interface for C++ with minimal dependencies</p></td>
<td style="text-align: left;"><p><img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_imgui.jpg"
alt="demo widgets imgui" /></p></td>
</tr>
<tr class="even">
<td style="text-align: left;"><p><a
href="https://github.com/ocornut/imgui_test_engine">ImGui Test
Engine</a>: Dear ImGui Tests &amp; Automation Engine</p></td>
<td style="text-align: left;"><p><img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_testengine.jpg"
alt="demo testengine" /></p></td>
</tr>
<tr class="odd">
<td style="text-align: left;"><p><a
href="https://github.com/pthom/hello_imgui.git">Hello ImGui</a>:
cross-platform Gui apps with the simplicity of a "Hello World"
app</p></td>
<td style="text-align: left;"><p><img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_docking.jpg"
alt="demo docking" /> <img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_custom_background.jpg"
alt="demo custom background" /></p></td>
</tr>
<tr class="even">
<td style="text-align: left;"><p><a
href="https://github.com/epezent/implot">ImPlot</a>: Immediate Mode
Plotting</p></td>
<td style="text-align: left;"><p><img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/battery_implot.jpg"
alt="battery implot" /></p></td>
</tr>
<tr class="odd">
<td style="text-align: left;"><p><a
href="https://github.com/CedricGuillemet/ImGuizmo.git">ImGuizmo</a>:
Immediate mode 3D gizmo for scene editing and other controls based on
Dear ImGui</p></td>
<td style="text-align: left;"><p><img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_gizmo.jpg"
alt="demo gizmo" /></p></td>
</tr>
<tr class="even">
<td style="text-align: left;"><p><a
href="https://github.com/BalazsJako/ImGuiColorTextEdit">ImGuiColorTextEdit</a>:
Colorizing text editor for ImGui</p></td>
<td style="text-align: left;"><p><img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_editor.jpg"
alt="demo widgets editor" /></p></td>
</tr>
<tr class="odd">
<td style="text-align: left;"><p><a
href="https://github.com/thedmd/imgui-node-editor">imgui-node-editor</a>:
Node Editor built using Dear ImGui</p></td>
<td style="text-align: left;"><p><img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_node_editor.jpg"
alt="demo node editor" /></p></td>
</tr>
<tr class="even">
<td style="text-align: left;"><p><a
href="https://github.com/mekhontsev/imgui_md.git">imgui_md</a>: Markdown
renderer for Dear ImGui using MD4C parser</p></td>
<td style="text-align: left;"><p><img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_md.jpg"
alt="demo widgets md" /></p></td>
</tr>
<tr class="odd">
<td style="text-align: left;"><p><a
href="https://github.com/pthom/immvision.git">ImmVision</a>: Immediate
image debugger and insights</p></td>
<td style="text-align: left;"><p><img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_immvision_process_1.jpg"
alt="demo immvision process 1" /> <img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_immvision_process_2.jpg"
alt="demo immvision process 2" /></p></td>
</tr>
<tr class="even">
<td style="text-align: left;"><p><a
href="https://github.com/andyborrell/imgui_tex_inspect">imgui_tex_inspect</a>:
A texture inspector tool for Dear ImGui</p></td>
<td style="text-align: left;"><p><img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_imgui_tex_inspector.jpg"
alt="demo imgui tex inspector" /></p></td>
</tr>
<tr class="odd">
<td style="text-align: left;"><p><a
href="https://github.com/pthom/ImFileDialog.git">ImFileDialog</a>: A
file dialog library for Dear ImGui</p></td>
<td style="text-align: left;"><p><img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_imfiledialog.jpg"
alt="demo widgets imfiledialog" /></p></td>
</tr>
<tr class="even">
<td style="text-align: left;"><p><a
href="https://github.com/samhocevar/portable-file-dialogs">portable-file-dialogs</a>
<em>OS native</em> file dialogs library (C++11, single-header)</p></td>
<td style="text-align: left;"><p><img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_portablefiledialogs.jpg"
alt="demo widgets portablefiledialogs" /></p></td>
</tr>
<tr class="odd">
<td style="text-align: left;"><p><a
href="https://github.com/altschuler/imgui-knobs">imgui-knobs</a>: Knobs
widgets for ImGui</p></td>
<td style="text-align: left;"><p><img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_knobs.jpg"
alt="demo widgets knobs" /></p></td>
</tr>
<tr class="even">
<td style="text-align: left;"><p><a
href="https://github.com/dalerank/imspinner">imspinner</a>: Set of nice
spinners for imgui</p></td>
<td style="text-align: left;"><p><img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_spinners.jpg"
alt="demo widgets spinners" /></p></td>
</tr>
<tr class="odd">
<td style="text-align: left;"><p><a
href="https://github.com/cmdwtf/imgui_toggle">imgui_toggle</a>: A toggle
switch widget for Dear ImGui</p></td>
<td style="text-align: left;"><p><img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_toggle.jpg"
alt="demo widgets toggle" /></p></td>
</tr>
<tr class="even">
<td style="text-align: left;"><p><a
href="https://github.com/aiekick/ImCoolBar">ImCoolBar</a>: A Cool bar
for Dear ImGui</p></td>
<td style="text-align: left;"><p><img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_coolbar.jpg"
alt="demo widgets coolbar" /></p></td>
</tr>
<tr class="odd">
<td style="text-align: left;"><p><a
href="https://github.com/hnOsmium0001/imgui-command-palette.git">imgui-command-palette</a>:
A Sublime Text or VSCode style command palette in ImGui</p></td>
<td style="text-align: left;"><p><img
src="https://raw.githubusercontent.com/pthom/imgui_bundle/main/bindings/imgui_bundle/doc/doc_images/demo_widgets_command_palette.jpg"
alt="demo widgets command palette" /></p></td>
</tr>
</tbody>
</table>

A big thank you to their authors for their awesome work!

## Easily port your code between python and C++

The python bindings are autogenerated via an advanced generator (so that
keeping them up to date is easy), and closely mirror the original C++
API, with fully typed bindings.

The original code documentation is meticulously kept inside the python
stubs. See for example the documentation for
[imgui](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/imgui/__init__.pyi)
,
[implot](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/implot.pyi),
and [hello
imgui](https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/hello_imgui.pyi)

Thanks to this, code completion in your favorite python IDE works like a
charm, and porting code between Python and C++ becomes easy.

GPT can help you translate between C++ and Python: see [this
conversation](https://chat.openai.com/share/1e61dfec-c2de-4c2a-8149-24926276bbd5)
where GPT4 was used to translate code and summarize the differences
between the C++ and Python APIs.

# Build and install instructions

## Install for Python

### Install from pypi

    pip install imgui-bundle
    pip install opencv-contrib-python

-   in order to run the immvision module, install opencv-python or
    opencv-contrib-python

Note: under windows, you might need to install [msvc
redist](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#visual-studio-2015-2017-2019-and-2022).

### Install from source:

    git clone https://github.com/pthom/imgui_bundle.git
    cd imgui_bundle
    git submodule update --init --recursive
    pip install -v .
    pip install opencv-contrib-python

-   Since there are lots of submodules, this might take a few minutes

-   The build process might take up to 5 minutes

### Run the python demo

Simply run `demo_imgui_bundle`.

The source for the demos can be found inside
[bindings/imgui\_bundle/demos\_python](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/demos_python).

Consider `demo_imgui_bundle` as an always available manual for Dear
ImGui Bundle with lots of examples and related code source.

## Install for C++

### Integrate Dear ImGui Bundle in your own project in 5 minutes

The easiest way to use Dear ImGui Bundle in an external project is to
use the template available at
<https://github.com/pthom/imgui_bundle_template>.

This template includes everything you need to set up your own project.

### Build from source

If you choose to clone this repo, follow these instructions:

    git clone https://github.com/pthom/imgui_bundle.git
    cd imgui_bundle
    git submodule update --init --recursive
    mkdir build
    cd build
    cmake .. -DIMMVISION_FETCH_OPENCV=ON
    make -j

-   Since there are lots of submodules, this might take a few minutes

-   The flag `-DIMMVISION_FETCH_OPENCV=ON` is optional. If set, a
    minimal version of OpenCV will be downloaded a compiled at this
    stage (this might require a few minutes)

The `immvision` module will only be built if OpenCV can be found.
Otherwise, it will be ignored, and no error will be emitted.

If you have an existing OpenCV install, set its path via:

    cmake .. -DOpenCV_DIR=/.../path/to/OpenCVConfig.cmake

### Run the C++ demo

If you built ImGuiBundle from source, Simply run
`build/bin/demo_imgui_bundle`.

The source for the demos can be found inside
[bindings/imgui\_bundle/demos\_cpp](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/demos_cpp/).

Consider `demo_imgui_bundle` as a manual with lots of examples and
related code source. It is always [available
online](https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html)

# Closing words

## Who is this project for

As mentioned in the intro,

[Dear ImGui Bundle](https://github.com/pthom/imgui_bundle) is a bundle
for [Dear ImGui](https://github.com/ocornut/imgui), including various
powerful libraries from its ecosystem. It enables to easily create ImGui
applications in C++ and Python, under Windows, macOS, and Linux. It is
aimed at application developers, researchers, and beginner developers
who want to quickly get started.

Dear ImGui Bundle aims to make applications prototyping fast and easy,
in a multiplatform / multi-tooling context. The intent is to reduce the
time between an idea and a first GUI prototype down to almost zero.

It is well adapted for

-   developers and researchers who want to switch easily between and
    research and development environment by facilitating the port of
    research artifacts

-   beginners and developers who want to quickly develop an application
    without learning a GUI framework

### Who is this project **not** for

You should prefer a more complete framework (such as Qt for example) if
your intent is to build a fully fledged application, with support for
internationalization, advanced styling, etc.

Also, the library makes no guarantee of ABI stability, and its API is
opened to slight adaptations and breaking changes if they are found to
make the overall usage better and/or safer.

## Acknowledgments

Dear ImGui Bundle would not be possible without the work of the authors
of "Dear ImGui", and especially [Omar
Cornut](https://www.miracleworld.net/).

It also includes a lot of other projects, and I’d like to thank their
authors for their awesome work!

A particular mention for [Evan Pezent](https://evanpezent.com/) (author
of ImPlot), [Cédric Guillemet](https://github.com/CedricGuillemet)
(author of ImGuizmo), [Balázs
Jákó](https://merlin3d.wordpress.com/about/) (author of
ImGuiColorTextEdit), and [Michał Cichoń](https://github.com/thedmd)
(author of imgui-node-editor), and [Dmitry
Mekhontsev](https://github.com/mekhontsev) (author of imgui-md), [Andy
Borrel](https://github.com/andyborrell) (author of imgui-tex-inspect,
another image debugging tool, which I discovered long after having
developed immvision).

This doc was built using [Asciidoc](https://asciidoc.org/).

Immvision was inspired by [The Image
Debugger](https://billbaxter.com/projects/imdebug/), by Bill Baxter.

## License

The MIT License (MIT)

Copyright (c) 2021-2024 Pascal Thomet

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Alternatives

[pyimgui](https://pyimgui.readthedocs.io/en/latest/) provides
battle-tested comprehensive python bindings for ImGui. I worked with
this project a lot, and contributed a bit to it. In the end, I had to
develop a separate project, in order to be able to add auto-generated
and auto-documented python modules.

[Dear PyGui](https://dearpygui.readthedocs.io/en/latest/)
([repository](https://github.com/hoffstadt/DearPyGui)) provides python
bindings for ImGui with a lot of addons, and a more pythonesque API,
which makes it perhaps more suited for Python only projects.

## About the author

Dear ImGui Bundle is developed by Pascal Thomet. I am reachable on my
[Github page](https://github.com/pthom). I sometimes
[blog](http://code-ballads.net/). There is a
[playlist](https://www.youtube.com/playlist?list=PLaJx_KrDECZPzttQ77Gv8DD7OAUwmtWUc)
related to ImGui Bundle on YouTube.

I have a past in computer vision, and a lot of experience in the
trenches between development and research teams; and I found ImGui to be
a nice way to reduce the delay between a research prototype and its use
in production code.

I also have an inclination for self documenting code, and the doc you
are reading was a way to explore new ways to document projects.

## How is Dear ImGui Bundle developed

The development of the initial version of Dear ImGui Bundle took about
one year at full time.

The bindings are auto-generated thanks to an advanced parser, so that
they are easy to keep up to date.

Please be tolerant if you find issues! Dear ImGui Bundle is developed
for free, under a very permissive license, by one main author (and most
of its API comes from external libraries).

If you need consulting about this library or about the bindings
generator in the context of a commercial project, please contact me by
email.

Contributions are welcome!

### History

Three of my past projects gave me the idea to develop this library.

-   [ImGui
    Manual](https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html),
    an interactive manual for Dear ImGui, which I developed in June 2020

-   [implot demo](https://traineq.org/implot_demo/src/implot_demo.html)
    which I developed in 2020.

-   [imgui\_datascience](https://github.com/pthom/imgui_datascience), a
    python package I developed in 2018 for image analysis and debugging.
    Its successor is immvision.

Developments for Dear ImGui Bundle and its related automatic binding
generator began in january 2022.
