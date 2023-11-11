# Use the latest version of Ubuntu as the base image
FROM ubuntu:latest

# Set non-interactive frontend to prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update

# Install required build utilities
RUN apt-get install -y build-essential git cmake python3 python3-pip python3-venv wget tree

# Install dependencies for imgui_bundle
RUN python3 -m pip install pybind11
RUN yes | apt-get install xorg-dev


# install_x11vnc
# /start_x_vnc.sh will start a "X server + vnc server + window manager" accessible via VNC
# -> you can connect to it via VNC on the port 5900 of the localhost
RUN apt-get install -y x11vnc xvfb icewm
RUN mkdir ~/.vnc &&\
    x11vnc -storepasswd xxx ~/.vnc/passwd &&\
    echo 'export DISPLAY=:0' >> ~/.bashrc &&\
    echo "Xvfb -screen 0 1280x1024x16 & sleep 1 && icewm & x11vnc -forever  -ncache 10" > /start_x_vnc.sh &&\
    chmod +x /start_x_vnc.sh && \
    apt-get install -y libglapi-mesa

RUN apt-get install ninja-build

## Install libs required by immvision
#RUN apt-get install -y libopencv-dev libsdl2-dev libgl1-mesa-dev
#
## Install pipewire (PipeWire multimedia server), required by sdl
#RUN apt-get install -y pipewire


# Set the working directory inside the container
RUN mkdir -p /dvp/build
WORKDIR /dvp/build
