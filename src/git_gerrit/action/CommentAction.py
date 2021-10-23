# -*- coding: utf-8 -*-

import urwid
import os
import json

from git_gerrit.model.Button import Button
from git_gerrit.model.InputHandler import InputHandler

class CommentAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        self.editor = urwid.Edit('', edit_text="", multiline=True)
        self.file_comments = {}
        self.drafts_left = {}
        self.file_comments_list = urwid.SimpleListWalker([])
        self.cview.add_hotkey("C", self.open_popup)
        super(CommentAction, self).__init__(Button("Comment", "button", self.open_popup))

    def load_drafts(self):
        try:
            self.drafts_left = {}
            draft_file = os.path.join(self.cview.main.cfg['tmp_dir'], self.cview.change['id'], "drafts.json")
            with open(draft_file, "r") as f:
                drafts = json.load(f)
                comments_for_revision = {}
                for path, comments in drafts.items():
                    comments_for_path = []
                    drafts_left_for_path = []
                    for c in comments:
                        if c['patch_set'] == str(self.cview.active_revision_number):
                            comments_for_path.append({"line" : c["line"], "message": c["message"]})
                            self.file_comments_list.append(urwid.Text(path + ":" + str(c["line"])))
                            self.file_comments_list.append(urwid.Text(c["message"]))
                        elif c['patch_set'] == "base":
                            comments_for_path.append({"line" : c["line"], "message": c["message"], "side": "PARENT"})
                            self.file_comments_list.append(urwid.Text(path + ":" + str(c["line"]) + " (base)"))
                            self.file_comments_list.append(urwid.Text(c["message"]))
                        else:
                            drafts_left_for_path.append(c)

                    if len(drafts_left_for_path) > 0:
                        self.drafts_left[path] = drafts_left_for_path

                    if len(comments_for_path) > 0:
                        comments_for_revision[path] = comments_for_path

                if len(comments_for_revision.keys()) == 0:
                    return None
                else:
                    return comments_for_revision

        except IOError:
            return None

    def remove_posted_drafts(self):
        dir_path = os.path.join(self.cview.main.cfg['tmp_dir'], self.cview.change['id'])
        draft_file = os.path.join(dir_path, "drafts.json")
        if not os.path.exists(dir_path):
            os.makedirs(os.path.join(self.cview.main.cfg['tmp_dir'], self.cview.change['id']))
        with open(draft_file, "w") as f:
            json.dump(self.drafts_left, f)


    def open_popup(self, w=None):
        self.file_comments = self.load_drafts()
        txt = urwid.Filler(urwid.Text('Enter Comment'))
        editor_box = urwid.LineBox(urwid.Filler(self.editor), tlcorner=u'·', tline=u'·', lline=u'·', trcorner=u'·', blcorner=u'·', rline=u'·', bline=u'·', brcorner=u'·')
        post = urwid.Filler(urwid.Padding(urwid.Button("Post", self.post_comment), 'center', 8))
        cancel = urwid.Filler(urwid.Padding(urwid.Button("Cancel", self.cview.main.close_popup), 'center', 10))
        buttons = urwid.Columns([post, cancel])
        pile = urwid.Pile([(1, txt), editor_box, (6, urwid.ListBox(self.file_comments_list)), (1, buttons)])
        self.cview.main.open_popup(InputHandler(urwid.LineBox(pile), {'meta s' : self.post_comment}), 21, 70)

    def set_comment(self, w, value):
        self.message = value

    def post_comment(self, w=None):
        self.cview.main.gerrit.post_comment(self.cview.change['id'], self.cview.active_revision_sha, self.editor.edit_text, self.file_comments)
        self.remove_posted_drafts()
        self.editor.edit_text = ""
        self.editor.edit_pos = 0
        self.cview.main.close_popup()
        self.cview.refresh()
