"""Quick verification test for immapp.nb module.

This test verifies that the module can be imported and has the expected API.
"""

def test_immapp_nb_module_exists():
    """Test that immapp.nb module can be imported."""
    from imgui_bundle import immapp
    assert hasattr(immapp, 'nb'), "immapp.nb module should exist"
    print("✓ immapp.nb module exists")


def test_immapp_nb_has_expected_functions():
    """Test that immapp.nb has the expected functions."""
    from imgui_bundle import immapp

    # Check for expected functions
    assert hasattr(immapp.nb, 'run'), "immapp.nb should have run()"
    assert hasattr(immapp.nb, 'start'), "immapp.nb should have start()"
    assert hasattr(immapp.nb, 'stop'), "immapp.nb should have stop()"
    assert hasattr(immapp.nb, 'is_running'), "immapp.nb should have is_running()"

    print("✓ immapp.nb has all expected functions")


def test_immapp_nb_is_running_initial_state():
    """Test that is_running() returns False initially."""
    from imgui_bundle import immapp

    assert not immapp.nb.is_running(), "is_running() should return False initially"
    print("✓ is_running() returns False initially")


def test_immapp_nb_functions_are_callable():
    """Test that all functions are callable."""
    from imgui_bundle import immapp

    assert callable(immapp.nb.run), "run should be callable"
    assert callable(immapp.nb.start), "start should be callable"
    assert callable(immapp.nb.stop), "stop should be callable"
    assert callable(immapp.nb.is_running), "is_running should be callable"

    print("✓ All functions are callable")


def test_immapp_nb_stop_when_not_running():
    """Test that stop() can be called when nothing is running."""
    from imgui_bundle import immapp

    # Should not raise an error
    immapp.nb.stop()
    print("✓ stop() can be called when nothing is running")


if __name__ == "__main__":
    print("Testing immapp.nb module...")
    print()

    test_immapp_nb_module_exists()
    test_immapp_nb_has_expected_functions()
    test_immapp_nb_is_running_initial_state()
    test_immapp_nb_functions_are_callable()
    test_immapp_nb_stop_when_not_running()

    print()
    print("All tests passed! ✓")
