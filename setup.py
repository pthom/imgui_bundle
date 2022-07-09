from skbuild import setup  # This line replaces 'from setuptools import setup'

setup(
    name="lg-hello-imgui",
    version="0.1.0",
    author="Pascal Thomet",
    author_email="pthomet@gmail.com",
    description="lg-hello-imgui, bindings for HelloImgui, ImGui and ImPlot using litgen",
    url="https://github.com/pthom/litgen",
    packages=(["lg_hello_imgui"]),
    package_dir={"": "bindings"},
    cmake_install_dir="bindings/lg_hello_imgui",
    include_package_data=True,
    extras_require={"test": ["pytest"]},
    python_requires=">=3.6",
    package_data={"lg_hello_imgui": ["py.typed", "*.pyi", "assets/fonts/*.ttf"]},
    install_requires=[
    ],
)
