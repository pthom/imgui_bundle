# Deploy to the web

Dear ImGui Bundle applications can be effortlessly deployed to the web using Pyodide, enabling Python code to run directly in web browsers. This capability allows developers to share interactive GUI applications without requiring users to install any software.

> **Note:** Pyodide cannot use large native packages (like TensorFlow or PyTorch), and initial loading can be slow.

## Pyodide Minimal Example

With Pyodide, web deployment is as easy as copying this HTML template. The Python code is unchanged from what you'd use for desktop.


```html
<!doctype html>
<html>
<head>
    <style>
        html, body { width: 100%; height: 100%; margin: 0; }
        #canvas { display: block; width: 100%; height: 100%;}
    </style>
    <script src="https://cdn.jsdelivr.net/pyodide/v0.28.2/full/pyodide.js"></script>
</head>
<body>
<canvas id="canvas" tabindex="0"></canvas>
<script type="text/javascript">
    // ====================== Start of Python code ============================
    // Write your python code here
    pythonCode = `
from imgui_bundle import imgui, immapp

def gui():
    imgui.text(f"hello, world")

immapp.run(gui, window_title="Hello World")
`
    // ====================== End of Python code ==============================
    async function main(){
        // This enables to use right click in the canvas
        document.addEventListener('contextmenu', event => event.preventDefault());
        // Load Pyodide
        let pyodide = await loadPyodide();
        // Setup SDL, cf https://pyodide.org/en/stable/usage/sdl.html
        let sdl2Canvas = document.getElementById("canvas");
        pyodide.canvas.setCanvas2D(sdl2Canvas);
        pyodide._api._skip_unwind_fatal_error = true; // SDL requires to enable an opt-in flag :
        // Load imgui_bundle
        await pyodide.loadPackage("imgui_bundle");
        // Run the Python code
        pyodide.runPython(pythonCode);
    }
    main();
</script>
</body>
</html>
```

## Pyodide API

In Pyodide (browser environment), `run()` behaves differently than on desktop: it starts the GUI and **returns immediately** (fire-and-forget), since browsers cannot block.

### Pattern 1: Fire-and-Forget with run() (Recommended)

The simplest pattern - same code as desktop, just works:

```python
from imgui_bundle import imgui, immapp

def gui():
    imgui.text("Hello from Pyodide!")
    if imgui.button("Exit"):
        from imgui_bundle import hello_imgui
        hello_imgui.get_runner_params().app_shall_exit = True

# In Pyodide: starts the GUI and returns immediately
# On desktop: blocks until GUI closes
immapp.run(gui, window_title="My App")
```

**This is perfect when:**
- You want the same code to work on desktop and in browser
- You don't need to do anything after the GUI closes
- You want the simplest possible code

*Note: In Pyodide, `run()` returns immediately. Use `run_async()` if you need to wait for the GUI to exit.*


### Pattern 2: Async Control with run_async()  

_(since v1.92.6)_

For workflows that need to wait for the GUI to exit:

```python
import asyncio
from imgui_bundle import imgui, immapp

def gui():
    imgui.text("Advanced async control")

async def main():
    # Wait for GUI to exit before continuing
    await immapp.run_async(gui, window_title="My App")
    print("GUI closed")

asyncio.create_task(main())
```

**Use this when:**
- You need to know when the GUI exits
- You're integrating with other async code
- You want to run sequential GUI sessions

## A more advanced example

* [animated heart](https://traineq.org/imgui_bundle_online/projects/min_bundle_pyodide_app/demo_heart.html),
* [source code](https://traineq.org/imgui_bundle_online/projects/min_bundle_pyodide_app/demo_heart.source.txt)

```{figure} ../images/heart.png
:alt: Animated heart app running in a web browser using Pyodide
:width: 300px
:align: left
```


## Online Python playground

With [this online playground](https://traineq.org/imgui_bundle_online/projects/imgui_bundle_playground/), you can edit and run imgui apps in the browser, without installing anything.

```{figure} ../images/pyodide_playground.jpg
:alt: A browser window showing the playground: to the right an interactive demo of the butterfly
:width: 600px
:align: center
A browser window showing the playground: to the right an interactive demo of the butterfly effect using a 3D plot, and to the left the python code that creates it.
```

