#!/usr/bin/env python3
import os
import subprocess
import sys


INVOKE_DIR = os.getcwd()
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_DIR = os.path.realpath(THIS_DIR + "/../..")
DOCKER_IMAGE_NAME = "docker_ubuntu_dev_image"
DOCKER_CONTAINER_NAME = "docker_ubuntu_dev"
SOURCES_MOUNT_DIR = "/dvp/sources"
VNC_PORT = 5900


def run_local_command(cmd, quiet=False):
    if not quiet:
        print(f"\n{cmd}\n")
    subprocess.check_call(cmd, shell=True)


def help_vnc():
    msg = f"""
    Inside the container, you can run graphical apps. Launch:
        /start_x_vnc.sh &
    Then, connect a VNC viewer to the address:
        localhost:{VNC_PORT}
    """
    lines = msg.split("\n")
    lines = map(lambda line: "# " + line, lines)
    msg = "\n".join(lines)
    print(msg)


def run_docker_command(commands, quiet: bool, interactive: bool):
    in_bash_commands = f'/bin/bash -c "{commands}"'
    interactive_flag = "-it" if interactive else ""
    run_local_command(
        f"docker start {DOCKER_CONTAINER_NAME} && docker exec {interactive_flag} {DOCKER_CONTAINER_NAME} {in_bash_commands}",
        quiet,
    )


def rm_container():
    try:
        run_local_command(f"docker stop {DOCKER_CONTAINER_NAME}")
        run_local_command(f"docker rm {DOCKER_CONTAINER_NAME}")
    except subprocess.CalledProcessError:
        pass


def rm_image():
    run_local_command(f"docker rmi {DOCKER_IMAGE_NAME}")


def create_container():
    run_local_command(
        f"docker run --name {DOCKER_CONTAINER_NAME} -p {VNC_PORT}:{VNC_PORT} -it -d -v {REPO_DIR}:{SOURCES_MOUNT_DIR} {DOCKER_IMAGE_NAME}  /bin/bash"
    )


def build_image():
    os.chdir(THIS_DIR)
    run_local_command(f"docker build -t {DOCKER_IMAGE_NAME} .")


def run_bash():
    run_local_command(
        f"docker start {DOCKER_CONTAINER_NAME} && docker exec -it {DOCKER_CONTAINER_NAME} /bin/bash"
    )


def full_build():
    rm_container()
    build_image()
    create_container()


def main():
    """
    Usage: docker_run.py    build | bash | exec [any command and args] | remove | remove_image

        docker_run.py build
    Will build the image, create a docker image {DOCKER_IMAGE_NAME} and start a container {DOCKER_CONTAINER_NAME}
    based on this image where the sources are mounted at {SOURCES_MOUNT_DIR},
    and where a VNC server can be launched on port {VNC_PORT}
        *Warning*: any previously running container named {DOCKER_CONTAINER_NAME} will be removed.

        docker_run.py bash
    Will log you into a bash session in the previously created container.

        docker_run.py exec [any command and args]
    Will start the container and run the commands given after "exec".
    For example, "{sys.argv[0]} exec ls -al" will list the files.

        docker_run.py exec_it [any command and args]
    Same, in interactive mode

        docker_run.py remove_image
    Will remove the docker image {DOCKER_IMAGE_NAME}
        docker_run.py remove
    Will remove the container {DOCKER_CONTAINER_NAME} and (you will lose all modifications in the Docker container)
    """
    os.chdir(THIS_DIR)
    if len(sys.argv) < 2:
        print(main.__doc__)
        return

    arg1 = sys.argv[1].lower()
    if arg1 == "build":
        full_build()
    elif arg1 == "bash":
        help_vnc()
        run_bash()
    elif arg1 == "exec":
        bash_commands = " ".join(sys.argv[2:])
        run_docker_command(bash_commands, quiet=False, interactive=False)
    elif arg1 == "exec_it":
        bash_commands = " ".join(sys.argv[2:])
        run_docker_command(bash_commands, quiet=False, interactive=True)
    elif arg1 == "remove":
        rm_container()
    elif arg1 == "remove_image":
        rm_image()
    else:
        print(main.__doc__)


if __name__ == "__main__":
    main()
