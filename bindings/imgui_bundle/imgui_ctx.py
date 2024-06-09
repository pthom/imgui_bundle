"""
imgui_ctx provide context managers to simplify the use of functions pairs like

    1. `imgui.begin()` and `imgui.end()`
        can be replaced by:  `with imgui_ctx.begin() as window:`

    2. `imgui.begin_child()` and `imgui.end_child()`
        can be replaced by:  `with imgui_ctx.begin_child() as child:`

    3. `imgui.begin_menu_bar()` and `imgui.end_menu_bar()`
        can be replaced by:  `with imgui_ctx.begin_menu_bar() as menu_bar:`

    etc.
"""


from imgui_bundle import imgui, ImVec2, ImVec4
from types import TracebackType
from typing import Optional, Callable, Any, Type


ChildFlags = int     # see enum imgui.ChildFlags_
WindowFlags = int    # see enum imgui.WindowFlags_
TableFlags = int     # see enum imgui.TableFlags_
TabBarFlags = int    # see enum imgui.TabBarFlags_
TabItemFlags = int   # see enum imgui.TabItemFlags_
DragDropFlags = int  # see enum imgui.DragDropFlags_


OptExceptType = Optional[Type[BaseException]]
OptBaseException = Optional[BaseException]
OptTraceback = Optional[TracebackType]

_EnterCallback = Callable[[], Any]

IM_VEC2_ZERO = ImVec2(0.0, 0.0)


class _BeginEndChild:
    visible: bool
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    _enter_callback: _EnterCallback = None

    def __init__(self,
                 str_id: str,
                 size: ImVec2 = IM_VEC2_ZERO,
                 child_flags: ChildFlags = 0,
                 window_flags: WindowFlags = 0) -> None:
        self._enter_callback = lambda: imgui.begin_child(str_id, size, child_flags, window_flags)

    def __enter__(self) -> "_BeginEndChild":
        self.visible = self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        imgui.end_child()

    def __bool__(self) -> bool:
        return self.visible

    def __repr__(self) -> str:
        return "{}(visible={})".format(
            self.__class__.__name__, self.visible
        )

    def __eq__(self, other) -> bool:
        if other.__class__ is self.__class__:
            return self.visible is other.visible
        return self.visible is other


def begin_child(str_id: str,
                size: ImVec2 = IM_VEC2_ZERO,
                child_flags: ChildFlags = 0,
                window_flags: WindowFlags = 0) -> _BeginEndChild:
    return _BeginEndChild(str_id, size, child_flags, window_flags)


class _BeginEnd:
    expanded: bool
    opened: bool
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    _enter_callback: _EnterCallback = None

    def __init__(self, name: str, p_open: Optional[bool] = None, flags: WindowFlags = 0) -> None:
        self._enter_callback = lambda: imgui.begin(name, p_open, flags)

    def __enter__(self) -> "_BeginEnd":
        self.expanded, self.opened = self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        imgui.end()

    def __bool__(self) -> bool:
        if self.opened is None:
            return self.expanded
        else:
            return self.expanded and self.opened

    def __getitem__(self, item):
        return (self.expanded, self.opened)[item]

    def __iter__(self):
        return iter((self.expanded, self.opened))

    def __repr__(self):
        return "{}(expanded={}, opened={})".format(
            self.__class__.__name__, self.expanded, self.opened
        )

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return (self.expanded, self.opened) == (other.expanded, other.opened)
        return (self.expanded, self.opened) == other


def begin(name: str, p_open: Optional[bool] = None, flags: WindowFlags = 0) -> _BeginEnd:
    r = _BeginEnd(name, p_open, flags)
    return r


class _BeginEndListBox:
    opened: bool
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    _enter_callback: _EnterCallback = None

    def __init__(self, label: str, size: ImVec2 = IM_VEC2_ZERO) -> None:
        self._enter_callback = lambda: imgui.begin_list_box(label, size)

    def __enter__(self) -> "_BeginEndListBox":
        self.opened = self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        if self.opened:  # only call end_list_box if begin_list_box was successful
            imgui.end_list_box()

    def __bool__(self) -> bool:
        return self.opened

    def __repr__(self) -> str:
        return "{}(opened={})".format(
            self.__class__.__name__, self.opened
        )

    def __eq__(self, other) -> bool:
        if other.__class__ is self.__class__:
            return self.opened is other.opened
        return self.opened is other


