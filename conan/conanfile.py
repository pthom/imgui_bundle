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
#     # from a commit of the repository (a nightly; the commit pins every submodule):
#     conan create conan --version=<version>-dev.<date> -c user.imgui_bundle:commit=<sha> --build=missing
#     # from a local checkout (e.g. this one; its tracked files, as they are on disk):
#     conan create conan -c user.imgui_bundle:source_dir=$PWD --build=missing
import os
import re
import shutil
import subprocess

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, load
from conan.tools.scm import Git


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
        # ImGui Test Engine (automation and tests). Off by default: its license is not free for every user
        "with_test_engine": [True, False],
        # Markdown: download images from URLs (requires libcurl)
        "with_image_download": [True, False],
    }
    default_options = {
        "fPIC": True,
        "platform_backend": "glfw",
        "rendering_backend": "opengl3",
        "with_test_engine": False,
        "with_image_download": True,
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

    def configure(self):
        if self.settings.os == "Windows" and self.options.with_image_download:
            # TLS through Windows itself (schannel): no OpenSSL to build, and the certificates Windows trusts
            self.options["libcurl"].with_ssl = "schannel"

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
        if self.options.with_image_download:
            self.requires("libcurl/8.21.0")

    def source(self):
        # A local checkout (development), a commit of the repository (a nightly), or the full source archive of a
        # release (srcs-full-<tag>.tar.gz, which includes all submodules; see conandata.yml)
        local_source_dir = self.conf.get("user.imgui_bundle:source_dir", default=None, check_type=str)
        if local_source_dir:
            # The tracked files only: a checkout also holds build folders, caches and venvs (several GB)
            self.output.info(f"Copying the tracked files of {local_source_dir} (submodules included)")
            listing = subprocess.run(["git", "ls-files", "--recurse-submodules", "-z"], cwd=local_source_dir,
                                     check=True, capture_output=True).stdout.decode()
            for rel in filter(None, listing.split("\0")):
                src, dst = os.path.join(local_source_dir, rel), os.path.join(self.source_folder, rel)
                if not os.path.lexists(src):
                    continue
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if os.path.islink(src):
                    os.symlink(os.readlink(src), dst)
                elif os.path.isfile(src):
                    shutil.copy2(src, dst)
            return
        commit = self.conf.get("user.imgui_bundle:commit", default=None, check_type=str)
        if commit:
            # The commit pins every submodule (the forks): a shallow fetch of it, then of its submodules
            self.output.info(f"Fetching {self.url} at {commit}, with its submodules")
            git = Git(self)
            git.run("init -q")
            git.run(f"fetch -q --depth 1 {self.url} {commit}")
            git.run("checkout -q FETCH_HEAD")
            git.run("submodule update -q --init --recursive --depth 1")
            return
        sources = self.conan_data.get("sources", {}).get(str(self.version))
        if not sources:
            raise ConanException(
                f"No source archive known for imgui_bundle/{self.version} (see conan/conandata.yml). "
                "To build from a commit: -c user.imgui_bundle:commit=<sha>; "
                "from a local checkout: -c user.imgui_bundle:source_dir=/path/to/imgui_bundle")
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
        tc.variables["IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES"] = bool(self.options.with_image_download)
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
