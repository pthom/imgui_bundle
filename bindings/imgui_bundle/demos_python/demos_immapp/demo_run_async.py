"""Demonstrate how immapp.run_async enables parallel Python execution with GUI rendering.

This demo runs a computation loop in Python while the GUI remains responsive.
By calling `immapp.run_async`, the GUI runs in an asyncio Task, allowing Python code to execute concurrently.

`immapp.run_async` automatically adjusts FPS idling parameters to optimize performance, so that the Python loop
can run at maximum speed.
"""

import asyncio
import time
from imgui_bundle import immapp, imgui, hello_imgui, imgui_md


GUI_FINISHED = False
PYTHON_FPS = 0.0


def gui():
    imgui.dummy(hello_imgui.em_to_vec2(20, 1))
    imgui.text(f"Gui FPS: {hello_imgui.frame_rate():.2f}")
    imgui.text(f'Python "FPS": {PYTHON_FPS:.1f}')

    imgui.separator()

    imgui_md.render_unindented("""
        **Explanations**

        The Python loop runs in parallel with GUI rendering with max performance for the python code.

        This is possible thanks to optimized FPS settings which are automatically set by `immapp.run_async`:
        * fps_idling_mode = early_return
        * vsync_to_monitor = False
        * fps_max = 60.0
    """)

    global GUI_FINISHED
    GUI_FINISHED = hello_imgui.get_runner_params().app_shall_exit


async def python_computation_loop():
    """Run computations while GUI is active."""
    global PYTHON_FPS
    last_update = time.time()
    start_time = time.time()

    total_count = 0
    current_count = 0

    while not GUI_FINISHED:
        # Simulate computation work: how many sums we can do in 1 second?
        # This will be our "PYTHON_FPS"
        _ = sum(range(1000))

        total_count += 1
        current_count += 1

        # Update FPS calculation every 0.5 seconds
        current_time = time.time()
        elapsed = current_time - last_update
        if elapsed >= 0.5:
            PYTHON_FPS = current_count / elapsed
            current_count = 0
            last_update = current_time

        # Yield to event loop to allow GUI rendering
        await asyncio.sleep(0)

    total_time = time.time() - start_time
    print("\nPerformance Summary:")
    print(f"  Total iterations: {total_count}")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Average FPS: {total_count / total_time:.1f}")


async def main():
    """Main async function."""
    print("Starting GUI with async performance test...")
    print("Watch the window to see Python loop performance.")
    print("The GUI remains responsive while Python executes in parallel.\n")

    # Start GUI non-blocking:
    # we create an asyncio Task for it (this returns immediately)
    _gui_task = asyncio.create_task(
        immapp.run_async(
            gui,
            window_title="Async Performance Demo",
            window_size_auto=True,
            top_most=True
        )
    )

    # Run Python loop in parallel (it will stop when GUI is closed, since it checks GUI_FINISHED)
    await python_computation_loop()

    print("\nDemo complete!")


if __name__ == "__main__":
    asyncio.run(main())
