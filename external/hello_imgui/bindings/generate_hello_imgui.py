# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os
from srcmlcpp.scrml_warning_settings import WarningType
from codemanip import amalgamated_header
from codemanip.code_utils import join_string_by_pipe_char

import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"

HELLO_IMGUI_DIR = os.path.realpath(THIS_DIR + "/../hello_imgui")
CPP_HEADERS_DIR = HELLO_IMGUI_DIR + "/src/hello_imgui"


def make_hello_imgui_amalgamated_header():
    hello_imgui_src_dir = HELLO_IMGUI_DIR + "/src/"

    options = amalgamated_header.AmalgamationOptions()

    options.base_dir = hello_imgui_src_dir
    options.local_includes_startwith = "hello_imgui/"
    options.include_subdirs = ["hello_imgui"]
    options.main_header_file = "hello_imgui.h"
    options.dst_amalgamated_header_file = PYDEF_DIR + "/hello_imgui_amalgamation.h"

    amalgamated_header.write_amalgamate_header_file(options)


def main():
    print("autogenerate_hello_imgui")
    make_hello_imgui_amalgamated_header()

    input_cpp_header = THIS_DIR + "/hello_imgui_amalgamation.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_hello_imgui.cpp"
    output_stub_pyi_file = STUB_DIR + "/hello_imgui.pyi"

    # Configure options
    from codemanip.code_replacements import RegexReplacement

    options = litgen.LitgenOptions()
    options.use_nanobind()
    options.fn_params_type_replacements.add_replacements([(r"\bImVec2\b", "ImVec2Like"), (r"\bImVec4\b", "ImVec4Like")])

    # options.original_location_flag_show = True
    options.original_signature_flag_show = True
    options.srcmlcpp_options.ignored_warnings = [WarningType.LitgenIgnoreElement]
    options.srcmlcpp_options.ignored_warning_parts = ["gAssetsSubfolderFolderName"]
    options.namespace_names_replacements.add_last_replacement("ImGui", "Imgui")
    options.namespaces_root = ["HelloImGui","ImGuiTheme"]
    options.fn_return_force_policy_reference_for_pointers__regex = (
        join_string_by_pipe_char([r"\bLoadFontTTF\w*", r"MergeFontAwesomeToLastFont"])
    )
    options.var_names_replacements.replacements = [
        RegexReplacement("imGui", "imgui"),
        RegexReplacement("ImGui", "Imgui"),
    ]
    options.function_names_replacements.replacements = [
        # RegexReplacement("imGui", "imgui"),
        RegexReplacement("ImGui", "Imgui"),
    ]
    options.fn_return_force_policy_reference_for_pointers__regex = r".*"
    options.fn_params_output_modifiable_immutable_to_return__regex = r".*"
    # setAssetsFolder & SetAssetsFolder offer the same function
    options.fn_exclude_by_name__regex = r"^setAssetsFolder$|^TranslateCommonGlyphRanges$|^SetLoadAssetFileDataFunction$|^LoadImageDataFromAsset$|^LoadImageDataFromEncodedData$|^ImageAndSizeFromEncodedData$|^CreateTextureGpuFromRgbaData$|^assetFileFullPath$"
    # TextureGpu is hand-bound below (abstract base + shared_ptr holder).
    options.class_exclude_by_name__regex = r"^ImageData$|^TextureGpu$"

    # Manual binding for ImageAndSizeFromEncodedData (const void* + size_t -> Python bytes)
    options.custom_bindings.add_custom_bindings_to_main_module(
        stub_code='''
            def image_and_size_from_encoded_data(data: bytes, cache_key: str = "") -> ImageAndSize:
                """Create a texture from encoded image data (PNG, JPEG, BMP, GIF, etc.).
                - data: bytes containing the encoded image
                - cache_key: if non-empty, the texture is cached and reused on subsequent calls with the same key
                Returns an ImageAndSize with texture_id and size."""
                pass
        ''',
        pydef_code='''
            LG_MODULE.def("image_and_size_from_encoded_data",
                [](nb::bytes data, const std::string& cache_key) -> HelloImGui::ImageAndSize {
                    return HelloImGui::ImageAndSizeFromEncodedData(data.c_str(), data.size(), cache_key);
                },
                nb::arg("data"), nb::arg("cache_key") = "",
                "Create a texture from encoded image data (PNG, JPEG, BMP, GIF, etc.).\\n"
                "- data: bytes containing the encoded image\\n"
                "- cache_key: if non-empty, the texture is cached and reused on subsequent calls with the same key\\n"
                "Returns an ImageAndSize with texture_id and size."
            );
        ''',
    )

    # Manual binding for TextureGpu (abstract base, shared_ptr holder) and
    # create_texture_gpu_from_rgba_data (numpy ndarray -> owning shared_ptr).
    #
    # litgen cannot autogenerate this because:
    #   - TextureGpu is an abstract class with backend-specific subclasses
    #   - the factory takes a `const unsigned char*` raw pointer that we want
    #     to expose as an HxWx4 uint8 numpy array (with shape/contiguity checks)
    options.custom_bindings.add_custom_bindings_to_main_module(
        stub_code='''
            class TextureGpu:
                """Opaque RAII handle owning a GPU texture.

                The GPU resource is freed when the last reference to this object
                is dropped (no separate `delete_texture` call). Hold the handle
                in Python for as long as you want to display the texture.

                Threading: must be created from the GUI thread, while a live
                rendering backend (OpenGL/Metal/Vulkan/DirectX11) is initialized.
                """
                width: int
                height: int
                def texture_id(self) -> int:
                    """Returns the underlying ImTextureID as a Python int.
                    Pass it to imgui.image() etc."""
                    pass

            def create_texture_gpu_from_rgba_data(rgba: np.ndarray) -> TextureGpu:
                """Upload an HxWx4 uint8 RGBA numpy array to a new GPU texture.

                - `rgba` must be a contiguous numpy array of dtype uint8 with
                  shape (height, width, 4). The pixel data is read once during
                  the upload; the numpy array does not need to outlive the call.
                - Returns an owning `TextureGpu` handle. Drop the last reference
                  to free the GPU resource.

                Threading: must be called from the GUI thread, while a live
                rendering backend is initialized (i.e. inside the gui callback,
                or after `hello_imgui.run` has set up the backend).
                """
                pass
        ''',
        pydef_code='''
            // TextureGpu: abstract base, registered with shared_ptr holder so
            // returning HelloImGui::TextureGpuPtr from a factory transfers
            // ownership to Python automatically.
            nb::class_<HelloImGui::TextureGpu>(LG_MODULE, "TextureGpu",
                "Opaque RAII handle owning a GPU texture.\\n"
                "The GPU resource is freed when the last Python reference is dropped.\\n"
                "Hold this in Python for as long as you want to display the texture.")
                .def_ro("width", &HelloImGui::TextureGpu::Width)
                .def_ro("height", &HelloImGui::TextureGpu::Height)
                .def("texture_id",
                    [](HelloImGui::TextureGpu& self) -> ImTextureID {
                        return self.TextureID();
                    },
                    "Returns the underlying ImTextureID. Pass to imgui.image().");

            LG_MODULE.def("create_texture_gpu_from_rgba_data",
                [](nb::ndarray<const uint8_t, nb::shape<-1, -1, 4>, nb::c_contig> rgba)
                    -> HelloImGui::TextureGpuPtr
                {
                    int h = (int)rgba.shape(0);
                    int w = (int)rgba.shape(1);
                    return HelloImGui::CreateTextureGpuFromRgbaData(rgba.data(), w, h);
                },
                nb::arg("rgba"),
                "Upload an HxWx4 uint8 RGBA numpy array to a new GPU texture.\\n"
                "Returns an owning TextureGpu handle (drop the last reference to free).\\n"
                "Threading: call from the GUI thread while a live rendering backend exists."
            );
        ''',
    )

    options.value_replacements.add_last_replacement("ImGuiDockNodeFlags_None", "DockNodeFlags_.none")
    options.value_replacements.add_last_replacement("ImGuiDockNodeFlags_PassthruCentralNode", "DockNodeFlags_.passthru_central_node")
    options.value_replacements.add_last_replacement("ImGuiCond_FirstUseEver", "Cond_.first_use_ever")
    options.value_replacements.add_last_replacement("ImGuiDir_Down", "Dir.down")

    options.python_run_black_formatter = True

    options.postprocess_stub_function = lambda code: code.replace("(VoidFunction)", "")

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    main()
