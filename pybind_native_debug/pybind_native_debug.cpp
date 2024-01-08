// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle

//This program reads the Python virtual environment path from a configuration file named
//    pybind_native_debug_venv.txt
//This file should be placed next to this C++ file, and must contain a single line that specifies the path
//to the Python virtual environment.
//
//Example of 'pybind_native_debug_venv.txt' content:
//
///home/me/venv

#include <pybind11/embed.h>
#include <optional>
#include <iostream>
#include <fstream>
#include <filesystem>


namespace py = pybind11;


// read pybind_native_debug_venv.txt
std::string read_venv_path_from_file(const std::filesystem::path& file_path)
{
    std::ifstream file_stream(file_path);
    if (!file_stream)
        throw std::runtime_error("Could not open the venv path file.");

    std::string venv_path;
    std::getline(file_stream, venv_path);
    return venv_path;
}


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
    std::string venv_path = read_venv_path_from_file(this_dir / "pybind_native_debug_venv.txt");
    initialize_python_with_venv(venv_path);

    // Add path to imgui_bundle bindings (in pip editable development mode)
    auto bundle_bindings_dir = this_dir.parent_path() / "bindings";
    add_python_path(bundle_bindings_dir.string());

    // Add path to this dir, so that we can import pybind_native_debug.py
    add_python_path(this_dir.string());

    // Run pybind_native_debug.py
    py::exec("import pybind_native_debug");
}
