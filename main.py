import pygame as pg

from codemenu import CodeMenu
from tilesetmenu import TilesetMenu
from musicmenu import MusicMenu
from emulatormenu import EmulatorMenu

class App:
    def __init__(self):
        pg.init()
        pg.display.set_caption('GB IDE')
        self.window = pg.display.set_mode((853, 480), pg.DOUBLEBUF | pg.RESIZABLE)
        self.window.set_alpha(None)
        self.clock = pg.time.Clock()
        self.running = True
        self.mode = 'code'
        self.createFont = lambda x: pg.font.Font('./tic-80-wide-font/tic-80-wide-font.ttf', x)
        #self.createFont = lambda x: pg.font.SysFont('Arial', x)
        #self.createFont = lambda x: pg.font.SysFont('Courier New', x)
        self.height = 18
        self.total = 0
        self.font = self.createFont(self.height)        
        pg.key.set_repeat(250, 40)
        self.code = CodeMenu(self.font)
        self.tileset = TilesetMenu(self.font)
        self.music = MusicMenu(self.font)
        self.emulator = EmulatorMenu(self.font)
    def compilerom(self):
        pass
    def run_wrap(self):
        try:
            self.run()
        except KeyboardInterrupt:
            pg.quit()
    def run(self):
        while self.running:
            self.window.fill((0, 0, 0))
            delta = self.clock.tick(60)/1000
            self.total += delta
            width, height = self.font.size('M')
            for e in pg.event.get():
                if e.type == pg.VIDEORESIZE:
                    self.window = pg.display.set_mode(e.size, pg.DOUBLEBUF | pg.RESIZABLE)
                if e.type == pg.QUIT:
                    self.running = False
                    break
                if self.mode == 'emulator' and e.type in [pg.KEYDOWN, pg.KEYUP]:
                    self.emulator.event(e)
                if e.type == pg.KEYDOWN:
                    if e.mod & pg.KMOD_CTRL:
                        if e.key == pg.K_MINUS:
                            self.height -= 1 if (e.mod & pg.KMOD_SHIFT)!=0 else 6
                            self.font = self.createFont(self.height)
                            self.code.font = self.font
                            self.screencol = 0
                        elif e.key == pg.K_EQUALS:
                            self.height += 1 if (e.mod & pg.KMOD_SHIFT)!=0 else 6
                            self.font = self.createFont(self.height)
                            self.code.font = self.font
                            self.screencol = 0
                        elif e.key == pg.K_RETURN:
                            if self.window.get_flags() & pg.FULLSCREEN:
                                self.window = pg.display.set_mode(self.window.get_size(), pg.DOUBLEBUF | pg.RESIZABLE)
                            else:
                                self.window = pg.display.set_mode(pg.display.list_modes()[0], pg.DOUBLEBUF | pg.RESIZABLE | pg.FULLSCREEN)
                    if e.key == pg.K_F1:
                        self.mode = 'code'
                    elif e.key == pg.K_F2:
                        self.mode = 'tileset'
                    elif e.key == pg.K_F3:
                        self.mode = 'map'
                    elif e.key == pg.K_F4:
                        self.mode = 'music'
                    elif e.key == pg.K_F5:
                        self.compilerom()
                        self.mode = 'emulator'
                    else:
                        getattr(self, self.mode, self.code).event(e)
            selectedcol = (0, 162, 232)
            unselectedcol = (48, 51, 163)
            bgcol = (63, 72, 204)
            pg.draw.rect(self.window, bgcol, pg.Rect((0, 0), (self.window.get_width(), height*3)))
            codecolor = selectedcol if self.mode=='code' else unselectedcol
            tilecolor = selectedcol if self.mode=='tileset' else unselectedcol
            mapcolor = selectedcol if self.mode=='map' else unselectedcol
            muscolor = selectedcol if self.mode=='music' else unselectedcol
            emucolor = selectedcol if self.mode=='emulator' else unselectedcol
            self.window.blit(self.font.render('Code', False, (255, 255, 255), codecolor), (height, height))
            self.window.blit(self.font.render('Tileset', False, (255, 255, 255), tilecolor), (height+self.font.size('Code ')[0], height))
            self.window.blit(self.font.render('Map', False, (255, 255, 255), mapcolor), (height+self.font.size('Code Tileset ')[0], height))
            self.window.blit(self.font.render('Music', False, (255, 255, 255), muscolor), (height+self.font.size('Code Tileset Map ')[0], height))
            self.window.blit(self.font.render('Emulator', False, (255, 255, 255), emucolor), (height+self.font.size('Code Tileset Map Music ')[0], height))
            getattr(self, self.mode, self.code).draw(self.window, self.total, selectedcol, unselectedcol, bgcol)
            pg.display.update()
        pg.quit()

def main():
    app = App()
    # import threading
    # threading.Thread(target=app.run_wrap, daemon=True).start()
    app.run_wrap()

if __name__=='__main__':
    main()
