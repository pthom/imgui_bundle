# How to use integrate ImGuiBundle into your application

This directory is a **standalone** demonstration on how to easily integrate ImGuiBundle to your own project.
This means that you can copy-paste this folder in your project, and it will build, with no extra step!
No manual download or git clone is required.


## Explanations

The [CMakeLists.txt](CMakeLists.txt) file will 
* download imgui_bundle at configure time
* select the desired backend
* make the "imgui_bundle_add_app" cmake function available
* Build ImGuiBundle and link it with your app at build time

````cmake
##########################################################
# Prepare imgui_bundle during configure time
##########################################################
# Download hello_imgui
include(FetchContent)
Set(FETCHCONTENT_QUIET FALSE)
FetchContent_Declare(
    imgui_bundle
    GIT_REPOSITORY https://github.com/pthom/imgui_bundle.git
    DOWNLOAD_NO_PROGRESS OFF
    GIT_PROGRESS TRUE
    # Enter the desired git tag below
    GIT_TAG dev
)
FetchContent_MakeAvailable(imgui_bundle)
# Make cmake function `imgui_bundle_add_app` available
list(APPEND CMAKE_MODULE_PATH ${IMGUIBUNDLE_CMAKE_PATH})
include(imgui_bundle_add_app)
````

After this, you only need to create your exe with one line!
````cmake
imgui_bundle_add_app(hello_world hello_world.main.cpp)
````
