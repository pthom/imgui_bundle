###############################################################################
# Get OpenCV package
###############################################################################

###############################################################################
# Note about pip and wheel builds:
#
# - opencv-python is the pip package for opencv: when installed it comes with a dll,
#   or a .so file (cv2.abi3.so)
#
# - when building wheels for macos and linux, the env variable
#  IMGUIBUNDLE_OPENCV_FETCH_SOURCE is set before running pip.
#  This way, a static minimal version of opencv will be linked into _imgui_bundle.so.
#  Thus there is no risk of doubly defined functions:
#     imgui_bundle will search into the linked functions inside _imgui_bundle.so,
#     and opencv-python will search inside cv2.abi3.so.
#
# - when building wheels for windows, the env variable
#   IMGUIBUNDLE_OPENCV_WIN_USE_OFFICIAL_PREBUILT_460 is set before running pip.
#   This way, an official release from OpenCV 4.6.0 for windows will be downloaded.
#   It includes an "opencv_world.dll" (a dll that groups all the code for all OpenCV modules).
#   This dll is deployed into imgui_bundle package (under windows)
#   No warning about doubly defined function was (yet?) observed, although a static link
#   might be needed in the future.
#   "Funny" note on how to set this env var under windows: choose your poison
#     * with PowerShell
#	      Set-Item -Path 'Env:IMGUIBUNDLE_OPENCV_WIN_USE_OFFICIAL_PREBUILT_460' -Value 'ON'
#     * With bash:
#	      export IMGUIBUNDLE_OPENCV_WIN_USE_OFFICIAL_PREBUILT_460=ON
#      * With dos:
#         set IMGUIBUNDLE_OPENCV_WIN_USE_OFFICIAL_PREBUILT_460=ON
# 
###############################################################################


macro(immvision_forward_opencv_env_variables)
    # Forward environment variable to standard variables that are used by OpenCVConfig.cmake
    # This is useful when building the pip package for which only env variables are available
    if(DEFINED ENV{OpenCV_DIR})
        set(OpenCV_STATIC "$ENV{OpenCV_DIR}")
        message("immvision_forward_opencv_env_variables: Forwarding env OpenCV_DIR=${OpenCV_DIR}")
    endif()

    if(DEFINED ENV{OpenCV_STATIC})
        set(OpenCV_STATIC "$ENV{OpenCV_STATIC}")
        message("immvision_forward_opencv_env_variables: Forwarding env OpenCV_STATIC=${OpenCV_STATIC}")
    endif()

    # I know I know, one should not hack CMAKE_GENERATOR_PLATFORM when not doing cross platform builds
    # But when you want to build for windows ARM64, this is the only option given by OpenCVConfig.cmake...
    if(DEFINED ENV{CMAKE_GENERATOR_PLATFORM})
        set(CMAKE_GENERATOR_PLATFORM "$ENV{CMAKE_GENERATOR_PLATFORM}")
        message("immvision_forward_opencv_env_variables: Forwarding env CMAKE_GENERATOR_PLATFORM=${CMAKE_GENERATOR_PLATFORM}")
    endif()
endmacro()


macro(immvision_download_opencv_static_package_win)
    # Download a precompiled version of opencv4.6.0
    # This is the official release from OpenCV for windows, under the form of a "opencv_world.dll"
    # The zip package we download is just a transcription of the exe provided by OpenCV, with the advantage that
    # it does not require any user click.
    # Mainly used for wheel builds, but can be used by windows users for their pip build from source
    if ("$ENV{IMGUIBUNDLE_OPENCV_WIN_USE_OFFICIAL_PREBUILT_460}" OR IMGUIBUNDLE_OPENCV_WIN_USE_OFFICIAL_PREBUILT_460)
        message("FIND OPENCV use immvision_download_opencv_static_package_win")

        include(FetchContent)
        Set(FETCHCONTENT_QUIET FALSE)
        FetchContent_Declare(
            opencv_static_package_win
            URL https://github.com/pthom/imgui_bundle/releases/download/v0.6.6/opencv-4.6.0_official_win_x64_world.zip
            URL_MD5 a9d92bdf8510d09c3bf3cb080731ea91
            DOWNLOAD_EXTRACT_TIMESTAMP ON
        )
        FetchContent_MakeAvailable(opencv_static_package_win)
        set(opencv_static_package_win_dir ${CMAKE_BINARY_DIR}/_deps/opencv_static_package_win-src/opencv/build)
        message(WARNING "opencv_static_package_win_dir=${opencv_static_package_win_dir}")
        set(OpenCV_DIR ${opencv_static_package_win_dir})
        set(OpenCV_STATIC ON)
    endif()
endmacro()


