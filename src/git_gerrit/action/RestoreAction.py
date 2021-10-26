import urwid

from git_gerrit.model.Button import Button


class RestoreAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        super().__init__(Button("Restore", "button", self.restore))

    def restore(self, w=None):
        self.cview.main.gerrit.restore(self.cview.change['id'])
        self.cview.refresh()
