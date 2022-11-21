import sys


def get_readme():
    with open("Readme.md") as f:
        r = f.read()
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
    version="0.6.6",  # Remember to mirror changes on line 2 of main CMakeLists!
    author="Pascal Thomet",
    author_email="pthomet@gmail.com",
    description="ImGui Bundle: easily create ImGui applications in Python and C++. Batteries included!",
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/pthom/imgui_bundle",
    packages=(
        [
            "imgui_bundle",
            "imgui_bundle.assets",
            "imgui_bundle.assets.fonts",
            "imgui_bundle.assets.fonts.Roboto",
            "imgui_bundle.assets.images",
            "imgui_bundle.demos",
            "imgui_bundle.demos.node_fn_compose",
            "imgui_bundle.demos.haikus",
            "imgui_bundle.demos.haikus.romeo_and_juliet",
            "imgui_bundle.demos.demos_hello_imgui",
        ]
    ),
    package_dir={"": "bindings"},
    cmake_install_dir="bindings/imgui_bundle",
    extras_require={"test": ["pytest"]},
    python_requires=">=3.6",
    package_data={
        "imgui_bundle": [
            "Readme.md",
            "LICENSE",
            "py.typed",
            "*.pyi",
            "assets/*.*",
            "assets/fonts/*.ttf",
            "assets/fonts/Roboto/*.*",
            "assets/images/*.*",
            "demos/demos_hello_imgui/assets/*.*",
            "demos/demos_hello_imgui/assets/fonts/*.*",
            "demos/demos_hello_imgui/assets/fonts/Roboto/*.*",
            "demos/demos_hello_imgui/assets/images/*.*",
        ]
    },
    install_requires=[
        "numpy >= 1.15", 
        "munch >= 2.0.0", 
        "glfw > 2.5",
        "PyOpenGL >= 3.0",
        # "opencv-python >= 4.5",
    ],
    entry_points={
        "console_scripts": ["imgui_bundle_demo=imgui_bundle.demos.demo_all:main"],
    },
)