def begin_list_box(label: str, size: ImVec2 = IM_VEC2_ZERO) -> _BeginEndListBox:
    return _BeginEndListBox(label, size)


class _BeginEndTooltip:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    visible: bool
    _enter_callback: _EnterCallback = None

    def __init__(self) -> None:
        self._enter_callback = lambda: imgui.begin_tooltip()

    def __enter__(self) -> "_BeginEndTooltip":
        self.visible = self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        if self.visible:
            imgui.end_tooltip()

    def __bool__(self) -> bool:
        return self.visible

    def __repr__(self) -> str:
        return "{}(opened={})".format(
            self.__class__.__name__, self.visible
        )

    def __eq__(self, other) -> bool:
        if other.__class__ is self.__class__:
            return self.visible is other.visible
        return self.visible is other


def begin_tooltip() -> _BeginEndTooltip:
    return _BeginEndTooltip()


class _BeginEndMenuMainBar:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    visible: bool
    _enter_callback: _EnterCallback = None

    def __init__(self) -> None:
        self._enter_callback = lambda: imgui.begin_main_menu_bar()

    def __enter__(self) -> "_BeginEndMenuMainBar":
        self.visible = self._enter_callback()
        return self

    def __exit__(self, exc_type: OptExceptType, exc_val: OptBaseException, exc_tb: OptTraceback) -> None:
        if self.visible:
            imgui.end_main_menu_bar()

    def __bool__(self) -> bool:
        return self.visible

    def __repr__(self) -> str:
        return "{}(opened={})".format(
            self.__class__.__name__, self.visible
        )

    def __eq__(self, other) -> bool:
        if other.__class__ is self.__class__:
            return self.visible is other.visible
        return self.visible is other


def begin_main_menu_bar() -> _BeginEndMenuMainBar:
    return _BeginEndMenuMainBar()


class _BeginEndMenuBar:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    visible: bool
    _enter_callback: _EnterCallback = None

    def __init__(self) -> None:
        self._enter_callback = lambda: imgui.begin_menu_bar()

    def __enter__(self) -> "_BeginEndMenuBar":
        self.visible = self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        if self.visible:  # only call end_list_box if begin_tooltip was successful
            imgui.end_menu_bar()

    def __bool__(self) -> bool:
        return self.visible

    def __repr__(self) -> str:
        return "{}(opened={})".format(
            self.__class__.__name__, self.visible
        )

    def __eq__(self, other) -> bool:
        if other.__class__ is self.__class__:
            return self.visible is other.visible
        return self.visible is other


def begin_menu_bar() -> _BeginEndMenuBar:
    return _BeginEndMenuBar()


class _BeginEndMenu:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    visible: bool
    _enter_callback: _EnterCallback = None

    def __init__(self, label: str, enabled: bool = True) -> None:
        self._enter_callback = lambda: imgui.begin_menu(label, enabled)

    def __enter__(self) -> "_BeginEndMenu":
        self.visible = self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        if self.visible:  # only call end_list_box if begin_tooltip was successful
            imgui.end_menu()

    def __bool__(self) -> bool:
        return self.visible

    def __repr__(self) -> str:
        return "{}(opened={})".format(
            self.__class__.__name__, self.visible
        )

    def __eq__(self, other) -> bool:
        if other.__class__ is self.__class__:
            return self.visible is other.visible
        return self.visible is other


def begin_menu(label: str, enabled: bool = True) -> _BeginEndMenu:
    return _BeginEndMenu(label, enabled)


class _BeginEndPopup:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    visible: bool
    _enter_callback: _EnterCallback = None

    def __init__(self, str_id: str, flags: WindowFlags = 0) -> None:
        self._enter_callback = lambda: imgui.begin_popup(str_id, flags)

    def __enter__(self) -> "_BeginEndPopup":
        self.visible = self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        if self.visible:  # only call end_list_box if begin_tooltip was successful
            imgui.end_popup()

    def __bool__(self) -> bool:
        return self.visible

    def __repr__(self) -> str:
        return "{}(opened={})".format(
            self.__class__.__name__, self.visible
        )

    def __eq__(self, other) -> bool:
        if other.__class__ is self.__class__:
            return self.visible is other.visible
        return self.visible is other


def begin_popup(str_id: str, flags: WindowFlags = 0) -> _BeginEndPopup:
    return _BeginEndPopup(str_id, flags)


