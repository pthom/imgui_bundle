from skbuild import setup  # This line replaces 'from setuptools import setup'

setup(
    name="hello-imgui",
    version="0.1.0",
    author="Pascal Thomet",
    author_email="pthomet@gmail.com",
    description="hello-imgui, bindings for HelloImgui, using litgen",
    url="https://github.com/pthom/litgen/example",
    packages=(["hello_imgui"]),
    package_dir={"": "bindings"},
    cmake_install_dir="bindings/hello_imgui",
    include_package_data=True,
    extras_require={"test": ["pytest"]},
    python_requires=">=3.6",
    package_data={"hello_imgui": ["*.pyi"]},
    install_requires = [
        "lg-imgui @ git+https://github.com/pthom/lg_imgui.git",
    ]
)
