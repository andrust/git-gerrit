import urwid

from Git import Git
from Button import Button
import ErrorPopup

class GitResetPrevAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        super(GitResetPrevAction, self).__init__(Button("Reset HEAD~1", "button", self.reset))

    def reset(self, w):
        git = Git()
        try:
            git.fetch(self.cview.change['revisions'][self.cview.active_revision_sha]['ref'])
            git.reset("HEAD~1")
        except Exception as e:
            ErrorPopup.display(self.cview.main, str(e))
