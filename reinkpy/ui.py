from . import usb, Device, EpsonDriver, PREFACE

import asciimatics as am, asciimatics.widgets as aw, asciimatics.scene, asciimatics.event
#, screen, exceptions

import re, string, sys, logging


class App:

    def __init__(self):
        self.device = aw.DropdownList(
            [('Select device…', None), *((str(d), d) for d in Device.ifind())],
            on_change=self.device_changed)
        self.brand = aw.DropdownList(
            [('Select brand…', None), ('EPSON', 'EPSON')],
            disabled=True, on_change=self.brand_changed)
        self.model = aw.DropdownList([], disabled=True, on_change=self.model_changed)
        self.ops = aw.ListBox(aw.Widget.FILL_FRAME, [], on_select=self.ops_onselect)
        self.msg = LoggingWidget()
        def prelude_cb(sel):
            if sel: raise am.exceptions.NextScene("main")
            else: quit_()
        self.gen_scenes = scener(
            prelude=[
                lambda screen: aw.PopUpDialog(screen, PREFACE, [
                    "NO, I'd rather not",
                    "YES, I shall do this",
                ], prelude_cb)
            ],
            main=[
                aw.Background,
                framer([
                    layouter([
                        (aw.Label("ReInkPy"), 1),
                        #(aw.Button("ReInkPy", quit_), 1),
                    ], [14,4,14]),
                    layouter([
                        aw.Divider(), self.device,
                        aw.Divider(), self.brand,
                        aw.Divider(), self.model,
                        aw.Divider(), self.ops,
                        aw.Divider(False, 2), self.msg,
                        # (aw.VerticalDivider(), 1)
                    ], [1,30,1], fill_frame=True)
                ],
                       height=lambda h: int(((10-h//40)/10) * h),
                       width=lambda w: int(((8-w//80)/8) * w),
                       has_border=not True, can_scroll=True, reduce_cpu=True) ]
        )

    def device_changed(self):
        self.brand.disabled = self.device.value is None
        self.brand.value = self.device.value and self.device.value.brand

    def brand_changed(self):
        if self.brand.value is None:
            self.model.options = []
            self.model.value = None
            self.model.disabled = True
        else:
            self.model.options = [('Select model…', None), ('Autodetect…', True),
                                   *((str(m), m) for m in sorted(self.driver.list_models()))]
            self.model.value = True
            self.model.disabled = False

    driver = property(lambda s: s.device.value.driver)
    def model_changed(self):
        # no loop here: configure should be idempotent
        self.model.value = self.driver.configure(self.model.value).spec.model
        if self.model.value:
            self.ops.options = [(getattr(self.driver, f).__doc__, f) for f in dir(self.driver)
                                if re.match('do_(reset_All|(?!reset))', f, re.I)]
            self.ops.disabled = False
        else:
            self.ops.options = [('(No operations available)', None)]
            self.ops.disabled = True

    def ops_onselect(self):
        if self.ops.value:
            f = getattr(self.driver, self.ops.value)
            def cb(sel):
                if sel == 1: self.run_op(f)
            # TODO: better way to discriminate write operations
            if re.search(r'reset|write', f.__doc__, re.I):
                self.ask(f"{f.__doc__}?", ["No", "Yes"], cb)
            else:
                self.run_op(f)

    def run_op(self, f):
        try:
            logging.info('Running %s', f.__name__)
            logging.info('%s:\n%r', f.__name__, f())
        except:
            logging.exception('')

    def ask(self, text, options, cb):
        p = aw.PopUpDialog(self._screen, text, options, has_shadow=True, on_close=cb)
        self._screen.current_scene.add_effect(p)

    # def show_info(self): pass

    # TODO: backup / rollback
    # def do_backup(self, fname='eeprom.txt'):
    #     "Save the current printer state (EEPROM) in a file"

    def run(self):
        def handle_input(event):
            if isinstance(event, am.event.KeyboardEvent):
                if event.key_code in (am.screen.Screen.KEY_ESCAPE,):
                    quit_()
        def play(screen, scene=None):
            self._screen = screen
            screen.play(self.gen_scenes(screen), start_scene=scene,
                        stop_on_resize=True, allow_int=True, unhandled_input=handle_input)
        last_scene = None
        while True:
            try:
                am.screen.Screen.wrapper(play, catch_interrupt=False, arguments=[last_scene])
                break
            except am.exceptions.ResizeScreenError as e:
                last_scene = e.scene


def quit_():
    raise am.exceptions.StopApplication("Quit")

def layouter(widgets, cols=[1], **kw):
    i = cols.index(max(cols))
    def make_layout(f):
        l = aw.Layout(cols, **kw)
        f.add_layout(l)
        for w in widgets:
            if not isinstance(w, tuple): w = (w, i)
            l.add_widget(*w)
        return l
    return make_layout

def framer(layouters, height=int, width=int, theme='green', **fkw):
    def make_frame(screen):
        f = aw.Frame(screen, height(screen.height), width(screen.width), **fkw)
        f.set_theme(theme)
        for l in layouters: l(f)
        f.fix()
        return f
    return make_frame

def scener(**nf):
    def make_scenes(screen):
        return [am.scene.Scene([f(screen) for f in framers], name=name)
                for (name, framers) in nf.items()]
    return make_scenes


class LoggingWidget(aw.TextBox):

    def __init__(self):
        super().__init__(22, as_string=True, line_wrap=not True, readonly=True, disabled=not True)
        logging.getLogger().addHandler(logging.StreamHandler(self))

    def write(self, msg: str):
        self.value = self.value + str(msg) + '\n'

    # MAYBE: modal dialog on level >= WARNING
    # def popup(self):


def main():
    import logging.handlers, os, time
    logging.basicConfig()
    logger = logging.getLogger()
    if not os.path.exists('logs'): os.mkdir('logs')
    logfile = os.path.join('logs', time.strftime('reinkpy-%Y%m%d.log'))
    h = logging.handlers.RotatingFileHandler(logfile, backupCount=5, delay=True)
    h.setFormatter(logger.handlers[0].formatter)
    h.doRollover()
    logger.addHandler(h)
    off = []
    for h in logger.handlers:
        if isinstance(h, logging.StreamHandler) and h.stream.name in ('<stdout>', '<stderr>'):
            off.append(h)
            logger.removeHandler(h)

    try:
        App().run()
    except:
        for h in off: logger.addHandler(h)
        logging.exception('')
    finally:
        h.close()
        if os.path.exists(logfile):
            print('Log file: ' + logfile)


if __name__ == "__main__":
    main()
