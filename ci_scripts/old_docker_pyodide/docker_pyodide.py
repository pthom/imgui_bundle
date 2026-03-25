#!/usr/bin/env python3
"""
Docker container management script for building imgui-bundle for Pyodide.
For more details, see Readme.md in this directory.

Usage:
======
    Docker image and container management:
        docker_pyodide.py recreate_all:      - remove and recreate image and container

        docker_pyodide.py create_image       - Build or update Docker image (long!)
        docker_pyodide.py remove_image       - Remove Docker image
        docker_pyodide.py create_container   - Create container
        docker_pyodide.py remove_container   - Remove container

    Build  and test:
        docker_pyodide.py build              - Build imgui-bundle wheel
        docker_pyodide.py serve              - Start local test server (to test the wheel in a browser)
        docker_pyodide.py check_version      - Check version consistency (between pyproject.toml and meta.yaml)

    Interactive:
        docker_pyodide.py bash               - Start interactive bash session
        docker_pyodide.py exec <cmd>         - Execute command in container


Typical workflow:
    1. docker_pyodide.py recreate_all # only first time or after Dockerfile changes
    2. docker_pyodide.py build
    3. docker_pyodide.py serve
"""
import os
import re
import subprocess
import sys

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_DIR = os.path.realpath(os.path.join(THIS_DIR, "../.."))
OUTPUT_DIR = os.path.join(THIS_DIR, "output")
RESOURCES_DIR = os.path.join(THIS_DIR, "docker_pyodide_resources")

DOCKER_IMAGE_NAME = "imgui_bundle_pyodide"
DOCKER_CONTAINER_NAME = "imgui_bundle_pyodide_container"

# Mount paths inside container
SDIST_MOUNT = "/mnt/imgui_bundle_sdist"
OUTPUT_MOUNT = "/mnt/output"

# Resource files
PYPROJECT_TOML = os.path.join(REPO_DIR, "pyproject.toml")
META_YAML_TEMPLATE = os.path.join(RESOURCES_DIR, "pyo_recipes_package_imgui_bundle.yml")
BUILD_SCRIPT = os.path.join(RESOURCES_DIR, "build_imgui_bundle.sh")

# Container paths
CONTAINER_META_YAML = "/opt/pyodide-recipes/packages/imgui-bundle/meta.yaml"
CONTAINER_BUILD_SCRIPT = "/opt/docker_pyodide_resources/build_imgui_bundle.sh"


def run_command(cmd: str, quiet: bool = False) -> int:
    """Run a shell command and return the exit code."""
    if not quiet:
        print(f"\n$ {cmd}\n")
    result = subprocess.run(cmd, shell=True)
    return result.returncode


def run_command_check(cmd: str, quiet: bool = False):
    """Run a shell command, raise exception on failure."""
    if not quiet:
        print(f"\n$ {cmd}\n")
    subprocess.check_call(cmd, shell=True)


def docker_exec(commands: str, interactive: bool = False, quiet: bool = False):
    """Execute commands inside the running container."""
    interactive_flag = "-it" if interactive else ""
    bash_cmd = f'/bin/bash -c "{commands}"'
    run_command_check(
        f"docker start {DOCKER_CONTAINER_NAME} && "
        f"docker exec {interactive_flag} {DOCKER_CONTAINER_NAME} {bash_cmd}",
        quiet
    )


# ==============================================================================
# Version management
# ==============================================================================

def _get_pyproject_version() -> str:
    """Extract version from pyproject.toml. (used by check_version)"""
    with open(PYPROJECT_TOML, 'r') as f:
        content = f.read()
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        raise RuntimeError("Could not find version in pyproject.toml")
    return match.group(1)


def _get_meta_yaml_version() -> str:
    """Extract version from meta.yaml template. (used by check_version)"""
    with open(META_YAML_TEMPLATE, 'r') as f:
        content = f.read()
    match = re.search(r'^\s*version:\s*(\S+)', content, re.MULTILINE)
    if not match:
        raise RuntimeError("Could not find version in meta.yaml template")
    return match.group(1)


def _update_meta_yaml_version(new_version: str):
    """Update version in meta.yaml template. (used by check_version)"""
    with open(META_YAML_TEMPLATE, 'r') as f:
        content = f.read()

    # Update version line
    content = re.sub(
        r'^(\s*version:\s*)\S+',
        rf'\g<1>{new_version}  # Should match version in pyproject.toml',
        content,
        count=1,
        flags=re.MULTILINE
    )

    with open(META_YAML_TEMPLATE, 'w') as f:
        f.write(content)


