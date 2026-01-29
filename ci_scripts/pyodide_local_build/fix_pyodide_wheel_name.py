#!/usr/bin/env python3
"""
Fix pyodide wheel naming on macOS until scikit-build-core v0.12+ is released.

This script renames wheels built on macOS from:
  imgui_bundle-X.Y.Z-cpXYZ-cpXYZ-macosx_*_arm64.whl
to:
  imgui_bundle-X.Y.Z-cpXYZ-cpXYZ-pyodide_2025_0_wasm32.whl

Context:
- The fix was merged in scikit-build-core PR #1196 (Dec 2024)
- Last release was v0.11.6 (Aug 2024)
- This workaround can be removed once v0.12+ is released

References:
- https://github.com/scikit-build/scikit-build-core/pull/1196
- https://github.com/scikit-build/scikit-build-core/issues/920
- https://pyodide.org/en/stable/development/abi.html
"""

import sys
import platform
from pathlib import Path
import re
import os
import shutil




def fix_pyodide_wheel_name():
    """Rename macOS-tagged wheel to pyodide-tagged wheel."""

    # Only needed on macOS builds

    if platform.system() != "Darwin":
        print("✓ Not on macOS, wheel naming should be correct")
        return 0

    # Change to repo root
    this_dir = Path(__file__).parent.resolve()
    repo_root = this_dir.parent.parent.resolve()
    print(repo_root)
    os.chdir(repo_root)

    print("")
    print("=" * 70)
    print("⚠️  macOS detected - applying pyodide wheel name fix")
    print("    (Workaround for scikit-build-core issue #920)")
    print("=" * 70)
    print("")

    dist_dir = Path("dist")
    if not dist_dir.exists():
        print(f"✗ Error: {dist_dir} directory not found")
        return 1

    # Find wheels with macOS tag
    macos_wheels = list(dist_dir.glob("*-macosx_*.whl"))

    if not macos_wheels:
        print("✓ No macOS-tagged wheels found, naming is correct")
        return 0

    if len(macos_wheels) > 1:
        print(f"⚠️  Found {len(macos_wheels)} macOS wheels, will rename all")
        print("")

    for old_wheel in macos_wheels:
        # Extract wheel components
        # Format: {name}-{version}-{python}-{abi}-{platform}.whl
        match = re.match(
            r"^(.+?)-(.+?)-(cp\d+)-(cp\d+)-macosx_.+?\.whl$",
            old_wheel.name
        )

        if not match:
            print(f"✗ Could not parse wheel name: {old_wheel.name}")
            continue

        name, version, python_tag, abi_tag = match.groups()

        # Create new pyodide-tagged name
        new_name = f"{name}-{version}-{python_tag}-{abi_tag}-pyodide_2025_0_wasm32.whl"
        new_wheel = dist_dir / new_name

        if new_wheel.exists():
            print(f"✓ Wheel already correctly named: {new_name}")
            if old_wheel != new_wheel:
                print(f"  Removing old wheel: {old_wheel.name}")
                old_wheel.unlink()
            continue

        # Rename the wheel
        print(f"📝 Renaming wheel:")
        print(f"   From: {old_wheel.name}")
        print(f"   To:   {new_name}")

        shutil.move(str(old_wheel), str(new_wheel))

        print("✓ Wheel renamed successfully")

    print("")
    print("=" * 70)
    print("ℹ️  This workaround can be removed once scikit-build-core v0.12+ is released")
    print("=" * 70)
    print("")

    return 0


if __name__ == "__main__":
    sys.exit(fix_pyodide_wheel_name())
