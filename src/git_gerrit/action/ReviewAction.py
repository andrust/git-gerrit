import urwid

from git_gerrit.model.Button import Button
from git_gerrit.model.InputHandler import InputHandler

class ReviewAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        self.labels = {"Verified": 0, "Code-Review": 0}
        self.cview.add_hotkey("R", self.open_popup)
        self.radiomap = {}
        super(ReviewAction, self).__init__(Button("Review", "button", self.open_popup))

    def open_popup(self, w=None):
        for r in self.cview.change_reviewers:
            if self.cview.main.cfg['user'] == r['username'] and 'approvals' in r.keys():
                self.labels = r['approvals']
                break
        content = []
        self.radiomap = {}
        for labelname, valid_values in self.cview.change['permitted_labels'].items():
            lst = []
            rgroup = []
            lst.append(urwid.Text(labelname))
            for i in valid_values:
                default = False
                if labelname in self.labels.keys() and int(i) == int(self.labels[labelname]):
                    default = True
                radio = urwid.RadioButton(rgroup, i, state=default, on_state_change=self.set_label, user_data=(labelname, i))
                lst.append(radio)
                self.radiomap[i] = radio
            content.append(urwid.ListBox(lst))
        col = urwid.BoxAdapter((urwid.Columns(content)), 7)
        apply_ = urwid.Padding(urwid.Button("Apply", self.send_labels), 'center', 9)
        layout = urwid.ListBox([col, apply_])
        hotkeys = { 'meta s' : self.send_labels,
                    '2' : self.cr_approved,
                    '1' : self.cr_suggested,
                    '0' : self.cr_neutral,
                    'meta 1' : self.cr_disliked,
                    'meta 2' : self.cr_denied
                  }
        self.cview.main.open_popup(InputHandler(urwid.LineBox(layout), hotkeys), 10, 36)

    def send_labels(self, button=None):
        if 0 < len(self.labels.keys()):
            self.cview.main.gerrit.set_labels(self.cview.change['id'], self.cview.active_revision_sha, self.labels)
        self.cview.main.close_popup()
        self.cview.refresh()

    def set_label(self, radio, state, value):
        if state:
            label, vote = value
            self.labels[label] = int(vote)

    def cr_approved(self):
        self.radiomap['+2'].set_state(True)

    def cr_suggested(self):
        self.radiomap['+1'].set_state(True)

    def cr_neutral(self):
        self.radiomap[' 0'].set_state(True)

    def cr_disliked(self):
        self.radiomap['-1'].set_state(True)

    def cr_denied(self):
        self.radiomap['-2'].set_state(True)
