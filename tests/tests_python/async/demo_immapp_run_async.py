"""Test suite for immapp.run_async() - all three overloads"""
import asyncio
from imgui_bundle import imgui, immapp, hello_imgui, implot
import numpy as np


# Shared state for testing
freq = 1.0
test_counter = 0


def gui_simple():
    """Simple GUI function for testing"""
    global freq, test_counter
    test_counter += 1

    changed, freq = imgui.slider_float("Frequency", freq, 0.1, 10.0)
    imgui.text(f"Current frequency: {freq:.2f}")
    imgui.text(f"Render count: {test_counter}")


def gui_with_plot():
    """GUI function with implot"""
    global freq
    changed, freq = imgui.slider_float("Frequency", freq, 0.1, 10.0)

    x = np.linspace(0, 2*np.pi, 1000)
    y = np.sin(freq * x)

    if implot.begin_plot("Sine Wave"):
        implot.plot_line("sin(x)", x, y)
        implot.end_plot()


# ============================================================================
# Test 1: run_async with GUI function (simple signature)
# ============================================================================
async def test_run_async_gui_function():
    """Test run_async() with a GUI function and keyword arguments"""
    print("\n" + "="*70)
    print("TEST 1: run_async(gui_function, window_title=..., ...)")
    print("="*70)
    print("This will open a simple GUI. Close it to continue to next test.")

    await immapp.run_async(
        gui_simple,
        window_title="Test 1: GUI Function",
        window_size_auto=True,
        fps_idle=10.0,
    )

    print(f"✓ Test 1 passed - rendered {test_counter} frames")


# ============================================================================
# Test 2: run_async with GUI function + implot addon
# ============================================================================
async def test_run_async_with_implot():
    """Test run_async() with implot addon enabled"""
    print("\n" + "="*70)
    print("TEST 2: run_async(gui_function, with_implot=True)")
    print("="*70)
    print("This will open a GUI with an ImPlot graph. Close it to continue.")

    global test_counter
    test_counter = 0

    await immapp.run_async(
        gui_with_plot,
        window_title="Test 2: With ImPlot",
        window_size_auto=True,
        with_implot=True,
        fps_idle=10.0,
    )

    print(f"✓ Test 2 passed - rendered {test_counter} frames")


# ============================================================================
# Test 3: run_async with SimpleRunnerParams
# ============================================================================
async def test_run_async_simple_params():
    """Test run_async() with SimpleRunnerParams"""
    print("\n" + "="*70)
    print("TEST 3: run_async(SimpleRunnerParams, AddOnsParams)")
    print("="*70)
    print("This will open a GUI using SimpleRunnerParams. Close it to continue.")

    global test_counter
    test_counter = 0

    simple_params = hello_imgui.SimpleRunnerParams()
    simple_params.gui_function = gui_simple
    simple_params.window_title = "Test 3: SimpleRunnerParams"
    simple_params.window_size_auto = True
    simple_params.fps_idle = 10.0

    await immapp.run_async(simple_params)

    print(f"✓ Test 3 passed - rendered {test_counter} frames")


# ============================================================================
# Test 4: run_async with full RunnerParams
# ============================================================================
async def test_run_async_runner_params():
    """Test run_async() with full RunnerParams + AddOnsParams"""
    print("\n" + "="*70)
    print("TEST 4: run_async(RunnerParams, AddOnsParams)")
    print("="*70)
    print("This will open a GUI with RunnerParams + implot. Close it to continue.")

    global test_counter
    test_counter = 0

    runner = hello_imgui.RunnerParams()
    runner.callbacks.show_gui = gui_with_plot
    runner.app_window_params.window_title = "Test 4: RunnerParams + AddOnsParams"
    runner.app_window_params.window_geometry.size = (800, 600)
    runner.fps_idling.fps_idle = 10.0

    addons = immapp.AddOnsParams()
    addons.with_implot = True

    await immapp.run_async(runner, addons)

    print(f"✓ Test 4 passed - rendered {test_counter} frames")


# ============================================================================
# Test 5: Programmatic exit
# ============================================================================
async def test_programmatic_exit():
    """Test programmatically closing the GUI"""
    print("\n" + "="*70)
    print("TEST 5: Programmatic exit")
    print("="*70)
    print("This will open a GUI and automatically close it after 2 seconds.")

    global test_counter
    test_counter = 0

    # Start the GUI as a task
    task = asyncio.create_task(
        immapp.run_async(
            gui_simple,
            window_title="Test 5: Auto-closing in 2 seconds...",
            window_size_auto=True,
            fps_idle=30.0,
        )
    )

    # Wait 2 seconds
    await asyncio.sleep(2)

    # Request exit
    hello_imgui.get_runner_params().app_shall_exit = True

    # Wait for task to complete
    await task

    print(f"✓ Test 5 passed - GUI auto-closed after {test_counter} frames")


# ============================================================================
# Main test runner
# ============================================================================
async def run_all_tests():
    """Run all tests sequentially"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "IMMAPP.RUN_ASYNC() TEST SUITE" + " "*24 + "║")
    print("╚" + "="*68 + "╝")
    print("\nThis will run 5 tests sequentially.")
    print("Please close each GUI window to proceed to the next test.\n")

    try:
        await test_run_async_gui_function()
        await test_run_async_with_implot()
        await test_run_async_simple_params()
        await test_run_async_runner_params()
        await test_programmatic_exit()

        print("\n" + "="*70)
        print("✓ ALL TESTS PASSED!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# Individual test runners (for manual testing)
# ============================================================================
def run_test_1():
    """Run only test 1"""
    asyncio.run(test_run_async_gui_function())

def run_test_2():
    """Run only test 2"""
    asyncio.run(test_run_async_with_implot())

def run_test_3():
    """Run only test 3"""
    asyncio.run(test_run_async_simple_params())

def run_test_4():
    """Run only test 4"""
    asyncio.run(test_run_async_runner_params())

def run_test_5():
    """Run only test 5"""
    asyncio.run(test_programmatic_exit())


if __name__ == "__main__":
    # Run all tests
    asyncio.run(run_all_tests())

    # Or run individual tests:
    # run_test_1()
    # run_test_2()
    # run_test_3()
    # run_test_4()
    # run_test_5()
