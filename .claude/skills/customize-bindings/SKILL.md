---
name: customize-bindings
description: How to customize Python bindings when the auto-generated litgen output is wrong (return policy, parameter lists, etc.). Covers excluding functions and providing custom pybind/stub code.
---

# Customizing Python Bindings

When litgen's auto-generated bindings have issues (wrong return policy, unnecessary parameters, incorrect types), use the **exclude + custom binding** pattern.

## Entry points

- Recipes: `libs_bindings <lib>` to regenerate after a change (see "After making changes"), then `mypy`.
- Docs: `docs/book/devel_docs/bindings_intro.md` (how the generation works), and litgen's options (next section).

## Reference: litgen options

Before customizing bindings, read the litgen options reference to understand all available configuration knobs:

- **Full options reference**: `../litgen/src/litgen/options.py` - all `LitgenOptions` fields with docstrings (exclusion regexes, return policies, type replacements, naming conventions, etc.)
- **imgui-specific options**: `external/imgui/bindings/litgen_options_imgui.py` - how imgui configures litgen

## Choosing the mechanism (in this order)

See "Adapting an API for Python: where does the change go?" in `docs/book/devel_docs/bindings_forks.md`:
1. a litgen option, if it is enough
2. a wrapper header (`external/imgui/imgui_pywrappers/`) when the Python version is plain C++ that litgen can bind
   (new struct, `std::string`, `std::optional`, tuple): bindings, stubs and docstrings are generated
3. a custom binding (this skill) when it needs nanobind types, member access from outside the class, or control over a
   whole overload set. If it replaces overloads, it must own the WHOLE set: exclude every C++ overload and register them all
   (Python overloads must be consecutive in the stubs; registration order decides which one wins; list overloads of float
   arrays should take `std::array<double, N>`, since nanobind's first pass rejects floats that are not exact in float32)
4. a patch in the fork only when the library's own behavior must change

Many binding issues can be fixed with litgen options alone (e.g., `fn_return_force_policy_reference_for_references__regex`, `fn_params_output_modifiable_immutable_to_return__regex`) without needing the full exclude + custom binding pattern. Check the options first.

## Pattern: Exclude + Custom Binding

Two steps:

1. **Exclude** the function from auto-generation in the litgen options
2. **Provide** a custom binding with correct behavior

### Step 1: Exclude in litgen options

In the library's litgen options file (e.g., `external/imgui/bindings/litgen_options_imgui.py`):

```python
options.fn_exclude_by_name__regex = join_string_by_pipe_char([
    # ... existing exclusions ...
    r"^FunctionName$",  # Comment explaining why excluded
])
```

If the options file is shared across multiple generators (like `litgen_options_imgui` is used by imgui, imgui_internal, and test_engine), the exclusion applies to all of them.

### Step 2: Add custom binding in the generator script

In the library's generator script (e.g., `external/imgui/bindings/generate_imgui.py`), add the custom binding to the **specific generator** that should have it (not the shared options):

```python
options.custom_bindings.add_custom_bindings_to_main_module(
    stub_code='''
    def function_name(arg1: Type1, arg2: Type2) -> ReturnType:
        """Docstring."""
        ...
''',
    pydef_code="""
    LG_MODULE.def("function_name",
        [](Type1 arg1, Type2 arg2) -> ReturnType {
            // custom implementation
        }, nb::arg("arg1"), nb::arg("arg2"),
        "Docstring.");
""",
)
```

**Important**: Add the custom binding to the specific generator's options (e.g., `options_imgui` in `autogenerate_imgui()`), NOT to the shared `litgen_options_imgui()` function. Otherwise it will be emitted in all generators that use those options.

## Available custom binding methods

- `add_custom_bindings_to_main_module(stub_code, pydef_code)` - for free functions in root namespaces
- `add_custom_bindings_to_class(qualified_class, stub_code, pydef_code)` - for class methods/properties
- `add_custom_bindings_to_submodule(qualified_namespace, stub_code, pydef_code)` - for functions in non-root namespaces

Placeholders in `pydef_code`: `LG_MODULE`, `LG_CLASS`, `LG_SUBMODULE`.

## Deduplication

`add_custom_bindings_to_main_module` emits code only once per generator, even when that generator processes multiple header files. This is handled by a flag in `CustomBindings._main_module_emitted_*`. Multiple calls to `add_custom_bindings_to_main_module` on the same options object accumulate and are emitted together.

## Common use cases

### Return by copy instead of reference

When C++ returns `const T&` and litgen uses `rv_policy::reference`, Python gets a mutable reference to internal state. Fix: return by value.

```python
# Exclude
r"^GetStyleColorVec4$",

# Custom binding returns ImVec4 by value (copy)
LG_MODULE.def("get_style_color_vec4",
    [](ImGuiCol idx) -> ImVec4 { return ImGui::GetStyleColorVec4(idx); },
    nb::arg("idx"), "...");
```

### Remove output parameters

When C++ uses `float&` output params, litgen may keep them as required inputs. Fix: only take inputs, fill outputs internally.

```python
# C++: void ColorConvertRGBtoHSV(float r, float g, float b, float& out_h, float& out_s, float& out_v)
# Bad Python: color_convert_rgb_to_hsv(r, g, b, out_h, out_s, out_v) -> Tuple
# Good Python: color_convert_rgb_to_hsv(r, g, b) -> Tuple

LG_MODULE.def("color_convert_rgb_to_hsv",
    [](float r, float g, float b) -> std::tuple<float, float, float> {
        float h, s, v;
        ImGui::ColorConvertRGBtoHSV(r, g, b, h, s, v);
        return std::make_tuple(h, s, v);
    }, nb::arg("r"), nb::arg("g"), nb::arg("b"), "...");
```

## Real examples

See `external/imgui/bindings/generate_imgui.py` for working examples of:
- `GetStyleColorVec4` (return by copy)
- `ColorConvertRGBtoHSV` / `ColorConvertHSVtoRGB` (remove output params)

See `external/imgui_rich_md/bindings/generate_rich_md.py` for:
- `set_download_function` and `on_download_data` (a Python callable kept as a `PyObject*`)

## After making changes

Always regenerate and verify:

```bash
just libs_bindings <lib_name>
git diff --stat  # only expected files should change
```

Check that internal.pyi, test_engine.pyi etc. are NOT modified (if using shared options, only the specific generator should get the custom binding).
