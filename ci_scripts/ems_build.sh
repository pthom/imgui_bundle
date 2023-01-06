#!/usr/bin/env bash
this_dir=$(dirname -- "$0")
repo_dir=$this_dir/..


cd $repo_dir
mkdir -p build_ems_release
cd build_ems_release
source ~/emsdk/emsdk_env.sh
emcmake cmake .. -DCMAKE_BUILD_TYPE=Release
make -j
