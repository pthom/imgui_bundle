# Hello, World!

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
