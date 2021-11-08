#!/usr/bin/python -B
# -*- coding: utf-8 -*-

import json
import os
import sys
import shutil

from gerrit_tui.model.GerritTUI import GerritTUI


def cleanup(tmpdir):
    for entry in os.listdir(tmpdir):
        entrypath = os.path.join(tmpdir, entry)
        if os.path.isdir(entrypath):
            draftpath = os.path.join(entrypath, "drafts.json")
            if os.path.exists(draftpath):
                with open(draftpath, "r", encoding='utf-8') as f:
                    if len(json.load(f)) == 0:
                        shutil.rmtree(entrypath)
            else:
                shutil.rmtree(entrypath)
        else:
            os.unlink(entrypath)


def main():
    if "LANG" not in os.environ:
        print("LANG environment variable not setted properly!")
        sys.exit()
    elif "utf-8" not in os.environ["LANG"].lower():
        print("LANG environment variable needs to be utf-8!")
        sys.exit()

    rcpath = os.path.join(os.path.expanduser('~'), '.gerritrc.json')

    if not os.path.isfile(rcpath):
        print(f"Please create your config file in {rcpath} based on default_config.json!")
        sys.exit()

    cfg = None
    with open(rcpath, 'r', encoding='utf-8') as cfg_file:
        cfg = json.load(cfg_file)

    GerritTUI(cfg).start()

    cleanup(cfg['tmp_dir'])

    os.system('clear')


if __name__ == '__main__':
    main()
