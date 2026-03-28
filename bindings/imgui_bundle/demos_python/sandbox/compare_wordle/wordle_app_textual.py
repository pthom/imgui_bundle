"""Wordle game - GUI with Textual (terminal UI)"""
import wordle
from textual.app import App, ComposeResult
from textual.widgets import Button, Label, Static
from textual.containers import Horizontal, Vertical, Center
from textual.css.query import NoMatches

CSS_COLORS = {
    wordle.LetterState.EMPTY:   "#404047",
    wordle.LetterState.ABSENT:  "#787d7d",
    wordle.LetterState.PRESENT: "#c9b559",
    wordle.LetterState.CORRECT: "#6bab63",
}


class WordleApp(App):
    CSS = """
    Screen { align: center middle; background: #1a1a2e; }
    #grid { width: auto; height: auto; }
    .tile-row { width: auto; height: auto; margin: 0 0 1 0; }
    .tile {
        width: 5; height: 1; text-align: center; content-align: center middle;
        margin: 0 1; text-style: bold;
    }
    .kb-row { width: auto; height: auto; align: center middle; }
    .key {
        width: 5; height: 3; text-align: center; content-align: center middle;
        margin: 0; min-width: 5;
    }
    .wide-key { width: 9; }
    #message { width: auto; height: 1; text-align: center; margin: 1 0; color: white; }
    #new-game { margin: 1 0; display: none; }
    """

    def __init__(self):
        super().__init__()
        self.game_state = wordle.GameState()

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical():
                # Grid
                with Vertical(id="grid"):
                    for row in range(6):
                        with Horizontal(classes="tile-row"):
                            for col in range(5):
                                yield Static(" ", classes="tile", id=f"tile-{row}-{col}")

                yield Label("\u00a0", id="message")

                # On-screen keyboard
                for i, row_keys in enumerate(wordle.KEYBOARD_ROWS):
                    with Horizontal(classes="kb-row"):
                        if i == 2:
                            yield Button("Ent", id="key-enter", classes="key wide-key")
                        for ch in row_keys:
                            yield Button(ch.upper(), id=f"key-{ch}", classes="key")
                        if i == 2:
                            yield Button("Del", id="key-del", classes="key wide-key")

                yield Button("New Game", id="new-game")

    def on_key(self, event) -> None:
        if event.key == "backspace":
            self.delete_letter()
        elif event.key == "enter":
            self.submit()
        elif event.character and len(event.character) == 1 and event.character.isalpha():
            self.type_letter(event.character.lower())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if btn_id == "key-enter":
            self.submit()
        elif btn_id == "key-del":
            self.delete_letter()
        elif btn_id == "new-game":
            self.new_game()
        elif btn_id.startswith("key-"):
            self.type_letter(btn_id[4:])

    def type_letter(self, ch: str):
        if self.game_state.is_over or len(self.game_state.current_input) >= 5:
            return
        self.game_state.current_input += ch
        self.game_state.message = ""
        self._refresh_ui()

    def delete_letter(self):
        if self.game_state.is_over or not self.game_state.current_input:
            return
        self.game_state.current_input = self.game_state.current_input[:-1]
        self.game_state.message = ""
        self._refresh_ui()

    def submit(self):
        self.game_state.submit_guess()
        self._refresh_ui()

    def new_game(self):
        self.game_state.reset()
        self._refresh_ui()

    def _refresh_ui(self):
        # Update grid tiles
        for row in range(6):
            for col in range(5):
                tile = self.query_one(f"#tile-{row}-{col}", Static)
                if row < len(self.game_state.guesses):
                    ch = self.game_state.guesses[row][col].upper()
                    ls = self.game_state.evaluations[row][col]
                elif row == len(self.game_state.guesses) and col < len(self.game_state.current_input):
                    ch = self.game_state.current_input[col].upper()
                    ls = wordle.LetterState.EMPTY
                else:
                    ch = " "
                    ls = wordle.LetterState.EMPTY
                tile.update(ch)
                tile.styles.background = CSS_COLORS[ls]

        # Update keyboard
        kb = self.game_state.keyboard_letter_states()
        for ch in "abcdefghijklmnopqrstuvwxyz":
            try:
                btn = self.query_one(f"#key-{ch}", Button)
                ls = kb.get(ch, wordle.LetterState.EMPTY)
                btn.styles.background = CSS_COLORS[ls]
            except NoMatches:
                pass

        # Message
        self.query_one("#message", Label).update(self.game_state.message or "\u00a0")

        # New game button
        new_game = self.query_one("#new-game", Button)
        new_game.styles.display = "block" if self.game_state.is_over else "none"


if __name__ == "__main__":
    WordleApp().run()