class _BeginEndPopupModal:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    visible: bool
    _enter_callback: _EnterCallback = None

    def __init__(self, name: str, flags: WindowFlags = 0) -> None:
        self._enter_callback = lambda: imgui.begin_popup_modal(name, None, flags)

    def __enter__(self) -> "_BeginEndPopupModal":
        self.visible, _ = self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        if self.visible:  # only call end_list_box if begin_tooltip was successful
            imgui.end_popup()

    def __bool__(self) -> bool:
        return self.visible

    def __repr__(self) -> str:
        return "{}(opened={})".format(
            self.__class__.__name__, self.visible
        )

    def __eq__(self, other) -> bool:
        if other.__class__ is self.__class__:
            return self.visible is other.visible
        return self.visible is other


def begin_popup_modal(name: str, flags: WindowFlags = 0) -> _BeginEndPopupModal:
    return _BeginEndPopupModal(name, flags)


class _BeginEndTable:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    visible: bool
    _enter_callback: _EnterCallback = None

    def __init__(self,
                 str_id: str,
                 column: int,
                 flags: TableFlags = 0,
                 outer_size: ImVec2 = IM_VEC2_ZERO,
                 inner_width: float = 0.0) -> None:
        self._enter_callback = lambda: imgui.begin_table(str_id, column, flags, outer_size, inner_width)

    def __enter__(self) -> "_BeginEndTable":
        self.visible = self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        if self.visible:  # only call end_list_box if begin_tooltip was successful
            imgui.end_table()

    def __bool__(self) -> bool:
        return self.visible

    def __repr__(self) -> str:
        return "{}(opened={})".format(
            self.__class__.__name__, self.visible
        )

    def __eq__(self, other) -> bool:
        if other.__class__ is self.__class__:
            return self.visible is other.visible
        return self.visible is other


def begin_table(str_id: str,
                column: int,
                flags: TableFlags = 0,
                outer_size: ImVec2 = IM_VEC2_ZERO,
                inner_width: float = 0.0) -> _BeginEndTable:
    return _BeginEndTable(str_id, column, flags, outer_size, inner_width)


class _BeginEndTabBar:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    visible: bool
    _enter_callback: _EnterCallback = None

    def __init__(self, str_id: str, flags: TabBarFlags = 0) -> None:
        self._enter_callback = lambda: imgui.begin_tab_bar(str_id, flags)

    def __enter__(self) -> "_BeginEndTabBar":
        self.visible = self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        if self.visible:  # only call end_list_box if begin_tooltip was successful
            imgui.end_tab_bar()

    def __bool__(self) -> bool:
        return self.visible

    def __repr__(self) -> str:
        return "{}(opened={})".format(
            self.__class__.__name__, self.visible
        )

    def __eq__(self, other) -> bool:
        if other.__class__ is self.__class__:
            return self.visible is other.visible
        return self.visible is other


def begin_tab_bar(str_id: str, flags: TabBarFlags = 0) -> _BeginEndTabBar:
    return _BeginEndTabBar(str_id, flags)


class _BeginEndTabItem:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    visible: bool
    _enter_callback: _EnterCallback = None

    def __init__(self, label: str, flags: TabItemFlags = 0) -> None:
        self._enter_callback = lambda: imgui.begin_tab_item(label, None, flags)

    def __enter__(self) -> "_BeginEndTabItem":
        self.visible, _ = self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        if self.visible:
            imgui.end_tab_item()

    def __bool__(self) -> bool:
        return self.visible

    def __repr__(self) -> str:
        return "{}(opened={})".format(
            self.__class__.__name__, self.visible
        )

    def __eq__(self, other) -> bool:
        if other.__class__ is self.__class__:
            return self.visible is other.visible
        return self.visible is other


def begin_tab_item(label: str, flags: TabItemFlags = 0) -> _BeginEndTabItem:
    return _BeginEndTabItem(label, flags)


class _BeginEndDragDropSource:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    is_dragging: bool
    _enter_callback: _EnterCallback = None

    def __init__(self, flags: DragDropFlags = 0) -> None:
        self._enter_callback = lambda: imgui.begin_drag_drop_source(flags)

    def __enter__(self) -> "_BeginEndDragDropSource":
        self.is_dragging = self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        if self.is_dragging:
            imgui.end_drag_drop_source()

    def __bool__(self) -> bool:
        return self.is_dragging

    def __repr__(self) -> str:
        return "{}(opened={})".format(
            self.__class__.__name__, self.is_dragging
        )

    def __eq__(self, other) -> bool:
        if other.__class__ is self.__class__:
            return self.is_dragging is other.is_dragging
        return self.is_dragging is other


