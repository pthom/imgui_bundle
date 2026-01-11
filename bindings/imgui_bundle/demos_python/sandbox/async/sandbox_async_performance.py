"""Demonstrate performance benefits of async mode with optimized FPS settings.

This sandbox shows how Python code can execute in parallel with GUI rendering
when using the optimized async configuration.
"""

import asyncio
import time
from imgui_bundle import immapp, imgui, hello_imgui


# Performance tracking
perf_stats = {
    "python_iterations": 0,
    "python_fps": 0.0,
    "last_update": time.time(),
    "start_time": time.time(),
}


def gui_with_perf_display():
    """GUI that displays Python loop performance."""
    imgui.text("Async Performance Demonstration")
    imgui.separator()

    imgui.text(f"Python Loop Iterations/sec: {perf_stats['python_fps']:.1f}")
    imgui.text(f"Total Python Iterations: {perf_stats['python_iterations']}")

    elapsed = time.time() - perf_stats["start_time"]
    imgui.text(f"Running Time: {elapsed:.1f}s")

    imgui.separator()
    imgui.text_wrapped(
        "The Python loop runs in parallel with GUI rendering. "
        "This is possible because of optimized FPS settings:"
    )
    imgui.bullet_text("fps_idling_mode = early_return")
    imgui.bullet_text("vsync_to_monitor = False")
    imgui.bullet_text("fps_max = 60.0")

    imgui.separator()
    if imgui.button("Stop"):
        hello_imgui.get_runner_params().app_shall_exit = True


async def python_computation_loop():
    """Run computations while GUI is active."""
    perf_stats["python_iterations"] = 0
    perf_stats["last_update"] = time.time()
    perf_stats["start_time"] = time.time()

    iteration_count = 0

    while immapp.nb.is_running():
        # Simulate computation work
        _ = sum(range(1000))

        perf_stats["python_iterations"] += 1
        iteration_count += 1

        # Update FPS calculation every 0.5 seconds
        current_time = time.time()
        elapsed = current_time - perf_stats["last_update"]
        if elapsed >= 0.5:
            perf_stats["python_fps"] = iteration_count / elapsed
            iteration_count = 0
            perf_stats["last_update"] = current_time

        # Yield to event loop to allow GUI rendering
        await asyncio.sleep(0)

    total_time = time.time() - perf_stats["start_time"]
    print("\nPerformance Summary:")
    print(f"  Total iterations: {perf_stats['python_iterations']}")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Average FPS: {perf_stats['python_iterations'] / total_time:.1f}")


async def main():
    """Main async function."""
    print("Starting GUI with async performance test...")
    print("Watch the window to see Python loop performance.")
    print("The GUI remains responsive while Python executes in parallel.\n")

    # Start GUI non-blocking
    immapp.nb.start(
        gui_with_perf_display,
        window_title="Async Performance Demo",
        window_size_auto=True,
        top_most=True
    )

    # Run Python loop in parallel
    await python_computation_loop()

    print("\nDemo complete!")


if __name__ == "__main__":
    asyncio.run(main())
