# Build and deploy to pypi:

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


# Build pip package on Windows x64 with immvision (incl OpenCV)

Download the latest windows package from https://opencv.org/releases/.
You should download and extract opencv-4.6.0-vc14_vc15.exe

F:\dvp\_opencv\opencv-4.6.0-vc14_vc15\opencv\build

F:/dvp/_opencv/opencv-4.6.0-vc14_vc15/opencv/build


Set an env variable OpenCV_DIR: 3 different ways

* with PowerShell
	Set-Item -Path 'Env:OpenCV_DIR' -Value 'F:/dvp/_opencv/opencv-4.6.0-vc14_vc15/opencv/build'
* With bash:
	export OpenCV_DIR=F:/dvp/_opencv/opencv-4.6.0-vc14_vc15/opencv/build
* With dos:
	set OpenCV_DIR=F:/dvp/_opencv/opencv-4.6.0-vc14_vc15/opencv/build


-------

# Windows ARM64 instructions


## Build and install a static version of OpenCV for ARM64

Git clone and checkout v4.6.0
````
mkdir _opencv
cd _opencv
git clone https://github.com/opencv/opencv.git
cd opencv
git checkout 4.6.0
cd ..
````

Build and install OpenCV with those settings:

Note: end of line handling in shells is a joke: 
Use 
- " ^" for dos
- " \" for bash 
- " `" for powerhell

````
mkdir build_ARM64
cd build_ARM64
^
cmake ../opencv ^
-A ARM64 ^
-DCMAKE_BUILD_TYPE=Release ^
-DBUILD_SHARED_LIBS=OFF ^
-DBUILD_opencv_apps=OFF ^
-DCMAKE_INSTALL_PREFIX=F:/dvp/_OpenCV/opencv4.6.0_static_install_win_vc17 ^
 ^
-DBUILD_TESTS=OFF ^
-DBUILD_PERF_TESTS=OFF ^
 ^
 -DBUILD_opencv_python2=OFF -DBUILD_opencv_python3=OFF ^
-DBUILD_JASPER=OFF ^
-DWITH_JASPER=OFF ^
 ^
-DWITH_CUDA=OFF ^
-DWITH_FFMPEG=OFF ^
-DWITH_GTK=OFF

cmake --build . --config Release
cmake --install .
cd ..
````


# Build CppLib on Windows ARM64

Specify cmake options

````
cmake .. -DOpenCV_DIR=F:\dvp\_opencv\opencv4.6.0_static_install_win_vc17 -DOpenCV_STATIC=ON -DCMAKE_GENERATOR_PLATFORM=ARM64 -DBUILD_SHARED_LIBS=OFF -DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded
````

Explanations:

* OpenCV_DIR: you opencv install path
* CMAKE_GENERATOR_PLATFORM: tells openCV to look in  the ARM64 folder
* OpenCV_STATIC: tells OpenCV to look in the ARM64/vc17/staticlib folder
* CMAKE_MSVC_RUNTIME_LIBRARY: tells MSVC to use static runtime (/MT)
* BUILD_SHARED_LIBS=OFF: build static libs. Normally, this could be ignored
  


# Build pip package on Windows ARM64 with immvision (incl OpenCV)

You need an arm version of python. See https://www.python.org/downloads/windows/

