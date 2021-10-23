import urwid

from git_gerrit.model.SelectableListItem import SelectableListItem
from git_gerrit.model.CommentFilter import is_filtered_comment
from git_gerrit.model.Timestamp import Timestamp

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
            if 'author' in m.keys() and m['author']['_account_id'] != ci_id and not is_filtered_comment(self.main.cfg, m["message"]):
                rev = m['_revision_number']
                commenter = self.main.gerrit.accounts(m['author']['_account_id'])['username']
                date = Timestamp(m['date']).str
                msg = urwid.Text(m['message'])
                header = urwid.SelectableIcon(("comment_header", "%13s #%2i %8s:" % (date, rev, commenter)))
                human_comments.append(urwid.Pile([header, msg, urwid.Divider()]))
        self._w = urwid.ListBox(urwid.SimpleFocusListWalker(human_comments))
