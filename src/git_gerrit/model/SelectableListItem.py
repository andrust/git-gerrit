import urwid
from urwid.util import is_mouse_press

class SelectableListItem(urwid.SelectableIcon):
    def __init__(self, text, cursor_position=0):
        super(SelectableListItem, self).__init__(text, cursor_position)

    def keypress(self, size, key):
        if key == 'enter':
            urwid.emit_signal(self, "click")
        else:
            super(SelectableListItem, self).keypress(size, key)
            return key

    def mouse_event(self, size, event, button, x, y, focus):
        if button != 1 or not is_mouse_press(event):
            return False

        urwid.emit_signal(self, "click")
        return True
