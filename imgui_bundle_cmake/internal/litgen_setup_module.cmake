set(litgen_cmake_help_message "

This Cmake module provides several public functions:

litgen_find_python
******************
litgen_find_python() will find Python >= 3.8 with the interpreter and Development module.
(and working around quirks of CMake 3.18 and below)

litgen_find_pybind11()
**********************
litgen_find_pybind11() will find pybind11 and Python3
It is equivalent to:
    find_package(Python 3.8 REQUIRED COMPONENTS Interpreter Development[.Module])
    find_package(pybind11 CONFIG REQUIRED)
(after having altered CMAKE_PREFIX_PATH by adding the path to pybind11 provided
by `pip install pybind11`. This is helpful when building the C++ library outside of skbuild)

When building via CMake, you may have to specify Python_EXECUTABLE via
     -DPython_EXECUTABLE=/path/to/your/venv/bin/python

litgen_find_nanobind
*********************
litgen_find_nanobind() will find nanobind and Python3

litgen_setup_module(bound_library python_native_module_name python_module_name)
*******************************************************************************
litgen_setup_module is a helper function that will:
* link the python native module (.so) to the bound C++ library (bound_library)
* set the install path of the native module to '.' (so that pip install works)
* set the VERSION_INFO macro to the project version defined in CMakeLists.txt
* when building as a C++ project (i.e. not with skbuild), it will copy the python module
  to the editable_bindings_folder and to the platform dependent installation directory
  (site-packages when using pip install), so that it is used by our next runs of python.


Note: how to specify the version of Python to use
*************************************************
When building via CMake, you may have to specify Python_EXECUTABLE via
     -DPython_EXECUTABLE=/path/to/your/venv/bin/python
")

macro(litgen_find_python)
    # cf https://nanobind.readthedocs.io/en/latest/building.html
    if (CMAKE_VERSION VERSION_LESS 3.18)
        set(DEV_MODULE Development)
    else()
        set(DEV_MODULE Development.Module)
    endif()

    find_package(Python 3.8 COMPONENTS Interpreter ${DEV_MODULE} REQUIRED)
endmacro()


# When building outside of skbuild, we need to add the path to pybind11 provided by pip
function(_lg_add_pybind11_pip_cmake_prefix_path)
    execute_process(
        COMMAND "${Python_EXECUTABLE}" -c
        "import pybind11; print(pybind11.get_cmake_dir())"
        OUTPUT_VARIABLE pybind11_cmake_dir
        OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ECHO STDOUT
        RESULT_VARIABLE _result
    )
    if(NOT _result EQUAL 0)
        message(FATAL_ERROR "
            Make sure pybind11 is installed via pip:
                pip install pybind11
            Also, make sure you are using the correct python executable:
                -DPython_EXECUTABLE=/path/to/your/venv/bin/python
        ")
    endif()
    set(CMAKE_PREFIX_PATH ${CMAKE_PREFIX_PATH} "${pybind11_cmake_dir}" PARENT_SCOPE)
endfunction()


function(litgen_find_pybind11)
    litgen_find_python()
    if(NOT SKBUILD)
        # when building via CMake, we need to add the path to pybind11 provided by pip
        # (skbuild does it automatically)
        _lg_add_pybind11_pip_cmake_prefix_path()
    endif()

    find_package(pybind11 CONFIG REQUIRED)
endfunction()


macro(litgen_find_nanobind)
    litgen_find_python()

    # Detect the installed nanobind package and import it into CMake
    execute_process(
        COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
        OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE nanobind_ROOT)
    find_package(nanobind CONFIG REQUIRED)

    if (NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
        set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
        set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
    endif()
endmacro()


function(litgen_setup_module
    # Parameters explanation, with an example: let's say we want to build binding for a C++ library named "foolib",
    bound_library               #  name of the C++ for which we build bindings ("foolib")
    python_native_module_name   #  name of the native python module that provides bindings (for example "_foolib")
    python_module_name          #  name of the standard python module that will import the native module (for example "foolib")
    editable_bindings_folder    # path to the folder containing the python bindings for editable mode (for example "_stubs/")
)
    target_link_libraries(${python_native_module_name} PRIVATE ${bound_library})

    # Set python_native_module_name install path to ${python_module_name} (required by skbuild)
    install(TARGETS ${python_native_module_name} DESTINATION ${python_module_name})

    # Set VERSION_INFO macro to the project version defined in CMakeLists.txt (absolutely optional)
    target_compile_definitions(${python_native_module_name} PRIVATE VERSION_INFO=${PROJECT_VERSION})

    if (NOT SKBUILD)
        # If we are **not** building with skbuild, it means that we are **not** building a wheel for pipy or conda.
        #
        # Instead, we are building as a standard C++ project: in this case, we want to deploy our compiled module
        # so that it is used by our next runs of python.
        #
        # We will copy it into two different locations, to cover all cases:
        # - 1. ${editable_bindings_folder}: the user selected binding folder
        #      (if the user did *manually* prepend it to his python path)
        # - 2. ${Python_SITEARCH}: the platform dependent installation directory
        #      (site-packages when using pip install)

        # 1. Copy the python module to editable_bindings_folder
        set(bindings_module_folder ${editable_bindings_folder}/${python_module_name})
        set(python_native_module_editable_location ${bindings_module_folder}/$<TARGET_FILE_NAME:${python_native_module_name}>)
        add_custom_target(
            ${python_module_name}_deploy_editable
            ALL
            COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${python_native_module_name}> ${python_native_module_editable_location}
            DEPENDS ${python_native_module_name}
        )

        # 2. Copy the python module to the platform dependent installation directory (site-packages when using pip install)
        # We'll rely on find_package(Python) which fills Python_SITEARCH, which is where we want to copy the module
        litgen_find_python()  # will call find_package(Python) and set Python_SITEARCH
        set(python_native_module_editable_location_site_packages ${Python_SITEARCH}/${python_module_name}/$<TARGET_FILE_NAME:${python_native_module_name}>)
        add_custom_target(
            ${python_module_name}_deploy_editable_site_packages
            ALL
            COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${python_native_module_name}> ${python_native_module_editable_location_site_packages}
            DEPENDS ${python_native_module_name})
        message(STATUS "litgen_setup_module: python native module will be copied to ${python_native_module_editable_location_site_packages}")
    endif(NOT SKBUILD)
endfunction()