def check_version(fix: bool = False) -> bool:
    """
    Check if versions match between pyproject.toml and meta.yaml template.
    Returns True if versions match (or were fixed), False otherwise.
    """
    pyproject_version = _get_pyproject_version()
    meta_yaml_version = _get_meta_yaml_version()

    print(f"  pyproject.toml version: {pyproject_version}")
    print(f"  meta.yaml version:      {meta_yaml_version}")

    if pyproject_version == meta_yaml_version:
        print("\n✓ Versions match!")
        return True

    print(f"\n✗ Version mismatch!")

    if fix:
        print(f"  Updating meta.yaml to version {pyproject_version}...")
        _update_meta_yaml_version(pyproject_version)
        print("  ✓ meta.yaml updated!")
        return True
    else:
        print(f"\n  To fix, run:")
        print(f"    {sys.argv[0]} check-version --fix")
        print(f"  Or manually edit: {META_YAML_TEMPLATE}")
        return False


# ==============================================================================
# Source distribution
# ==============================================================================

def _prepare_sdist_directory():
    """
    (used by build_package)
    Create source distribution and extract it to docker_pyodide_resources/imgui_bundle_sdist.
    This directory will be mounted in the container, avoiding symlink issues.
    """
    import tarfile
    import shutil

    sdist_dir = os.path.join(RESOURCES_DIR, "imgui_bundle_sdist")

    print("\nPreparing source distribution...")

    # Clean up old sdist directory if it exists
    if os.path.exists(sdist_dir):
        print(f"  Removing old sdist directory...")
        shutil.rmtree(sdist_dir)

    # Create sdist tarball (respects sdist.exclude patterns)
    print("  Creating source distribution tarball...")
    subprocess.check_call(
        ["python", "-m", "build", "--sdist", "--outdir", RESOURCES_DIR],
        cwd=REPO_DIR,
        stdout=subprocess.DEVNULL
    )

    # Find the created tarball
    import glob
    tarballs = sorted(
        glob.glob(os.path.join(RESOURCES_DIR, "imgui_bundle-*.tar.gz")),
        key=os.path.getmtime,
        reverse=True
    )

    if not tarballs:
        raise RuntimeError("Failed to create source distribution")

    tarball = tarballs[0]
    print(f"  ✓ Created {os.path.basename(tarball)}")

    # Extract tarball
    print(f"  Extracting to imgui_bundle_sdist/...")
    os.makedirs(sdist_dir, exist_ok=True)

    with tarfile.open(tarball, 'r:gz') as tar:
        tar.extractall(sdist_dir)

    # The tarball extracts to a subdirectory like "imgui_bundle-1.92.6b1/"
    # Move contents up one level for cleaner mounting
    extracted_dirs = [d for d in os.listdir(sdist_dir) if os.path.isdir(os.path.join(sdist_dir, d))]
    if extracted_dirs:
        extracted_dir = os.path.join(sdist_dir, extracted_dirs[0])
        for item in os.listdir(extracted_dir):
            shutil.move(os.path.join(extracted_dir, item), sdist_dir)
        os.rmdir(extracted_dir)

    # Clean up tarball
    os.remove(tarball)

    print(f"  ✓ Source extracted to {sdist_dir}")
    print("    (This directory will be mounted in the container)")

    return sdist_dir


def _copy_sdist_to_container(sdist_dir: str):
    """
    Copy the sdist directory into the container.
    Docker volumes bound at creation time don't reflect host changes,
    so we copy the prepared sdist into the container.
    (used by build_package)
    """
    print("\nCopying sdist to container...")

    # Clean up any old sdist in container
    docker_exec("rm -rf /mnt/imgui_bundle_sdist", quiet=True)

    # Copy the sdist directory
    run_command_check(
        f"docker cp {sdist_dir}/. {DOCKER_CONTAINER_NAME}:{SDIST_MOUNT}/",
        quiet=False
    )

    # Verify it was copied
    result = subprocess.run(
        f"docker exec {DOCKER_CONTAINER_NAME} ls {SDIST_MOUNT}/pyproject.toml",
        shell=True,
        capture_output=True
    )

    if result.returncode == 0:
        print(f"  ✓ Sdist copied to {SDIST_MOUNT} in container")
    else:
        raise RuntimeError(f"Failed to copy sdist to container")


# ==============================================================================
# Docker operations
# ==============================================================================

def create_image():
    """Build or update the Docker image."""
    print("Building Docker image (this may take a while on first run)...")
    os.chdir(THIS_DIR)
    run_command_check(f"docker build -t {DOCKER_IMAGE_NAME} .")


def remove_image():
    """Remove the Docker image."""
    # Check if image exists
    result = subprocess.run(
        f"docker images -q {DOCKER_IMAGE_NAME}",
        shell=True,
        capture_output=True,
        text=True
    )

    if not result.stdout.strip():
        print(f"⚠️  Warning: Docker image '{DOCKER_IMAGE_NAME}' does not exist")
        return

    run_command_check(f"docker rmi {DOCKER_IMAGE_NAME}")


