# Build imgui-bundle for pyodide using Docker

# Introduction

Building for pyodide is actually quite tricky because

- You need to build it from inside the pyodide and pyodide-recipes repositories
  (if you build it outside, you will get linking errors, and runtime errors, mostly due to side loaded libraries)
- You cannot build on macOS because of a subtle issue in scikit-build-core

Below are some instructions to build the imgui-bundle package which work on a linux machine.

# Instructions to build the pyodide package:

Building imgui-bundle for pyodide is quite complex and the only way I managed to compile is "as an internal recipe", following the instructions from https://pyodide.org/en/stable/development/building-from-sources.html


Then

**Create a virtual environment for Pyodide build**

```
python3.13 -m venv venv_pyodidebuild
source venv_pyodidebuild/bin/activate
```

**Clone Pyodide repository and initialize submodules**
```
git clone https://github.com/pyodide/pyodide.git
cd pyodide
pip install -r requirements.txt
git submodule update --init --recursive
cd -
```

**Install Pyodide build**
```
cd pyodide/pyodide-build 
pip install -v -e .
cd -
```

**Build pyodide (will build emsdk, pyodide, and the packages)**

```
cd pyodide
make
cd -
```

**Clone imgui_bundle**

```
git clone https://github.com/pthom/imgui_bundle
cd imgui_bundle
git submodule update --init --recursive
cd -
```


**Clone pyodide-recipes**

```
git clone https://github.com/pyodide/pyodide-recipes.git
```


**Edit pyodide-recipes/packages/imgui-bundle/meta.yaml**

1. change its source path**

For example

```
source:
  path: /home/pascal/dvp/_Bundle/_Pyodide/tst_pyo_scratch_202511/imgui_bundle
  # Below, comment out old url
  # url: https://github.com/pthom/imgui_bundle/releases/download/v1.92.4/srcs-full-v1.92.4.tar.gz
  # sha256: c53afb7fb410c12f9727ce504b61125d048f60aeb6ca0d50ccbb395c40ccd3c8
```

2. Change the version number

For example

```
package:
  name: imgui-bundle
  version: 1.92.5
  top-level:
    - imgui_bundle
```

**Build imgui-bundle pyodide package**
```
cd pyodide
pyodide build-recipes imgui-bundle --recipe-dir ../pyodide-recipes/packages --install
cd -
```

The build package will be placed inside pyodide/dist/


# Goals

I would like to be able to use those instructions inside a docker container, with the following goals:
- A semi resident docker container that has all the build tools installed (python 3.13, emsdk, cmake, ninja, pyodide checked out, pyodide-recipes checked out, etc)
- A way to mount the imgui-bundle source code into the container, so that I can build new versions without rebuilding the entire docker image
- A way to trigger the build and copy the built package out of the container
- A way to test the built package in a browser
- We will need to define a nice directory structure in the repo machine to hold all those files

For example this html file

````
<!doctype html>
<html>
<head>
    <style>
        html, body { width: 100%; height: 100%; margin: 0; }
        #canvas { display: block; width: 100%; height: 100%;}
    </style>
    <!-- Here, we could use either a local copy of pyodide.js, or one from the CDN -->
    <script src="pyodide_dist/pyodide.js"></script>
    <!-- <script src="https://cdn.jsdelivr.net/pyodide/v0.29.2/full/pyodide.js"></script> -->
</head>
<body>
<canvas id="canvas" tabindex="0"></canvas>
<script type="text/javascript">

    // ====================== Start of Python code ============================
    pythonCode = `
import os
import imgui_bundle
print(imgui_bundle.info())
`
    // ====================== End of Python code ==============================


    async function main(){
        // This enables to use right click in the canvas
        document.addEventListener('contextmenu', event => event.preventDefault());

        // Load Pyodide
        let pyodide = await loadPyodide();

        // Setup SDL, cf https://pyodide.org/en/stable/usage/sdl.html
        // 1. Set the canvas for SDL2
        let sdl2Canvas = document.getElementById("canvas");
        pyodide.canvas.setCanvas2D(sdl2Canvas);
        // 2. SDL requires to enable an opt-in flag :
        pyodide._api._skip_unwind_fatal_error = true;

        // 3. Load imgui_bundle
        // 3.i Either via loadPackage : here we would pass a full url to our built package
        await pyodide.loadPackage("imgui_bundle");
        // 3.ii Or with micropip
        // await pyodide.loadPackage("micropip");
        // const micropip = pyodide.pyimport("micropip");
        // await micropip.install('imgui_bundle');

        // Run the Python code
        pyodide.runPython(pythonCode);
    }
    main();
</script>
</body>
</html>
````
