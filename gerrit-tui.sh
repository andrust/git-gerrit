#!/usr/bin/env bash

set -euo pipefail

GIT_REPO="${GIT_REPO:-$(git -C $(dirname ${BASH_SOURCE[0]}) rev-parse --show-toplevel)}"
export PYTHONPATH="${GIT_REPO}/src"
export LANG='en_US.UTF-8'
MISSING_DEPENDENCIES=()

function dependency_check() {
    installed_pip_packages=$(pip list 2>/dev/null)
    for DEP in "${@}";
    do
        if ! echo "${installed_pip_packages}" | grep -q "${DEP}"; then
            MISSING_DEPENDENCIES+=("${DEP}")
        fi
    done
}

dependency_check urwid requests python-dateutil

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

python3 -B -m gerrit_tui
