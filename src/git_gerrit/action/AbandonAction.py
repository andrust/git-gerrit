import urwid

from git_gerrit.model.Button import Button


class AbandonAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        self.cview.add_hotkey("A", self.abandon)
        super().__init__(Button("Abandon", "button", self.abandon))

    def abandon(self, w):
        self.cview.main.gerrit.abandon(self.cview.change_id)
        self.cview.refresh()
