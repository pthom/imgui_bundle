###############################################################################
# Get OpenCV package
###############################################################################

macro(immvision_download_opencv_static_package_win)
    if ("$ENV{IMGUIBUNDLE_OPENCV_USE_PREBUILT_STATIC_WIN_VC17}" OR IMGUIBUNDLE_OPENCV_USE_PREBUILT_STATIC_WIN_VC17)
        include(FetchContent)
        Set(FETCHCONTENT_QUIET FALSE)
        FetchContent_Declare(
            opencv_static_package_win
            URL https://traineq.org/_imgui_bundle/opencv4.6.0_static_install_win_vc17.zip
            URL_MD5 76d44d29b2f5aa5e61f7d621f37aa8c6
            DOWNLOAD_EXTRACT_TIMESTAMP ON
        )
        FetchContent_MakeAvailable(opencv_static_package_win)
        set(opencv_static_package_win_dir ${CMAKE_BINARY_DIR}/_deps/opencv_static_package_win-src)
        message(WARNING "opencv_static_package_win_dir=${opencv_static_package_win_dir}")
        set(OpenCV_DIR ${opencv_static_package_win_dir})
        set(OpenCV_STATIC ON)
    endif()
endmacro()


macro(immvision_try_install_opencv_with_conan)
    if ("$ENV{IMGUIBUNDLE_OPENCV_USE_CONAN}" OR IMGUIBUNDLE_OPENCV_USE_CONAN)


        set(conan_folder ${CMAKE_BINARY_DIR})
        file(MAKE_DIRECTORY ${conan_folder})

        if(WIN32)
            set(conanfile "conanfile_opencv_default.txt")
        elseif(APPLE AND NOT IOS)
            set(conanfile "conanfile_opencv_minimal.txt")
        elseif(${CMAKE_SYSTEM_NAME} STREQUAL "Linux")
            set(conanfile "conanfile_opencv_minimal_linux.txt")
        else()
            message(WARNING "This system (${CMAKE_SYSTEM_NAME}) is not yet supported for installing OpenCV via conan for immvision")
        endif()

        execute_process(COMMAND
            conan install ${CMAKE_CURRENT_LIST_DIR}/${conanfile} --build=missing
            WORKING_DIRECTORY ${conan_folder}
            RESULT_VARIABLE conan_install_result
            )

        if (NOT ${conan_install_result} EQUAL "0")
            message(STATUS "conan install failed!
                The following command:
                    conan install ${CMAKE_CURRENT_LIST_DIR}/${conanfile} --build=missing
                Failed, when it was run in the folder:
                    ${conan_folder}
                With the result:
                    ${conan_install_result}
            ")
        else()
            # For conan, add binary dir to module search path
            set(new_cmake_module_path ${CMAKE_MODULE_PATH} ${conan_folder})
            set(CMAKE_MODULE_PATH ${new_cmake_module_path})
        endif()
    endif()
endmacro()


set(immvision_conan_help_message "

    ---------------------------------------------------------------
    immvision requires OpenCV, which can easily be built with Conan
    ---------------------------------------------------------------
    If desired, install it before running pip install or cmake.

    On linux:
        pip install conan
        conan profile new default --detect
        conan profile update settings.compiler.libcxx=libstdc++11 default
    On MacOS
        brew install conan
        conan profile new default --detect
    On Windows
        pip install conan
        conan profile new default --detect
    ---------------------------------------------------------------
")


macro(immvision_find_opencv)
    immvision_download_opencv_static_package_win()

    find_package(OpenCV)
    if (NOT OpenCV_FOUND)
        immvision_try_install_opencv_with_conan()
    endif()

    find_package(OpenCV)
    if (NOT OpenCV_FOUND)
        message(${immvision_conan_help_message})
    endif()
endmacro()
