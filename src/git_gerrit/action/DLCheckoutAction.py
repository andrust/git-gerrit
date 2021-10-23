import urwid

from git_gerrit.model.Git import Git
from git_gerrit.model.Button import Button
from git_gerrit.model.ErrorPopup import display

class DLCheckoutAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        super(DLCheckoutAction, self).__init__(Button("Checkout", "button", self.checkout))

    def checkout(self, w):
        git = Git()
        try:
            git.fetch(self.cview.change['revisions'][self.cview.active_revision_sha]['ref'])
            git.checkout(self.cview.active_revision_sha)
            display(self.cview.main, "Checkout successful")
        except Exception as e:
            display(self.cview.main, str(e))
