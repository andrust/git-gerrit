import urwid

class Reviewers(urwid.WidgetWrap):
    def __init__(self, reviewers):
        super(Reviewers, self).__init__(urwid.Filler(urwid.Text("Loading...")))
        self.refresh(reviewers)

    def get_color(self, a):
        if a == '-2':
            return "bad_label"
        elif a == '-1':
            return "bad_label"
        elif a == ' 0':
            return "neutral_label"
        elif a == '+1':
            return "good_label"
        elif a == '+2':
            return "good_label"


    def refresh(self, reviewers):
        rows = ["%10s  V CR" % ('id',)]
        for r in reviewers:
            if 'approvals' in r.keys():
                v = " 0"
                cr = " 0"
                if 'Verified' in r['approvals'].keys():
                    v = "%2s" % r['approvals']['Verified']
                if 'Code-Review' in r['approvals'].keys():
                    cr = "%2s" % r['approvals']['Code-Review']

                user = "%10s" % r['username']
                rows.append([("reviewer_name", user), " ", (self.get_color(v), v), " ", (self.get_color(cr), cr)])

        self._w = urwid.ListBox([urwid.Text(i) for i in rows])
