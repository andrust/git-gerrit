# -*- coding: utf-8 -*-

import urwid

from ChangeList import ChangeList
from InputHandler import InputHandler

class SearchView(urwid.WidgetWrap):
    def __init__(self, gerrittui):
        self.main = gerrittui
        self.results = urwid.WidgetWrap(urwid.Filler(urwid.Text("Enter search")))

        favorites = self.get_favorites()
        self.editor = urwid.Edit('', multiline=False)
        editor_box = urwid.LineBox(urwid.Filler(self.editor), tlcorner=u'·', tline=u'·', lline=u'·', trcorner=u'·', blcorner=u'·', rline=u'·', bline=u'·', brcorner=u'·')
        search_button = urwid.Filler(urwid.Padding(urwid.Button("search", self.search), 'center', 10))
        self.search_row = urwid.Columns([editor_box, (10, search_button)])
        layout = urwid.Pile([(1, favorites), (3, InputHandler(self.search_row, {'enter':self.search})), self.results])
        super(SearchView, self).__init__(layout)

    def get_favorites(self):
        if "predefined_search" in self.main.cfg.keys():
            favorites = []
            for title, query in self.main.cfg['predefined_search'].items():
                favorites.append((len(title) + 4, urwid.Filler(urwid.Padding(urwid.Button(title, self.do_search, query.split())))))
            return urwid.Columns(favorites)
        else:
            return urwid.Filler(urwid.Text("No favorites adefined in config"))

    def do_search(self, widget, query):
        self.editor.edit_text = ' '.join(query)
        self.results._w = ChangeList(self.main, query, [])

    def search(self, w=None):
        self.do_search(None, self.editor.edit_text.split())

    def refresh(self):
        self.results._w.refresh()
