"""The values of c found by the users of the Julia map: shared, listed, voted on

They live on a server: a Cloudflare Worker with a database (cloudflare/julia_points in the repository of Dear ImGui
Bundle). Its requests run in the background (immapp.start_download): the GUI looks at their answers at each frame.

The admin mode (the curation): with the server's admin token in JULIA_POINTS_ADMIN (an environment variable on the
desktop; in the browser, localStorage.setItem("JULIA_POINTS_ADMIN", token) in the console), the list also shows the
hidden points, and a button hides or shows each point. Users have no token: they see nothing of it.
"""
import json
import os
import uuid
from dataclasses import dataclass
from typing import Any, Callable

from imgui_bundle import imgui, immapp, hello_imgui, em_size, icons_fontawesome_4 as fa, __bundle_pyodide__

# The server. For local tests (just demo_julia_points_dev): http://localhost:8787/julia_points
POINTS_API = "https://imgui-bundle-api.pthomet.workers.dev/julia_points"
TAB_EM = 26.0  # the width of the tab "Found by users", in em
MAX_NAME, MAX_STORY, MAX_AUTHOR = 40, 300, 40  # the server's limits, in characters
RED = imgui.ImVec4(1.0, 0.4, 0.4, 1.0)


@dataclass
class Point:
    id: int
    name: str
    c: complex
    view_width: float  # the width of the map's view when it was shared
    max_iter: int  # the iterations when it was shared
    story: str
    author: str
    created: str  # ISO 8601: the date, then the time
    votes: int
    voted_by_me: bool
    status: str  # "shown", or "hidden" (the admin sees those too)


def point_from_json(d: dict[str, Any]) -> Point:
    return Point(d["id"], d["name"], complex(d["c_re"], d["c_im"]), d["view_width"], d["max_iter"], d["story"],
                 d["author"], d["created"], d["votes"], d["voted_by_me"], d["status"])


def error_text(download: immapp.Download) -> str:
    """The server's explanation ({"error": ...}), else the failure of the request"""
    try:
        return str(json.loads(download.data)["error"])
    except (ValueError, KeyError, TypeError):
        pass
    if "CERTIFICATE_VERIFY_FAILED" in download.error:  # Python from python.org on macOS, before its certificates
        return download.error + " (run the Install Certificates.command of your Python)"
    return download.error


def load_voter_id() -> str:
    """A random id that tells this user's votes apart, kept across runs: in the browser's storage, or in the ini file
    of the app"""
    key = "julia_points_voter"
    if __bundle_pyodide__:
        import js  # type: ignore[import-not-found]
        voter = js.localStorage.getItem(key) or ""
        if not voter:
            voter = str(uuid.uuid4())
            js.localStorage.setItem(key, voter)
    else:
        voter = hello_imgui.load_user_pref(key)
        if not voter:
            voter = str(uuid.uuid4())
            hello_imgui.save_user_pref(key, voter)
    return voter


def load_admin_token() -> str:
    """The server's admin token, on the admin's machine only (see the top of this file)"""
    if __bundle_pyodide__:
        import js  # type: ignore[import-not-found]
        return str(js.localStorage.getItem("JULIA_POINTS_ADMIN") or "")
    return os.environ.get("JULIA_POINTS_ADMIN", "")


