# -*- coding: utf-8 -*-

import urwid

from ChangeList import ChangeList

class HomeView(urwid.WidgetWrap):
    def __init__(self, gerrittui):
        self.outgoing = ChangeList(gerrittui, ['owner:self', 'status:open'])
        self.outgoing_box = urwid.LineBox(self.outgoing, 'Outgoing (' + str(self.outgoing.size()) + ')', 'left', tlcorner='*', tline=' ', lline='', trcorner='', blcorner='', rline='', bline='', brcorner='')

        self.incoming_done = ChangeList(gerrittui, 'reviewer:self status:open -owner:self AND ( -label:Code-Review=0,self OR ( label:Code-Review=-2,user=self AND reviewedby:self ) )'.split())
        self.incoming_done_box = urwid.LineBox(self.incoming_done, 'Incoming Seen (' + str(self.incoming_done.size()) + ')', 'left', tlcorner='*', tline=' ', lline='', trcorner='', blcorner='', rline='', bline='', brcorner='')

        self.incoming = ChangeList(gerrittui, 'reviewer:self status:open -owner:self AND ( label:Code-Review=0,self OR ( label:Code-Review=-2,user=self AND -reviewedby:self ) )'.split())
        self.incoming_box = urwid.LineBox(self.incoming, 'Incoming New (' + str(self.incoming.size()) + ')', 'left', tlcorner='*', tline=' ', lline='', trcorner='', blcorner='', rline='', bline='', brcorner='')

        pile = urwid.Pile([('weight', self.outgoing.size() + 1, self.outgoing_box), (1, urwid.Filler(urwid.Divider(u'·'))), ('weight', self.incoming.size() + 1, self.incoming_box), (1, urwid.Filler(urwid.Divider(u'·'))), ('weight', self.incoming_done.size() + 1, self.incoming_done_box)])
        super(HomeView, self).__init__(pile)

    def refresh(self):
        self.incoming.refresh()
        self.incoming_box.set_title('Incoming New (' + str(self.incoming.size()) + ')')

        self.outgoing.refresh()
        self.outgoing_box.set_title('Outgoing (' + str(self.outgoing.size()) + ')')

        self.incoming_done.refresh()
        self.incoming_done_box.set_title('Incoming Seen (' + str(self.incoming_done.size()) + ')')
