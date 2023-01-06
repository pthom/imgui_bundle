#!/usr/bin/env bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
REPO_DIR=$THIS_DIR/..
cd $REPO_DIR

./ci_scripts/ems_build.sh
cd build_ems_release
rsync -vaz bin pascal@traineq.org:HTML/ImGuiBundle/emscripten
