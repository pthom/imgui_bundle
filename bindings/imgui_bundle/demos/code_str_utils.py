from typing import List
import itertools


def strip_empty_lines_in_list(code_lines: List[str]) -> List[str]:
    code_lines = list(itertools.dropwhile(lambda s: len(s.strip()) == 0, code_lines))
    code_lines = list(reversed(code_lines))
    code_lines = list(itertools.dropwhile(lambda s: len(s.strip()) == 0, code_lines))
    code_lines = list(reversed(code_lines))

    return code_lines


def strip_empty_lines(code_lines: str) -> str:
    lines = code_lines.split("\n")
    lines = strip_empty_lines_in_list(lines)
    return "\n".join(lines)


def count_spaces_at_start_of_line(line: str) -> int:
    nb_spaces_this_line = 0
    for char in line:
        if char == " ":
            nb_spaces_this_line += 1
        else:
            return nb_spaces_this_line
    return nb_spaces_this_line


def remove_trailing_spaces(line: str) -> str:
    r = line
    while r[-1:] == " ":
        r = r[:-1]
    return r


def compute_code_indent_size(code: str) -> int:
    lines = code.split("\n")
    for line in lines:
        if len(line.replace(" ", "")) == 0:
            continue
        return count_spaces_at_start_of_line(line)
    return 0


def unindent_code(code: str, flag_strip_empty_lines: bool = False, is_markdown: bool = False) -> str:
    """unindent the code but keep the inner indentation"""
    indent_size = compute_code_indent_size(code)
    what_to_replace = " " * indent_size

    lines = code.split("\n")

    processed_lines = []
    for line in lines:
        if line.startswith(what_to_replace):
            processed_line = line[indent_size:]
        else:
            processed_line = line
        if is_markdown:
            processed_lines.append(processed_line + " ")
        else:
            processed_lines.append(remove_trailing_spaces(processed_line))

    r = "\n".join(processed_lines)

    if flag_strip_empty_lines:
        r = strip_empty_lines(r)

    return r
