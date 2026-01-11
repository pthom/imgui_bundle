"""Quick verification test for hello_imgui.nb module.

This test verifies that the module can be imported and has the expected API.
"""

def test_hello_imgui_nb_module_exists():
    """Test that hello_imgui.nb module can be imported."""
    from imgui_bundle import hello_imgui
    assert hasattr(hello_imgui, 'nb'), "hello_imgui.nb module should exist"
    print("✓ hello_imgui.nb module exists")


def test_hello_imgui_nb_has_expected_functions():
    """Test that hello_imgui.nb has the expected functions."""
    from imgui_bundle import hello_imgui

    # Check for expected functions
    assert hasattr(hello_imgui.nb, 'run'), "hello_imgui.nb should have run()"
    assert hasattr(hello_imgui.nb, 'start'), "hello_imgui.nb should have start()"
    assert hasattr(hello_imgui.nb, 'stop'), "hello_imgui.nb should have stop()"
    assert hasattr(hello_imgui.nb, 'is_running'), "hello_imgui.nb should have is_running()"

    print("✓ hello_imgui.nb has all expected functions")


def test_hello_imgui_nb_is_running_initial_state():
    """Test that is_running() returns False initially."""
    from imgui_bundle import hello_imgui

    assert not hello_imgui.nb.is_running(), "is_running() should return False initially"
    print("✓ is_running() returns False initially")


def test_hello_imgui_nb_functions_are_callable():
    """Test that all functions are callable."""
    from imgui_bundle import hello_imgui

    assert callable(hello_imgui.nb.run), "run should be callable"
    assert callable(hello_imgui.nb.start), "start should be callable"
    assert callable(hello_imgui.nb.stop), "stop should be callable"
    assert callable(hello_imgui.nb.is_running), "is_running should be callable"

    print("✓ All functions are callable")


def test_hello_imgui_nb_stop_when_not_running():
    """Test that stop() can be called when nothing is running."""
    from imgui_bundle import hello_imgui

    # Should not raise an error
    hello_imgui.nb.stop()
    print("✓ stop() can be called when nothing is running")


if __name__ == "__main__":
    print("Testing hello_imgui.nb module...")
    print()

    test_hello_imgui_nb_module_exists()
    test_hello_imgui_nb_has_expected_functions()
    test_hello_imgui_nb_is_running_initial_state()
    test_hello_imgui_nb_functions_are_callable()
    test_hello_imgui_nb_stop_when_not_running()

    print()
    print("All tests passed! ✓")
