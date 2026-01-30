# Debug native C++ in Python bindings

ImGui Bundle provides tooling to help you debug the C++ side when you encounter a bug that is difficult to diagnose from Python.
For this, you will need to clone the repository and build the C++ project `pybind_native_debug` in debug mode.
It can be used in two steps:

1. Edit the file `pybind_native_debug/pybind_native_debug.py`. Change its content so that it runs the Python code you would like to debug. Make sure it works when you run it as a Python script.

2. Now, debug the C++ project `pybind_native_debug` which is defined in the directory `pybind_native_debug/`. This will run your Python code from C++, and you can debug the C++ side (place breakpoints, watch variables, etc).

