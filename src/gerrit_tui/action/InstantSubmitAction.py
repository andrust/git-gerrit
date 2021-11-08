import urwid

from gerrit_tui.model.Button import Button


class InstantSubmitAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        super().__init__(Button("Instant Submit", "button", self.instant_submit))

    def instant_submit(self, w):
        labels = {"Verified": 1, "Code-Review": 2}
        self.cview.main.gerrit.set_labels(self.cview.change_id, self.cview.change['current_revision'], labels)
        self.cview.main.gerrit.submit(self.cview.change_id, self.cview.change['current_revision'])
        self.cview.refresh()
