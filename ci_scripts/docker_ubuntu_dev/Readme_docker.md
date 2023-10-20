use docker_run.py

cmake ../sources/ -DIMGUI_BUNDLE_BUILD_PYTHON=ON -DCMAKE_BUILD_TYPE=Release -DIMMVISION_FETCH_OPENCV=OFF -GNinja
ninja
