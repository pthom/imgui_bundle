"""Wordle game - GUI with NiceGUI"""
import wordle  # type: ignore
from nicegui import ui

CSS_COLORS = {
    wordle.LetterState.EMPTY:   "#404047",
    wordle.LetterState.ABSENT:  "#787d7d",
    wordle.LetterState.PRESENT: "#c9b559",
    wordle.LetterState.CORRECT: "#6bab63",
}


game_state = wordle.GameState()

# References to UI elements that need updating
tile_buttons: list[list[ui.button]] = []
key_buttons: dict[str, ui.button] = {}
message_label: ui.label
new_game_btn: ui.button


def refresh_ui():
    """Update all UI elements to reflect current game state."""
    # Update grid tiles
    for row in range(6):
        for col in range(5):
            btn = tile_buttons[row][col]
            if row < len(game_state.guesses):
                ch = game_state.guesses[row][col].upper()
                ls = game_state.evaluations[row][col]
            elif row == len(game_state.guesses) and col < len(game_state.current_input):
                ch = game_state.current_input[col].upper()
                ls = wordle.LetterState.EMPTY
            else:
                ch = ""
                ls = wordle.LetterState.EMPTY
            btn.text = ch
            btn.style(f"background-color: {CSS_COLORS[ls]} !important")

    # Update keyboard key colors
    kb = game_state.keyboard_letter_states()
    for ch, btn in key_buttons.items():
        ls = kb.get(ch, wordle.LetterState.EMPTY)
        btn.style(f"background-color: {CSS_COLORS[ls]} !important")

    # Update message
    message_label.text = game_state.message or "\u00a0"

    # Show/hide new game button
    new_game_btn.set_visibility(game_state.is_over)


def on_key(ch: str):
    if game_state.is_over or len(game_state.current_input) >= 5:
        return
    game_state.append_letter(ch)
    refresh_ui()


def on_delete():
    if game_state.is_over or not game_state.current_input:
        return
    game_state.remove_last_letter()
    refresh_ui()


def on_enter():
    game_state.submit_guess()
    refresh_ui()


def on_new_game():
    game_state.reset()
    refresh_ui()


def on_keyboard_event(e):
    """Handle physical keyboard input."""
    if e.action.keydown and not e.action.repeat:
        name = e.key.name
        if name == "Backspace":
            on_delete()
        elif name == "Enter":
            on_enter()
        elif len(name) == 1 and name.isalpha():
            on_key(name.lower())


# ── Build UI ──────────────────────────────────────────────────────────────

tile_style = "width: 58px; height: 58px; font-size: 24px; font-weight: bold; color: white;"
key_style = "min-width: 36px; height: 46px; font-size: 14px; font-weight: bold; color: white;"
wide_key_style = "min-width: 62px; height: 46px; font-size: 12px; font-weight: bold; color: white;"

ui.keyboard(on_key=on_keyboard_event)

with ui.column().classes("items-center w-full gap-1 mt-4"):
    # Grid
    for _row in range(6):
        row_buttons = []
        with ui.row().classes("gap-1"):
            for _col in range(5):
                btn = ui.button("", on_click=lambda: None).style(
                    f"{tile_style} background-color: {CSS_COLORS[wordle.LetterState.EMPTY]} !important"
                )
                row_buttons.append(btn)
        tile_buttons.append(row_buttons)

    # Status message
    message_label = ui.label("\u00a0").classes("text-lg text-white mt-2")

    # On-screen keyboard
    for i, row_keys in enumerate(wordle.KEYBOARD_ROWS):
        with ui.row().classes("gap-1 mt-1"):
            if i == 2:
                ui.button("Enter", on_click=on_enter).style(
                    f"{wide_key_style} background-color: {CSS_COLORS[wordle.LetterState.EMPTY]} !important"
                )
            for ch in row_keys:
                btn = ui.button(ch.upper(), on_click=lambda c=ch: on_key(c)).style(
                    f"{key_style} background-color: {CSS_COLORS[wordle.LetterState.EMPTY]} !important"
                )
                key_buttons[ch] = btn
            if i == 2:
                ui.button("Del", on_click=on_delete).style(
                    f"{wide_key_style} background-color: {CSS_COLORS[wordle.LetterState.EMPTY]} !important"
                )

    # New game button (initially hidden)
    new_game_btn = ui.button("New Game", on_click=on_new_game).classes("mt-4")
    new_game_btn.set_visibility(False)


ui.dark_mode(True)
ui.run(title="Wordle", port=8080)