def begin_drag_drop_source(flags: DragDropFlags = 0) -> _BeginEndDragDropSource:
    return _BeginEndDragDropSource(flags)


class _BeginEndDragDropTarget:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    is_receiving: bool
    _enter_callback: _EnterCallback = None

    def __init__(self) -> None:
        self._enter_callback = lambda: imgui.begin_drag_drop_target()

    def __enter__(self) -> "_BeginEndDragDropTarget":
        self.is_receiving = self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        if self.is_receiving:
            imgui.end_drag_drop_target()

    def __bool__(self) -> bool:
        return self.is_receiving

    def __repr__(self) -> str:
        return "{}(opened={})".format(
            self.__class__.__name__, self.is_receiving
        )

    def __eq__(self, other) -> bool:
        if other.__class__ is self.__class__:
            return self.is_receiving is other.is_receiving
        return self.is_receiving is other


def begin_drag_drop_target() -> _BeginEndDragDropTarget:
    return _BeginEndDragDropTarget()


class _BeginEndGroup:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    _enter_callback: _EnterCallback = None

    def __init__(self) -> None:
        self._enter_callback = lambda: imgui.begin_group()

    def __enter__(self) -> "_BeginEndGroup":
        self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        imgui.end_group()

    def __repr__(self) -> str:
        return "{}".format(self.__class__.__name__)


def begin_group() -> _BeginEndGroup:
    return _BeginEndGroup()


class _BeginHorizontal:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    _enter_callback: _EnterCallback = None

    def __init__(self, str_id: str, size: ImVec2 | None = None, align: float = -1.0) -> None:
        if size is None:
            size = ImVec2(0, 0)
        self._enter_callback = lambda: imgui.begin_horizontal(str_id, size, align)

    def __enter__(self) -> "_BeginHorizontal":
        self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        imgui.end_horizontal()

    def __repr__(self) -> str:
        return "{}".format(self.__class__.__name__)


def begin_horizontal(str_id: str, size: ImVec2 | None = None, align: float = -1.0) -> _BeginHorizontal:
    return _BeginHorizontal(str_id, size, align)


class _BeginVertical:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    _enter_callback: _EnterCallback = None

    def __init__(self, str_id: str, size: ImVec2 | None = None, align: float = -1.0) -> None:
        if size is None:
            size = ImVec2(0, 0)
        self._enter_callback = lambda: imgui.begin_vertical(str_id, size, align)

    def __enter__(self) -> "_BeginVertical":
        self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        imgui.end_vertical()

    def __repr__(self) -> str:
        return "{}".format(self.__class__.__name__)


def begin_vertical(str_id: str, size: ImVec2 | None = None, align: float = -1.0) -> _BeginVertical:
    return _BeginVertical(str_id, size, align)


class _WithTreeNode:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    visible: bool
    _enter_callback: _EnterCallback = None

    def __init__(self, label: str) -> None:
        self._enter_callback = lambda: imgui.tree_node(label)

    def __enter__(self) -> "_WithTreeNode":
        self.visible = self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        if self.visible:
            imgui.tree_pop()

    def __bool__(self) -> bool:
        return self.visible

    def __repr__(self) -> str:
        return "{}(opened={})".format(
            self.__class__.__name__, self.visible
        )

    def __eq__(self, other) -> bool:
        if other.__class__ is self.__class__:
            return self.visible is other.visible
        return self.visible is other


def tree_node(label: str) -> _WithTreeNode:
    return _WithTreeNode(label)


class _WithPushID:
    _enter_callback: _EnterCallback = None

    def __init__(self, str_id: str) -> None:
        self._enter_callback = lambda: imgui.push_id(str_id)

    def __enter__(self) -> "_WithPushID":
        self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        imgui.pop_id()

    def __repr__(self) -> str:
        return self.__class__.__name__


def push_id(str_id: str) -> _WithPushID:
    return _WithPushID(str_id)


def push_obj_id(obj: Any) -> _WithPushID:
    return _WithPushID(str(id(obj)))


class _WithPushFont:
    _enter_callback: _EnterCallback = None

    def __init__(self, font: imgui.ImFont) -> None:
        self._enter_callback = lambda: imgui.push_font(font)

    def __enter__(self) -> "_WithPushFont":
        self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        imgui.pop_font()

    def __repr__(self) -> str:
        return self.__class__.__name__


