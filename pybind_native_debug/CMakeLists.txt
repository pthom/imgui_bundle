set(CMAKE_CXX_STANDARD 20)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/dll)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

function(_compute_python_dll_path_win32 out_python_dll_path)
    set(note "
    Workaround DLL issue under windows (if python is not added to PATH):
    ********************************************************************

    We want to set VS_DEBUGGER_ENVIRONMENT to include python path.
    Since we instruct user to use a virtual environment, Python_EXECUTABLE will be of the form
    <virtual_env_path>/Scripts/python.exe

    However, the dlls are located in the original python installation directory. We need to open
    <virtual_env_path>/pyvenv.cfg to find the original python installation directory.

    It look like this:
        home = F:\\Utils\\Python311-amd64
        include-system-site-packages = false
        ...
    ")

    # Get the path to pyenv.cfg, i.e. dirname(Python_EXECUTABLE)/../pyenv.cfg
    get_filename_component(Python_EXECUTABLE_DIR ${Python_EXECUTABLE} DIRECTORY)
    set(pyvenvcfg_path ${Python_EXECUTABLE_DIR}/../pyvenv.cfg)

    # Read the content of pyvenv.cfg
    if (EXISTS ${pyvenvcfg_path})
        file(READ ${pyvenvcfg_path} pyvenvcfg_content)
        # Get the first line from pyvenvcfg_content
        string(REGEX MATCH "^[^\n]*" pyvenvcfg_first_line "${pyvenvcfg_content}")
        # Remove the part "home = "
        string(REGEX REPLACE "^home = " "" home_path "${pyvenvcfg_first_line}")

        set(${out_python_dll_path} "${home_path}" PARENT_SCOPE)
    endif()
endfunction()

#
# Add the executable
#
add_executable(pybind_native_debug pybind_native_debug.cpp)
find_package(pybind11 CONFIG REQUIRED)
target_link_libraries(pybind_native_debug PRIVATE pybind11::embed)
# Set the path to the venv
find_package(Python 3.8 REQUIRED COMPONENTS Interpreter Development)
get_filename_component(Python_EXECUTABLE_DIR ${Python_EXECUTABLE} DIRECTORY)
target_compile_definitions(pybind_native_debug PRIVATE VENV_PATH="${Python_EXECUTABLE_DIR}/../")


# Patch for windows
if(WIN32)
    set_property(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT pybind_native_debug)
    _compute_python_dll_path_win32(python_dll_path)
    if(python_dll_path)
        set_property(TARGET pybind_native_debug PROPERTY VS_DEBUGGER_ENVIRONMENT "PATH=%PATH%;${python_dll_path}")
        message(STATUS "set_property(TARGET pybind_native_debug PROPERTY VS_DEBUGGER_ENVIRONMENT \"PATH=%PATH%;${python_dll_path}\"")
    endif()
endif()