macro(immvision_fetch_opencv_from_source)
    # Will fetch, build and install a very-minimalist OpenCV if IMGUIBUNDLE_OPENCV_FETCH_SOURCE
    # It is so minimalist that it is only usable within the python bindings!!!
    # It will contain only opencv_core (core), opencv_imgcodecs (load/save), and opencv_imgproc (affine transforms, etc)
    # Mainly used for wheel builds.

    if ("$ENV{IMGUIBUNDLE_OPENCV_FETCH_SOURCE}" OR IMGUIBUNDLE_OPENCV_FETCH_SOURCE)
        message("FIND OPENCV use immvision_fetch_opencv_from_source")

        # Build opencv with only opencv_core, opencv_imgproc and opencv_imgcodecs
        set(opencv_cmake_args -DCMAKE_BUILD_TYPE=Release -DINSTALL_CREATE_DISTRIB=ON -DBUILD_SHARED_LIBS=OFF -DCMAKE_BUILD_TYPE=Release -DBUILD_opencv_apps=OFF -DBUILD_TESTS=OFF -DBUILD_PERF_TESTS=OFF -DWITH_1394=OFF -DWITH_AVFOUNDATION=OFF -DWITH_CAP_IOS=OFF -DWITH_VTK=OFF -DWITH_CUDA=OFF -DWITH_CUFFT=FALSE -DWITH_CUBLAS=OFF -DWITH_EIGEN=OFF -DWITH_FFMPEG=OFF -DWITH_GSTREAMER=OFF -DWITH_GTK=OFF -DWITH_GTK_2_X=OFF -DWITH_HALIDE=OFF -DWITH_VULKAN=OFF -DWITH_OPENEXR=OFF -DBUILD_opencv_python2=OFF -DBUILD_opencv_python3=OFF -DBUILD_opencv_features2d=OFF -DBUILD_opencv_calib3d=OFF -DBUILD_opencv_dnn=OFF -DBUILD_opencv_flann=OFF -DBUILD_opencv_gapi=OFF -DBUILD_opencv_highgui=OFF -DBUILD_opencv_java=OFF -DBUILD_opencv_js=OFF -DBUILD_opencv_ml=OFF -DBUILD_opencv_objc=OFF -DBUILD_opencv_objdetect=OFF -DBUILD_opencv_photo=OFF -DBUILD_opencv_python=OFF -DBUILD_opencv_stiching=OFF -DBUILD_opencv_video=OFF -DBUILD_opencv_videoio=OFF -DBUILD_opencv_js=OFF)

        # Pass current compilation flags to OpenCV compilation
        # For example, when compiling x86_64 on a Mac M1 (arm64), we have the following variable set
        #    CMAKE_HOST_SYSTEM_PROCESSOR=x86_64  # Host compiler architecture
        #    CMAKE_SYSTEM_PROCESSOR=x86_64       # Target architecture (but not always)
        #    CMAKE_OSX_DEPLOYMENT_TARGET=10.16   # MacOS specific
        #    CMAKE_OSX_ARCHITECTURES=x86_64      # This is the target architecture (Mac Only)
        set(compile_arch_flags_to_pass
            CMAKE_HOST_SYSTEM_PROCESSOR
            CMAKE_SYSTEM_PROCESSOR
            CMAKE_OSX_DEPLOYMENT_TARGET
            CMAKE_OSX_ARCHITECTURES
            )

        # Note: we cannot compile universal2 wheels at this time, because CMake confuses itself
        # The incoming CMAKE_OSX_ARCHITECTURES is "x86_64;arm64"
        # However, it is difficult to pass it as is to the cmake args for OpenCV,
        # since CMake happily splits it in two...

        foreach(compile_arch_flag ${compile_arch_flags_to_pass})
            if (DEFINED ${compile_arch_flag})
                if (NOT ${compile_arch_flag} STREQUAL "")
                    list(APPEND opencv_cmake_args -D${compile_arch_flag}=${${compile_arch_flag}})
                    # message(WARNING "list(APPEND opencv_cmake_args -D${compile_arch_flag}=${${compile_arch_flag}})")
                endif()
            endif()
        endforeach()

        message("
        -----------------------------------------------------------------------
        immvision_fetch_opencv_from_source: opencv_cmake_args=
            ${opencv_cmake_args}
        -----------------------------------------------------------------------
        ")

        include(FetchContent)
        Set(FETCHCONTENT_QUIET FALSE)
        FetchContent_Declare(
            OpenCV_Fetch
            GIT_REPOSITORY https://github.com/opencv/opencv.git
            GIT_TAG 4.6.0
            # GIT_REMOTE_UPDATE_STRATEGY REBASE
        )
        # It is not possible to build opencv completely via FetchContent_MakeAvailable,
        # since the opencv include folder is populated only at opencv install!
        FetchContent_Populate(OpenCV_Fetch)

        # Neither FetchContent, nor ExternalProject permit to install OpenCV before the generation step.
        # So we have to build and install OpenCV manually
        # (Note: it is likely that cmake arch options may need to be transferred to this sub-build)
        set(opencv_src_dir "${CMAKE_BINARY_DIR}/_deps/opencv_fetch-src")
        set(opencv_build_dir "${CMAKE_BINARY_DIR}/_deps/opencv_fetch-build")
        set(opencv_install_dir "${CMAKE_BINARY_DIR}/_deps/opencv_fetch-install")

        # cmake
        execute_process(
            COMMAND ${CMAKE_COMMAND} ${opencv_src_dir} -DCMAKE_INSTALL_PREFIX=${opencv_install_dir} ${opencv_cmake_args}
            WORKING_DIRECTORY ${opencv_build_dir}
            RESULT_VARIABLE result
        )
        if (NOT ${result} EQUAL "0")
            message(FATAL_ERROR "my_checked_execute_process_check failed during cmake")
        endif()
        # build
        execute_process(
            COMMAND ${CMAKE_COMMAND} --build . --config Release  -j 3
            WORKING_DIRECTORY ${opencv_build_dir}
            RESULT_VARIABLE result
        )
        if (NOT ${result} EQUAL "0")
            message(FATAL_ERROR "my_checked_execute_process_check failed during build")
        endif()
        # install
        execute_process(
            COMMAND ${CMAKE_COMMAND} --install .
            WORKING_DIRECTORY ${opencv_build_dir}
            RESULT_VARIABLE result
        )
        if (NOT ${result} EQUAL "0")
            message(FATAL_ERROR "my_checked_execute_process_check failed during install")
        endif()

        if (WIN32)
            set(OpenCV_DIR ${opencv_install_dir})
            # Under windows, OpenCV will not use the static lib unless we set this variable
            set(OpenCV_STATIC ON CACHE BOOL "" FORCE)
        else()
            if (IS_DIRECTORY ${opencv_install_dir}/lib/cmake/opencv4)
                set(OpenCV_DIR ${opencv_install_dir}/lib/cmake/opencv4)
            elseif(IS_DIRECTORY ${opencv_install_dir}/lib64/cmake/opencv4)
                set(OpenCV_DIR ${opencv_install_dir}/lib64/cmake/opencv4)
            endif()            
        endif()
        if (NOT EXISTS ${OpenCV_DIR}/OpenCVConfig.cmake)
            message(FATAL_ERROR "
            immvision_fetch_opencv_from_source: can't find OpenCvConfig.cmake
            ")
        endif()


        # Since we build a minimalist version of OpenCV,
        # find_package(OpenCV) may fail because these files do not exist
        # We create dummy versions, since we do not use them
        file(WRITE ${opencv_install_dir}/lib/opencv4/3rdparty/liblibprotobuf.a "dummy")
        file(WRITE ${opencv_install_dir}/lib/opencv4/3rdparty/libquirc.a "dummy")
        file(WRITE ${opencv_install_dir}/lib/opencv4/3rdparty/libade.a "dummy")
        file(WRITE ${opencv_install_dir}/lib64/opencv4/3rdparty/liblibprotobuf.a "dummy")
        file(WRITE ${opencv_install_dir}/lib64/opencv4/3rdparty/libquirc.a "dummy")
        file(WRITE ${opencv_install_dir}/lib64/opencv4/3rdparty/libade.a "dummy")
        if (WIN32)
            file(WRITE ${opencv_install_dir}/x64/vc17/staticlib/libprotobuf.lib "dummy")
            file(WRITE ${opencv_install_dir}/x64/vc17/staticlib/quirc.lib "dummy")
            file(WRITE ${opencv_install_dir}/x64/vc17/staticlib/ade.lib "dummy")
        endif()
    endif()
endmacro()


macro(immvision_try_install_opencv_with_conan)
    # Tries to install OpenCV via conan
    if ("$ENV{IMGUIBUNDLE_OPENCV_USE_CONAN}" OR IMGUIBUNDLE_OPENCV_USE_CONAN)
		message("FIND OPENCV use CONAN")


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
    immvision_fetch_opencv_from_source()  # Will fetch, build and install OpenCV if IMGUIBUNDLE_OPENCV_FETCH_SOURCE
    immvision_forward_opencv_env_variables() # Forward environment variable to standard variables that are used by OpenCVConfig.cmake
    immvision_download_opencv_static_package_win() # will download prebuilt package if IMGUIBUNDLE_OPENCV_WIN_USE_OFFICIAL_PREBUILT_460

    find_package(OpenCV)
    if (NOT OpenCV_FOUND)
        immvision_try_install_opencv_with_conan() # Will try to install OpenCV with Conan
    endif()

    find_package(OpenCV)
    if (NOT OpenCV_FOUND)
        message(${immvision_conan_help_message})
    else()
        dump_cmake_variables(OpenCV)
        message("found OpenCV OpenCV_DIR=${OpenCV_DIR} ")
    endif()

    # Under windows install dll opencv_worldxxx.dll to package
    if (WIN32)
        set(immvision_OpenCV_DLL_PATH "${OpenCV_LIB_PATH}/../bin")
        message("immvision_OpenCV_DLL_PATH=${immvision_OpenCV_DLL_PATH}")
        file(GLOB immvision_opencv_world_dll ${immvision_OpenCV_DLL_PATH}/opencv_world*.dll)
        if (immvision_opencv_world_dll)
            if (IMGUI_BUNDLE_BUILD_PYTHON)
                install(FILES ${immvision_opencv_world_dll} DESTINATION .)
            endif()
            set(IMMVISION_OPENCV_WORLD_DLL ${immvision_opencv_world_dll} CACHE STRING "opencv_word dll needed by cpp programs" FORCE)
        endif()
    endif()
endmacro()