def push_font(font: imgui.ImFont) -> _WithPushFont:
    return _WithPushFont(font)


class _WithPushStyleColor:
    _enter_callback: _EnterCallback = None

    def __init__(self, idx: int, col: ImVec4) -> None:
        self._enter_callback = lambda: imgui.push_style_color(idx, col)

    def __enter__(self) -> "_WithPushStyleColor":
        self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        imgui.pop_style_color()

    def __repr__(self) -> str:
        return self.__class__.__name__


def push_style_color(idx: int, col: ImVec4) -> _WithPushStyleColor:
    return _WithPushStyleColor(idx, col)


class _WithPushStyleVar:
    _enter_callback: _EnterCallback = None

    def __init__(self, idx: int, val: Any) -> None:
        self._enter_callback = lambda: imgui.push_style_var(idx, val)

    def __enter__(self) -> "_WithPushStyleVar":
        self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        imgui.pop_style_var()

    def __repr__(self) -> str:
        return self.__class__.__name__


def push_style_var(idx: int, val: Any) -> _WithPushStyleVar:
    return _WithPushStyleVar(idx, val)


class _WithPushItemWidth:
    _enter_callback: _EnterCallback = None

    def __init__(self, item_width: float) -> None:
        self._enter_callback = lambda: imgui.push_item_width(item_width)

    def __enter__(self) -> "_WithPushItemWidth":
        self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        imgui.pop_item_width()

    def __repr__(self) -> str:
        return self.__class__.__name__


def push_item_width(item_width: float) -> _WithPushItemWidth:
    return _WithPushItemWidth(item_width)


class _WithPushTextWrapPos:
    _enter_callback: _EnterCallback = None

    def __init__(self, wrap_pos_x: float = 0.0) -> None:
        self._enter_callback = lambda: imgui.push_text_wrap_pos(wrap_pos_x)

    def __enter__(self) -> "_WithPushTextWrapPos":
        self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        imgui.pop_text_wrap_pos()

    def __repr__(self) -> str:
        return self.__class__.__name__


def push_text_wrap_pos(wrap_pos_x: float = 0.0) -> _WithPushTextWrapPos:
    return _WithPushTextWrapPos(wrap_pos_x)


class _WithPushButtonRepeat:
    _enter_callback: _EnterCallback = None

    def __init__(self, repeat: bool = True) -> None:
        self._enter_callback = lambda: imgui.push_button_repeat(repeat)

    def __enter__(self) -> "_WithPushButtonRepeat":
        self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        imgui.pop_button_repeat()

    def __repr__(self) -> str:
        return self.__class__.__name__


def push_button_repeat(repeat: bool = True) -> _WithPushButtonRepeat:
    return _WithPushButtonRepeat(repeat)


class _WithPushClipRect:
    _enter_callback: _EnterCallback = None

    def __init__(self, clip_rect_min: ImVec2, clip_rect_max: ImVec2, intersect_with_current_clip_rect: bool) -> None:
        self._enter_callback = lambda: imgui.push_clip_rect(
            clip_rect_min, clip_rect_max, intersect_with_current_clip_rect)

    def __enter__(self) -> "_WithPushClipRect":
        self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        imgui.pop_clip_rect()

    def __repr__(self) -> str:
        return self.__class__.__name__


def push_clip_rect(
        clip_rect_min: ImVec2,
        clip_rect_max: ImVec2,
        intersect_with_current_clip_rect: bool
        ) -> _WithPushClipRect:
    return _WithPushClipRect(clip_rect_min, clip_rect_max, intersect_with_current_clip_rect)


class _WithPushTabStop:
    _enter_callback: _EnterCallback = None

    def __init__(self, tab_stop: bool) -> None:
        self._enter_callback = lambda: imgui.push_tab_stop(tab_stop)

    def __enter__(self) -> "_WithPushTabStop":
        self._enter_callback()
        return self

    def __exit__(self, _exc_type: OptExceptType, _exc_val: OptBaseException, _exc_tb: OptTraceback) -> None:
        imgui.pop_tab_stop()

    def __repr__(self) -> str:
        return self.__class__.__name__


def push_tab_stop(tab_stop: bool) -> _WithPushTabStop:
    return _WithPushTabStop(tab_stop)
