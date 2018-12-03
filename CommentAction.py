# -*- coding: utf-8 -*-

import urwid

from Button import Button

class CommentAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        self.editor = urwid.Edit('', edit_text="", multiline=True)
        super(CommentAction, self).__init__(Button("Comment", "button", self.open_popup))

    def open_popup(self, w):
        txt = urwid.Filler(urwid.Text('Enter Comment'))
        editor_box = urwid.LineBox(urwid.Filler(self.editor), tlcorner=u'·', tline=u'·', lline=u'·', trcorner=u'·', blcorner=u'·', rline=u'·', bline=u'·', brcorner=u'·')
        post = urwid.Filler(urwid.Padding(urwid.Button("Post", self.post_comment), 'center', 8))
        cancel = urwid.Filler(urwid.Padding(urwid.Button("Cancel", self.cview.main.close_popup), 'center', 10))
        buttons = urwid.Columns([post, cancel])
        pile = urwid.Pile([(1, txt), editor_box, (1, buttons)])
        self.cview.main.open_popup(urwid.LineBox(pile), 15, 70)

    def set_comment(self, w, value):
        self.message = value

    def post_comment(self, w):
        self.cview.main.gerrit.post_comment(self.cview.change['id'], self.cview.active_revision_sha, self.editor.edit_text)
        self.editor.edit_text = ""
        self.editor.edit_pos = 0
        self.cview.main.close_popup()
        self.cview.refresh()
