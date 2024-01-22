# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
import os

import litgen


THIS_DIR = os.path.dirname(__file__)
PYDEF_DIR = THIS_DIR
STUB_DIR = THIS_DIR + "/../../../bindings/imgui_bundle/"


code = """
namespace pfd
{
    enum class button
    {
        cancel = -1,
        ok,
        yes,
        no,
        abort,
        retry,
        ignore,
    };

    enum class choice
    {
        ok = 0,
        ok_cancel,
        yes_no,
        yes_no_cancel,
        retry_cancel,
        abort_retry_ignore,
    };

    enum class icon
    {
        info = 0,
        warning,
        error,
        question,
    };

    // Additional option flags for various dialog constructors
    enum class opt : uint8_t
    {
        none = 0,
        // For file open, allow multiselect.
        multiselect     = 0x1,
        // For file save, force overwrite and disable the confirmation dialog.
        force_overwrite = 0x2,
        // For folder select, force path to be the provided argument instead
        // of the last opened directory, which is the Microsoft-recommended,
        // user-friendly behaviour.
        force_path      = 0x4,
    };

    //
    // The notify widget
    //
    class notify : public internal::dialog
    {
    public:
        notify(std::string const &title,
               std::string const &message,
               icon _icon = icon::info);

        bool ready(int timeout = default_wait_timeout) const;
        bool kill() const;
    };

    //
    // The message widget
    //
    class message : public internal::dialog
    {
    public:
        message(std::string const &title,
                std::string const &text,
                choice _choice = choice::ok_cancel,
                icon _icon = icon::info);

        button result();

        bool ready(int timeout = default_wait_timeout) const;
        bool kill() const;
    };

    std::vector<std::string> all_files_filter() {
        return {"All files", "*"};
    }

    //
    // The open_file, save_file, and open_folder widgets
    //
    class open_file : public internal::file_dialog
    {
    public:
        open_file(std::string const &title,
                  std::string const &default_path = "",
                  std::vector<std::string> const &filters = all_files_filter(),
                  opt options = opt::none);

        bool ready(int timeout = default_wait_timeout) const;
        bool kill() const;

        std::vector<std::string> result();
    };

    class save_file : public internal::file_dialog
    {
    public:
        save_file(std::string const &title,
                  std::string const &default_path = "",
                  std::vector<std::string> const &filters = all_files_filter(),
                  opt options = opt::none);

        bool ready(int timeout = default_wait_timeout) const;
        bool kill() const;

        std::string result();
    };

    class select_folder : public internal::file_dialog
    {
    public:
        select_folder(std::string const &title,
                      std::string const &default_path = "",
                      opt options = opt::none);

        bool ready(int timeout = default_wait_timeout) const;
        bool kill() const;

        std::string result();
    };

}
"""


def main():
    print("autogenerate_portable_file_dialogs")
    # input_cpp_header = CPP_HEADERS_DIR + "/portable_file_dialogs.h"
    output_cpp_pydef_file = PYDEF_DIR + "/pybind_portable_file_dialogs.cpp"
    output_stub_pyi_file = STUB_DIR + "/portable_file_dialogs.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    options.namespaces_root = ["pfd"]
    options.namespace_exclude__regex = ""
    options.python_run_black_formatter = True

    generator = litgen.LitgenGenerator(options)
    generator.process_cpp_code(code, filename="portable_file_dialogs_simplified.h")

    generator.write_generated_code(
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )


if __name__ == "__main__":
    main()
