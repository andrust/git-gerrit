import urwid
from git_gerrit.model.Git import Git
from git_gerrit.model.Button import Button
from git_gerrit.model.ErrorPopup import display

class DLCherryPickAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        super(DLCherryPickAction, self).__init__(Button("Cherry-Pick", "button", self.cherry_pick))

    def cherry_pick(self, w):
        git = Git()
        try:
            git.fetch(self.cview.change['revisions'][self.cview.active_revision_sha]['ref'])
            git.cherry_pick(self.cview.active_revision_sha)
            display(self.cview.main, "Cherry-Pick successful")
        except Exception as e:
            display(self.cview.main, str(e))
