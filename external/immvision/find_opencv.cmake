macro(try_install_opencv_with_conan)

    set(conan_help_message "

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

    set(conan_folder ${CMAKE_CURRENT_BINARY_DIR}/conan_third)
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

        message(${conan_help_message})

    else()
        # For conan, add binary dir to module search path
        set(new_cmake_module_path ${CMAKE_MODULE_PATH} ${conan_folder})
        set(CMAKE_MODULE_PATH ${new_cmake_module_path})
    endif()
endmacro()


macro(find_opencv)
    find_package(OpenCV)
    if (NOT OpenCV_FOUND)
        try_install_opencv_with_conan()
        find_package(OpenCV)
    endif()
endmacro()
