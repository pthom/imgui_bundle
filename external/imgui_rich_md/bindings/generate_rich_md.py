# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"


def main() -> None:
    print("autogenerate_imgui_md")
    input_cpp_header = THIS_DIR + "/../../imgui_rich_md/imgui_rich_md/imgui_rich_md/rich_md.h"
    input_cpp_header_host = THIS_DIR + "/../../imgui_rich_md/imgui_rich_md/imgui_rich_md/rich_md_host.h"  # only the download types
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_rich_md.cpp"
    output_stub_pyi_file = STUB_DIR + "/rich_md.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.use_nanobind()
    options.fn_params_type_replacements.add_replacements([(r"\bImVec2\b", "ImVec2Like"), (r"\bImVec4\b", "ImVec4Like")])

    options.namespaces_root = ["RichMd"]
    options.python_run_black_formatter = True
    options.value_replacements.add_last_replacement(
        "OnOpenLink_Default", "on_open_link_default"
    )
    options.value_replacements.add_last_replacement(
        "OnImage_Default", "on_image_default"
    )
    options.struct_create_default_named_ctor__regex = ""
    # the contexts belong to rich_md (destroy_context), never to Python
    options.fn_return_force_policy_reference_for_pointers__regex = "GetCodeFont|GetFont|CreateContext|GetCurrentContext"

    # Exclude members that need custom bindings
    options.member_exclude_by_name_and_class__regex = {
        "MarkdownCallbacks": r"^OnDownloadData$",
        "MarkdownDownloadResult": r"^data$",
    }
    options.fn_exclude_by_name__regex = r"^FillFromData$|^GetStyle$"
    # rich_md_host.h: the host services are C++ only, except the download types (used by set_download_function)
    options.fn_exclude_by_name__regex += r"|^UploadRgbaDefault$|^ReadAssetDefault$|^SetHostServices$|^GetHostServices$"
    options.class_exclude_by_name__regex = r"^HostServices$|^MarkdownTexture$|^LatexBitmap$|^EmbeddedAsset$"

    # Context: opaque in Python (its definition, in rich_md_internal.h, is not bound)
    options.custom_bindings.add_custom_bindings_to_main_module(
        stub_code='''
            class Context:
                """A markdown context (its options, its fonts, its caches): made by create_context, destroyed by
                destroy_context. Opaque."""
                pass
        ''',
        pydef_code=r'''
            nb::class_<RichMd::Context>(LG_MODULE, "Context", "A markdown context (made by create_context, destroyed by destroy_context). Opaque.");
        ''',
    )

    # set_download_function: HostServices.Download, kept as a Python object (same PyObject* pattern as on_download_data)
    options.custom_bindings.add_custom_bindings_to_main_module(
        stub_code='''
            def set_download_function(fn: Optional[Callable[[str], MarkdownDownloadResult]]) -> None:
                """Sets the function that downloads URL images (HostServices.Download), for every markdown context.
                imgui_bundle installs one at import (urllib in a thread on desktop, JS fetch in Pyodide).
                Called every frame for a URL until it returns Ready or Failed; an asynchronous download returns
                Downloading first and tracks its pending downloads itself. None disables URL images."""
                pass
        ''',
        pydef_code=r'''
            static PyObject* s_host_download_func = nullptr;

            LG_MODULE.def("set_download_function",
                [](nb::object py_func) {
                    auto services = RichMd::GetHostServices();
                    Py_XDECREF(s_host_download_func);
                    s_host_download_func = nullptr;
                    services.Download = nullptr;
                    if (!py_func.is_none()) {
                        s_host_download_func = py_func.ptr();
                        Py_INCREF(s_host_download_func);
                        services.Download = [](const std::string& url) -> RichMd::MarkdownDownloadResult {
                            nb::gil_scoped_acquire acquire;
                            nb::object func = nb::borrow(s_host_download_func);
                            return nb::cast<RichMd::MarkdownDownloadResult>(func(nb::cast(url)));
                        };
                    }
                    RichMd::SetHostServices(services);
                },
                nb::arg("fn"),
                "Sets the function that downloads URL images (HostServices.Download); None disables URL images."
            );
        ''',
    )

    # Custom binding for MarkdownDownloadResult.fill_from_bytes: Python bytes -> C++ data
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="RichMd::MarkdownDownloadResult",
        stub_code='''
            def fill_from_bytes(self, data: bytes) -> None:
                """Fill the result data from a Python bytes object."""
                ...
        ''',
        pydef_code=r'''
            LG_CLASS.def("fill_from_bytes",
                [](RichMd::MarkdownDownloadResult& self, nb::bytes data) {
                    self.FillFromData(data.c_str(), data.size());
                },
                nb::arg("data"),
                "Fill the result data from a Python bytes object."
            );
        ''',
    )

    # Custom binding for OnDownloadData callback on MarkdownCallbacks
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="RichMd::MarkdownCallbacks",
        stub_code='''
            @property
            def on_download_data(self) -> Optional[str]:
                """Deprecated: use rich_md.set_download_function. Returns None if not set, or a status string
                (reading back the callable itself is not supported)."""
                ...
            @on_download_data.setter
            def on_download_data(self, fn: Optional[Callable[[str], MarkdownDownloadResult]]) -> None:
                """Deprecated: use rich_md.set_download_function (same contract). When set, the function becomes
                the download service when the markdown context is created."""
                ...
        ''',
        pydef_code=r'''
            // Static storage for the Python download callable (prevents crash at exit)
            static PyObject* s_download_func = nullptr;

            LG_CLASS.def_prop_rw("on_download_data",
                [](const RichMd::MarkdownCallbacks& self) -> nb::object {
                    (void)self;
                    if (!self.OnDownloadData)
                        return nb::none();
                    return nb::cast(std::string("on_download_data is set (read-back of the callable is not supported)"));
                },
                [](RichMd::MarkdownCallbacks& self, nb::object py_func) {
                    if (py_func.is_none()) {
                        Py_XDECREF(s_download_func);
                        s_download_func = nullptr;
                        self.OnDownloadData = nullptr;
                        return;
                    }
                    Py_XDECREF(s_download_func);
                    s_download_func = py_func.ptr();
                    Py_INCREF(s_download_func);
                    self.OnDownloadData = [](const std::string& url) -> RichMd::MarkdownDownloadResult {
                        nb::gil_scoped_acquire acquire;
                        nb::object func = nb::borrow(s_download_func);
                        nb::object py_result = func(nb::cast(url));
                        return nb::cast<RichMd::MarkdownDownloadResult>(py_result);
                    };
                },
                "Deprecated: use rich_md.set_download_function (same contract)."
            );
        ''',
    )

    generator = litgen.LitgenGenerator(options, omit_boxed_types=True)
    generator.process_cpp_file(input_cpp_header_host)
    generator.process_cpp_file(input_cpp_header)
    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    main()
