import re

def is_filtered_comment(cfg, comment):
    if "comment_filter" in cfg.keys():
        for pattern in cfg["comment_filter"]:
            if re.search(pattern, comment):
                return True
    return False
