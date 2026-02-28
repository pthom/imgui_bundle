#!/bin/bash
# Pre-build minimalist static OpenCV for CI wheel builds.
# Run once per container (via cibuildwheel before-all) so that
# all Python version builds reuse the same pre-built OpenCV.
#
# The cmake flags here must stay in sync with immvision_fetch_opencv_from_source()
# in external/immvision/immvision/cmake/find_opencv.cmake
#
# See docs/book/devel_docs/build_opencv_immvision.md for the full picture.
set -ex

INSTALL_DIR="${1:-/opt/opencv_minimalist}"
OPENCV_VERSION="4.11.0"

# Download OpenCV source
cd /tmp
if [ -n "${IMMVISION_OPENCV_GIT_REPO}" ]; then
    git clone --depth 1 --branch "${OPENCV_VERSION}" "${IMMVISION_OPENCV_GIT_REPO}" opencv_src
else
    curl -sL "https://github.com/opencv/opencv/archive/refs/tags/${OPENCV_VERSION}.tar.gz" -o opencv.tar.gz
    tar xzf opencv.tar.gz
    mv "opencv-${OPENCV_VERSION}" opencv_src
fi

mkdir -p opencv_build && cd opencv_build

# Minimalist static OpenCV: only core, imgcodecs, imgproc.
# These flags are duplicated from find_opencv.cmake — keep them in sync.
cmake /tmp/opencv_src \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}" \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -DINSTALL_CREATE_DISTRIB=ON \
    -DBUILD_SHARED_LIBS=OFF \
    -DBUILD_opencv_apps=OFF \
    -DBUILD_TESTS=OFF \
    -DBUILD_PERF_TESTS=OFF \
    -DWITH_OPENJPEG=OFF \
    -DWITH_JASPER=OFF \
    -DWITH_1394=OFF \
    -DWITH_AVFOUNDATION=OFF \
    -DWITH_CAP_IOS=OFF \
    -DWITH_VTK=OFF \
    -DWITH_CUDA=OFF \
    -DWITH_CUFFT=OFF \
    -DWITH_CUBLAS=OFF \
    -DWITH_EIGEN=OFF \
    -DWITH_FFMPEG=OFF \
    -DWITH_GSTREAMER=OFF \
    -DWITH_GTK=OFF \
    -DWITH_GTK_2_X=OFF \
    -DWITH_HALIDE=OFF \
    -DWITH_VULKAN=OFF \
    -DWITH_OPENEXR=OFF \
    -DWITH_ADE=OFF \
    -DWITH_AVIF=OFF \
    -DWITH_AOM=OFF \
    -DWITH_VMAF=OFF \
    -DWITH_TIFF=OFF \
    -DWITH_WEBP=OFF \
    -DWITH_PROTOBUF=OFF \
    -DWITH_JPEG=ON \
    -DBUILD_JPEG=ON \
    -DWITH_PNG=ON \
    -DBUILD_PNG=ON \
    -DBUILD_opencv_python2=OFF \
    -DBUILD_opencv_python3=OFF \
    -DBUILD_opencv_features2d=OFF \
    -DBUILD_opencv_calib3d=OFF \
    -DBUILD_opencv_dnn=OFF \
    -DBUILD_opencv_flann=OFF \
    -DBUILD_opencv_gapi=OFF \
    -DBUILD_opencv_highgui=OFF \
    -DBUILD_opencv_java=OFF \
    -DBUILD_opencv_js=OFF \
    -DBUILD_opencv_ml=OFF \
    -DBUILD_opencv_objc=OFF \
    -DBUILD_opencv_objdetect=OFF \
    -DBUILD_opencv_photo=OFF \
    -DBUILD_opencv_python=OFF \
    -DBUILD_opencv_stiching=OFF \
    -DBUILD_opencv_video=OFF \
    -DBUILD_opencv_videoio=OFF

cmake --build . --config Release -j "$(nproc)"
cmake --install .

# Create dummy 3rdparty files (OpenCVConfig.cmake references modules we didn't build)
mkdir -p "${INSTALL_DIR}/lib/opencv4/3rdparty"
for f in liblibprotobuf.a libquirc.a libade.a; do
    echo "dummy" > "${INSTALL_DIR}/lib/opencv4/3rdparty/${f}"
done

# Cleanup to save disk space in the container
rm -rf /tmp/opencv_src /tmp/opencv_build /tmp/opencv.tar.gz
