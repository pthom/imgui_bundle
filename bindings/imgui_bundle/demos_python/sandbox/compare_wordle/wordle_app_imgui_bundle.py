"""Wordle game - GUI with Dear ImGui Bundle"""
import wordle  # type: ignore
from imgui_bundle import imgui, ImVec2, hello_imgui


COLORS = {
    wordle.LetterState.EMPTY:   (0.25, 0.25, 0.28, 1.0),
    wordle.LetterState.ABSENT:  (0.47, 0.49, 0.49, 1.0),
    wordle.LetterState.PRESENT: (0.79, 0.71, 0.35, 1.0),
    wordle.LetterState.CORRECT: (0.42, 0.67, 0.39, 1.0)
}


def colored_button(label: str, letter_state: wordle.LetterState, size: ImVec2) -> bool:
    """Button with Wordle-colored background."""
    color = COLORS[letter_state]
    imgui.push_style_color(imgui.Col_.button.value, color)
    imgui.push_style_color(imgui.Col_.button_hovered.value, color)
    imgui.push_style_color(imgui.Col_.button_active.value, color)
    pressed = imgui.button(label, size)
    imgui.pop_style_color(3)
    return pressed


# Horizontal layout helper that centers its contents by putting springs on either side.
def begin_horizontal_centered(str_id: str):
    imgui.begin_horizontal(str_id, ImVec2(imgui.get_content_region_avail().x, 0), 0.5)
    imgui.spring()


def end_horizontal_centered():
    imgui.spring()
    imgui.end_horizontal()


def gui(game_state: wordle.GameState):
    em = imgui.get_font_size()
    imgui.get_style().item_spacing = ImVec2(em * 0.2, em * 0.2)
    tile_size = ImVec2(int(em * 1.7), int(em * 1.7))
    key_size = ImVec2(int(em * 1.5), int(em * 1.8))
    wide_key_size = ImVec2(int(em * 2.8), int(key_size.y))

    # Handle Physical keyboard inputs
    if not game_state.is_over:
        for c in "abcdefghijklmnopqrstuvwxyz":
            if imgui.is_key_pressed(getattr(imgui.Key, c)) and len(game_state.current_input) < 5:
                game_state.append_letter(c)
        if imgui.is_key_pressed(imgui.Key.backspace) and game_state.current_input:
            game_state.remove_last_letter()
        if imgui.is_key_pressed(imgui.Key.enter):
            game_state.submit_guess()

    # -- Grid (6 rows x 5 tiles) --
    for row in range(6):
        imgui.push_id(row)
        begin_horizontal_centered("r")
        for col in range(5):
            imgui.push_id(col)
            if row < len(game_state.guesses):
                key_letter = game_state.guesses[row][col].upper()
                letter_state = game_state.evaluations[row][col]
            elif row == len(game_state.guesses) and col < len(game_state.current_input):
                key_letter = game_state.current_input[col].upper()
                letter_state = wordle.LetterState.EMPTY
            else:
                key_letter = " "
                letter_state = wordle.LetterState.EMPTY
            colored_button(key_letter, letter_state, tile_size)
            imgui.pop_id()
        end_horizontal_centered()
        imgui.pop_id()

    imgui.text(game_state.message or " ")

    # -- On-screen keyboard --
    keys_states = game_state.keyboard_letter_states()
    for i, row_keys in enumerate(wordle.KEYBOARD_ROWS):
        begin_horizontal_centered(str(i))
        if i == 2:
            if imgui.button("Enter", wide_key_size):
                game_state.submit_guess()
        for key_letter in row_keys:
            imgui.push_id(key_letter)
            if colored_button(key_letter.upper(), keys_states.get(key_letter, wordle.LetterState.EMPTY), key_size):
                if not game_state.is_over and len(game_state.current_input) < 5:
                    game_state.append_letter(key_letter)
            imgui.pop_id()
        if i == 2:
            if imgui.button("Del", wide_key_size):
                if not game_state.is_over and game_state.current_input:
                    game_state.remove_last_letter()
        end_horizontal_centered()

    # New game button (shown when game is over)
    if game_state.is_over and imgui.button("New Game"):
        game_state.reset()


if __name__ == "__main__":
    game_state = wordle.GameState()
    params = hello_imgui.RunnerParams()
    params.callbacks.show_gui = lambda : gui(game_state)
    params.app_window_params.window_geometry.size = (440, 500)
    def load_bigger_font():
        hello_imgui.load_font("fonts/Roboto/Roboto-Bold.ttf", 24)
    params.callbacks.load_additional_fonts = load_bigger_font
    hello_imgui.run(params)
