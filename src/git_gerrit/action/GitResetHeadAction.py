import urwid

from git_gerrit.model.Git import Git
from git_gerrit.model.Button import Button
from git_gerrit.model.ErrorPopup import display


class GitResetHeadAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        super().__init__(Button("Reset HEAD", "button", self.reset))

    def reset(self, w):
        git = Git()
        try:
            git.fetch(self.cview.change['revisions'][self.cview.active_revision_sha]['ref'])
            git.reset("HEAD")
        except Exception as e:
            display(self.cview.main, str(e))
