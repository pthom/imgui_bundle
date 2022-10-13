import sys


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
    name="lg-imgui-bundle",
    version="0.1.0",
    author="Pascal Thomet",
    author_email="pthomet@gmail.com",
    description="lg-imgui-bundle, bindings for HelloImgui, ImGui and ImPlot using litgen",
    url="https://github.com/pthom/litgen",
    packages=(["lg_imgui_bundle"]),
    package_dir={"": "bindings"},
    cmake_install_dir="bindings/lg_imgui_bundle",
    include_package_data=True,
    extras_require={"test": ["pytest"]},
    python_requires=">=3.6",
    package_data={"lg_imgui_bundle": ["py.typed", "*.pyi", "assets/fonts/*.ttf"]},
    install_requires=["numpy >= 1.15"],
)
