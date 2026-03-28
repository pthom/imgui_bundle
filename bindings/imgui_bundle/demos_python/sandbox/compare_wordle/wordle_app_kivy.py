"""Wordle game - GUI with Kivy"""
import wordle
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

CSS_COLORS = {
    wordle.LetterState.EMPTY:   "#404047",
    wordle.LetterState.ABSENT:  "#787d7d",
    wordle.LetterState.PRESENT: "#c9b559",
    wordle.LetterState.CORRECT: "#6bab63",
}


def color_for(ls: wordle.LetterState):
    return get_color_from_hex(CSS_COLORS[ls])


class WordleApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_state = wordle.GameState()
        self.tile_buttons: list[list[Button]] = []
        self.key_buttons: dict[str, Button] = {}
        self.message_label: Label | None = None
        self.new_game_btn: Button | None = None

    def build(self):
        Window.size = (800, 520)
        Window.clearcolor = get_color_from_hex("#1a1a2e")
        Window.bind(on_key_down=self.on_keyboard)

        root = BoxLayout(orientation="vertical", padding=10, spacing=5)

        # -- Grid --
        for row in range(6):
            row_buttons = []
            h = BoxLayout(orientation="horizontal", spacing=4, size_hint_y=None, height=54)
            for col in range(5):
                btn = Button(
                    text="", font_size=24, bold=True, color=(1, 1, 1, 1),
                    background_normal="", background_color=color_for(wordle.LetterState.EMPTY),
                    size_hint=(None, None), size=(54, 54),
                )
                h.add_widget(btn)
                row_buttons.append(btn)
            root.add_widget(h)
            self.tile_buttons.append(row_buttons)

        # -- Status message --
        self.message_label = Label(
            text=" ", font_size=16, color=(1, 1, 1, 1),
            size_hint_y=None, height=40,
        )
        root.add_widget(self.message_label)

        # -- On-screen keyboard --
        key_h = 36
        for i, row_keys in enumerate(wordle.KEYBOARD_ROWS):
            h = BoxLayout(orientation="horizontal", spacing=2, size_hint_y=None, height=key_h)
            if i == 2:
                btn = Button(
                    text="Enter", font_size=12, bold=True, color=(1, 1, 1, 1),
                    background_normal="", background_color=color_for(wordle.LetterState.EMPTY),
                    size_hint=(1.8, None), height=key_h,
                )
                btn.bind(on_press=lambda _: self.on_enter())
                h.add_widget(btn)
            for ch in row_keys:
                btn = Button(
                    text=ch.upper(), font_size=14, bold=True, color=(1, 1, 1, 1),
                    background_normal="", background_color=color_for(wordle.LetterState.EMPTY),
                    size_hint=(1, None), height=key_h,
                )
                btn.bind(on_press=lambda _, c=ch: self.on_key(c))
                h.add_widget(btn)
                self.key_buttons[ch] = btn
            if i == 2:
                btn = Button(
                    text="Del", font_size=12, bold=True, color=(1, 1, 1, 1),
                    background_normal="", background_color=color_for(wordle.LetterState.EMPTY),
                    size_hint=(1.8, None), height=key_h,
                )
                btn.bind(on_press=lambda _: self.on_delete())
                h.add_widget(btn)
            root.add_widget(h)

        # -- New game button --
        self.new_game_btn = Button(
            text="New Game", font_size=14, color=(1, 1, 1, 1),
            background_normal="", background_color=color_for(wordle.LetterState.EMPTY),
            size_hint=(None, None), size=(120, 40), opacity=0, disabled=True,
        )
        self.new_game_btn.bind(on_press=lambda _: self.on_new_game())
        root.add_widget(self.new_game_btn)

        return root

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        if key == 8:  # backspace
            self.on_delete()
        elif key == 13:  # enter
            self.on_enter()
        elif codepoint and len(codepoint) == 1 and codepoint.isalpha():
            self.on_key(codepoint.lower())

    def on_key(self, ch: str):
        if self.game_state.is_over or len(self.game_state.current_input) >= 5:
            return
        self.game_state.current_input += ch
        self.game_state.message = ""
        self.refresh_ui()

    def on_delete(self):
        if self.game_state.is_over or not self.game_state.current_input:
            return
        self.game_state.current_input = self.game_state.current_input[:-1]
        self.game_state.message = ""
        self.refresh_ui()

    def on_enter(self):
        self.game_state.submit_guess()
        self.refresh_ui()

    def on_new_game(self):
        self.game_state.reset()
        self.refresh_ui()

    def refresh_ui(self):
        # Update grid tiles
        for row in range(6):
            for col in range(5):
                btn = self.tile_buttons[row][col]
                if row < len(self.game_state.guesses):
                    ch = self.game_state.guesses[row][col].upper()
                    ls = self.game_state.evaluations[row][col]
                elif row == len(self.game_state.guesses) and col < len(self.game_state.current_input):
                    ch = self.game_state.current_input[col].upper()
                    ls = wordle.LetterState.EMPTY
                else:
                    ch = ""
                    ls = wordle.LetterState.EMPTY
                btn.text = ch
                btn.background_color = color_for(ls)

        # Update keyboard
        kb = self.game_state.keyboard_letter_states()
        for ch, btn in self.key_buttons.items():
            ls = kb.get(ch, wordle.LetterState.EMPTY)
            btn.background_color = color_for(ls)

        # Message
        self.message_label.text = self.game_state.message or " "

        # New game button
        visible = self.game_state.is_over
        self.new_game_btn.opacity = 1 if visible else 0
        self.new_game_btn.disabled = not visible


if __name__ == "__main__":
    WordleApp().run()
