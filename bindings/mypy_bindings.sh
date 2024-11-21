#!/usr/bin/env bash
 mypy imgui_bundle \
    | grep -v "\.pyi" \
    | grep -v " Missing type parameters for generic type \"ndarray\"" \
    | grep -v "will never be matched" \
    | grep -v "Single overload definition"


