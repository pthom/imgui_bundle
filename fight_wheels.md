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


Pistes:
    Compiler et linker OpenCV normalement
        Erreur double definition si link opencv_highgui (python "which one will be used is undefined")
        "Marche" (i.e. fait pas de message) si on supprime link avec opencv_highgui
            => test windows & mac
            Cependant, c'est inquietant. Il recherche quand meme les dylib de homebrew
    Compiler et linker OpenCV en static avec Conan
        Requires Conan from pip with CI stability issues (windows only?) 
        Long compil time in CI
    Compiler et linker OpenCV en static a la mano
        See /Users/pascal/dvp/_opencv/build_xxx.sh
            Sur MacM1: checkout = 1minutes, build=1'40"
            Sous windows: build=3'34"
        Quelle difference de taille sur bundle .so?
            (export OpenCV_DIR=/Users/pascal/dvp/_opencv/opencv4.6.0_install_mac_static/lib/cmake/opencv4)
            Sans link: 11M Dec  8 14:39 _imgui_bundle.cpython-311-darwin.so
            Avec link: 15M Dec  8 14:45 _imgui_bundle.cpython-311-darwin.so

        
    Ne pas linker OpenCV, mais seulement include path
        => symbol not found in flat ...
    Linker avec des dylib vides?
        Faudra quand meme changer leur path...
    Linker avec openCV homebrew, mais hacker DYLD_LIBRARY_PATH + faire des symlinks
        export DYLD_LIBRARY_PATH=/Users/pascal/dvp/OpenSource/ImGuiWork/litgen/demos/litgen/imgui_bundle/venv/lib/python3.11/site-packages/cv2/:$DYLD_LIBRARY_PATH
        =>  (cannot link against bundle '/Users/pascal/dvp/OpenSource/ImGuiWork/litgen/demos/litgen/imgui_bundle/venv/lib/python3.11/site-packages/cv2//libopencv_highgui.406.dylib')



Conundrum / How to link OpenCV when building wheels.
Context:
- On Mac OS and Linux, there exist standard OpenCV packages (apt & homebrew) , built with *a set* of *dynamic* libraries
- On Windows, there is no such package. However there an official distribution provided by OpenCV that uses a *single opencv_world* dynamic library
- the python package opencv-python provides a dynamic library (cv2.abi3.so)
