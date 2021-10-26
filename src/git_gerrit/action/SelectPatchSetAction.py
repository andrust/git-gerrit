import urwid

from git_gerrit.model.Button import Button
from git_gerrit.model.InputHandler import InputHandler


class SelectPatchSetAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        self.cview.add_hotkey("P", self.open_popup)
        super().__init__(Button("Select Patch", "button", self.open_popup))

    def open_popup(self, w=None):
        button_grp = []
        buttons = []
        for sha, rev in self.cview.change['revisions'].items():
            default = self.cview.active_revision_sha == sha
            num = rev['_number']
            num_text = f"{num} ({rev['kind'].lower().replace('_', ' ')})"
            buttons.append(urwid.RadioButton(button_grp, num_text, state=default, on_state_change=self.set_current_patchset, user_data=(num, sha)))
        select_button = urwid.Filler(urwid.Padding(urwid.Button("Select", self.activate_selected_revision), 'center', 10), "top")
        button_listbox = urwid.ListBox(sorted(buttons, reverse=True, key=lambda w: int(w.get_label().split()[0])))
        layout = urwid.Columns([button_listbox, select_button])
        self.cview.main.open_popup(InputHandler(urwid.LineBox(layout), {'ctrl ^': self.activate_selected_revision}), len(buttons) + 2, 50)

    def set_current_patchset(self, w, state, value):
        if state:
            num, sha = value
            self.cview.active_revision_number = num
            self.cview.active_revision_sha = sha

    def activate_selected_revision(self, w=None):
        self.cview.main.close_popup()
        self.cview.refresh()
