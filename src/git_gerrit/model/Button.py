import urwid

def Button(text, attr, callback, callback_arg=None):
    return urwid.Padding(urwid.AttrMap(urwid.Button(text, callback, callback_arg), attr, attr + ".focus"), "center", len(text) + 4)
