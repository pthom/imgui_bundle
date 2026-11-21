"""ImmVision's inspector: an image may be added before the app runs, with no OpenGL context yet."""

import subprocess
import sys

import pytest
import imgui_bundle

pytestmark = pytest.mark.skipif(
    not imgui_bundle.has_submodule("immvision"),
    reason="immvision submodule not available in this build",
)

ADD_BEFORE_THE_APP = """
import numpy as np
from imgui_bundle import immvision
immvision.inspector_add_image(np.zeros((8, 8), np.uint8), "before the app")
immvision.inspector_clear_images()
"""


def test_inspector_add_image_without_opengl() -> None:
    # In a process of its own: a crash must not take the test session down
    result = subprocess.run([sys.executable, "-c", ADD_BEFORE_THE_APP], capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, f"exit {result.returncode}\n{result.stderr}"
