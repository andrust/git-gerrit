import urwid

from gerrit_tui.model.Git import Git
from gerrit_tui.model.Button import Button
from gerrit_tui.model.ErrorPopup import display


class DLCheckoutAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        super().__init__(Button("Checkout", "button", self.checkout))

    def checkout(self, w):
        git = Git()
        try:
            git.fetch(self.cview.change['revisions'][self.cview.active_revision_sha]['ref'])
            git.checkout(self.cview.active_revision_sha)
            display(self.cview.main, "Checkout successful")
        except Exception as e:
            display(self.cview.main, str(e))
