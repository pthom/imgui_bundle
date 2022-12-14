# Requirement for immvision: OpenCV 

immvision is a powerful submodule that displays and analyses images.
OpenCV is required if you want to have immvision inside imgui_bundle. Below are several alternative for an easy installation:

## Windows: get a prebuilt OpenCV library
Download the latest windows package from https://opencv.org/releases/: you should download and extract opencv-4.6.0-vc14_vc15.exe

## ubuntu
	sudo apt-get install libopencv-dev

## MacOS
	brew install opencv

## Other installation methods
You can also install OpenCV with any other method (conan, vcpkg, etc.). Just make sure it can be found (to help discovery, you can set the env var OpenCV_DIR).

# Python pip package build instructions

## Note on pip package cache

When building from source, there are some caches in the folder _skbuild. Remove it to redo a full build from scratch.

## How to have immmvision: Set OpenCV_DIR
Under windows, if you want to have the immvision module, you will need to have a working OpenCV library, 
and to set the environment variable OpenCV_DIR before invoking `pip install -v .`
See [How to install OpenCV](#How_to_install_OpenCV)

Under linux and Ubuntu, if you installed OpenCV via a system package manager, it should be found automatically.

Not so funny note: there are at least 4 incompatible ways to set an env var in Windows:
* the clicky way
* with PowerShell
	Set-Item -Path 'Env:OpenCV_DIR' -Value 'C:/your/path/to/opencv-4.6.0-vc14_vc15/opencv/build'
* With bash:
	export OpenCV_DIR=C:/your/path/to/opencv-4.6.0-vc14_vc15/opencv/build
* With dos:
	set OpenCV_DIR=C:/your/path/to/opencv-4.6.0-vc14_vc15/opencv/build

## Build ImGui Bundle pip package from sources

````
cd path/to/your/project  # optional step, but recommended:
python -m venv venv      # create and activate a virtual env
.\venv\Script\activate      

git clone https://github.com/pthom/imgui_bundle.git
cd imgui_bundle
pip install -v .          # install the library
````



### Build and the library pip package from sources:

    pip install -v .


# C++ build instructions

````
git clone https://github.com/pthom/imgui_bundle.git
cd imgui_bundle
mkdir build
cd build 
cmake ..
````

If you want immvision, install OpenCV prior to this, and under windows, set the environment variable OpenCV_DIR to the correct location.

Note: if you are on windows ARM64 and want to build for x64 use:
    cmake .. -A x64

# Windows ARM64 specific instructions

There is no prebuild version of OpenCV for Windows ARM64. See instructions below, in order to build your own.


## Using a "world" dll version of OpenCV 

### Build and install a DLL "world" version of OpenCV for ARM64
(world means you get only one dll for all OpenCV)

The two important options are INSTALL_CREATE_DISTRIB (will create dll opencv_world), BUILD_SHARED_LIBS=ON (required for world build).

You can tweak the other options, which are here to reduce the build time.

 (**Change the last parameter of the cmake command to your desired installation path**)

````
mkdir build_arm64_dll_world
cd build_arm64_dll_world

cmake ../opencv_git -DINSTALL_CREATE_DISTRIB=ON -DBUILD_SHARED_LIBS=ON -A ARM64 -DCMAKE_BUILD_TYPE=Release -DBUILD_opencv_apps=OFF -DBUILD_TESTS=OFF -DBUILD_PERF_TESTS=OFF -DBUILD_opencv_python2=OFF -DBUILD_opencv_python3=OFF -DCMAKE_INSTALL_PREFIX=F:/dvp/_OpenCV/opencv4.6.0_arm64_dll_world

cmake --build . --config Release
cmake --install . --config Release

cmake --build . --config Debug
cmake --install . --config Debug

cd ..
````


### Build ImGui Bundle pip package on Windows ARM64 with "world" opencv

> Note / December 2022: at the time of writing, the pip package "opencv-python" refuses to build with python ARM64 on windows. imgui_bundle does work however but one cannot use opencv (aka cv2) from python.

You need an arm version of python. See https://www.python.org/downloads/windows/
(if you need pip, youd need the full setup, not the embeddable version)

Set OpenCV env variables: 
* OpenCV_DIR=/path/to/your/opencv_world_install
* CMAKE_GENERATOR_PLATFORM=ARM64

Not so funny note: there are at least 4 incompatible ways to set an env var in Windows. 

* *The clicky way*
* *with PowerShell*
	Set-Item -Path 'Env:OpenCV_DIR' -Value 'F:/dvp/_opencv/opencv4.6.0_arm64_dll_world'
	Set-Item -Path 'Env:CMAKE_GENERATOR_PLATFORM' -Value 'ARM64'
* *With bash*
	export OpenCV_DIR=F:/dvp/_opencv/opencv4.6.0_arm64_dll_world
	export CMAKE_GENERATOR_PLATFORM=ARM64
* *With dos*
	set OpenCV_DIR=F:/dvp/_opencv/opencv4.6.0_arm64_dll_world
	set CMAKE_GENERATOR_PLATFORM=ARM64


Then, pip install:
    pip install -v .

### Build CppLib on Windows ARM64 with world OpenCV

Specify cmake options

	cmake .. -DOpenCV_DIR=F:/dvp/_opencv/opencv4.6.0_arm64_dll_world -DCMAKE_GENERATOR_PLATFORM=ARM64

Explanations:

* OpenCV_DIR: you opencv install path
* CMAKE_GENERATOR_PLATFORM: tells openCV to look in  the ARM64 folder
  


## Using a static version of OpenCV 

### Build and install a static version of OpenCV for ARM64


Git clone and checkout v4.6.0
````
mkdir _opencv
cd _opencv
git clone https://github.com/opencv/opencv.git opencv_git
cd opencv_git
git checkout 4.6.0
cd ..
````

Build and install OpenCV with those settings (**Change the last parameter of the cmake command to your desired installation path**)

The important option is BUILD_SHARED_LIBS=OFF. 
You can tweak the other options, which are here to reduce the build time.


````
mkdir build_ARM64
cd build_ARM64

cmake ../opencv_git -A ARM64 -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF -DBUILD_opencv_apps=OFF -DBUILD_TESTS=OFF -DBUILD_PERF_TESTS=OFF -DBUILD_opencv_python2=OFF -DBUILD_opencv_python3=OFF -DBUILD_JASPER=OFF -DWITH_JASPER=OFF -DWITH_CUDA=OFF -DWITH_FFMPEG=OFF -DWITH_GTK=OFF -DCMAKE_INSTALL_PREFIX=F:/dvp/_OpenCV/opencv4.6.0_static_install_win_vc17

cmake --build . --config Release
cmake --install .
cd ..
````


### Build ImGui Bundle pip package on Windows ARM64 with *static* OpenCV

You need an arm version of python. See https://www.python.org/downloads/windows/
(if you need pip, youd need the full setup, not the embeddable version)


Set OpenCV env variables:
* with PowerShell

	Set-Item -Path 'Env:OpenCV_DIR' -Value 'F:/dvp/_opencv/opencv4.6.0_static_install_win_vc17'
	Set-Item -Path 'Env:OpenCV_STATIC' -Value 'ON'

	Set-Item -Path 'Env:CMAKE_GENERATOR_PLATFORM' -Value 'ARM64'

* With bash:
	export OpenCV_DIR=F:/dvp/_opencv/opencv-4.6.0-vc14_vc15/opencv/build
* With dos:
	set OpenCV_DIR=F:/dvp/_opencv/opencv-4.6.0-vc14_vc15/opencv/build




### Build CppLib on Windows ARM64 with static OpenCV

Specify cmake options

````
cmake .. -DOpenCV_DIR=F:/dvp/_opencv/opencv4.6.0_static_install_win_vc17 -DOpenCV_STATIC=ON -DCMAKE_GENERATOR_PLATFORM=ARM64 -DBUILD_SHARED_LIBS=OFF -DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded
````

Explanations:

* OpenCV_DIR: you opencv install path
* CMAKE_GENERATOR_PLATFORM: tells openCV to look in  the ARM64 folder
* OpenCV_STATIC: tells OpenCV to look in the ARM64/vc17/staticlib folder
* CMAKE_MSVC_RUNTIME_LIBRARY: tells MSVC to use static runtime (/MT)
* BUILD_SHARED_LIBS=OFF: build static libs. Normally, this could be ignored
  


# Private note for this library author :  

- Cpp: use ARM64 build

````
cmake .. -DOpenCV_DIR=F:/dvp/_opencv/opencv4.6.0_arm64_dll_world -DCMAKE_GENERATOR_PLATFORM=ARM64 -DHELLOIMGUI_BUILD_DEMOS=ON
````

- Python: prefer python x64 (because numpy does not work on python arm64)

````
F:\Utils\Python311-amd64\python.exe -m venv venv_arm
.\venv_amd\Scripts\activate
Set-Item -Path 'Env:OpenCV_DIR' -Value 'F:\dvp\_opencv\opencv-4.6.0_official_win_x64_world\opencv\build'
pip install -v .
````



# imgui bundle package distribution
## Build and deploy to pypi:

````
python3 -m build --wheel  --sdist . 
python3 -m build --sdist .

# or 
python3 -m build  .

# then

twine upload dist/*
````

login = __token__
password = ...api_token...

