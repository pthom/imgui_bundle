# Developer notes / emscripten

Install emscripten:
see
https://emscripten.org/docs/getting_started/downloads.html
or use external/hello_imgui/hello_imgui/tools/emscripten/install_emscripten.sh

## Build imgui_bundle for emscripten

```bash
mkdir build_ems
cd build_ems
source ~/emsdk/emsdk_env.sh
emcmake cmake .. -DCMAKE_BUILD_TYPE=Release  # This will download a precompiled version of OpenCV4.7.0 for emscripten
make -j
```


Test:
```
python -m http.server
```


Then open http://localhost:8000/bin/ in a browser

## How to build the precompiled OpenCV package for emscripten

**Moved to [docs/book/devel_docs/build_opencv_immvision.md](../build_opencv_immvision.md)** — see the "Rebuilding the emscripten precompiled package" section.
