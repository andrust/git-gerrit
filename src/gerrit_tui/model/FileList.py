import errno
import json
import os
import subprocess
import shlex
import time
import urwid

from gerrit_tui.model.SelectableListItem import SelectableListItem
from gerrit_tui.model.InputHandler import InputHandler
from gerrit_tui.model.Button import Button
from gerrit_tui.model.Git import Git

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))


class FileList(urwid.WidgetWrap):
    def __init__(self, gerrittui, change, selected_revision_sha):
        self.git = Git()
        self.sha = selected_revision_sha
        self.main = gerrittui
        self.change = change
        self.diff_against = "base"
        self.drafts = None
        super().__init__(urwid.Filler(urwid.Text("Loading...")))
        self.refresh(change, selected_revision_sha)

    def refresh(self, change, selected_revision_sha):
        self.sha = selected_revision_sha
        self.comments = self.main.gerrit.comments(change['id'])
        self.patchset = change["revisions"][self.sha]["_number"]
        self.load_drafts()

        txt = urwid.Text("Diff against:")
        self.base_select = Button("base       ", "button", self.diff_against_popup)
        diff_against_selector = urwid.Filler(urwid.Columns([(14, txt), (15, self.base_select)]))
        flist = []
        for f, desc in sorted(change['revisions'][self.sha]['files'].items()):
            old_source = f
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
            urwid.connect_signal(f_item.original_widget, "click", self.diff_prepare, (f, old_source))

            line_contents = [(2, state_text), f_item, (5, added_text), (5, deleted_text)]

            comments = self.get_comment_count(f)
            if comments is not None:
                comments_text = urwid.Text("C" + str(comments))
            else:
                comments_text = urwid.Text("")
            line_contents.append((3, urwid.AttrMap(comments_text, "filelist_comment_count")))

            drafts = self.get_draft_count(fname)
            if drafts is not None:
                drafts_text = urwid.Text("D" + str(drafts))
            else:
                drafts_text = urwid.Text("")
            line_contents.append((3, urwid.AttrMap(drafts_text, "filelist_draft_count")))

            flist.append(urwid.Columns(line_contents))

        listwalker = urwid.SimpleFocusListWalker(flist)
        urwid.connect_signal(listwalker, "modified", self.set_focus_colors, listwalker)
        layout = urwid.Pile([(1, diff_against_selector), urwid.ListBox(listwalker)])
        self._w = layout

    def load_drafts(self):
        try:
            with open(os.path.join(self.main.cfg['tmp_dir'], self.change['id'], "drafts.json"), encoding='utf-8') as f:
                self.drafts = json.load(f)
        except Exception:
            self.drafts = {}

    def get_draft_count(self, fname):
        drafts_for_patch = []
        if fname in self.drafts.keys():
            for c in self.drafts[fname]:
                if c["patch_set"] == str(self.patchset):
                    drafts_for_patch.append(c)

        if len(drafts_for_patch) > 0:
            return len(drafts_for_patch)
        else:
            return None

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
            for field, _ in listitem.contents:
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
        self.main.open_popup(InputHandler(urwid.LineBox(layout), {'ctrl ^': self.main.close_popup}), selected_revision_number + 3, 25)

    def set_selected_base(self, w, selected, value):
        if selected:
            self.diff_against = value
            if value == "base":
                self.base_select.base_widget.set_label(value)
            else:
                self.base_select.base_widget.set_label("revision " + str(value))

    def dump_comments(self, fname):
        with open(fname, "w", encoding='utf-8') as f:
            f.write(json.dumps(self.comments))

    def diff_open(self, base_fname, gerrit_fname, repo_path_gerrit):
        cmd = ["/bin/vim", "--cmd", f"""'let g:change_id = "{self.change["id"]}"'""", '-u', os.path.join(CURRENT_PATH, '..', 'util', 'diffrc'), '-d', base_fname, gerrit_fname]

        if "diff-window" not in self.main.cfg.keys() or self.main.cfg["diff-window"] == "internal" or 'TMUX' not in os.environ:
            term = urwid.Terminal([x.replace("'", "") for x in cmd], main_loop=self.main.mainloop, escape_sequence='meta a')
            term.change_focus(True)
            urwid.connect_signal(term, "closed", self.main.close_popup)
            self.main.open_popup(urwid.LineBox(term), ("relative", 90), ("relative", 90))
        else:
            tmux_cmd = ' '.join(cmd)
            if self.main.cfg["diff-window"] == "tmux-split":
                win = subprocess.check_output(shlex.split("tmux display-message -p '#I'")).strip()
                pane = subprocess.check_output(shlex.split("tmux display-message -p '#P'")).strip()
                with open('/tmp/gerrit-debug', 'w', encoding='utf-8') as dbg:
                    dbg.write(f'win: {win} pane: {pane}')
                subprocess.check_call(['tmux', 'split-window', '-t', f"{win}.{pane}", tmux_cmd])
                time.sleep(0.1)
                subprocess.check_call(['tmux', 'resize-pane', '-Z'])
            elif self.main.cfg["diff-window"] == "tmux-window":
                subprocess.check_call(['tmux', 'new-window', '-n', f'{self.sha[0:7]}~{os.path.basename(repo_path_gerrit)}', tmux_cmd])
            else:
                raise Exception("cfg.diff-window must be one of 'internal', 'tmux-window', 'tmux-split'")

    def diff_prepare(self, sources):
        tmpdir = os.path.join(self.main.cfg['tmp_dir'], self.change['id'])
        try:
            os.makedirs(tmpdir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        repo_path_gerrit, repo_path_base = sources

        # is_rename = bool(repo_path_base != repo_path_gerrit)

        # set filenames
        gerrit_fname = os.path.join(tmpdir, f'ps{self.patchset}_{os.path.basename(repo_path_gerrit)}')
        base_fname = os.path.join(tmpdir, f'ps{str(self.diff_against)}_{os.path.basename(repo_path_base)}')

        # Fetch refspec, and base refspec
        if self.diff_against == "base":
            base_sha = self.sha + '~1'
        else:
            for bsha, desc in self.change["revisions"].items():
                if desc['_number'] == self.diff_against:
                    base_sha = bsha
                    break
            self.git.fetch(self.change['revisions'][base_sha]['ref'])

        self.git.fetch(self.change['revisions'][self.sha]['ref'])

        # Dump contents of gerrit version
        self.git.get_file(self.sha, repo_path_gerrit, gerrit_fname, "DELETED_FILE")

        # Dump contents of base version
        self.git.get_file(base_sha, repo_path_base, base_fname, "NEW_FILE")

        # Dump Comments
        self.dump_comments(os.path.join(tmpdir, "comments.json"))

        # Dump diff Properties
        diff_properties = {
            "before": {"patch_set": str(self.diff_against), "fname": base_fname, "repopath": repo_path_base},
            "after": {"patch_set": str(self.patchset), "fname": gerrit_fname, "repopath": repo_path_gerrit}
        }
        with open(os.path.join(tmpdir, "diff_properties.json"), "w", encoding="utf-8") as dp:
            json.dump(diff_properties, dp)

        self.diff_open(base_fname, gerrit_fname, repo_path_gerrit)
