import pygame as pg
from menu import Menu

class CodeMenu(Menu):
    def __init__(self, font):
        super().__init__(font)
        self.filename = 'new.asm'
        self.code = ''
        self.cursorline = 0
        self.cursorcol = 0
        self.screencol = 0
    def event(self, e):
        if (self.saving or self.loading):
            if e.key == pg.K_BACKSPACE:
                if len(self.filename)>0:
                    self.filename = self.filename[:-1]
            elif e.key in [pg.K_DELETE, pg.K_LEFT, pg.K_RIGHT, pg.K_UP,
                           pg.K_DOWN, pg.K_HOME, pg.K_END]:
                return
            elif e.key == pg.K_RETURN:
                if self.loading:
                    try:
                        with open(self.filename, 'r') as file:
                            self.code = file.read()
                            file.close()
                        self.cursorline = 0
                        self.cursorcol = 0
                    except:
                        pass
                    self.loading = False
                elif self.saving:
                    try:
                        with open(self.filename, 'w') as file:
                            file.write(self.code)
                            file.close()
                    except:
                        pass
                    self.saving = False
            elif e.mod & pg.KMOD_CTRL and e.key == pg.K_c:
                self.loading = False
                self.saving = False
            elif e.unicode not in '':
                self.filename += e.unicode
            return
        elif e.mod & pg.KMOD_CTRL and e.key == pg.K_s:
            self.saving = True
        elif e.mod & pg.KMOD_CTRL and e.key == pg.K_o:
            self.loading = True
        elif e.mod & pg.KMOD_CTRL and e.key == pg.K_n:
            self.code = ''
            self.cursorcol = 0
            self.cursorline = 0
            self.filename = 'new.asm'
        elif e.key == pg.K_BACKSPACE:
            if len(self.code)>0:
                splitted = self.code.split('\n')
                #print(repr(splitted[self.cursorline]))
                if splitted[self.cursorline] and self.cursorcol>0:
                    #print('ok')
                    #print(repr(splitted[self.cursorline][:self.cursorcol-1]))
                    #print(repr(splitted[self.cursorline][self.cursorcol:]))
                    splitted[self.cursorline] = splitted[self.cursorline][:self.cursorcol-1] + splitted[self.cursorline][self.cursorcol:]
                    #print(repr(splitted[self.cursorline]))
                    self.cursorcol -= 1
                else:
                    if self.cursorcol>0:
                        splitted[self.cursorline] = splitted[self.cursorline][:self.cursorcol-1] + splitted.pop(self.cursorline)
                        self.cursorcol = len(splitted[self.cursorline])
                    else:
                        self.cursorline -= 1
                        self.cursorcol = len(splitted[self.cursorline])
                        splitted[self.cursorline] += splitted.pop(self.cursorline+1)
                self.code = '\n'.join(splitted)
            return
        elif e.key == pg.K_DELETE:
            if len(self.code)>0:
                splitted = self.code.split('\n')
                if splitted[self.cursorline][self.cursorcol:]:
                    splitted[self.cursorline] = splitted[self.cursorline][:self.cursorcol] + splitted[self.cursorline][self.cursorcol+1:]
                elif self.cursorline+1<len(splitted):
                    #print(splitted, self.cursorline)
                    self.cursorcol = len(splitted[self.cursorline])
                    splitted[self.cursorline] += splitted.pop(self.cursorline+1)
                self.code = '\n'.join(splitted)
        elif e.key == pg.K_UP:
            if self.cursorline>0:
                self.cursorline -= 1
                self.cursorcol = min(len(self.code.split('\n')[self.cursorline]), self.cursorcol)
        elif e.key == pg.K_DOWN:
            if self.cursorline<self.code.count('\n'):
                self.cursorline += 1
                self.cursorcol = min(len(self.code.split('\n')[self.cursorline]), self.cursorcol)
        elif e.key == pg.K_LEFT:
            if self.cursorcol>0:
                self.cursorcol -= 1
            else:
                if self.cursorline>0:
                    self.cursorline -= 1
                    self.cursorcol = len(self.code.split('\n')[self.cursorline])
                else:
                    self.cursorline = self.code.count('\n')
                    self.cursorcol = len(self.code.split('\n')[self.cursorline])
        elif e.key == pg.K_RIGHT:
            if self.cursorcol<len(self.code.split('\n')[self.cursorline]):
                self.cursorcol += 1
            else:
                self.cursorcol = 0
                if self.cursorline<self.code.count('\n'):
                    self.cursorline += 1
                else:
                    self.cursorline = 0
        elif e.key == pg.K_END:
            self.cursorcol = len(self.code.split('\n')[self.cursorline])
        elif e.key == pg.K_HOME:
            self.cursorcol = 0
        elif e.key == pg.K_RETURN:
            splitted = self.code.split('\n')
            splitted[self.cursorline] = splitted[self.cursorline][:self.cursorcol] + '\n' + splitted[self.cursorline][self.cursorcol:]
            self.code = '\n'.join(splitted)
            self.cursorline += 1
            self.cursorcol = 0
        elif e.unicode not in '':
            splitted = self.code.split('\n')
            line = splitted[self.cursorline]
            splitted[self.cursorline] = line[:self.cursorcol] + e.unicode + line[self.cursorcol:]
            self.cursorcol += 1
            self.code = '\n'.join(splitted)
    def draw(self, window, total, selectedcol, unselectedcol, bgcol):
        width, height = self.font.size('M')
        for i, line in enumerate(self.code.split('\n')):
            #print(line)
            rect = window.blit(self.font.render(line, False, (255, 255, 255), (0, 0, 0)), (width+height*3, height*(4+i)))
            if not self.saving and total % 1 > 0.5 and i==self.cursorline:
                cursor = pg.Rect((0, 0), (width, height))
                cursor.bottomleft = rect.bottomleft
                cursor.left += self.font.size(line[:self.cursorcol])[0]-(width*self.screencol)
                pg.draw.rect(window, (255, 255, 255), cursor)
        pg.draw.rect(window, (32, 32, 32), pg.Rect((0, height*3), (height*3, window.get_height())))
        for i in range(self.code.count('\n')+1):
            center = 1-len(str(i+1))//2
            window.blit(self.font.render(str(i+1), False, (255, 255, 255), (32, 32, 32)), (width*center, height*(4+i)))
        pg.draw.rect(window, (255, 255, 255), pg.Rect((0, window.get_height()-height), (window.get_width(), height)))
        window.blit(self.font.render('line {}/{} col {}'.format(self.cursorline+1, self.code.count('\n')+1, self.cursorcol+1), False, (0, 0, 0), (255, 255, 255)), (0, int(window.get_height()+height/12-height)))
        window.blit(self.font.render(self.filename, False, (0, 0, 0), (255, 255, 255)), (window.get_width()-self.font.size(self.filename)[0], window.get_height()-height))
        if self.saving or self.loading:
            pos = (window.get_width()//2-height*10, window.get_height()//2-height*2)
            center = (window.get_width()//2-height*9, window.get_height()//2)
            pg.draw.rect(window, unselectedcol, pg.Rect(pos, (20*height, 4*height)))
            pg.draw.rect(window, bgcol, pg.Rect(pos, (20*height, height)))
            pg.draw.rect(window, (0, 0, 0), pg.Rect(center, (18*height, height)))
            window.blit(self.font.render('Save As' if self.saving else 'Load', False, (255, 255, 255), bgcol), pos)
            window.blit(self.font.render(self.filename, False, (255, 255, 255), (0, 0, 0)), center)
