function(find_pybind11)
    if (NOT DEFINED PYTHON_EXECUTABLE)
        find_program(PYTHON_EXECUTABLE "python3")
        if ("${PYTHON_EXECUTABLE}" STREQUAL "PYTHON_EXECUTABLE-NOTFOUND")
            message(FATAL_ERROR "
                Did not find python executable. Please run cmake with -DPYTHON_EXECUTABLE=/path/to/python")
        endif()
    endif()

    ####################################################
    # Add pybind11
    ####################################################
    execute_process(
        COMMAND "${PYTHON_EXECUTABLE}" -c
        "import pybind11; print(pybind11.get_cmake_dir())"
        OUTPUT_VARIABLE _tmp_dir
        OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ECHO STDOUT)
    list(APPEND CMAKE_PREFIX_PATH "${_tmp_dir}")

    find_package(pybind11 CONFIG)
    if (NOT pybind11_FOUND)
        message(FATAL_ERROR "pybind11 is required to build python bindings! Please install it with the command:
            pip install pybind11
        ")
    endif()
endfunction()