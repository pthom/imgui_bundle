#!/usr/bin/env bash

#
# Install conan
#
if [ $(uname) = 'Darwin' ]; then
  brew install conan
else
  python3 -m pip install conan
fi
conan profile new default --detect
if [ $(uname) = 'Linux' ]; then
  conan profile update settings.compiler.libcxx=libstdc++11 default
fi

#
# Install pybind11
#
python3 -m pip install pybind11
