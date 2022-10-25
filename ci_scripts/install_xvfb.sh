#!/usr/bin/env bash

if [ $(uname) = 'Linux' ]; then
  sudo apt-get update && sudo apt-get install -y xvfb icewm libglapi-mesa
  Xvfb -screen 0 1280x1024x16 & sleep 1 && DISPLAY=:0 icewm & sleep 3
fi
