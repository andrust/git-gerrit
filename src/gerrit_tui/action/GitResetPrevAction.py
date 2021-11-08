import urwid

from gerrit_tui.model.Git import Git
from gerrit_tui.model.Button import Button
from gerrit_tui.model.ErrorPopup import display


class GitResetPrevAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        super().__init__(Button("Reset HEAD~1", "button", self.reset))

    def reset(self, w):
        git = Git()
        try:
            git.fetch(self.cview.change['revisions'][self.cview.active_revision_sha]['ref'])
            git.reset("HEAD~1")
        except Exception as e:
            display(self.cview.main, str(e))
