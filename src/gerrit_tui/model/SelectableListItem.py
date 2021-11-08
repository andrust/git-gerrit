import urwid
from urwid.util import is_mouse_press


class SelectableListItem(urwid.SelectableIcon):
    def keypress(self, size, key):
        if key == 'enter':
            urwid.emit_signal(self, "click")
        else:
            super().keypress(size, key)
        return key

    def mouse_event(self, size, event, button, x, y, focus):
        if button != 1 or not is_mouse_press(event):
            return False

        urwid.emit_signal(self, "click")
        return True
