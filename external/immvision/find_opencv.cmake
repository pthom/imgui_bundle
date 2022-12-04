###############################################################################
# Get OpenCV package
###############################################################################

macro(immvision_forward_opencv_env_variables)
	# Forward environment variable to standard variables that are used by OpenCVConfig.cmake
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
    if ("$ENV{IMGUIBUNDLE_OPENCV_USE_PREBUILT_STATIC_WIN_VC17}" OR IMGUIBUNDLE_OPENCV_USE_PREBUILT_STATIC_WIN_VC17)
		message("FIND OPENCV use immvision_download_opencv_static_package_win")

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
	immvision_forward_opencv_env_variables()
    immvision_download_opencv_static_package_win()

	message("FIND OPENCV 1")
    find_package(OpenCV)
    if (NOT OpenCV_FOUND)
        immvision_try_install_opencv_with_conan()
    endif()

	message("FIND OPENCV 2")
    find_package(OpenCV)
    if (NOT OpenCV_FOUND)
        message(${immvision_conan_help_message})
    endif()

	if (OpenCV_FOUND)
		message(STATUS "------ immvision found OpenCV_LIB_PATH=${OpenCV_LIB_PATH}")
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
