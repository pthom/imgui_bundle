"""rich_md's documents from Python: the renders of a document share their headings (a repeated title is numbered in the
document, a section of widgets gets its slug from document_heading()), and rich_md.document() ends the document when
its block raises. A document that asks for folds: document_heading() returns False when its section is folded."""

from imgui_bundle import imgui, rich_md
from imgui_bundle.immapp import testing


def test_rich_md_document() -> None:
    slugs: dict[str, list[str]] = {}
    raised: list[str] = []

    def gui() -> None:
        with rich_md.document("doc", (0, 300)):
            rich_md.render("## Intro\n\n## Notes\n\nSome text.")
            slugs["first"] = [h.slug for h in rich_md.last_render_headings()]
            rich_md.document_heading(2, "A section of widgets")
            slugs["widgets"] = [h.slug for h in rich_md.last_render_headings()]
            imgui.button("A widget")
            rich_md.render("## Notes\n\nThe second section named Notes.")
            slugs["second"] = [h.slug for h in rich_md.last_render_headings()]
        try:
            with rich_md.document("failing", (0, 100)):
                rich_md.render("## Before the error")
                raise RuntimeError("in the document")
        except RuntimeError as e:
            raised.append(str(e))
        rich_md.render_document("one call", "## One\n\n## Two\n", (0, 100))

    def test_fn(ctx: imgui.test_engine.TestContext) -> None:
        ctx.yield_(3)

    testing.run(gui, test_fn, with_markdown=True, window_size=(600, 800))

    assert slugs["first"] == ["intro", "notes"], slugs
    assert slugs["widgets"] == ["a-section-of-widgets"], slugs
    assert slugs["second"] == ["notes-1"], slugs  # numbered in the document, not in its render
    assert raised and raised[-1] == "in the document", raised  # the next document of the frame still works


def test_rich_md_document_folds() -> None:
    phase = ["open"]  # set by the test: "open", "folding", "folded", "unfolding", "unfolded"
    request: list[bool] = []  # fold_all_headings(folded), asked in the next frame
    shown: list[tuple[str, bool]] = []  # per frame: the phase, what document_heading() returned

    def gui() -> None:
        options = rich_md.DocumentOptions()
        options.foldable_headings = True
        with rich_md.document("doc", (0, 300), options):
            rich_md.render("## Intro\n\nSome text.")
            visible = rich_md.document_heading(2, "A section of widgets")
            shown.append((phase[0], visible))
            if visible:
                imgui.button("A widget")
            if request:
                rich_md.fold_all_headings(request.pop())

    def test_fn(ctx: imgui.test_engine.TestContext) -> None:
        ctx.yield_(3)
        phase[0] = "folding"
        request.append(True)
        ctx.yield_(2)
        phase[0] = "folded"
        ctx.yield_(2)
        phase[0] = "unfolding"
        request.append(False)
        ctx.yield_(2)
        phase[0] = "unfolded"
        ctx.yield_(2)

    testing.run(gui, test_fn, with_markdown=True, window_size=(600, 800))

    assert all(v for p, v in shown if p == "open"), shown
    assert any(p == "folded" for p, _ in shown) and not any(v for p, v in shown if p == "folded"), shown
    assert any(p == "unfolded" for p, _ in shown) and all(v for p, v in shown if p == "unfolded"), shown
