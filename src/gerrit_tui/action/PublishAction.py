import urwid

from gerrit_tui.model.Button import Button


class PublishAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        super().__init__(Button("Publish", "button", self.publish))

    def publish(self, w):
        self.cview.main.gerrit.publish(self.cview.change['id'], self.cview.change['current_revision'])
        self.cview.refresh()
