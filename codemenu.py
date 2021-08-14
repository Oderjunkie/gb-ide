import pygame as pg
from menu import Menu
from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import TerminalTrueColorFormatter

class CodeMenu(Menu):
    def __init__(self, font):
        super().__init__(font)
        self.filename = 'new.asm'
        self.code = ''
        self.cursorline = 0
        self.cursorcol = 0
        self.screencol = 0
        self.lexer = get_lexer_for_filename(self.filename)
        self.formatter = TerminalTrueColorFormatter()
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
                self.lexer = get_lexer_for_filename(self.filename)
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
            self.lexer = get_lexer_for_filename(self.filename)
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
            char = e.unicode
            istab = e.unicode == '\t'
            if istab:
                char = '    '
            splitted[self.cursorline] = line[:self.cursorcol] + char + line[self.cursorcol:]
            if istab:
                self.cursorcol += 4
            else:
                self.cursorcol += 1
            self.code = '\n'.join(splitted)
    def pretty_print_ansi_line(self, window, line, anti: bool, fgcol: tuple, bgcol: tuple, pos: tuple):
        #return window.blit(self.font.render(line, anti, fgcol, bgcol), pos)
        x, y = pos
        blit = window.blit
        render = self.font.render
        segments = line.strip('\n').split('\x1b[')
        #print(repr(segments))
        for segment in segments:
            if segment.startswith('38'):
                _, __, r, g, text = segment.split(';', 4)
                b, text = text.split('m', 1)
                if ';' in b:
                    b = b.split(';', 1)[0]
                #print('{4!r}: {0!r}, {1!r}, {2!r} [{3!r}]'.format(r, g, b, text, segment))
                r, g, b = int(r), int(g), int(b)
                #print(repr(text))
                rendered = render(text, anti, (r, g, b), bgcol)
                blit(rendered, (x, y))
                x += rendered.get_width()
                continue
            elif segment.startswith('39'):
                _, segment = segment.split('m', 1)
            rendered = render(segment, anti, fgcol, bgcol)
            blit(rendered, (x, y))
            x += rendered.get_width()
        return pg.Rect(pos, self.font.size(line))
    def draw(self, window, total, selectedcol, unselectedcol, bgcol):
        width, height = self.font.size('M')
        for i, line in enumerate(self.code.split('\n')):
            #print(line)
            rect = self.pretty_print_ansi_line(window, highlight(line, self.lexer, self.formatter), False, (255, 255, 255), (0, 0, 0), (width+height*3, height*(4+i)))
            if not (self.saving or self.loading) and total % 1 > 0.5 and i==self.cursorline:
                cursor = pg.Rect((0, 0), (width, height))
                #print(rect.bottomleft)
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
