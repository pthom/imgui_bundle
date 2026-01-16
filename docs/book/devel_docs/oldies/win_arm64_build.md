# Developer note: Windows ARM64

:::{admonition} Summary
:class: note

Summary (private note for this library author):
- Cpp: use ARM64 build

```bash
cmake .. -DOpenCV_DIR=F:/dvp/_opencv/opencv4.6.0_arm64_dll_world -DCMAKE_GENERATOR_PLATFORM=ARM64 -DHELLOIMGUI_USE_SDL_OPENGL3=ON
```

- Python: prefer python x64 aka amd64 (because numpy does not work on python arm64)

```bash
F:\Utils\Python311-amd64\python.exe -m venv venv_x64
.\venv_x64\Scripts\activate
pip install -v .
pip install opencv-contrib-python
demo_imgui_bundle
```
:::

There is no prebuild version of OpenCV for Windows ARM64. See instructions below, in order to build your own.

Note: if you are on windows ARM64 and want to build for x64 use:
```bash
cmake .. -A x64
```


## Using a "world" dll version of OpenCV

### Build and install a DLL "world" version of OpenCV for ARM64
(world means you get only one dll for all OpenCV)

The two important options are INSTALL_CREATE_DISTRIB (will create dll opencv_world), BUILD_SHARED_LIBS=ON (required for world build).

You can tweak the other options, which are here to reduce the build time.

 (**Change the last parameter of the cmake command to your desired installation path**)

```bash
mkdir build_arm64_dll_world
cd build_arm64_dll_world

cmake ../opencv_git -DINSTALL_CREATE_DISTRIB=ON -DBUILD_SHARED_LIBS=ON -A ARM64 -DCMAKE_BUILD_TYPE=Release -DBUILD_opencv_apps=OFF -DBUILD_TESTS=OFF -DBUILD_PERF_TESTS=OFF -DBUILD_opencv_python2=OFF -DBUILD_opencv_python3=OFF -DCMAKE_INSTALL_PREFIX=F:/dvp/_OpenCV/opencv4.6.0_arm64_dll_world

cmake --build . --config Release
cmake --install . --config Release

cmake --build . --config Debug
cmake --install . --config Debug

cd ..
```


### Build ImGui Bundle pip package on Windows ARM64 with "world" opencv

Note / December 2022: at the time of writing, the pip package "opencv-python" refuses to build with python ARM64 on windows. imgui_bundle does work however but one cannot use opencv (aka cv2) from python.

You need an arm version of python. See https://www.python.org/downloads/windows/
(if you need pip, youd need the full setup, not the embeddable version)

Set OpenCV env variables:

* OpenCV_DIR=/path/to/your/opencv_world_install
* CMAKE_GENERATOR_PLATFORM=ARM64

Not so funny note: there are at least 4 incompatible ways to set an env var in Windows.

* **The clicky way**
* **with PowerShell**
    ```powershell
    Set-Item -Path 'Env:OpenCV_DIR' -Value 'F:/dvp/_opencv/opencv4.6.0_arm64_dll_world'
    Set-Item -Path 'Env:CMAKE_GENERATOR_PLATFORM' -Value 'ARM64'
    ```
* **With bash**
    ```bash
    export OpenCV_DIR=F:/dvp/_opencv/opencv4.6.0_arm64_dll_world
    export CMAKE_GENERATOR_PLATFORM=ARM64
    ```
* **With dos**
    ```cmd
    set OpenCV_DIR=F:/dvp/_opencv/opencv4.6.0_arm64_dll_world
    set CMAKE_GENERATOR_PLATFORM=ARM64
    ```


Then, pip install:

```bash
pip install -v .
```

### Build CppLib on Windows ARM64 with world OpenCV

Specify cmake options

```bash
cmake .. -DOpenCV_DIR=F:/dvp/_opencv/opencv4.6.0_arm64_dll_world -DCMAKE_GENERATOR_PLATFORM=ARM64
```

Explanations:

* OpenCV_DIR: you opencv install path
* CMAKE_GENERATOR_PLATFORM: tells openCV to look in  the ARM64 folder



## Using a static version of OpenCV

