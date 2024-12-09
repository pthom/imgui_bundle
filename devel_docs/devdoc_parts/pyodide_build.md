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
pip install -r requirements.txt
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
and imgui_bundle_cmake/imgui_bundle_pyodide.cmake:ibd_pyodide_manually_link_sdl_to_bindings()
=> We need to build a custom built SDL2 library with -fPIC
  and to place it in bindings/pyodide_web_demo/build_resources/libSDL2_emscripten_fPIC/libSDL2.a

How to build a new version of the custom SDL2 library with -fPIC
(this file is versioned in git, 1.3MB)
```bash
# Go to pyodide directory
cd path/to/pyodide
# Activate emsdk environment
source emsdk/emsdk/emsdk_env.sh
export SDL_PIC_INSTALL_DIR=$(pwd)/temp_install_sdl2_pic

# Go to SDL2 directory inside emsdk
cd emsdk/emsdk/upstream/emscripten/cache/ports/sdl2/SDL-release-2.28.4
# Configure and build SDL2 with -fPIC with install prefix=$SDL_PIC_INSTALL_DIR
chmod +x ./configure
emconfigure ./configure --host=wasm32-unknown-emscripten --disable-pthreads --disable-assembly --disable-cpuinfo --prefix="$SDL_PIC_INSTALL_DIR" CFLAGS="-fPIC -sUSE_SDL=0 -O3" CXXFLAGS="-fPIC -sUSE_SDL=0 -O3"
emmake make -j
emmake make install

# Then copy libSDL2.a from
#   pyodide/temp_install_sdl2_pic/lib/libSDL2.a
# to
#   imgui_bundle/bindings/pyodide_web_demo/build_resources/libSDL2_emscripten_fPIC/
```