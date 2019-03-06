import urwid

from Button import Button

class AbandonAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        self.cview.add_hotkey("A", self.abandon)
        super(AbandonAction, self).__init__(Button("Abandon", "button", self.abandon))

    def abandon(self, w):
        self.cview.main.gerrit.abandon(self.cview.change_id)
        self.cview.refresh()
