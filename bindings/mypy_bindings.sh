#!/usr/bin/env bash
 mypy imgui_bundle \
    | grep -v "(default has type \"int\", argument has type \"ImColor" \
