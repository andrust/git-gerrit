import urwid

from Button import Button
from InputHandler import InputHandler

class ReviewAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        self.labels = {"Verified": 0, "Code-Review": 0}
        super(ReviewAction, self).__init__(Button("Review", "button", self.open_popup))

    def open_popup(self, w):
        for r in self.cview.change_reviewers:
            if self.cview.main.cfg['user'] == r['username'] and 'approvals' in r.keys():
                self.labels = r['approvals']
                break
        content = []
        for labelname, valid_values in self.cview.change['permitted_labels'].iteritems():
            lst = []
            rgroup = []
            lst.append(urwid.Text(labelname))
            for i in valid_values:
                default = False
                if int(i) == int(self.labels[labelname]):
                    default = True
                lst.append(urwid.RadioButton(rgroup, i, state=default, on_state_change=self.set_label, user_data=(labelname, i)))
            content.append(urwid.ListBox(lst))
        col = urwid.BoxAdapter((urwid.Columns(content)), 7)
        apply_ = urwid.Padding(urwid.Button("Apply", self.send_labels), 'center', 9)
        layout = urwid.ListBox([col, apply_])
        self.cview.main.open_popup(InputHandler(urwid.LineBox(layout), {'ctrl ^' : self.send_labels}), 10, 26)

    def send_labels(self, button=None):
        if 0 < len(self.labels.keys()):
            self.cview.main.gerrit.set_labels(self.cview.change['id'], self.cview.active_revision_sha, self.labels)
        self.cview.main.close_popup()
        self.cview.refresh()

    def set_label(self, radio, state, value):
        if state:
            label, vote = value
            self.labels[label] = int(vote)
