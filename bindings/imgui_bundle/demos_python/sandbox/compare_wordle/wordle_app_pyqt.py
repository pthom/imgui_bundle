"""Wordle game - GUI with PyQt6"""
import sys
import wordle
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QSizePolicy,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QKeyEvent

CSS_COLORS = {
    wordle.LetterState.EMPTY:   "#404047",
    wordle.LetterState.ABSENT:  "#787d7d",
    wordle.LetterState.PRESENT: "#c9b559",
    wordle.LetterState.CORRECT: "#6bab63",
}

TILE_STYLE = "font-size: 24px; font-weight: bold; color: white; border: none; border-radius: 4px;"
KEY_STYLE = "font-size: 14px; font-weight: bold; color: white; border: none; border-radius: 4px; padding: 0px; margin: 0px;"


class WordleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.game_state = wordle.GameState()
        self.tile_buttons: list[list[QPushButton]] = []
        self.key_buttons: dict[str, QPushButton] = {}

        self.setWindowTitle("Wordle")
        self.setStyleSheet("background-color: #1a1a2e;")

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # -- Grid --
        grid_widget = QWidget()
        grid_widget.setFixedSize(5 * 58 + 4 * 6, 6 * 58 + 5 * 8)
        grid = QGridLayout(grid_widget)
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(8)
        grid.setContentsMargins(0, 0, 0, 0)
        for row in range(6):
            row_buttons = []
            for col in range(5):
                btn = QPushButton("")
                btn.setFixedSize(QSize(58, 58))
                btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                grid.addWidget(btn, row, col)
                row_buttons.append(btn)
            self.tile_buttons.append(row_buttons)
        root.addWidget(grid_widget, alignment=Qt.AlignmentFlag.AlignHCenter)

        # -- Status message --
        self.message_label = QLabel("\u00a0")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("color: white; font-size: 16px; margin: 8px;")
        root.addWidget(self.message_label)

        # -- On-screen keyboard --
        for i, row_keys in enumerate(wordle.KEYBOARD_ROWS):
            h = QHBoxLayout()
            h.setSpacing(2)
            h.setContentsMargins(0, 0, 0, 0)
            h.addStretch()
            if i == 2:
                btn = QPushButton("Enter")
                btn.setFixedSize(QSize(72, 36))
                btn.setStyleSheet(f"{KEY_STYLE} background-color: {CSS_COLORS[wordle.LetterState.EMPTY]};")
                btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                btn.clicked.connect(self.on_enter)
                h.addWidget(btn, alignment=Qt.AlignmentFlag.AlignVCenter)
            for ch in row_keys:
                btn = QPushButton(ch.upper())
                btn.setFixedSize(QSize(36, 36))
                btn.setStyleSheet(f"{KEY_STYLE} background-color: {CSS_COLORS[wordle.LetterState.EMPTY]};")
                btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                btn.clicked.connect(lambda _, c=ch: self.on_key(c))
                h.addWidget(btn, alignment=Qt.AlignmentFlag.AlignVCenter)
                self.key_buttons[ch] = btn
            if i == 2:
                btn = QPushButton("Del")
                btn.setFixedSize(QSize(72, 36))
                btn.setStyleSheet(f"{KEY_STYLE} background-color: {CSS_COLORS[wordle.LetterState.EMPTY]};")
                btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                btn.clicked.connect(self.on_delete)
                h.addWidget(btn, alignment=Qt.AlignmentFlag.AlignVCenter)
            h.addStretch()
            root.addLayout(h)

        # -- New game button --
        self.new_game_btn = QPushButton("New Game")
        self.new_game_btn.setFixedSize(QSize(120, 36))
        self.new_game_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.new_game_btn.clicked.connect(self.on_new_game)
        self.new_game_btn.setStyleSheet("color: white; font-size: 14px; margin-top: 8px;")
        self.new_game_btn.hide()
        root.addWidget(self.new_game_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.refresh_ui()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.text()
        if event.key() == Qt.Key.Key_Backspace:
            self.on_delete()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.on_enter()
        elif len(key) == 1 and key.isalpha():
            self.on_key(key.lower())

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
                btn.setText(ch)
                btn.setStyleSheet(f"{TILE_STYLE} background-color: {CSS_COLORS[ls]};")

        # Update keyboard
        kb = self.game_state.keyboard_letter_states()
        for ch, btn in self.key_buttons.items():
            ls = kb.get(ch, wordle.LetterState.EMPTY)
            btn.setStyleSheet(f"{KEY_STYLE} background-color: {CSS_COLORS[ls]};")

        # Message
        self.message_label.setText(self.game_state.message or "\u00a0")

        # New game button
        self.new_game_btn.setVisible(self.game_state.is_over)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WordleWindow()
    window.resize(440, 520)
    window.show()
    sys.exit(app.exec())
