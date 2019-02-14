import urwid

from SelectableListItem import SelectableListItem

class ChangeList(urwid.ListBox):
    def __init__(self, gerrittui, query, options=[]):
        self.main = gerrittui
        self.q = query
        self.o = options
        if 'SUBMITTABLE' not in self.o:
            self.o.append('SUBMITTABLE')
        if 'LABELS' not in self.o:
            self.o.append('LABELS')
        body = urwid.SimpleFocusListWalker([urwid.Text("Loading")])
        urwid.connect_signal(body, "modified", self.set_focus_colors, body)
        super(ChangeList, self).__init__(body)
        self.refresh()

    def set_focus_colors(self, w):
        focused = w.focus
        for i, listitem in enumerate(w):
            for field, opt in listitem.contents:
                m = field.attr_map[None]
                if i == focused and self.focus:
                    if not m.endswith(".focus"):
                        field.attr_map = {None: m + ".focus"}
                else:
                    if m.endswith(".focus"):
                        field.attr_map = {None: m[:-6]}

    def refresh(self):
        stuff = []
        for c in self.main.gerrit.query_changes(self.q, self.o):
            project = urwid.AttrMap(urwid.Text(c['project']), "line")
            branch = urwid.AttrMap(urwid.Text(c['branch']), "line")
            ins = urwid.AttrMap(urwid.Text('+' + str(c['insertions'])), "insertion")
            dels = urwid.AttrMap(urwid.Text('-' + str(c['deletions'])), "deletion")
            owner = urwid.AttrMap(urwid.Text(self.main.gerrit.accounts(c['owner']['_account_id'])['username']), "change_list_owner")
            updated = urwid.AttrMap(urwid.Text(c['updated'][0:16]), "line")
            subject = urwid.AttrMap(SelectableListItem(c['subject']), "line")
            urwid.connect_signal(subject.original_widget, "click", self.main.set_change_view, c['id'])
            status = self.get_status(c)
            # score = self.get_score(c)
            line = urwid.Columns([(8, owner), subject, (15, project), (14, branch), (6, ins), (6, dels), (12, status), (16, updated)])
            stuff.append(line)
        self.body[:] = stuff

    def get_score(self, c):
        score_map = {
            "rejected": {"Verified": "-1", "Code-Review": "-2"},
            "disliked": {"Verified": "-1", "Code-Review": "-1"},
            "recommended": {"Verified": "1", "Code-Review": "1"},
            "approved": {"Verified": "1", "Code-Review": "2"}
        }
        labels = []
        for label in c["labels"]:
            for score in score_map.keys():
                if score in label.keys():
                    labels.append((label[score]["_account_id"], score_map[score][label]))
                    break

        return urwid.AttrMap(urwid.Text())

    def get_status(self, c):
        if c['status'] == 'NEW':
            if "mergeable" in c.keys() and "submittable" in c.keys():
                if c['mergeable']:
                    if c['submittable']:
                        return urwid.AttrMap(urwid.Text("submittable"), "status_submittable")
                    else:
                        return urwid.AttrMap(urwid.Text("pending"), "status_pending")
                else:
                    return urwid.AttrMap(urwid.Text("conflict"), "status_conflict")
            else:
                return urwid.AttrMap(urwid.Text("undefined"), "line")
        elif c['status'] == 'MERGED':
            return urwid.AttrMap(urwid.Text("merged"), "status_merged")
        elif c['status'] == 'ABANDONED':
            return urwid.AttrMap(urwid.Text("abandoned"), "status_abandoned")
        elif c['status'] == 'DRAFT':
            return urwid.AttrMap(urwid.Text("draft"), "status_draft")
        else:
            return urwid.AttrMap(urwid.Text("undefined"), "line")

    def size(self):
        return len(self.body)
