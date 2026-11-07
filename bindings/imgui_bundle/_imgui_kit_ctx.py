"""The context managers of imgui_kit, attached to the native module `imgui_bundle.imgui_kit` when the bundle loads it.

The rule (decided on 2026-11-07): `begin_x()` / `end_x()` are the raw pair, as in C++; the bare name `x` is the
context manager. When C++ has a plain function of the bare name (`help_marker(text)`), the context manager takes
the suffix `_ctx`.
"""

from types import ModuleType
from typing import Any


def install_context_managers(kit: ModuleType) -> None:
    """Adds the context managers to the module `kit` (the native imgui_kit)"""

    class FillRow:
        def __init__(self, str_id: str) -> None:
            self._str_id = str_id
            self.width = 0.0

        def __enter__(self) -> "FillRow":
            self.width = kit.begin_fill_row(self._str_id)
            return self

        def tail(self) -> None:
            kit.fill_row_tail()

        def __exit__(self, *args: Any) -> None:
            kit.end_fill_row()

    class _BlockContext:
        def __init__(self, begin: Any, end: Any) -> None:
            self._begin, self._end = begin, end

        def __enter__(self) -> "_BlockContext":
            self._begin()
            return self

        def __exit__(self, *args: Any) -> None:
            self._end()

    class HelpMarkerContext:
        def __init__(self, str_id: str, width_em: float) -> None:
            self._str_id, self._width_em = str_id, width_em
            self.shown = False

        def __bool__(self) -> bool:
            return self.shown

        def __enter__(self) -> "HelpMarkerContext":
            self.shown = kit.begin_help_marker(self._str_id, self._width_em)
            return self

        def __exit__(self, *args: Any) -> None:
            if self.shown:
                kit.end_help_marker()

    def fill_row(str_id: str) -> FillRow:
        return FillRow(str_id)

    def aligned_group(str_id: str, align_x: float) -> _BlockContext:
        return _BlockContext(lambda: kit.begin_aligned_group(str_id, align_x), kit.end_aligned_group)

    def column(str_id: str) -> _BlockContext:
        return _BlockContext(lambda: kit.begin_column(str_id), kit.end_column)

    def flow(str_id: str) -> _BlockContext:
        return _BlockContext(lambda: kit.begin_flow(str_id), kit.end_flow)

    def help_marker_ctx(str_id: str, width_em: float = 0.0) -> HelpMarkerContext:
        return HelpMarkerContext(str_id, width_em)

    for fn in (fill_row, aligned_group, column, flow, help_marker_ctx):
        setattr(kit, fn.__name__, fn)
