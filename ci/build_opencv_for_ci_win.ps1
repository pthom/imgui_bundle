# Pre-build minimalist static OpenCV for CI wheel builds on Windows.
# Run once per runner (via cibuildwheel before-all) so that
# all Python version builds reuse the same pre-built OpenCV.
#
# The cmake flags here must stay in sync with immvision_fetch_opencv_from_source()
# in external/immvision/immvision/cmake/find_opencv.cmake
#
# See docs/book/devel_docs/build_opencv_immvision.md for the full picture.

$ErrorActionPreference = "Stop"

$INSTALL_DIR = if ($args.Count -gt 0) { $args[0] } else { "C:\opencv_minimalist" }
$OPENCV_VERSION = "4.11.0"
$SRC_DIR = "$env:TEMP\opencv-$OPENCV_VERSION"
$BUILD_DIR = "$env:TEMP\opencv_build"

# Download OpenCV source
Write-Host "Downloading OpenCV $OPENCV_VERSION..."
$zipUrl = "https://github.com/opencv/opencv/archive/refs/tags/$OPENCV_VERSION.zip"
$zipFile = "$env:TEMP\opencv.zip"
Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile -UseBasicParsing
Expand-Archive -Path $zipFile -DestinationPath $env:TEMP -Force

# Configure — minimalist static OpenCV: only core, imgcodecs, imgproc.
# These flags are duplicated from find_opencv.cmake — keep them in sync.
New-Item -ItemType Directory -Force -Path $BUILD_DIR | Out-Null
Write-Host "Configuring OpenCV..."
cmake -S $SRC_DIR -B $BUILD_DIR `
    -G "Visual Studio 17 2022" -A x64 `
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR" `
    -DCMAKE_BUILD_TYPE=Release `
    -DINSTALL_CREATE_DISTRIB=ON `
    -DBUILD_SHARED_LIBS=OFF `
    -DBUILD_opencv_apps=OFF `
    -DBUILD_TESTS=OFF `
    -DBUILD_PERF_TESTS=OFF `
    -DWITH_OPENJPEG=OFF `
    -DWITH_JASPER=OFF `
    -DWITH_1394=OFF `
    -DWITH_AVFOUNDATION=OFF `
    -DWITH_CAP_IOS=OFF `
    -DWITH_VTK=OFF `
    -DWITH_CUDA=OFF `
    -DWITH_CUFFT=OFF `
    -DWITH_CUBLAS=OFF `
    -DWITH_EIGEN=OFF `
    -DWITH_FFMPEG=OFF `
    -DWITH_GSTREAMER=OFF `
    -DWITH_GTK=OFF `
    -DWITH_GTK_2_X=OFF `
    -DWITH_HALIDE=OFF `
    -DWITH_VULKAN=OFF `
    -DWITH_OPENEXR=OFF `
    -DWITH_ADE=OFF `
    -DWITH_AVIF=OFF `
    -DWITH_AOM=OFF `
    -DWITH_VMAF=OFF `
    -DWITH_TIFF=OFF `
    -DWITH_WEBP=OFF `
    -DWITH_PROTOBUF=OFF `
    -DWITH_JPEG=ON `
    -DBUILD_JPEG=ON `
    -DWITH_PNG=ON `
    -DBUILD_PNG=ON `
    -DBUILD_opencv_python2=OFF `
    -DBUILD_opencv_python3=OFF `
    -DBUILD_opencv_features2d=OFF `
    -DBUILD_opencv_calib3d=OFF `
    -DBUILD_opencv_dnn=OFF `
    -DBUILD_opencv_flann=OFF `
    -DBUILD_opencv_gapi=OFF `
    -DBUILD_opencv_highgui=OFF `
    -DBUILD_opencv_java=OFF `
    -DBUILD_opencv_js=OFF `
    -DBUILD_opencv_ml=OFF `
    -DBUILD_opencv_objc=OFF `
    -DBUILD_opencv_objdetect=OFF `
    -DBUILD_opencv_photo=OFF `
    -DBUILD_opencv_python=OFF `
    -DBUILD_opencv_stiching=OFF `
    -DBUILD_opencv_video=OFF `
    -DBUILD_opencv_videoio=OFF

if ($LASTEXITCODE -ne 0) { throw "OpenCV configure failed" }

# Build
Write-Host "Building OpenCV..."
cmake --build $BUILD_DIR --config Release --parallel
if ($LASTEXITCODE -ne 0) { throw "OpenCV build failed" }

# Install
Write-Host "Installing OpenCV..."
cmake --install $BUILD_DIR --config Release
if ($LASTEXITCODE -ne 0) { throw "OpenCV install failed" }

# Create dummy 3rdparty files (OpenCVConfig.cmake references modules we didn't build)
$dummyDir = "$INSTALL_DIR\x64\vc17\staticlib"
if (-not (Test-Path $dummyDir)) {
    New-Item -ItemType Directory -Force -Path $dummyDir | Out-Null
}
foreach ($f in @("libprotobuf.lib", "quirc.lib", "ade.lib")) {
    "dummy" | Out-File -FilePath "$dummyDir\$f" -Encoding ascii
}

# Cleanup
Remove-Item -Recurse -Force $zipFile, $SRC_DIR, $BUILD_DIR -ErrorAction SilentlyContinue

Write-Host "OpenCV $OPENCV_VERSION installed to $INSTALL_DIR"