class Community:
    """The tab "Found by users": the list of the points, their votes, and the form that shares the current c"""

    def __init__(self) -> None:
        self.voter = ""  # loaded at the first display (the ini file is known once the app runs)
        self.admin_token = ""
        self.points: list[Point] = []
        self.loading: immapp.Download | None = None
        self.error = ""  # the last failure of a request (load, vote, admin), shown above the list
        self.selected_id: int | None = None
        self.filter = imgui.TextFilter()
        self.voting: dict[int, tuple[immapp.Download, bool]] = {}  # point id -> the request, the vote it sends
        self.curating: dict[int, tuple[immapp.Download, str]] = {}  # point id -> the request, the status it sends
        self.sharing = False  # the form is shown
        self.name, self.story, self.author = "", "", ""
        self.sending: immapp.Download | None = None
        self.send_error = ""

    def admin_headers(self) -> dict[str, str] | None:
        return {"Authorization": f"Bearer {self.admin_token}"} if self.admin_token else None

    def load(self) -> None:
        self.loading = immapp.start_download(f"{POINTS_API}?voter={self.voter}", headers=self.admin_headers())
        self.error = ""

    def poll(self) -> None:
        """At each frame: the answers that arrived"""
        if self.loading is not None and self.loading.done:
            if self.loading.error:
                self.error = f"Could not load the points found by users: {error_text(self.loading)}"
            else:
                self.points = [point_from_json(d) for d in json.loads(self.loading.data)]
            self.loading = None
        for point_id, (download, vote) in list(self.voting.items()):
            if download.done:
                del self.voting[point_id]
                point = next((p for p in self.points if p.id == point_id), None)
                if download.error:
                    self.error = f"The vote failed: {error_text(download)}"
                elif point is not None:
                    point.votes, point.voted_by_me = json.loads(download.data)["votes"], vote
        for point_id, (download, status) in list(self.curating.items()):
            if download.done:
                del self.curating[point_id]
                point = next((p for p in self.points if p.id == point_id), None)
                if download.error:
                    self.error = f"Admin: {error_text(download)}"
                elif point is not None:
                    point.status = status
        if self.sending is not None and self.sending.done:
            if self.sending.error:
                self.send_error = error_text(self.sending)
            else:
                self.sharing, self.name, self.story = False, "", ""
                self.selected_id = json.loads(self.sending.data)["id"]
                self.load()
            self.sending = None

    def gui(self, c: complex, view_width: float, max_iter: int, width: float, go_to: Callable[[Point], None]) -> None:
        """The tab, width wide. A click on a point calls go_to(point)"""
        if not self.voter:
            self.voter, self.admin_token = load_voter_id(), load_admin_token()
            self.load()
        self.poll()
        if self.sharing:
            self.share_form(c, view_width, max_iter, width)
            return
        if imgui.button("Share the current c..."):
            self.sharing, self.send_error = True, ""
        imgui.same_line()
        imgui.begin_disabled(self.loading is not None)
        if imgui.button("Reload"):
            self.load()
        imgui.end_disabled()
        if self.loading is not None:
            imgui.same_line()
            imgui.text("Loading...")
        if self.error:
            imgui.push_text_wrap_pos(imgui.get_cursor_pos_x() + width)
            imgui.text_colored(RED, self.error)
            imgui.pop_text_wrap_pos()
        if self.admin_token:
            imgui.text_colored(imgui.ImVec4(1.0, 0.7, 0.2, 1.0), "Admin mode: the hidden points are greyed")
        label = "filter"
        self.filter.draw(label, width - imgui.calc_text_size(label).x - imgui.get_style().item_inner_spacing.x)
        self.table(width, go_to)
        self.details(width)

    def sorted_points(self) -> list[Point]:
        """In the order chosen by a click on a header of the table"""
        specs = imgui.table_get_sort_specs()
        if specs is None or specs.specs_count == 0:
            return self.points
        spec = specs.get_specs(0)
        attribute = ("name", "votes", "author", "created", "status")[spec.column_index]
        return sorted(self.points, key=lambda p: getattr(p, attribute),
                      reverse=spec.get_sort_direction() == imgui.SortDirection.descending)

    def table(self, width: float, go_to: Callable[[Point], None]) -> None:
        flags = (imgui.TableFlags_.sortable | imgui.TableFlags_.scroll_y | imgui.TableFlags_.row_bg
                 | imgui.TableFlags_.borders_inner_h)
        height = 12 * imgui.get_text_line_height_with_spacing()
        admin = bool(self.admin_token)
        if not imgui.begin_table("##points found by users", 5 if admin else 4, flags, imgui.ImVec2(width, height)):
            return
        imgui.table_setup_scroll_freeze(0, 1)  # the headers stay in view
        imgui.table_setup_column("Name", imgui.TableColumnFlags_.width_stretch)
        imgui.table_setup_column("Votes", imgui.TableColumnFlags_.width_fixed | imgui.TableColumnFlags_.default_sort
                                 | imgui.TableColumnFlags_.prefer_sort_descending)
        imgui.table_setup_column("Author", imgui.TableColumnFlags_.width_fixed, em_size(6))
        imgui.table_setup_column("Date", imgui.TableColumnFlags_.width_fixed)
        if admin:
            imgui.table_setup_column("Status", imgui.TableColumnFlags_.width_fixed)
        imgui.table_headers_row()
        for point in self.sorted_points():
            if not self.filter.pass_filter(f"{point.name} {point.author} {point.story}"):
                continue
            hidden = point.status == "hidden"
            if hidden:
                imgui.push_style_color(imgui.Col_.text, imgui.get_style_color_vec4(imgui.Col_.text_disabled))
            imgui.table_next_row()
            imgui.table_next_column()
            row_flags = imgui.SelectableFlags_.span_all_columns | imgui.SelectableFlags_.allow_overlap  # + vote button
            if imgui.selectable(f"{point.name}##{point.id}", point.id == self.selected_id, row_flags)[0]:
                self.selected_id = point.id
                go_to(point)
            imgui.table_next_column()
            self.vote_button(point)
            imgui.table_next_column()
            imgui.text(point.author)
            imgui.table_next_column()
            imgui.text(point.created[:10])
            if admin:
                imgui.table_next_column()
                self.status_button(point)
            if hidden:
                imgui.pop_style_color()
        imgui.end_table()

    def status_button(self, point: Point) -> None:
        """For the admin: "Hide" a shown point, "Show" a hidden one"""
        new_status = "shown" if point.status == "hidden" else "hidden"
        imgui.begin_disabled(point.id in self.curating)  # a request is on its way
        if imgui.small_button(f"{'Show' if new_status == 'shown' else 'Hide'}###status {point.id}"):
            url = f"{POINTS_API}/{point.id}/status"
            download = immapp.start_download(url, "POST", {"status": new_status}, headers=self.admin_headers())
            self.curating[point.id] = (download, new_status)
        imgui.end_disabled()

    def vote_button(self, point: Point) -> None:
        """A thumb and the votes: highlighted when this user voted. A click votes, or takes the vote back"""
        imgui.begin_disabled(point.id in self.voting or point.status == "hidden")  # on its way, or no votes when hidden
        if point.voted_by_me:
            imgui.push_style_color(imgui.Col_.button, imgui.get_style_color_vec4(imgui.Col_.button_active))
        if imgui.small_button(f"{fa.ICON_FA_THUMBS_UP} {point.votes}###vote {point.id}"):  # ###: an id without votes
            vote = not point.voted_by_me
            body = {"voter": self.voter, "vote": vote}
            self.voting[point.id] = (immapp.start_download(f"{POINTS_API}/{point.id}/vote", "POST", body), vote)
        if point.voted_by_me:
            imgui.pop_style_color()
        imgui.end_disabled()

    def details(self, width: float) -> None:
        """The selected point: visible text, not a tooltip (a phone has no mouse to hover)"""
        point = next((p for p in self.points if p.id == self.selected_id), None)
        imgui.push_text_wrap_pos(imgui.get_cursor_pos_x() + width)
        if point is None:
            imgui.text_disabled("Click a name: the map flies there.")
        else:
            by = f", by {point.author}" if point.author else ""
            imgui.text(f"{point.name}{by} ({point.created[:10]})")
            imgui.text(f"c = {point.c.real:g} {point.c.imag:+g} i, view width {point.view_width:.2g}, "
                       f"{point.max_iter} iterations")
            if point.story:
                imgui.text(point.story)
        imgui.pop_text_wrap_pos()

    def share_form(self, c: complex, view_width: float, max_iter: int, width: float) -> None:
        imgui.push_text_wrap_pos(imgui.get_cursor_pos_x() + width)
        imgui.text(f"Share c = {c.real:.6g} {c.imag:+.6g} i (view width {view_width:.2g}, {max_iter} iterations) "
                   "with the users of this demo: everyone will see it.")
        imgui.pop_text_wrap_pos()
        imgui.set_next_item_width(width)
        _, name = imgui.input_text_with_hint("##name", "its name (required)", self.name)
        imgui.set_next_item_width(width)
        _, story = imgui.input_text_with_hint("##story", "what to see there (optional)", self.story)
        imgui.set_next_item_width(width)
        _, author = imgui.input_text_with_hint("##author", "your name (optional)", self.author)
        self.name, self.story, self.author = name[:MAX_NAME], story[:MAX_STORY], author[:MAX_AUTHOR]
        imgui.begin_disabled(self.sending is not None or not self.name.strip())
        if imgui.button("Send"):
            body = {"name": self.name, "c_re": c.real, "c_im": c.imag, "view_width": view_width,
                    "max_iter": max_iter, "story": self.story, "author": self.author}
            self.sending, self.send_error = immapp.start_download(POINTS_API, "POST", body), ""
        imgui.end_disabled()
        imgui.same_line()
        if imgui.button("Cancel"):
            self.sharing = False
        if self.sending is not None:
            imgui.same_line()
            imgui.text("Sending...")
        if self.send_error:
            imgui.push_text_wrap_pos(imgui.get_cursor_pos_x() + width)
            imgui.text_colored(RED, self.send_error)
            imgui.pop_text_wrap_pos()
