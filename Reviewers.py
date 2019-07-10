import urwid

class Reviewers(urwid.WidgetWrap):
    def __init__(self, reviewers, label_types):
        super(Reviewers, self).__init__(urwid.Filler(urwid.Text("Loading...")))
        self.label_types = label_types
        self.refresh(reviewers)

    def get_color(self, v):
        a = v.strip()
        if a == '-2':
            return "bad_label"
        elif a == '-1':
            return "bad_label"
        elif a == '0':
            return "neutral_label"
        elif a == '+1':
            return "good_label"
        elif a == '+2':
            return "good_label"

    def get_title_row(self):
        title_row = ["%10s" % ('id',)]
        for la in self.label_types:
            title_row.append(self.get_short_name(la))

        return [" ".join(title_row)]

    def get_short_name(self, name):
        short_name = ""
        for word in name.split('-'):
            short_name += word.upper()[0]
        if len(short_name) > 3:
            short_name = short_name[:3]
        return "%3s" % (short_name)


    def get_reviewer_row(self, r):
        vote = []
        for la in self.label_types:
            if la in r['approvals'].keys():
                vote.append(r['approvals'][la].strip())
            else:
                vote.append("0")
        return vote


    def refresh(self, reviewers):
        votes = {}

        rows = self.get_title_row()

        for r in reviewers:
            if 'approvals' in r.keys():
                votes[r['username']] = self.get_reviewer_row(r)

        for u in votes.keys():
            row_content = [("reviewer_name", "%10s" % u)]
            for v in votes[u]:
                row_content += [" ", (self.get_color(v), "%3s" % (v))]
            rows.append(row_content)

        self._w = urwid.ListBox([urwid.Text(i) for i in rows])
