import urwid

def display(gerrittui, text):
    lines = text.split('\n')
    m = 0
    for li in lines:
        m = max(m, len(li))
    txt = urwid.Filler(urwid.Text(text))
    ok = urwid.Filler(urwid.Padding(urwid.Button("OK", gerrittui.close_popup), 'center', 6))
    layout = urwid.Pile([txt, (1, ok)])
    gerrittui.open_popup(urwid.LineBox(layout), len(lines) + 3, m + 2)
