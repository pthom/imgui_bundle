import os
from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout


class ImGuiBundleTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        # A GUI app cannot run in a headless test: check that it was built and linked
        built = [os.path.join(root, f) for root, _, files in os.walk(self.build_folder)
                 for f in files if f in ("test_package", "test_package.exe")]
        assert built, "test_package executable not found"
        self.output.info(f"Built: {built[0]}")
