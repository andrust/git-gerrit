import urwid

from git_gerrit.model.Button import Button

class PublishAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        super(PublishAction, self).__init__(Button("Publish", "button", self.publish))

    def publish(self, w):
        self.cview.main.gerrit.publish(self.cview.change['id'], self.cview.change['current_revision'])
        self.cview.refresh()

