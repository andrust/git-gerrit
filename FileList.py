import urwid
import os
import json

from SelectableListItem import SelectableListItem
from Button import Button
from Git import Git

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

class FileList(urwid.WidgetWrap):
    def __init__(self, gerrittui, change, selected_revision_sha):
        self.git = Git()
        self.sha = selected_revision_sha
        self.main = gerrittui
        self.change = change
        self.diff_against = "base"
        super(FileList, self).__init__(urwid.Filler(urwid.Text("Loading...")))
        self.refresh(change, selected_revision_sha)

    def refresh(self, change, selected_revision_sha):
        self.sha = selected_revision_sha
        self.comments = self.main.gerrit.comments(change['id'])
        self.patchset = change["revisions"][self.sha]["_number"]

        txt = urwid.Text("Diff against:")
        self.base_select = Button("base       ", "button", self.diff_against_popup)
        diff_against_selector = urwid.Filler(urwid.Columns([(14, txt), (15, self.base_select)]))
        flist = []
        for f, desc in sorted(change['revisions'][self.sha]['files'].iteritems()):
            old_source = None
            fname = f
            state = "M"
            if "status" in desc.keys():
                state = desc['status']
                if state == 'R':
                    old_source = desc['old_path']
                    fname += '\n    ' + desc['old_path']
            state_text = urwid.AttrMap(urwid.Text(state), "filelist_state" + state)

            added = ""
            if "lines_inserted" in desc.keys():
                added = '+' + str(desc['lines_inserted'])
            added_text = urwid.AttrMap(urwid.Text(added), "insertion")

            deleted = ""
            if "lines_deleted" in desc.keys():
                deleted = '-' + str(desc['lines_deleted'])
            deleted_text = urwid.AttrMap(urwid.Text(deleted), "deletion")

            f_item = urwid.AttrMap(SelectableListItem(fname), "line")
            urwid.connect_signal(f_item.original_widget, "click", self.diff_popup, (f, old_source))

            line_contents = [(2, state_text), f_item, (5, added_text), (5, deleted_text)]

            comments = self.get_comment_count(f)
            if comments is not None:
                comments_text = urwid.Text("C" + str(comments))
            else:
                comments_text = urwid.Text("")
            line_contents.append((3, urwid.AttrMap(comments_text, "filelist_comment_count")))

            flist.append(urwid.Columns(line_contents))

        listwalker = urwid.SimpleFocusListWalker(flist)
        urwid.connect_signal(listwalker, "modified", self.set_focus_colors, listwalker)
        layout = urwid.Pile([(1, diff_against_selector), urwid.ListBox(listwalker)])
        self._w = layout

    def get_comment_count(self, fname):
        comments_for_patch = []
        if fname in self.comments.keys():
            for c in self.comments[fname]:
                if c["patch_set"] == self.patchset:
                    comments_for_patch.append(c)

        if len(comments_for_patch) > 0:
            return len(comments_for_patch)
        else:
            return None

    def set_focus_colors(self, w):
        focused = w.focus
        for i, listitem in enumerate(w):
            for field, opt in listitem.contents:
                m = field.attr_map[None]
                if i == focused:
                    if not m.endswith(".focus"):
                        field.attr_map = {None: m + ".focus"}
                else:
                    if m.endswith(".focus"):
                        field.attr_map = {None: m[:-6]}

    def diff_against_popup(self, w):
        self.set_selected_base(None, True, "base")
        selected_revision_number = self.change['revisions'][self.sha]["_number"]
        gr = []
        radios = [urwid.RadioButton(gr, "base", True, self.set_selected_base, "base")]
        for i in range(1, selected_revision_number):
            radios.append(urwid.RadioButton(gr, str(i), False, self.set_selected_base, i))
        radio_list = urwid.ListBox(radios)
        select_button = urwid.Filler(urwid.Padding(urwid.Button("Select", self.main.close_popup), 'center', 10), "top")
        layout = urwid.Columns([radio_list, select_button])
        self.main.open_popup(urwid.LineBox(layout), selected_revision_number + 3, 25)

    def set_selected_base(self, w, selected, value):
        if selected:
            self.diff_against = value
            if value == "base":
                self.base_select.base_widget.set_label(value)
            else:
                self.base_select.base_widget.set_label("revision " + str(value))

    def dump_comments(self, fname):
        with open(fname, "w") as f:
            f.write(json.dumps(self.comments))

    def diff_popup(self, sources):
        source, old_path = sources
        tmpdir = self.main.cfg['tmp_dir']
        gerrit_fname = os.path.join(tmpdir, 'ps%d_%s' % (self.patchset, os.path.basename(source)))
        if old_path:
            base_fname = os.path.join(tmpdir, 'ps%s_%s' % (str(self.diff_against), os.path.basename(old_path)))
        else:
            base_fname = os.path.join(tmpdir, 'ps%s_%s' % (str(self.diff_against), os.path.basename(source)))

        base_sha = self.sha + '~1'
        if self.diff_against != "base":
            for bsha, desc in self.change["revisions"].iteritems():
                if desc['_number'] == self.diff_against:
                    base_sha = bsha
                    break
            self.git.fetch(self.change['revisions'][base_sha]['ref'])

        self.git.fetch(self.change['revisions'][self.sha]['ref'])
        self.git.get_file(self.sha, source, gerrit_fname, "DELETED_FILE")
        if old_path:
            self.git.get_file(base_sha, old_path, base_fname, "NEW_FILE")
        else:
            self.git.get_file(base_sha, source, base_fname, "NEW_FILE")

        comments_file = os.path.join(self.main.cfg['tmp_dir'], "comments")
        self.dump_comments(comments_file)
        if 'TMUX' in os.environ:
            os.system("tmux new-window -nsinter '" + ' '.join(["/bin/vim", '-u', os.path.join(CURRENT_PATH, 'diffrc'), '-d', base_fname, gerrit_fname]) + "'")
        else:
            term = urwid.Terminal(["/bin/vim", '-u', os.path.join(CURRENT_PATH, 'diffrc'), '-d', base_fname, gerrit_fname], main_loop=self.main.mainloop, escape_sequence='meta a')
            term.change_focus(True)
            urwid.connect_signal(term, "closed", self.main.close_popup)
            self.main.open_popup(urwid.LineBox(term), ("relative", 90), ("relative", 90))
