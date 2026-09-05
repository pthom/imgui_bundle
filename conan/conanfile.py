# Conan 2 recipe for Dear ImGui Bundle (C++ package).
#
# One monolithic package: the bundled libraries (imgui, hello_imgui, implot, immvision, ...)
# are built from the sources of this repository (with their submodules) and installed with
# CMake. Consumers use the installed CMake package:
#     find_package(imgui_bundle CONFIG REQUIRED)
#     imgui_bundle_add_app(my_app my_app.cpp)   # or target_link_libraries(my_app PRIVATE imgui_bundle::imgui_bundle)
#
# Usage:
#     # from a release (sources listed in conandata.yml):
#     conan create conan --version=<version> --build=missing
#     # from a local checkout (e.g. this one):
#     conan create conan -c user.imgui_bundle:source_dir=$PWD --build=missing
import os
import re

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, load


class ImGuiBundleConan(ConanFile):
    name = "imgui_bundle"
    description = "Dear ImGui Bundle: Dear ImGui and a set of libraries from its ecosystem (ImPlot, ImmVision, node editor, markdown, ...), for C++"
    license = "MIT"
    url = "https://github.com/pthom/imgui_bundle"
    homepage = "https://pthom.github.io/imgui_bundle"
    topics = ("imgui", "gui", "immediate-mode")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        # Hello ImGui platform backend
        "platform_backend": ["glfw", "sdl2"],
        # Hello ImGui rendering backend (metal / vulkan / directx: not packaged yet)
        "rendering_backend": ["opengl3"],
        # ImGui Test Engine (automation and tests)
        "with_test_engine": [True, False],
    }
    default_options = {
        "fPIC": True,
        "platform_backend": "glfw",
        "rendering_backend": "opengl3",
        "with_test_engine": True,
    }

    def set_version(self):
        # Default version: the one of the checkout containing this recipe (CMakeLists.txt)
        if self.version:
            return
        cmakelists = os.path.join(self.recipe_folder, "..", "CMakeLists.txt")
        if os.path.exists(cmakelists):
            m = re.search(r'project\(imgui_bundle VERSION "([^"]+)"', load(self, cmakelists))
            if m:
                self.version = m.group(1)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        check_min_cppstd(self, 17)

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        # System-ish dependencies come from Conan (nothing is downloaded during the build).
        # They are also dependencies of the installed package (find_dependency in imgui_bundle-config.cmake)
        self.requires("freetype/2.13.3")
        self.requires("opengl/system")
        if self.options.platform_backend == "glfw":
            self.requires("glfw/3.4")
        else:
            self.requires("sdl/2.32.10")

    def source(self):
        # Either a local checkout (development), or the full source archive of a release
        # (srcs-full-<tag>.tar.gz, which includes all submodules; see conandata.yml)
        local_source_dir = self.conf.get("user.imgui_bundle:source_dir", default=None, check_type=str)
        if local_source_dir:
            self.output.info(f"Copying sources from {local_source_dir}")
            copy(self, "*", src=local_source_dir, dst=self.source_folder,
                 excludes=["builds/*", "build/*", "build_*/*", "conan_experiments/*", "v314/*", "dist/*",
                           ".git", "**/.git", "**/__pycache__/*", "_example_integration/build*/*", "_example_integration/external/*"])
            return
        sources = self.conan_data.get("sources", {}).get(str(self.version))
        if not sources:
            raise ConanException(
                f"No source archive known for imgui_bundle/{self.version} (see conan/conandata.yml). "
                "To build from a local checkout: conan create conan -c user.imgui_bundle:source_dir=/path/to/imgui_bundle")
        get(self, **sources, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["IMGUI_BUNDLE_BUILD_DEMOS"] = False
        tc.variables["IMGUI_BUNDLE_INSTALL_CPP"] = True
        tc.variables["IMGUI_BUNDLE_AUTO_CLONE_SUBMODULES"] = False  # sources are complete
        tc.variables["CMAKE_FIND_NO_INSTALL_PREFIX"] = True
        # Backends
        tc.variables["HELLOIMGUI_USE_GLFW3"] = self.options.platform_backend == "glfw"
        tc.variables["HELLOIMGUI_USE_SDL2"] = self.options.platform_backend == "sdl2"
        tc.variables["HELLOIMGUI_HAS_OPENGL3"] = self.options.rendering_backend == "opengl3"
        tc.variables["HELLOIMGUI_WITH_TEST_ENGINE"] = bool(self.options.with_test_engine)
        # Dependencies are provided by Conan: never download them
        tc.variables["HELLOIMGUI_USE_FREETYPE"] = True
        tc.variables["HELLOIMGUI_DOWNLOAD_FREETYPE_IF_NEEDED"] = False
        tc.variables["HELLOIMGUI_DOWNLOAD_GLFW_IF_NEEDED"] = False
        tc.variables["HELLOIMGUI_DOWNLOAD_SDL_IF_NEEDED"] = False
        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        CMake(self).install()

    def package_info(self):
        # Consumers use the CMake package installed by imgui_bundle (lib/cmake/imgui_bundle/imgui_bundle-config.cmake):
        # it carries the ~30 targets, their compile definitions and find_dependency() calls.
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs = [os.path.join("lib", "cmake", "imgui_bundle")]
