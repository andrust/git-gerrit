import urwid

from SelectableListItem import SelectableListItem

class JenkinsComments(urwid.WidgetWrap):
    def __init__(self, gerrittui, change, selected_revision_number):
        self.main = gerrittui
        super(JenkinsComments, self).__init__(urwid.Filler(urwid.Text("Loading...")))
        self.refresh(change, selected_revision_number)


    def refresh(self, change, selected_revision_number):
        ci_id = self.main.gerrit.accounts(self.main.cfg['ci_user'])["_account_id"]

        latest_revision_number = change['revisions'][change['current_revision']]['_number']
        ci_comments = []
        for m in reversed(change['messages']):
            rev = m['_revision_number']
            if m['author']['_account_id'] == ci_id and rev == selected_revision_number:
                commenter = self.main.gerrit.accounts(m['author']['_account_id'])['username']
                date = m['date'][0:16]
                msg = urwid.Text(m['message'])
                header = urwid.SelectableIcon(("comment_header", "%13s #%2i %8s:" % (date, rev, commenter)))
                ci_comments.append(urwid.Pile([header, msg, urwid.Divider()]))
        self._w = urwid.ListBox(urwid.SimpleFocusListWalker(ci_comments))
