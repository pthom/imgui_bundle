# Closing words

## Who is this project for

As mentioned in the intro,

[Dear ImGui Bundle](https://github.com/pthom/imgui_bundle) is a bundle for [Dear ImGui](https://github.com/ocornut/imgui), including various powerful libraries from its ecosystem. It enables to easily create ImGui applications in C++ and Python, under Windows, macOS, and Linux. It is aimed at application developers, researchers, and beginner developers who want to quickly get started.

Dear ImGui Bundle aims to make applications prototyping fast and easy, in a multiplatform / multi-tooling context. The intent is to reduce the time between an idea and a first GUI prototype down to almost zero.

It is well adapted for

-   developers and researchers who want to switch easily between and research and development environment by facilitating the port of research artifacts

-   beginners and developers who want to quickly develop an application without learning a GUI framework

### Who is this project **not** for

You should prefer a more complete framework (such as Qt for example) if your intent is to build a fully fledged application, with support for internationalization, advanced styling, etc.

Also, the library makes no guarantee of ABI stability, and its API is opened to slight adaptations and breaking changes if they are found to make the overall usage better and/or safer.

## Acknowledgments

Dear ImGui Bundle would not be possible without the work of the authors of \"Dear ImGui\", and especially [Omar Cornut](https://www.miracleworld.net/).

It also includes a lot of other projects, and I'd like to thank their authors for their awesome work!

A particular mention for [Evan Pezent](https://evanpezent.com/) (author of ImPlot), [Cédric Guillemet](https://github.com/CedricGuillemet) (author of ImGuizmo), [Balázs Jákó](https://merlin3d.wordpress.com/about/) (author of ImGuiColorTextEdit), and [Michał Cichoń](https://github.com/thedmd) (author of imgui-node-editor), and [Dmitry Mekhontsev](https://github.com/mekhontsev) (author of imgui-md), [Andy Borrel](https://github.com/andyborrell) (author of imgui-tex-inspect, another image debugging tool, which I discovered long after having developed immvision).

This doc was built using [Asciidoc](https://asciidoc.org/).

Immvision was inspired by [The Image Debugger](https://billbaxter.com/projects/imdebug/), by Bill Baxter.

## License

The MIT License (MIT)

Copyright (c) 2021-2023 Pascal Thomet

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Alternatives

[pyimgui](https://pyimgui.readthedocs.io/en/latest/) provides battle-tested comprehensive python bindings for ImGui. I worked with this project a lot, and contributed a bit to it. In the end, I had to develop a separate project, in order to be able to add auto-generated and auto-documented python modules.

[Dear PyGui](https://dearpygui.readthedocs.io/en/latest/) ([repository](https://github.com/hoffstadt/DearPyGui)) provides python bindings for ImGui with a lot of addons, and a more pythonesque API, which makes it perhaps more suited for Python only projects.

## About the author

Dear ImGui Bundle is developed by Pascal Thomet. I am reachable on my [Github page](https://github.com/pthom). I sometimes [blog](http://code-ballads.net/). There is a [playlist](https://www.youtube.com/playlist?list=PLaJx_KrDECZPzttQ77Gv8DD7OAUwmtWUc) related to ImGui Bundle on YouTube.

I have a past in computer vision, and a lot of experience in the trenches between development and research teams; and I found ImGui to be a nice way to reduce the delay between a research prototype and its use in production code.

I also have an inclination for self documenting code, and the doc you are reading was a way to explore new ways to document projects.

## How is Dear ImGui Bundle developed

The development of the initial version of Dear ImGui Bundle took about one year at full time.

The bindings are auto-generated thanks to an advanced parser, so that they are easy to keep up to date. I'll give more information about the bindings generator a bit later in 2023.

Please be tolerant if you find issues! Dear ImGui Bundle is developed for free, under a very permissive license, by one main author (and most of its API comes from external libraries).

If you need consulting about this library or about the bindings generator in the context of a commercial project, please contact me by email.

Contributions are welcome!

### History

Three of my past projects gave me the idea to develop this library.

-   [ImGui Manual](https://pthom.github.io/imgui_manual_online/manual/imgui_manual.html), an interactive manual for Dear ImGui, which I developed in June 2020

-   [implot demo](https://traineq.org/implot_demo/src/implot_demo.html) which I developed in 2020.

-   [imgui_datascience](https://github.com/pthom/imgui_datascience), a python package I developed in 2018 for image analysis and debugging. Its successor is immvision.

Developments for Dear ImGui Bundle and its related automatic binding generator began in january 2022.
