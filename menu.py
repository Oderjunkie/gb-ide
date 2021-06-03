class Menu:
    def __init__(self, font):
        self.saving = False
        self.loading = False
        self.filename = 'new'
        self.font = font
    def event(self, e):
        if self.saving or self.loading:
            if e.key == pg.K_BACKSPACE:
                if len(self.filename)>0:
                    self.filename = self.filename[:-1]
            elif e.key in [pg.K_DELETE, pg.K_LEFT, pg.K_RIGHT, pg.K_UP,
                           pg.K_DOWN, pg.K_HOME, pg.K_END]:
                return
            elif e.mod & pg.KMOD_CTRL and e.key == pg.K_c:
                self.loading = False
                self.saving = False
            elif e.unicode not in '':
                self.filename += e.unicode
        elif e.key == pg.K_s:
            self.saving = True
        elif e.key == pg.K_o:
            self.loading = True
    def draw(self, window, font):
        pass
