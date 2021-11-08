import urwid

# from gerrit_tui.model.Button import Button


class InputHandler(urwid.WidgetWrap):
    def __init__(self, widget, callbacks):
        self.callbacks = callbacks
        super().__init__(widget)

    def keypress(self, size, key):
        if key in self.callbacks.keys():
            self.callbacks[key]()
            # TODO: should we call a return here pylint inconsistent-return-statements
            return super().keypress(size, key)
        else:
            # print(f"key:'{key}' size:'{str(size)}'")
            return super().keypress(size, key)
