import urwid
from Git import Git
from Button import Button
import ErrorPopup

class DLCherryPickAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        super(DLCherryPickAction, self).__init__(Button("Cherry-Pick", "button", self.cherry_pick))

    def cherry_pick(self, w):
        git = Git()
        try:
            git.fetch(self.cview.change['revisions'][self.cview.active_revision_sha]['ref'])
            git.cherry_pick(self.cview.active_revision_sha)
            ErrorPopup.display(self.cview.main, "Cherry-Pick successful")
        except Exception as e:
            ErrorPopup.display(self.cview.main, str(e))
