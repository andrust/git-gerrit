import urwid

from SelectableListItem import SelectableListItem

class Comments(urwid.WidgetWrap):
    def __init__(self, gerrittui, change):
        self.main = gerrittui
        super(Comments, self).__init__(urwid.Filler(urwid.Text("Loading...")))
        self.refresh(change)


    def refresh(self, change):
        if 'ci' in self.main.cfg:
            ci_id = self.main.gerrit.accounts(self.main.cfg['ci']['ci_user'])["_account_id"]
        else:
            ci_id = ""

        human_comments = []
        for m in reversed(change['messages']):
            if m['author']['_account_id'] != ci_id:
                rev = m['_revision_number']
                commenter = self.main.gerrit.accounts(m['author']['_account_id'])['username']
                date = m['date'][0:16]
                msg = urwid.Text(m['message'])
                header = urwid.SelectableIcon(("comment_header", "%13s #%2i %8s:" % (date, rev, commenter)))
                human_comments.append(urwid.Pile([header, msg, urwid.Divider()]))
        self._w = urwid.ListBox(urwid.SimpleFocusListWalker(human_comments))
