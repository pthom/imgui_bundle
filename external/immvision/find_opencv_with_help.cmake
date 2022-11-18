function(find_opencv_with_help)
  if(DEFINED ENV{OpenCV_DIR})
    set(OpenCV_DIR $ENV{OpenCV_DIR})
    message(WARNING "Got OpenCV_DIR from enviroment: ${OpenCV_DIR}")
  endif()

  #
  # Add OpenCv via conan, if not found on the machine
  #
  set(opencv_install_help "
  Could not find OpenCV. Please install it first.

  1. Either via a global installation
  Under ubuntu, you can install it with apt:
      sudo apt-get install libopencv-dev

  2. Or via a local installation, using conan (https://conan.io/):
  First, install conan:
      pip install conan # brew install conan for MacOS
      conan profile new default --detect

      If (and only if) you are using gcc, it is also recommended to run:
          conan profile update settings.compiler.libcxx=libstdc++11 default

  Then, install OpenCV for this package via:

      mkdir -p /tmp/foo
      cd /tmp/foo
      # For mac, run:
      conan install ${CMAKE_CURRENT_LIST_DIR}/conanfile_mac.txt --build=missing
      # For other platforms, run:
      conan install ${CMAKE_CURRENT_LIST_DIR}/conanfile.txt --build=missing
  ")

  find_package(OpenCV) # test if opencv can be found

  if (NOT OpenCV_FOUND AND IMMVISION_USE_CONAN)
    message(WARNING "Did not find a global OpenCV installation. Will try to install it via conan")

    find_program(conan_executable "conan")
    # message(FATAL_ERROR "conan_executable=${conan_executable}")
    set(conan_folder ${CMAKE_CURRENT_BINARY_DIR}/conan_third)
    file(MAKE_DIRECTORY ${conan_folder})

    if(WIN32)
      set(conanfile "conanfile_opencv_default.txt")
    else()
      set(conanfile "conanfile_opencv_minimal.txt")
    endif()

    execute_process(COMMAND
        ${conan_executable} install ${CMAKE_CURRENT_LIST_DIR}/${conanfile} --build=missing
        WORKING_DIRECTORY ${conan_folder}
        RESULT_VARIABLE conan_install_result
        )
    if (NOT ${conan_install_result} EQUAL "0")
      message(WARNING "conan_install_result=${conan_install_result}")
      message(FATAL_ERROR ${opencv_install_help})
    endif()

    # For conan, add binary dir to module search path
    list(APPEND CMAKE_MODULE_PATH ${conan_folder})

  endif()

  find_package(OpenCV)
  if (NOT OpenCV_FOUND)
    message(FATAL_ERROR ${opencv_install_help})
  endif()
endfunction()