def create_container():
    """Create and start the container with volume mounts."""
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    run_command_check(
        f"docker run "
        f"--name {DOCKER_CONTAINER_NAME} "
        f"-v {OUTPUT_DIR}:{OUTPUT_MOUNT} "
        f"-it -d "
        f"{DOCKER_IMAGE_NAME} /bin/bash"
    )
    print(f"\n✓ Container '{DOCKER_CONTAINER_NAME}' ready!")
    print(f"  - Output directory: {OUTPUT_DIR}")
    print(f"\nNote: Source code will be copied into container at build time")


def remove_container():
    """Stop and remove the container."""
    # Check if container exists
    result = subprocess.run(
        f"docker ps -a -q -f name=^{DOCKER_CONTAINER_NAME}$",
        shell=True,
        capture_output=True,
        text=True
    )

    if not result.stdout.strip():
        print(f"⚠️  Warning: Container '{DOCKER_CONTAINER_NAME}' does not exist")
        return

    run_command(f"docker stop {DOCKER_CONTAINER_NAME}")
    run_command(f"docker rm {DOCKER_CONTAINER_NAME}")


def run_bash():
    """Start an interactive bash session in the container."""
    run_command_check(
        f"docker start {DOCKER_CONTAINER_NAME} && "
        f"docker exec -it {DOCKER_CONTAINER_NAME} /bin/bash"
    )


def install_meta_yaml():
    """Copy meta.yaml template to pyodide-recipes in container."""
    print("Installing meta.yaml to pyodide-recipes...")
    # Read local template and escape for shell
    with open(META_YAML_TEMPLATE, 'r') as f:
        content = f.read()

    # Create directory and write file in container
    docker_exec(
        f"mkdir -p /opt/pyodide-recipes/packages/imgui-bundle && "
        f"cat > {CONTAINER_META_YAML} << 'METAYAMLEOF'\n{content}\nMETAYAMLEOF",
        quiet=True
    )
    print("  ✓ meta.yaml installed")


def build_package():
    """Build the imgui-bundle pyodide wheel."""
    print("Checking version consistency...")
    if not check_version(fix=False):
        print("\n✗ Build aborted due to version mismatch.")
        print("  Fix the version and try again.")
        return False

    # Prepare clean source distribution
    sdist_dir = _prepare_sdist_directory()

    # Copy sdist into container (Docker volumes don't reflect host changes after creation)
    _copy_sdist_to_container(sdist_dir)

    print("\nInstalling meta.yaml...")
    install_meta_yaml()

    print("\nBuilding imgui-bundle for Pyodide...")
    docker_exec(CONTAINER_BUILD_SCRIPT, interactive=True)
    print("\n✓ Build complete! Check output/ directory for the wheel.")
    return True


def serve():
    """Start local test server."""
    os.chdir(THIS_DIR)
    run_command_check("python3 serve_test.py")


def print_help():
    """Print usage information."""
    help_text = f"""
Usage: {sys.argv[0]} <command>

{__doc__.replace("docker_pyodide.py", sys.argv[0])}

Paths:
    Image name:     {DOCKER_IMAGE_NAME}
    Container name: {DOCKER_CONTAINER_NAME}
    Source:         Copied from docker_pyodide_resources/imgui_bundle_sdist -> {SDIST_MOUNT}
    Output mount:   {OUTPUT_DIR} -> {OUTPUT_MOUNT}
    
Resources:
    meta.yaml template: {META_YAML_TEMPLATE}
    Build script:       {BUILD_SCRIPT}
"""
    print(help_text)


def main():
    if len(sys.argv) < 2:
        print_help()
        return 1

    command = sys.argv[1].lower()

    if command == "recreate_all":
        remove_container()
        remove_image()
        create_image()
        create_container()
        return 0
    elif command == "create_image":
        create_image()
    elif command == "remove_image":
        remove_image()
    elif command == "create_container":
        create_container()
    elif command == "remove_container":
        remove_container()

    elif command == "build":
        if not build_package():
            return 1
    elif command == "serve":
        serve()
    elif command == "check_version":
        fix = "--fix" in sys.argv
        if not check_version(fix=fix):
            return 1

    elif command == "bash":
        run_bash()
    elif command == "exec":
        if len(sys.argv) < 3:
            print("Error: 'exec' requires a command argument")
            return 1
        commands = " ".join(sys.argv[2:])
        docker_exec(commands, interactive=True)

    elif command in ("-h", "--help", "help"):
        print_help()
    else:
        print(f"Unknown command: {command}")
        print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

