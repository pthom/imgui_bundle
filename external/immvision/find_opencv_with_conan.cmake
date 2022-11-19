function(find_opencv_with_conan)
    find_program(conan_executable "conan")
    if ("${conan_executable}" STREQUAL "conan_executable-NOTFOUND")
        message(FATAL_ERROR "
            conan C++ package manager is required by immvision (https://conan.io)
            Please install it first (it will be used to build a static version of OpenCV, used by immvision)

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
        ")
    endif()

    set(conan_folder ${CMAKE_CURRENT_BINARY_DIR}/conan_third)
    file(MAKE_DIRECTORY ${conan_folder})

    if(WIN32)
        set(conanfile "conanfile_opencv_default.txt")
    elseif(APPLE AND NOT IOS)
        set(conanfile "conanfile_opencv_minimal.txt")
    elseif(${CMAKE_SYSTEM_NAME} STREQUAL "Linux")
        set(conanfile "conanfile_opencv_minimal_linux.txt")
    else()
        message(FATAL_ERROR "This system (${CMAKE_SYSTEM_NAME}) is not yet supported for immvision/OpenCV")
    endif()

    set(conan_install_command "${conan_executable} install ${CMAKE_CURRENT_LIST_DIR}/${conanfile} --build=missing")
    set(conan_install_command_list "${conan_install_command}")
    separate_arguments(conan_install_command_list)
    execute_process(COMMAND
        ${conan_install_command_list}
        WORKING_DIRECTORY ${conan_folder}
        RESULT_VARIABLE conan_install_result
        )
    if (NOT ${conan_install_result} EQUAL "0")
        message(WARNING "conan_install_result=${conan_install_result}")
        message(FATAL_ERROR "conan install failed!
            The following command:
                ${conan_install_command}
            Failed, when it was run in the folder:
                ${conan_folder}
        ")
    endif()

    # For conan, add binary dir to module search path
    list(APPEND CMAKE_MODULE_PATH ${conan_folder})

    find_package(OpenCV)
    if (NOT OpenCV_FOUND)
        message(FATAL_ERROR ${opencv_install_help})
    endif()
endfunction()