import urwid

from Button import Button

class InputHandler(urwid.WidgetWrap):
    def __init__(self, widget, callbacks):
        self.callbacks = callbacks
        super(InputHandler, self).__init__(widget)

    def keypress(self, size, key):
        if key in self.callbacks.iterkeys():
            self.callbacks[key]()
        else:
            #print "key:'%s' size:'%s'" % (key, str(size))
            return super(InputHandler, self).keypress(size, key)
