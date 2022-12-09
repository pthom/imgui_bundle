cibuildwheel:
https://cibuildwheel.readthedocs.io/en/stable/

pipx run cibuildwheel --platform macos

On my mac:
python3.8 x86_64
python3.9 3.10 & 3.11: Mach-O universal binary with 2 architectures: [x86_64:Mach-O 64-bit executable x86_64] [arm64:Mach-O 64-bit executable arm64]

* Extract all wheels
````bash
    for whl in *.whl; do whl_dir=${whl%.*}; echo $whl_dir; mkdir $whl_dir; cd $whl_dir; unzip ../$whl; cd ..;  done
````


----

### OpenCV & wheels

Status: see doc inside [external/immvision/find_opencv.cmake](external/immvision/find_opencv.cmake)

Here are the different alternatives that were explored to get OpenCV for immvision.
   
##### Linux and MacOS: use OpenCV provided by package manager.
_Abandoned alternative_
Too dangerous when the user "import cv2": doubly defined functions inside cv2.abi3 (from opencv-python) 
and inside the system package dlls from libopencv-dev.

##### Use Conan to link a static version of OpenCV
_Abandoned alternative_
Conan is too fragile and not trustable for CI. What works one day, can fail the next day (Experienced this with jasper)
Compilation time can be huge: Conan does not offer a way to reduce OpenCV to the absolute needed minimum
(opencv_core _imgproc and _imgcodecs)

##### Download an official build of OpenCV under windows
_Active alternative under windows_
This is what is done under windows.
See immvision_download_opencv_static_package_win() inside [external/immvision/find_opencv.cmake](external/immvision/find_opencv.cmake)

This is activated via the env var `IMGUIBUNDLE_OPENCV_WIN_USE_OFFICIAL_PREBUILT_460`.
"Funny" note on how to set this env var under windows: choose your poison
* with PowerShell
    Set-Item -Path 'Env:IMGUIBUNDLE_OPENCV_WIN_USE_OFFICIAL_PREBUILT_460' -Value 'ON'
* With bash:
    export IMGUIBUNDLE_OPENCV_WIN_USE_OFFICIAL_PREBUILT_460=ON
* With dos:
    set IMGUIBUNDLE_OPENCV_WIN_USE_OFFICIAL_PREBUILT_460=ON

If the env IMGUIBUNDLE_OPENCV_WIN_USE_OFFICIAL_PREBUILT_460 is set before running pip.
This way, an official release from OpenCV 4.6.0 for windows will be downloaded.
t includes an "opencv_world.dll" (a dll that groups all the code for all OpenCV modules).
This dll is deployed into imgui_bundle package (under windows)


##### Truc to use opencv-python dynamic libraries?
...Did not find a way to get this to work.

##### Fetch, build, and install OpenCV *static* during configure (current under Linux & MacOS)
This must be a very simplified version of OpenCV, with only opencv_core, opencv_imgproc and opencv_imgcodecs.

* Warning: OpenCV must be built and *installed* for this to work (otherwise its include folder is not populated).
* Drama: neither ExternalProject_Add nor FetchContent_MakeAvailable are able to _install_ a subproject before the cmake 
generation step!!!

=> Solutions: a mix of FetchContent_Declare + manual compilation where we forward the architecture compilation flags.
This required some hacks so that "find_package(OpenCV)" works: since we build a minimalist version, some unneeded files
are flagged as missing => artificially create them.
