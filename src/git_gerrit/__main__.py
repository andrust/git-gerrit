#!/usr/bin/python -B
# -*- coding: utf-8 -*-

import json
import os
import sys
import shutil

from git_gerrit.model.GerritTUI import GerritTUI

def cleanup(tmpdir):
    for entry in os.listdir(tmpdir):
        entrypath = os.path.join(tmpdir, entry)
        if os.path.isdir(entrypath):
            draftpath = os.path.join(entrypath, "drafts.json")
            if os.path.exists(draftpath):
                with open(draftpath, "r") as f:
                    if len(json.load(f)) == 0:
                        shutil.rmtree(entrypath)
            else:
                shutil.rmtree(entrypath)
        else:
            os.unlink(entrypath)


if __name__ == '__main__':
    if not "LANG" in os.environ.keys():
        print("LANG environment variable not setted properly!")
        exit()
    elif not "utf-8" in os.environ["LANG"].lower():
        print("LANG environment variable needs to be utf-8!")
        exit()

    rcpath = os.path.join(os.path.expanduser('~'), '.gerritrc.json')

    if not os.path.isfile(rcpath):
        print(f"Please create your config file in {rcpath} based on default_config.json!")
        exit()

    cfg = None
    with open(rcpath, 'r') as f:
        cfg = json.load(f)

    GerritTUI(cfg).start()

    cleanup(cfg['tmp_dir'])


    os.system('clear')
