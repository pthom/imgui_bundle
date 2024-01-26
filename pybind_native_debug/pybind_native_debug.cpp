#include <pybind11/embed.h>
#include <optional>
#include <iostream>
#include <filesystem>

// This file relies on VENV_PATH to be set as a compile definition by CMake.

namespace py = pybind11;


// Search for the 'site-packages' directory within the venv
std::optional<std::string> find_site_packages_from_venv(const std::string& venv_path)
{
    for (const auto& dir_entry : std::filesystem::recursive_directory_iterator(venv_path))
        if (dir_entry.is_directory() && dir_entry.path().filename() == "site-packages")
            return dir_entry.path().string();
    return std::nullopt;
}

// adds a path to sys.path
void add_python_path(const std::string& path)
{
    std::string cmd;
    cmd += "import sys\n";
    cmd += "sys.path.append(\"" + path + "\")\n";
    py::exec(cmd);
}


// Given a venv path, add site-packages to sys.path
void initialize_python_with_venv(const std::string& venv_path)
{
    auto site_packages_path_opt = find_site_packages_from_venv(venv_path);
    if (!site_packages_path_opt)
        throw std::runtime_error("Error: 'site-packages' directory not found in '" + venv_path);
    add_python_path(*site_packages_path_opt);
}


int main()
{
    py::scoped_interpreter guard{};

    //This program reads the Python virtual environment path from a configuration file named
    //    pybind_native_debug_venv.txt
    //This file should be placed next to this C++ file, and must contain a single line that specifies the path
    //to the Python virtual environment.
    //
    //Example of 'pybind_native_debug_venv.txt' content:
    //
    ///home/me/venv

    // Initialize python path with the virtual environment
    auto this_dir = std::filesystem::path(__FILE__).parent_path();
    std::string venv_path = VENV_PATH; // VENV_PATH is set by CMake
    initialize_python_with_venv(venv_path);

    // Add path to src/python_bindings (in pip editable development mode)
    auto bundle_bindings_dir = this_dir.parent_path() / "bindings";
    add_python_path(bundle_bindings_dir.string());

    // Add path to this dir, so that we can import pybind_native_debug.py
    add_python_path(this_dir.string());

    // Run pybind_native_debug.py
    try
    {
        py::exec("import pybind_native_debug");
    }
    catch (pybind11::error_already_set &e)
    {
        std::cout << "Python exception details:\n";
        std::cout << "- Type: " << py::str(e.type()).cast<std::string>() << "\n";
        std::cout << "- Value: " << py::str(e.value()).cast<std::string>() << "\n";
        if(e.trace())
            std::cout << "- Traceback: " << py::str(e.trace()).cast<std::string>() << "\n";
        else
            std::cout << "- Traceback: None\n";
        e.restore();
        PyErr_Print();  // This line requires Python.h to be included
    }
}
