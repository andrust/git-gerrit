# -*- coding: utf-8 -*-

import urwid

from Button import Button

class ManageReviewersAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        self.reviewers_to_add = []
        self.reviewers_to_remove = []
        super(ManageReviewersAction, self).__init__(Button("Set Reviewers", "button", self.open_popup))

    def apply_reviewers(self, w):
        for r in self.reviewers_to_remove:
            self.cview.main.gerrit.remove_reviewer(self.cview.change_id, r)
        for r in self.reviewers_to_add:
            self.cview.main.gerrit.add_reviewer(self.cview.change_id, r)
        self.reviewers_to_add = []
        self.reviewers_to_remove = []
        self.cview.main.close_popup()
        self.cview.refresh()

    def set_reviewers_to_add(self, w, editor):
        try:
            acc = self.cview.main.gerrit.accounts(editor.edit_text)
            self.reviewers_to_add.append(acc["_account_id"])
            editor.edit_text = ""
        except Exception:
            editor.edit_text = "Not found"
            editor.edit_pos = len(editor.edit_text)

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

        editor = urwid.Edit('', edit_text='', multiline=True)
        editor_box = urwid.LineBox(urwid.Filler(editor), tlcorner=u'·', tline=u'·', lline=u'·', trcorner=u'·', blcorner=u'·', rline=u'·', bline=u'·', brcorner=u'·')

        apply_button = urwid.Filler(urwid.Padding(urwid.Button("Apply", self.apply_reviewers), 'center', 10))
        add_button = urwid.Filler(urwid.Padding(urwid.Button("Add", self.set_reviewers_to_add, editor), 'center', 10))

        add_row = urwid.Columns([editor_box, add_button])
        pile = urwid.Pile([(3, add_row), urwid.ListBox(removable_items), (1, apply_button)])
        self.cview.main.open_popup(urwid.LineBox(pile), 15, 60)
