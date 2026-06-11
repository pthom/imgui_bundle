"""Add IMGUI_DEMO_MARKER calls to a Python demo file, matching section names from its C++ counterpart.

Reads the C++ file to extract: C++ function name → section name.
Converts C++ function names (Demo_LinePlots) to Python (demo_line_plots).
Inserts IMGUI_DEMO_MARKER("section") at the start of each matching Python function.
Also adds the stub definition and import if not already present.

Usage: python add_python_markers.py <cpp_file> <py_file>
"""
import re
import sys


CAMEL_TO_SNAKE_OVERRIDES = {
    "Demo_Histogram2D": "demo_histogram2d",
    "Demo_NaNValues": "demo_nan_values",
    "DemoNaNValues": "demo_nan_values",
}

def camel_to_snake(name: str) -> str:
    """Convert Demo_LinePlots to demo_line_plots."""
    if name in CAMEL_TO_SNAKE_OVERRIDES:
        return CAMEL_TO_SNAKE_OVERRIDES[name]
    # Remove "Demo_" or "Demo" prefix
    if name.startswith("Demo_"):
        name = name[5:]  # strip "Demo_"
    elif name.startswith("Demo"):
        name = name[4:]  # strip "Demo"
    # Handle transitions: insert _ between lowercase→uppercase
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', s)
    s = s.lower()
    return "demo_" + s


def extract_cpp_markers(cpp_path: str) -> dict[str, str]:
    """Extract function_name → section_name from C++ IMGUI_DEMO_MARKER calls.

    Looks for patterns like:
        void Demo_Xxx() {
            IMGUI_DEMO_MARKER("Section/Name");
    """
    with open(cpp_path) as f:
        lines = f.readlines()

    func_re = re.compile(r'^void (Demo\w+)\(')
    marker_re = re.compile(r'^\s*IMGUI_DEMO_MARKER\("(.+?)"\)')

    result = {}
    current_func = None
    for line in lines:
        m = func_re.match(line)
        if m:
            current_func = m.group(1)
            continue
        if current_func:
            m = marker_re.match(line)
            if m:
                result[current_func] = m.group(1)
                current_func = None  # only take the first marker per function
            elif line.strip() and not line.strip().startswith('//') and not line.strip() == '{':
                current_func = None  # non-empty, non-comment line without marker -> give up
    return result


def process_python(py_lines: list[str], cpp_to_section: dict[str, str]) -> list[str]:
    """Add IMGUI_DEMO_MARKER to Python functions matching C++ markers."""
    # Build python_func_name → section_name mapping
    py_to_section = {}
    for cpp_func, section in cpp_to_section.items():
        py_func = camel_to_snake(cpp_func)
        py_to_section[py_func] = section

    func_re = re.compile(r'^def (\w+)\(')
    result = []
    i = 0
    added = 0

    while i < len(py_lines):
        m = func_re.match(py_lines[i])
        if m:
            func_name = m.group(1)
            section = py_to_section.get(func_name)
            if section:
                result.append(py_lines[i])
                # Check if next non-blank, non-docstring line already has IMGUI_DEMO_MARKER
                j = i + 1
                # Skip docstrings and blank lines
                while j < len(py_lines) and (py_lines[j].strip() == '' or py_lines[j].strip().startswith('"""') or py_lines[j].strip().startswith("'''")):
                    result.append(py_lines[j])
                    j += 1
                if j < len(py_lines) and 'IMGUI_DEMO_MARKER' in py_lines[j]:
                    # Already has marker
                    i = j
                    continue
                # Add the marker
                result.append(f'    IMGUI_DEMO_MARKER("{section}")\n')
                added += 1
                i = j
                continue
        result.append(py_lines[i])
        i += 1

    print(f"  Added {added} marker(s), {len(py_to_section) - added} already present or unmatched")
    # Report unmatched
    matched_funcs = set()
    for line in result:
        m = func_re.match(line)
        if m and m.group(1) in py_to_section:
            matched_funcs.add(m.group(1))
    unmatched = set(py_to_section.keys()) - matched_funcs
    if unmatched:
        print(f"  Unmatched Python functions: {unmatched}")
    return result


def ensure_marker_stub(py_lines: list[str]) -> list[str]:
    """Add IMGUI_DEMO_MARKER stub definition if not present."""
    for line in py_lines:
        if 'def IMGUI_DEMO_MARKER' in line or 'IMGUI_DEMO_MARKER' in line and 'import' in line:
            return py_lines  # already defined

    # Find insertion point: after imports, before first function
    insert_at = 0
    for i, line in enumerate(py_lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_at = i + 1
        elif line.startswith('def ') or line.startswith('class '):
            break
        elif line.strip() and not line.startswith('#') and not line.startswith('import') and not line.startswith('from'):
            insert_at = i + 1

    stub = [
        '\n',
        'def IMGUI_DEMO_MARKER(section: str) -> None:\n',
        '    """Marker for the Explorer. Maps sections to source code."""\n',
        '    pass\n',
        '\n',
    ]
    return py_lines[:insert_at] + stub + py_lines[insert_at:]


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <cpp_file> <py_file>")
        sys.exit(1)

    cpp_path, py_path = sys.argv[1], sys.argv[2]

    # Extract C++ markers
    cpp_markers = extract_cpp_markers(cpp_path)
    print(f"Found {len(cpp_markers)} markers in {cpp_path}")

    # Read Python file
    with open(py_path) as f:
        py_lines = f.readlines()

    # Add stub if needed
    py_lines = ensure_marker_stub(py_lines)

    # Add markers
    py_lines = process_python(py_lines, cpp_markers)

    # Write back
    with open(py_path, 'w') as f:
        f.writelines(py_lines)
    print(f"Processed {py_path}")


if __name__ == '__main__':
    main()
