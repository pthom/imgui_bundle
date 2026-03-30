# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"


def main():
    print("autogenerate_imgui_md")
    input_cpp_header = THIS_DIR + "/../imgui_md_wrapper/imgui_md_wrapper.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_imgui_md.cpp"
    output_stub_pyi_file = STUB_DIR + "/imgui_md.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.use_nanobind()
    options.fn_params_type_replacements.add_replacements([(r"\bImVec2\b", "ImVec2Like"), (r"\bImVec4\b", "ImVec4Like")])

    options.namespaces_root = ["ImGuiMd"]
    options.python_run_black_formatter = True
    options.value_replacements.add_last_replacement(
        "OnOpenLink_Default", "on_open_link_default"
    )
    options.value_replacements.add_last_replacement(
        "OnImage_Default", "on_image_default"
    )
    options.struct_create_default_named_ctor__regex = ""
    options.fn_return_force_policy_reference_for_pointers__regex = "GetCodeFont|GetFont"

    # Exclude members that need custom bindings
    options.member_exclude_by_name_and_class__regex = {
        "MarkdownCallbacks": r"^OnDownloadData$",
        "MarkdownDownloadResult": r"^data$",
    }
    options.fn_exclude_by_name__regex = r"^FillFromData$|^Priv_SetOnInitializeMarkdownCallback$"

    # Custom binding for Priv_SetOnInitializeMarkdownCallback (same PyObject* pattern as OnDownloadData)
    options.custom_bindings.add_custom_bindings_to_main_module(
        stub_code='''
            def _set_on_initialize_markdown_callback(callback: Optional[Callable[[MarkdownOptions], None]]) -> None:
                """Private. Set a callback called during initialize_markdown() to customize options.
                Used internally by imgui_bundle to inject URL image download support."""
                pass
        ''',
        pydef_code=r'''
            static PyObject* s_init_md_callback = nullptr;

            LG_MODULE.def("_set_on_initialize_markdown_callback",
                [](nb::object py_func) {
                    if (py_func.is_none()) {
                        Py_XDECREF(s_init_md_callback);
                        s_init_md_callback = nullptr;
                        ImGuiMd::Priv_SetOnInitializeMarkdownCallback(nullptr);
                        return;
                    }
                    Py_XDECREF(s_init_md_callback);
                    s_init_md_callback = py_func.ptr();
                    Py_INCREF(s_init_md_callback);
                    ImGuiMd::Priv_SetOnInitializeMarkdownCallback(
                        [](ImGuiMd::MarkdownOptions& options) {
                            nb::gil_scoped_acquire acquire;
                            nb::object func = nb::borrow(s_init_md_callback);
                            func(nb::cast(options, nb::rv_policy::reference));
                        }
                    );
                },
                nb::arg("callback"),
                "Set a callback called during initialize_markdown() to customize options."
            );
        ''',
    )

    # Custom binding for MarkdownDownloadResult.fill_from_bytes: Python bytes -> C++ data
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImGuiMd::MarkdownDownloadResult",
        stub_code='''
            def fill_from_bytes(self, data: bytes) -> None:
                """Fill the result data from a Python bytes object."""
                ...
        ''',
        pydef_code=r'''
            LG_CLASS.def("fill_from_bytes",
                [](ImGuiMd::MarkdownDownloadResult& self, nb::bytes data) {
                    self.FillFromData(data.c_str(), data.size());
                },
                nb::arg("data"),
                "Fill the result data from a Python bytes object."
            );
        ''',
    )

    # Custom binding for OnDownloadData callback on MarkdownCallbacks
    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="ImGuiMd::MarkdownCallbacks",
        stub_code='''
            @property
            def on_download_data(self) -> Optional[str]:
                """Returns None if not set, or a status string if set.
                Reading back the callable itself is not supported."""
                ...
            @on_download_data.setter
            def on_download_data(self, fn: Optional[Callable[[str], MarkdownDownloadResult]]) -> None:
                """Set a callable that downloads data from a URL.
                The callable receives a URL string and should return a MarkdownDownloadResult.
                The callback is stateful: it will be called every frame for a given URL until
                it returns Ready or Failed. For synchronous downloads, return Ready or Failed
                immediately. For async downloads, return Downloading on first call, then
                Ready/Failed once done.
                Set to None to disable URL image support."""
                ...
        ''',
        pydef_code=r'''
            // Static storage for the Python download callable (prevents crash at exit)
            static PyObject* s_download_func = nullptr;

            LG_CLASS.def_prop_rw("on_download_data",
                [](const ImGuiMd::MarkdownCallbacks& self) -> nb::object {
                    (void)self;
                    if (!self.OnDownloadData)
                        return nb::none();
                    return nb::cast(std::string("on_download_data is set (read-back of the callable is not supported)"));
                },
                [](ImGuiMd::MarkdownCallbacks& self, nb::object py_func) {
                    if (py_func.is_none()) {
                        Py_XDECREF(s_download_func);
                        s_download_func = nullptr;
                        self.OnDownloadData = nullptr;
                        return;
                    }
                    Py_XDECREF(s_download_func);
                    s_download_func = py_func.ptr();
                    Py_INCREF(s_download_func);
                    self.OnDownloadData = [](const std::string& url) -> ImGuiMd::MarkdownDownloadResult {
                        nb::gil_scoped_acquire acquire;
                        nb::object func = nb::borrow(s_download_func);
                        nb::object py_result = func(nb::cast(url));
                        return nb::cast<ImGuiMd::MarkdownDownloadResult>(py_result);
                    };
                },
                "OnDownloadData: downloads data from a URL (empty by default).\n"
                "When set, OnImage_Default will use it to fetch images from URLs.\n"
                "The callable should accept a URL string and return a MarkdownDownloadResult."
            );
        ''',
    )

    litgen.write_generated_code_for_file(
        options,
        input_cpp_header_file=input_cpp_header,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        omit_boxed_types=True,
    )


if __name__ == "__main__":
    main()
