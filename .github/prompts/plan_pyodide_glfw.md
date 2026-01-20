# Using glfw instead of sdl2 with pyodide

emscripten-glfw (https://github.com/pongasoft/emscripten-glfw) uses some js code see: https://github.com/pongasoft/emscripten-glfw/tree/master/src/js

=> We have the same issue as with sdl2 where we need the main pyodide module to link with this js code. imgui_bundle is just a side module and cannot provide the js code to the main pyodide module.

What was tried:
-