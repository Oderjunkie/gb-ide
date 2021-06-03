import pygame as pg
from menu import Menu
from pyboy import PyBoy, WindowEvent

class EmulatorMenu(Menu):
    def __init__(self, font):
        super().__init__(font)
        self.filename = 'pokered.gb'
        self.game = PyBoy(self.filename, window_type='headless')
    def event(self, e):
        if e.type == pg.KEYUP:
            if e.key == pg.K_RIGHT:
                self.game.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
            elif e.key == pg.K_LEFT:
                self.game.send_input(WindowEvent.RELEASE_ARROW_LEFT)
            elif e.key == pg.K_UP:
                self.game.send_input(WindowEvent.RELEASE_ARROW_UP)
            elif e.key == pg.K_DOWN:
                self.game.send_input(WindowEvent.RELEASE_ARROW_DOWN)
            elif e.key == pg.K_z:
                self.game.send_input(WindowEvent.RELEASE_BUTTON_A)
            elif e.key == pg.K_x:
                self.game.send_input(WindowEvent.RELEASE_BUTTON_B)
            elif e.key == pg.K_RETURN:
                self.game.send_input(WindowEvent.RELEASE_BUTTON_START)
            elif e.key == pg.K_SPACE:
                self.game.send_input(WindowEvent.RELEASE_BUTTON_SELECT)
            return
        if e.key == pg.K_RIGHT:
            self.game.send_input(WindowEvent.PRESS_ARROW_RIGHT)
        elif e.key == pg.K_LEFT:
            self.game.send_input(WindowEvent.PRESS_ARROW_LEFT)
        elif e.key == pg.K_UP:
            self.game.send_input(WindowEvent.PRESS_ARROW_UP)
        elif e.key == pg.K_DOWN:
            self.game.send_input(WindowEvent.PRESS_ARROW_DOWN)
        elif e.key == pg.K_z:
            self.game.send_input(WindowEvent.PRESS_BUTTON_A)
        elif e.key == pg.K_x:
            self.game.send_input(WindowEvent.PRESS_BUTTON_B)
        elif e.key == pg.K_RETURN:
            self.game.send_input(WindowEvent.PRESS_BUTTON_START)
        elif e.key == pg.K_SPACE:
            self.game.send_input(WindowEvent.PRESS_BUTTON_SELECT)
        elif e.key == pg.K_r:
            self.game.stop()
            self.game = PyBoy(self.filename, window_type='headless')
    def draw(self, window, total, selectedcol, unselectedcol, bgcol):
        width, height = self.font.size('M')
        scrn = self.game.botsupport_manager().screen()
        form = scrn.raw_screen_buffer_format()
        dims = scrn.raw_screen_buffer_dims()
        buff = scrn.raw_screen_buffer()
        surf = pg.image.frombuffer(buff, dims, form)
        tmpwidth = window.get_width()//2
        tmpheight = int(144*(tmpwidth/160))
        surf = pg.transform.scale(surf, (tmpwidth, tmpheight))
        window.blit(surf, ((window.get_width()-tmpwidth)//2, (window.get_height()-height*3-tmpheight)//2+height*3))
        self.game.tick()
