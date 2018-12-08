import urwid
import os

from Gerrit import Gerrit
from SelectableListItem import SelectableListItem
from HomeView import HomeView
from ChangeView import ChangeView
from SearchView import SearchView

class GerritTUI(object):
    def __init__(self, cfg):

        urwid.set_encoding('utf8')
        self.cfg = cfg

        tmp_dir = cfg['tmp_dir']
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        self.gerrit = Gerrit(cfg['gerrit_url'] + '/a', cfg['user'], cfg['api_token'], self.set_status)

        self.register_signals()
        self.previous_views = []

        self.main_screen = self.create_main_screen()
        self.body = HomeView(self)

        self.mainloop = urwid.MainLoop(self.main_screen, unhandled_input=self.global_keys, palette=self.setup_palette())
        self.mainloop.screen.set_terminal_properties(colors=256)

        self.overlayed = None

    def register_signals(self):
        urwid.register_signal(SelectableListItem, "click")

    def setup_palette(self):

        palette_entries = [
            "commit_sha",
            "comment_header",
            "insertion",
            "deletion",
            "filelist_stateD",
            "filelist_stateA",
            "filelist_stateM",
            "filelist_stateR",
            "filelist_comment_count",
            "bad_label",
            "good_label",
            "neutral_label",
            "change_list_owner",
            "reviewer_name",
            "job_FAILURE",
            "job_SUCCESS",
            "job_ABORTED",
            "job_STARTED",
            "job_UNSTABLE",
            "status_pending",
            "status_submittable",
            "status_conflict",
            "status_abandoned",
            "status_merged",
            "line",
            "button"
        ]
        default_palette_entry = ["", "", ""]
        theme = {}
        if "palette" in self.cfg.keys():
            theme = self.cfg["palette"]

        palette = []
        for entry in palette_entries:
            palette += self.add_palette_entry(entry, theme[entry] if entry in theme.keys() else default_palette_entry)
        return palette

    def add_palette_entry(self, id, entry):
        return [
            (id, '', '', '', entry[0], entry[1]),
            (id + ".focus", '', '', '', entry[0], entry[2]),
        ]

    @property
    def body(self):
        return self.main_screen.body.original_widget

    @body.setter
    def body(self, widget):
        self.main_screen.body = urwid.LineBox(widget)

    def set_change_view(self, change_id):
        self.previous_views.append(self.body)
        self.body = ChangeView(self, change_id)

    def set_home_view(self):
        self.previous_views.append(self.body)
        self.body = HomeView(self)

    def open_popup(self, widget, h, w, triggering_widget=None):
        self.overlayed = self.body
        self.body = urwid.Overlay(widget, self.overlayed, align='center', valign='middle', height=h, width=w)

    def close_popup(self, w=None):
        if self.overlayed is not None:
            self.body = self.overlayed
            self.overlayed = None

    def set_search_view(self):
        self.previous_views.append(self.body)
        self.body = SearchView(self)

    def global_keys(self, key):
        if key == 'q':
            raise urwid.ExitMainLoop()
        elif key == 'h':
            self.set_home_view()
        elif key == 'r':
            self.body.refresh()
        elif key == 't':
            self.set_terminal_view()
        elif key == 's':
            self.set_search_view()
        elif key == 'backspace':
            if len(self.previous_views) > 0:
                self.body = self.previous_views[-1]
                del self.previous_views[-1]
            else:
                self.set_home_view()
        elif key == 'esc':
            self.close_popup()

    def set_terminal_view(self):
        term = urwid.Terminal(["/bin/bash"], main_loop=self.mainloop, escape_sequence='meta a')
        urwid.connect_signal(term, "closed", self.set_home_view)
        self.previous_views.append(self.body)
        self.body = term

    def set_status(self, status):
        self.status_box._w = urwid.Text(status)

    def create_main_screen(self):
        title = urwid.Text('GerritTUI', align='left')
        self.status_box = urwid.WidgetWrap(urwid.Text(""))
        footer = urwid.Columns([(15, self.status_box), urwid.Text('h:Home r:Refresh q:Quit t:Terminal s:Search', align='right')])
        body = urwid.LineBox(urwid.Filler(urwid.Text('Loading')))
        return urwid.Frame(body, title, footer)

    def start(self):
        self.mainloop.run()
