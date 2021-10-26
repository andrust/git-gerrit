import urwid


class CommitMsg(urwid.WidgetWrap):
    def __init__(self, change, selected_revision_sha):
        super().__init__(urwid.Filler(urwid.Text("Loading...")))
        self.refresh(change, selected_revision_sha)

    def refresh(self, change, selected_revision_sha):
        msg = change["revisions"][selected_revision_sha]["commit"]["message"]
        self._w = urwid.ListBox([urwid.Text(('commit_sha', selected_revision_sha)), urwid.Text(msg)])
