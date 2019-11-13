#!/usr/bin/env bash

set -euo pipefail

export LANG='en_US.UTF-8'
MISSING_DEPENDENCIES=()

function dependency_check() {
    if ! pip list 2>/dev/null | grep -q ${1}; then
        MISSING_DEPENDENCIES+=("${1}")
    fi
}

dependency_check urwid
dependency_check requests

if [ "${#MISSING_DEPENDENCIES[@]}" -ne 0 ]; then
    echo "Please install missing dependencies with the following command:"
    echo ""
    echo -n "    pip install "

    for DEP in "${MISSING_DEPENDENCIES[@]}";
    do
        echo -n "${DEP} "
    done

    echo ""
    exit 1
fi

python -B ./git-gerrit
