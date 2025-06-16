# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2025 Pascal Thomet - https://github.com/pthom/imgui_bundle

# Notes:
# - lots of automated tests are performed in the CI pipeline, see .github/workflows/ci_automation_test.yml
#   They are performed on Windows and Linux after a pip install
# - this file is used to test binary wheels produced by cibuildwheel, and especially if imgui.create_context() works
#
# We skip windows, as GitHub Actions can't import imgui_bundle on Windows CI Runners in the wheel test
# (the error is: "ImportError: DLL load failed while importing imgui_bundle: The specified module could not be found.")
# GH Runners probably don't have the OpenGL DLLs required by imgui_bundle
# (this issue is solved in the pip.yml workflow, by installing the OpenGL DLLs)
import ast
import sys
from pathlib import Path


def test_version():
    if sys.platform == "win32":
        return

    import imgui_bundle
    assert imgui_bundle.__version__ >= "0.6.0"


def test_imgui_context_creation():
    if sys.platform == "win32":
        return

    # Check that this complex issue is fixed:
    #     https://github.com/pthom/imgui_bundle/issues/170#issuecomment-1900100904
    from imgui_bundle import imgui

    ctx = imgui.create_context()
    assert ctx is not None
    imgui.destroy_context(ctx)


def test_pyi_files_syntax() -> None:
    """Test that all .pyi files in the bindings directory have valid Python syntax."""
    import imgui_bundle
    
    root = Path(imgui_bundle.__file__).parent

    errors: list[str] = []
    pyi_files = list(root.rglob("*.pyi"))
    if not pyi_files:
        raise AssertionError("No .pyi files found in the bindings directory.")

    for pyi_file in root.rglob("*.pyi"):
        try:
            # try to parse the .pyi file
            ast.parse(pyi_file.read_text(encoding="utf-8"), filename=str(pyi_file))
        except Exception as e:
            msg = f"{type(e).__name__} parsing {pyi_file.relative_to(root)}:\n{e}"
            errors.append(msg)
            

    # Report all syntax errors found
    if errors:
        error_summary = (
            f"Found {len(errors)} .pyi files with syntax errors:\n\n"
            + "\n".join(errors)
        )
        raise AssertionError(error_summary)
