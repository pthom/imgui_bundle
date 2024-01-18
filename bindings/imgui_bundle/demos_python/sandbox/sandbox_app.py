from __future__ import annotations
from imgui_bundle import imgui, immapp, hello_imgui
import threading
import time
import math


SHALL_EXIT = False


def my_thread_proc():
    global SHALL_EXIT
    start_time = time.time()
    counter = 0
    while not SHALL_EXIT:
        counter += 1
    total_time = time.time() - start_time
    count_per_second = counter / total_time
    log_count_per_second = math.log10(count_per_second)
    print(f"my_thread_proc: count_per_second={count_per_second} log_count_per_second={log_count_per_second} total_time={total_time} counter={counter}")


def gui():
    imgui.text("Hello world")
    imgui.text(f"FPS = {hello_imgui.frame_rate()}")


def main():
    start_time = time.time()
    global SHALL_EXIT

    my_thread = threading.Thread(target=my_thread_proc)

    def thread_start_post_init():
        my_thread.start()

    runner_params = hello_imgui.RunnerParams()
    runner_params.callbacks.show_gui = gui
    runner_params.callbacks.post_init = thread_start_post_init
    runner_params.fps_idling.enable_idling = False
    runner_params.use_imgui_test_engine = True

    immapp.run(runner_params)
    SHALL_EXIT = True
    my_thread.join()
    print("App total time=", time.time() - start_time)


if __name__ == "__main__":
    main()
