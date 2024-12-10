# Build instructions for Pyodide

You will need a **Linux** system to build Pyodide.

cf https://pyodide.org/en/stable/development/building-from-sources.html#using-make


## Clone the Pyodide repository fork
```bash
# git clone https://github.com/pyodide/pyodide.git
git clone https://github.com/pthom/pyodide.git
cd pyodide
git checkout imgui_bundle
git submodule update --init --recursive
```

* Create conda environment (pyodide-env)
```bash
conda env create -f environment.yml
conda activate pyodide-env
```

* Build minimal packages
This will download, compile and install emsdk, cpython, and some minimal pyodide packages.
```bash
make
```

## Justfile recipes:

The justfile bindings/pyodide_web_demo/justfile contains recipes
that enable to control the build process of Pyodide and the needed packages on a distant computer.

### Build packages that are needed (apart from imgui_bundle)

Use justfile bindings/pyodide_web_demo/justfile, recipe build_base_packages
```bash
pyodide build-recipes numpy Pillow pandas ipython requests opencv-python typing-extensions pydantic munch matplotlib future scikit-learn
```

### Build and install all needed packages
See bindings/pyodide_web_demo/justfile, recipe build_dist

### Sync the build to the web demo
See bindings/pyodide_web_demo/justfile, recipe copy_dist


# Specific instructions for SDL2 / Link native side with fPIC

There is an issue within pyodide:
A module which links with SDL will link with library_sdl.js but not libSDL2.a :
* Attempting to use functions which are defined in library_sdl.js works (such as as SDL_Init)
* Attempting to use functions which are defined in libSDL2.a fails (such as as SDL_SetHint)

See https://github.com/pyodide/pyodide/issues/5248:
=> We need to trigger the build of a SDL2 library with -fPIC
Use this command to trigger it (from inside the pyodide repository):
```bash
# Activate emscripten
source emsdk/emsdk/emsdk_env.sh
# Create a fake project to trigger the build of the custom SDL2 library with -fPIC
# (aka RELOCATABLE=1, within emscripten)
echo 'int main() {}' | emcc -x c -sUSE_SDL=2 -sRELOCATABLE=1  - -o output.js && rm output.js
```
