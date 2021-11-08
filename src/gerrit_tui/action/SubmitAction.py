import urwid

from gerrit_tui.model.Button import Button


class SubmitAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        self.cview.add_hotkey("S", self.submit)
        super().__init__(Button("Submit", "button", self.submit))

    def submit(self, w=None):
        self.cview.main.gerrit.submit(self.cview.change['id'], self.cview.change['current_revision'])
        self.cview.refresh()
