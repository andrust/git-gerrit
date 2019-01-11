# -*- coding: utf-8 -*-

import urwid
import os
import json

from Button import Button

class CommentAction(urwid.WidgetWrap):
    def __init__(self, chageview):
        self.cview = chageview
        self.editor = urwid.Edit('', edit_text="", multiline=True)
        self.file_comments = {}
        self.drafts_left = {}
        self.file_comments_list = urwid.SimpleListWalker([])
        super(CommentAction, self).__init__(Button("Comment", "button", self.open_popup))

    def load_drafts(self):
        try:
            self.drafts_left = {}
            draft_file = os.path.join(self.cview.main.cfg['tmp_dir'], "drafts.json")
            with open(draft_file, "r") as f:
                drafts = json.load(f)
                comments_for_revision = {}
                for path, comments in drafts.iteritems():
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

        except OSError:
            return None

    def remove_posted_drafts(self):
        draft_file = os.path.join(self.cview.main.cfg['tmp_dir'], "drafts.json")
        with open(draft_file, "w") as f:
            json.dump(self.drafts_left, f)


    def open_popup(self, w):
        self.file_comments = self.load_drafts()
        txt = urwid.Filler(urwid.Text('Enter Comment'))
        editor_box = urwid.LineBox(urwid.Filler(self.editor), tlcorner=u'·', tline=u'·', lline=u'·', trcorner=u'·', blcorner=u'·', rline=u'·', bline=u'·', brcorner=u'·')
        post = urwid.Filler(urwid.Padding(urwid.Button("Post", self.post_comment), 'center', 8))
        cancel = urwid.Filler(urwid.Padding(urwid.Button("Cancel", self.cview.main.close_popup), 'center', 10))
        buttons = urwid.Columns([post, cancel])
        pile = urwid.Pile([(1, txt), editor_box, (6, urwid.ListBox(self.file_comments_list)), (1, buttons)])
        self.cview.main.open_popup(urwid.LineBox(pile), 21, 70)

    def set_comment(self, w, value):
        self.message = value

    def post_comment(self, w):
        self.cview.main.gerrit.post_comment(self.cview.change['id'], self.cview.active_revision_sha, self.editor.edit_text, self.file_comments)
        self.remove_posted_drafts()
        self.editor.edit_text = ""
        self.editor.edit_pos = 0
        self.cview.main.close_popup()
        self.cview.refresh()
