from docutils import nodes
from docutils.parsers.rst import Directive
from pathlib import Path
from docutils.statemachine import StringList
from sphinx.util.nodes import nested_parse_with_titles


class CodesIncludeDirective(Directive):
    has_content = False  # No content allowed
    required_arguments = 1  # Requires one argument
    optional_arguments = 0  # No additional optional arguments
    final_argument_whitespace = False  # No multi-word arguments
    option_spec = {}  # No specific options

    def run(self):
        base_name = self.arguments[0]  # The filename provided in the directive

        content = []

        # Generate tab-set Markdown syntax
        content.append("`````{tab-set}")
        python_file = Path(f"{base_name}.py")
        if python_file.exists():
            content.append("````{tab-item} Python")
            content.append("```python")
            content.append(python_file.read_text())
            content.append("```")
            content.append("````")

        cpp_file = Path(f"{base_name}.cpp")
        if cpp_file.exists():
            content.append("````{tab-item} C++")
            content.append("```cpp")
            content.append(cpp_file.read_text())
            content.append("```")
            content.append("````")

        content.append("`````")

        # Use StringList to parse the Markdown content
        content_list = StringList(content)
        node = nodes.container()
        nested_parse_with_titles(self.state, content_list, node)

        return [node]


def setup(app):
    app.add_directive("codes_include", CodesIncludeDirective)