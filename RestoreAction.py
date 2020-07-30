import urwid

from Button import Button

class RestoreAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        super(RestoreAction, self).__init__(Button("Restore", "button", self.restore))

    def restore(self, w=None):
        self.cview.main.gerrit.restore(self.cview.change['id'])
        self.cview.refresh()

