"""Wordle game - logic"""
from __future__ import annotations
import random
from enum import IntEnum


# Read WORDS from words/english.txt, one word per line
import os
this_dir = os.path.dirname(__file__)
with open(f"{this_dir}/words/english.txt") as f:
    WORDS = f.read().splitlines()


class LetterState(IntEnum):
    """State of a letter in a guess, used for coloring tiles and keyboard keys."""
    EMPTY = 0     # not yet evaluated
    ABSENT = 1    # letter not in word (gray)
    PRESENT = 2   # letter in word, wrong spot (yellow)
    CORRECT = 3   # letter in correct spot (green)


class GameState:
    """The game state: stores solution and guesses"""
    secret: str
    guesses: list[str]
    evaluations: list[list[LetterState]]
    current_input: str
    message: str

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self.secret = random.choice(WORDS)
        self.guesses = []
        self.evaluations = []
        self.current_input = ""
        self.message = ""

    @property
    def is_won(self) -> bool:
        return bool(self.guesses) and self.guesses[-1] == self.secret

    @property
    def is_over(self) -> bool:
        return self.is_won or len(self.guesses) >= 6

    def submit_guess(self) -> None:
        if self.is_over or len(self.current_input) != 5:
            return
        if self.current_input not in WORDS:
            self.message = "Not in word list"
            return
        self.guesses.append(self.current_input)
        self.evaluations.append(_evaluate(self.current_input, self.secret))
        self.current_input = ""
        if self.is_won:
            self.message = "Well done!"
        elif self.is_over:
            self.message = f"The word was: {self.secret.upper()}"
        else:
            self.message = ""

    def keyboard_letter_states(self) -> dict[str, LetterState]:
        """Best known state per letter: CORRECT > PRESENT > ABSENT."""
        best: dict[str, LetterState] = {}
        for guess, evl in zip(self.guesses, self.evaluations):
            for ch, ls in zip(guess, evl):
                if ch not in best or ls > best[ch]:
                    best[ch] = ls
        return best


def _evaluate(guess: str, secret: str) -> list[LetterState]:
    """Per-letter color evaluation. Handles duplicate letters correctly."""
    result = [LetterState.ABSENT] * 5
    remaining = list(secret)
    for i in range(5):                          # pass 1: exact matches
        if guess[i] == secret[i]:
            result[i] = LetterState.CORRECT
            remaining[i] = ""
    for i in range(5):                          # pass 2: wrong position
        if result[i] == LetterState.ABSENT and guess[i] in remaining:
            result[i] = LetterState.PRESENT
            remaining[remaining.index(guess[i])] = ""
    return result


KEYBOARD_ROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
