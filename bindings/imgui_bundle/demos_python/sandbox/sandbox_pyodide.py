from imgui_bundle import hello_imgui, imgui
from time import time


def gui(start_time: float):
    elapsed = time() - start_time
    imgui.text(f"Hello, world! {elapsed:.1f} elapsed")
    if elapsed > 5.0:
        hello_imgui.get_runner_params().app_shall_exit = True
    if imgui.button("Exit"):
        hello_imgui.get_runner_params().app_shall_exit = True


def main():
    start_time = time()
    hello_imgui.run(lambda: gui(start_time))


if __name__ == "__main__":
    main()
