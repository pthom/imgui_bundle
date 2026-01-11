"""Test suite for hello_imgui.run_async() - all three overloads"""
import asyncio
from imgui_bundle import imgui, hello_imgui


# Shared state for testing
value = 50.0
test_counter = 0


def gui_simple():
    """Simple GUI function for testing"""
    global value, test_counter
    test_counter += 1

    changed, value = imgui.slider_float("Value", value, 0.0, 100.0)
    imgui.text(f"Current value: {value:.2f}")
    imgui.text(f"Render count: {test_counter}")


# ============================================================================
# Test 1: run_async with GUI function (simple signature)
# ============================================================================
async def test_run_async_gui_function():
    """Test run_async() with a GUI function and keyword arguments"""
    print("\n" + "="*70)
    print("TEST 1: hello_imgui.run_async(gui_function, window_title=..., ...)")
    print("="*70)
    print("This will open a simple GUI. Close it to continue to next test.")

    await hello_imgui.run_async(
        gui_simple,
        window_title="Test 1: GUI Function",
        window_size_auto=True,
        fps_idle=10.0,
    )

    print(f"✓ Test 1 passed - rendered {test_counter} frames")


# ============================================================================
# Test 2: run_async with SimpleRunnerParams
# ============================================================================
async def test_run_async_simple_params():
    """Test run_async() with SimpleRunnerParams"""
    print("\n" + "="*70)
    print("TEST 2: hello_imgui.run_async(SimpleRunnerParams)")
    print("="*70)
    print("This will open a GUI using SimpleRunnerParams. Close it to continue.")

    global test_counter
    test_counter = 0

    simple_params = hello_imgui.SimpleRunnerParams()
    simple_params.gui_function = gui_simple
    simple_params.window_title = "Test 2: SimpleRunnerParams"
    simple_params.window_size_auto = True
    simple_params.fps_idle = 10.0

    await hello_imgui.run_async(simple_params)

    print(f"✓ Test 2 passed - rendered {test_counter} frames")


# ============================================================================
# Test 3: run_async with full RunnerParams
# ============================================================================
async def test_run_async_runner_params():
    """Test run_async() with full RunnerParams"""
    print("\n" + "="*70)
    print("TEST 3: hello_imgui.run_async(RunnerParams)")
    print("="*70)
    print("This will open a GUI with RunnerParams. Close it to continue.")

    global test_counter
    test_counter = 0

    runner = hello_imgui.RunnerParams()
    runner.callbacks.show_gui = gui_simple
    runner.app_window_params.window_title = "Test 3: RunnerParams"
    runner.app_window_params.window_geometry.size = (400, 200)
    runner.fps_idling.fps_idle = 10.0

    await hello_imgui.run_async(runner)

    print(f"✓ Test 3 passed - rendered {test_counter} frames")


# ============================================================================
# Test 4: Programmatic exit
# ============================================================================
async def test_programmatic_exit():
    """Test programmatically closing the GUI"""
    print("\n" + "="*70)
    print("TEST 4: Programmatic exit")
    print("="*70)
    print("This will open a GUI and automatically close it after 2 seconds.")

    global test_counter
    test_counter = 0

    # Start the GUI as a task
    task = asyncio.create_task(
        hello_imgui.run_async(
            gui_simple,
            window_title="Test 4: Auto-closing in 2 seconds...",
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

    print(f"✓ Test 4 passed - GUI auto-closed after {test_counter} frames")


# ============================================================================
# Main test runner
# ============================================================================
async def run_all_tests():
    """Run all tests sequentially"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*13 + "HELLO_IMGUI.RUN_ASYNC() TEST SUITE" + " "*21 + "║")
    print("╚" + "="*68 + "╝")
    print("\nThis will run 4 tests sequentially.")
    print("Please close each GUI window to proceed to the next test.\n")

    try:
        await test_run_async_gui_function()
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
    asyncio.run(test_run_async_simple_params())

def run_test_3():
    """Run only test 3"""
    asyncio.run(test_run_async_runner_params())

def run_test_4():
    """Run only test 4"""
    asyncio.run(test_programmatic_exit())


if __name__ == "__main__":
    # Run all tests
    asyncio.run(run_all_tests())

    # Or run individual tests:
    # run_test_1()
    # run_test_2()
    # run_test_3()
    # run_test_4()
