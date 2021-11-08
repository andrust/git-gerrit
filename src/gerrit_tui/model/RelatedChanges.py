import urwid
from gerrit_tui.model.SelectableListItem import SelectableListItem


class RelatedChanges(urwid.WidgetWrap):
    def __init__(self, gerrittui, change, selected_revision_sha):
        self.main = gerrittui
        super().__init__(urwid.Filler(urwid.Text("Loading...")))
        self.refresh(change, selected_revision_sha)

    def refresh(self, change, selected_revision_sha):
        rel = self.main.gerrit.related(change['id'], selected_revision_sha)
        contents = [urwid.Text("Related Changes")]
        for c in rel["changes"]:
            color = ''
            if c['status'] == 'MERGED':
                color = 'related_merged'
            elif c['status'] == 'NEW':
                if c['_revision_number'] == c['_current_revision_number']:
                    color = 'related_open_current'
                else:
                    color = 'related_open_outdated'
            elif c['status'] == 'ABANDONED':
                color = 'related_abandoned'

            line = SelectableListItem(c["commit"]["subject"][0:min(76, len(c["commit"]["subject"]))])
            urwid.connect_signal(line, "click", self.main.set_change_view, c['change_id'])
            contents.append(urwid.AttrMap(line, color))

        self._w = urwid.Filler(urwid.ListBox(contents), height=('relative', 100), valign='top', bottom=1)
