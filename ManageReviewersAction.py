# -*- coding: utf-8 -*-

import urwid

from Button import Button
from InputHandler import InputHandler

class ManageReviewersAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        self.reviewers_to_add = []
        self.reviewers_to_remove = []
        self.reviewers_proposed = urwid.SimpleListWalker([])
        self.editor = None
        super(ManageReviewersAction, self).__init__(Button("Set Reviewers", "button", self.open_popup))

    def apply_reviewers(self, w=None):
        for r in self.reviewers_to_remove:
            self.cview.main.gerrit.remove_reviewer(self.cview.change_id, r)
        for r in self.reviewers_to_add:
            self.cview.main.gerrit.add_reviewer(self.cview.change_id, r)
        self.reviewers_to_add = []
        self.reviewers_to_remove = []
        self.cview.main.close_popup()
        self.reviewers_proposed[:] = []
        self.cview.refresh()

    def set_reviewers_to_add(self, w=None):
        try:
            acc = self.cview.main.gerrit.accounts(self.editor.edit_text)
            self.reviewers_to_add.append(acc["_account_id"])
            self.editor.edit_text = ""
            self.reviewers_proposed.append(urwid.Text(acc["username"]))
        except Exception:
            self.editor.edit_text = "Not found"
            self.editor.edit_pos = len(self.editor.edit_text)

    def set_reviewers_to_remove(self, w, state):
        if state and w.get_label() not in self.reviewers_to_remove:
            self.reviewers_to_remove.append(w.get_label())
        else:
            while self.reviewers_to_remove.count(w.get_label()) > 0:
                self.reviewers_to_remove.remove(w.get_label())

    def open_popup(self, w):
        removable_items = []
        for r in self.cview.change["removable_reviewers"]:
            name = self.cview.main.gerrit.accounts(r["_account_id"])["username"]
            removable_items.append(urwid.CheckBox(name, on_state_change=self.set_reviewers_to_remove))

        self.editor = urwid.Edit('', edit_text='', multiline=False)
        editor_box = InputHandler(urwid.LineBox(urwid.Filler(self.editor), tlcorner=u'·', tline=u'·', lline=u'·', trcorner=u'·', blcorner=u'·', rline=u'·', bline=u'·', brcorner=u'·'),  {'enter' : self.set_reviewers_to_add})

        apply_button = urwid.Filler(urwid.Padding(urwid.Button("Apply", self.apply_reviewers), 'center', 10))
        add_button = urwid.Filler(urwid.Padding(urwid.Button("Add", self.set_reviewers_to_add), 'center', 10))

        add_row = urwid.Columns([editor_box, (8, add_button), (10, apply_button)])

        reviewers_column = urwid.Columns([urwid.ListBox(removable_items), urwid.ListBox(self.reviewers_proposed)])

        pile = urwid.Pile([(3, add_row), reviewers_column])
        self.cview.main.open_popup(InputHandler(urwid.LineBox(pile), {'ctrl ^' : self.apply_reviewers}), 15, 60)
