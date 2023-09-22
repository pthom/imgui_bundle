# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
from typing import List
import sys
import os

VERSION = "0.9.0"  # Remember to mirror changes on line 2 of main CMakeLists!
THIS_DIR = os.path.dirname(__file__)
ROOT_PACKAGE_FOLDER = "bindings/imgui_bundle"
ROOT_PACKAGE_NAME = "imgui_bundle"


def get_readme():
    with open(ROOT_PACKAGE_FOLDER + "/Readme_pypi.md", encoding="utf8") as f:
        r = f.read()
    return r


def _get_assets_and_demos_cpp_dirs() -> List[str]:
    r = []

    dir_name: str
    for dir_name, subdir_list, file_list in os.walk(ROOT_PACKAGE_FOLDER):

        def is_assets_dir_or_subdir():
            dir_parts = dir_name.replace("\\", "/").split("/")
            return "assets" in dir_parts or "demos_cpp" in dir_parts or "demos_assets" or "doc" in dir_parts

        if is_assets_dir_or_subdir():
            relative_dir = os.path.relpath(dir_name, ROOT_PACKAGE_FOLDER)
            r.append(relative_dir)

    return r


def get_imgui_bundle_package_data() -> List[str]:
    data = [
        "Readme.md",
        "LICENSE",
        "py.typed",
        "*.pyi",
        "*/*.pyi",
        "*/py.typed",
        "demos_python/notebooks/*.ipynb",
        "demos_python/demos_node_editor/demo_node_editor_basic.json",
    ]
    for asset_dir in _get_assets_and_demos_cpp_dirs():
        data.append(asset_dir + "/*.*")
    return data


def get_imgui_bundle_packages() -> List[str]:
    r = []
    dir_name: str
    for dir_name, subdir_list, file_list in os.walk(ROOT_PACKAGE_FOLDER):
        if os.path.isfile(dir_name + "/__init__.py"):
            package_dir = os.path.relpath(dir_name, ROOT_PACKAGE_FOLDER)
            if package_dir == ".":
                package_name = ROOT_PACKAGE_NAME
            else:
                package_name = ROOT_PACKAGE_NAME + "." + package_dir.replace("/", ".")
            r.append(package_name)
    return r


try:
    from skbuild import setup
except ImportError:
    print(
        "Please update pip, you need pip 10 or greater,\n"
        " or you need to install the PEP 518 requirements in pyproject.toml yourself",
        file=sys.stderr,
    )
    raise

setup(
    name="imgui-bundle",
    version=VERSION,
    author="Pascal Thomet",
    author_email="pthomet@gmail.com",
    description="Dear ImGui Bundle: easily create ImGui applications in Python and C++. Batteries included!",
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/pthom/imgui_bundle",
    packages=(get_imgui_bundle_packages()),
    package_dir={"": "bindings"},
    cmake_install_dir="bindings/imgui_bundle",
    extras_require={"test": ["pytest"]},
    python_requires=">=3.6",
    package_data={"imgui_bundle": get_imgui_bundle_package_data()},
    install_requires=[
        "numpy >= 1.15",
        "munch >= 2.0.0",
        "glfw > 2.5",
        "PyOpenGL >= 3.0",
        "pillow >= 9.0.0",
    ],
    entry_points={
        "console_scripts": [
            "demo_imgui_bundle=imgui_bundle.demos_python.demo_imgui_bundle:main",
            "imgui_bundle_demo=imgui_bundle.demos_python.demo_imgui_bundle:main",
        ],
    },
)
