import urwid

from Git import Git
from Button import Button
import ErrorPopup

class DLCheckoutAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        super(DLCheckoutAction, self).__init__(Button("Checkout", "button", self.checkout))

    def checkout(self, w):
        git = Git()
        try:
            git.fetch(self.cview.change['revisions'][self.cview.active_revision_sha]['ref'])
            git.checkout(self.cview.active_revision_sha)
            ErrorPopup.display(self.cview.main, "Checkout successful")
        except Exception as e:
            ErrorPopup.display(self.cview.main, str(e))
