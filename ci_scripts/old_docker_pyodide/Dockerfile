# Dockerfile for building imgui-bundle for Pyodide
# Based on Ubuntu with Python 3.13, Pyodide, and all build dependencies

FROM ubuntu:24.04

# Pyodide version to use
ARG PYODIDE_VERSION=0.29.2
# Python version to use (required by Pyodide, see pyodide/Makefile.env)
ARG PYTHON_VERSION=3.13

# Set non-interactive frontend to prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required system packages
#=============================================

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    cmake \
    ninja-build \
    ccache \
    wget \
    curl \
    pkg-config \
    # Autotools - needed for libffi build
    autoconf \
    automake \
    libtool \
    # Python build dependencies
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Install Rust via rustup (required by some Pyodide test packages)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:$PATH"


# Install Python version PYTHON_VERSION (required by Pyodide)
# ===========================================
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-dev && \
    rm -rf /var/lib/apt/lists/*

# Set Python 3.13 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VERSION} 1

# Create working directory
WORKDIR /opt

# Create and activate virtual environment for pyodide build
RUN python3.13 -m venv /opt/venv_pyodide
ENV PATH="/opt/venv_pyodide/bin:$PATH"
ENV VIRTUAL_ENV="/opt/venv_pyodide"

# Upgrade pip
RUN pip install --upgrade pip


# Prepare build folders
# ============================
# Create mount points
RUN mkdir -p /mnt/imgui_bundle /mnt/output

# Copy resources (build script, meta.yaml template)
COPY docker_pyodide_resources/ /opt/docker_pyodide_resources/
RUN chmod +x /opt/docker_pyodide_resources/build_imgui_bundle.sh


# Clone pyodide-recipes repository
# =================================
RUN git clone --depth 1 https://github.com/pyodide/pyodide-recipes.git /opt/pyodide-recipes


#
# Clone and build Pyodide, using version from PYODIDE_VERSION
# ===========================
RUN git clone --depth 1 --branch ${PYODIDE_VERSION} https://github.com/pyodide/pyodide.git /opt/pyodide
WORKDIR /opt/pyodide

# Install Pyodide requirements
RUN pip install -r requirements.txt

# Initialize submodules
RUN git submodule update --init --recursive

# Install pyodide-build in editable mode
WORKDIR /opt/pyodide/pyodide-build
RUN pip install -v -e .

# Build Pyodide (this downloads emsdk, builds cpython, and core packages)
# This is the longest step - it compiles everything
WORKDIR /opt/pyodide
RUN make  # (This may take a while: downloads and builds emscripten, CPython, and core packages)


# Final setup
# ============================
# Set working directory for interactive use
WORKDIR /opt/pyodide

# Default command
CMD ["/bin/bash"]
