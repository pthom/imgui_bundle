"""
imgui_node_editor_ctx provide context managers to simplify the use of functions pairs like

    `ed.begin()` and `ed.end()`
        can be replaced by:  `with imgui_node_editor.begin()

    etc.
"""
from imgui_bundle import ImVec2, ImVec4
from imgui_bundle import imgui_node_editor as ed
from types import TracebackType
from typing import Optional, Callable, Any, Type
import logging


OptExceptType = Optional[Type[BaseException]]
OptBaseException = Optional[BaseException]
OptTraceback = Optional[TracebackType]

_EnterCallback = Callable[[], Any]

IM_VEC2_ZERO = ImVec2(0.0, 0.0)
IM_VEC4_ONE = ImVec4(1.0, 1.0, 1.0, 1.0)


class _Begin:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    _enter_callback: _EnterCallback = None

    def __init__(self, editor_id: str, size: ImVec2 = IM_VEC2_ZERO) -> None:
        self._enter_callback = lambda: ed.begin(editor_id, size)

    def __enter__(self) -> "_Begin":
        self._enter_callback()
        return self

    def __exit__(self, exc_type: OptExceptType, exc_val: OptBaseException, exc_tb: OptTraceback) -> None:
        try:
            ed.end()
        finally:
            if exc_type is not None:
                logging.error("Exception occurred in _Begin context", exc_info=(exc_type, exc_val, exc_tb))

    def __repr__(self):
        return self.__class__.__name__


def begin(editor_id: str, size: ImVec2 = IM_VEC2_ZERO) -> _Begin:
    return _Begin(editor_id, size)


class _BeginNode:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    _enter_callback: _EnterCallback = None

    def __init__(self, node_id: ed.NodeId) -> None:
        self._enter_callback = lambda: ed.begin_node(node_id)

    def __enter__(self) -> "_BeginNode":
        self._enter_callback()
        return self

    def __exit__(self, exc_type: OptExceptType, exc_val: OptBaseException, exc_tb: OptTraceback) -> None:
        try:
            ed.end_node()
        finally:
            if exc_type is not None:
                logging.error("Exception occurred in _BeginNode context", exc_info=(exc_type, exc_val, exc_tb))

    def __repr__(self):
        return self.__class__.__name__


def begin_node(node_id: ed.NodeId) -> _BeginNode:
    return _BeginNode(node_id)


class _BeginPin:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    _enter_callback: _EnterCallback = None

    def __init__(self, pin_id: ed.PinId, kind: ed.PinKind) -> None:
        self._enter_callback = lambda: ed.begin_pin(pin_id, kind)

    def __enter__(self) -> "_BeginPin":
        self._enter_callback()
        return self

    def __exit__(self, exc_type: OptExceptType, exc_val: OptBaseException, exc_tb: OptTraceback) -> None:
        try:
            ed.end_pin()
        finally:
            if exc_type is not None:
                logging.error("Exception occurred in _BeginPin context", exc_info=(exc_type, exc_val, exc_tb))

    def __repr__(self):
        return self.__class__.__name__


def begin_pin(pin_id: ed.PinId, kind: ed.PinKind) -> _BeginPin:
    return _BeginPin(pin_id, kind)


class _BeginCreate:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    _enter_callback: _EnterCallback = None

    def __init__(self, color: ImVec4 = IM_VEC4_ONE, thickness: float = 1.0) -> None:
        self._enter_callback = lambda: ed.begin_create(color, thickness)

    def __enter__(self) -> "_BeginCreate":
        self._enter_callback()
        return self

    def __exit__(self, exc_type: OptExceptType, exc_val: OptBaseException, exc_tb: OptTraceback) -> None:
        try:
            ed.end_create()
        finally:
            if exc_type is not None:
                logging.error("Exception occurred in _BeginCreate context", exc_info=(exc_type, exc_val, exc_tb))

    def __repr__(self):
        return self.__class__.__name__


def begin_create(color: ImVec4 = IM_VEC4_ONE, thickness: float = 1.0) -> _BeginCreate:
    return _BeginCreate(color, thickness)


class _BeginDelete:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    _enter_callback: _EnterCallback = None

    def __init__(self) -> None:
        self._enter_callback = lambda: ed.begin_delete()

    def __enter__(self) -> "_BeginDelete":
        self._enter_callback()
        return self

    def __exit__(self, exc_type: OptExceptType, exc_val: OptBaseException, exc_tb: OptTraceback) -> None:
        try:
            ed.end_delete()
        finally:
            if exc_type is not None:
                logging.error("Exception occurred in _BeginDelete context", exc_info=(exc_type, exc_val, exc_tb))

    def __repr__(self):
        return self.__class__.__name__


def begin_delete() -> _BeginDelete:
    return _BeginDelete()


class _BeginGroupHint:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    _enter_callback: _EnterCallback = None

    def __init__(self, node_id: ed.NodeId) -> None:
        self._enter_callback = lambda: ed.begin_group_hint(node_id)

    def __enter__(self) -> "_BeginGroupHint":
        self._enter_callback()
        return self

    def __exit__(self, exc_type: OptExceptType, exc_val: OptBaseException, exc_tb: OptTraceback) -> None:
        try:
            ed.end_group_hint()
        finally:
            if exc_type is not None:
                logging.error("Exception occurred in _BeginGroupHint context", exc_info=(exc_type, exc_val, exc_tb))

    def __repr__(self):
        return self.__class__.__name__


def begin_group_hint(node_id: ed.NodeId) -> _BeginGroupHint:
    return _BeginGroupHint(node_id)


class _BeginShortcut:
    # _enter_callback will be called in __enter__. Captures all __init__ arguments.
    _enter_callback: _EnterCallback = None

    def __init__(self) -> None:
        self._enter_callback = lambda: ed.begin_shortcut()

    def __enter__(self) -> "_BeginShortcut":
        self._enter_callback()
        return self

    def __exit__(self, exc_type: OptExceptType, exc_val: OptBaseException, exc_tb: OptTraceback) -> None:
        try:
            ed.end_shortcut()
        finally:
            if exc_type is not None:
                logging.error("Exception occurred in _BeginShortcut context", exc_info=(exc_type, exc_val, exc_tb))

    def __repr__(self):
        return self.__class__.__name__


def begin_shortcut() -> _BeginShortcut:
    return _BeginShortcut()
