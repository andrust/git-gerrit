import urwid

from Button import Button

class SubmitAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        super(SubmitAction, self).__init__(Button("Submit", "button", self.submit))

    def submit(self, w):
        self.cview.main.gerrit.submit(self.cview.change['id'], self.cview.change['current_revision'])
        self.cview.refresh()
