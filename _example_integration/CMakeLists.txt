cmake_minimum_required(VERSION 3.12)
project(imgui_bundle_example_integration)
set(CMAKE_CXX_STANDARD 17)


##########################################################
# Prepare imgui_bundle during configure time
##########################################################
# Download imgui_bundle if not part of the project
if (NOT TARGET imgui_bundle)
    include(FetchContent)
    Set(FETCHCONTENT_QUIET FALSE)
    FetchContent_Declare(imgui_bundle GIT_REPOSITORY https://github.com/pthom/imgui_bundle.git GIT_TAG main)
    FetchContent_MakeAvailable(imgui_bundle)
    # Uncomment the next line if you which to also automatically fetch and compile OpenCV for immvision support
    # set(IMMVISION_FETCH_OPENCV ON)
endif()


##########################################################
# Build your app
##########################################################
# Call imgui_bundle_add_app
imgui_bundle_add_app(imgui_bundle_example_integration hello_world.cpp)

# Now you can build your app with
#     mkdir build && cd build && cmake .. && cmake --build .
