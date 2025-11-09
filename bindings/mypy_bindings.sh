#!/usr/bin/env bash
 mypy imgui_bundle \
    | grep -v "\.pyi"
