import pygame as pg
from pyboy import PyBoy, WindowEvent

class App:
    def __init__(self):
        pg.init()
        pg.display.set_caption('GB IDE')
        App.window = pg.display.set_mode((640, 480), pg.DOUBLEBUF)
        App.window.set_alpha(None)
        App.clock = pg.time.Clock()
        App.running = True
        App.mode = 'code'
        App.saving = False
        App.loading = False
        App.filename = 'new.asm'
        App.createFont = lambda x: pg.font.Font('./tic-80-wide-font/tic-80-wide-font.ttf', x)
        #App.createFont = lambda x: pg.font.SysFont('Arial', x)
        App.height = 18
        App.ratio = 558
        App.screencol = 0
        App.font = App.createFont(App.height)
        App.code = ''
        App.cursorline = 0
        App.cursorcol = 0
        App.total = 0
        App.game = PyBoy('pokered.gb', window_type='headless')
        pg.key.set_repeat(250, 40)
    def run_wrap(self):
        try:
            self.run()
        except KeyboardInterrupt:
            pg.quit()
    def run(self):
        while App.running:
            App.window.fill((0, 0, 0))
            delta = App.clock.tick(60)/1000
            App.total += delta
            width, height = App.font.size('M')
            #print(height)
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    App.running = False
                    break
                if e.type == pg.KEYUP:
                    if e.key == pg.K_RIGHT:
                        App.game.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
                    elif e.key == pg.K_LEFT:
                        App.game.send_input(WindowEvent.RELEASE_ARROW_LEFT)
                    elif e.key == pg.K_UP:
                        App.game.send_input(WindowEvent.RELEASE_ARROW_UP)
                    elif e.key == pg.K_DOWN:
                        App.game.send_input(WindowEvent.RELEASE_ARROW_DOWN)
                    elif e.key == pg.K_z:
                        App.game.send_input(WindowEvent.RELEASE_BUTTON_A)
                    elif e.key == pg.K_x:
                        App.game.send_input(WindowEvent.RELEASE_BUTTON_B)
                    elif e.key == pg.K_RETURN:
                        App.game.send_input(WindowEvent.RELEASE_BUTTON_START)
                    elif e.key == pg.K_SPACE:
                        App.game.send_input(WindowEvent.RELEASE_BUTTON_SELECT)
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_F1:
                        App.mode = 'code'
                    elif e.key == pg.K_F2:
                        App.mode = 'map'
                    elif e.key == pg.K_F3:
                        App.mode = 'music'
                    elif e.key == pg.K_F4:
                        App.mode = 'emulator'
                    elif App.mode == 'emulator':
                        if e.key == pg.K_RIGHT:
                            App.game.send_input(WindowEvent.PRESS_ARROW_RIGHT)
                        elif e.key == pg.K_LEFT:
                            App.game.send_input(WindowEvent.PRESS_ARROW_LEFT)
                        elif e.key == pg.K_UP:
                            App.game.send_input(WindowEvent.PRESS_ARROW_UP)
                        elif e.key == pg.K_DOWN:
                            App.game.send_input(WindowEvent.PRESS_ARROW_DOWN)
                        elif e.key == pg.K_z:
                            App.game.send_input(WindowEvent.PRESS_BUTTON_A)
                        elif e.key == pg.K_x:
                            App.game.send_input(WindowEvent.PRESS_BUTTON_B)
                        elif e.key == pg.K_RETURN:
                            App.game.send_input(WindowEvent.PRESS_BUTTON_START)
                        elif e.key == pg.K_SPACE:
                            App.game.send_input(WindowEvent.PRESS_BUTTON_SELECT)
                        continue
                    elif e.mod & pg.KMOD_CTRL:
                        if e.key == pg.K_MINUS:
                            App.height -= 1 if (e.mod & pg.KMOD_SHIFT)!=0 else 6
                            App.font = App.createFont(App.height)
                            App.screencol = 0
                        elif e.key == pg.K_EQUALS:
                            App.height += 1 if (e.mod & pg.KMOD_SHIFT)!=0 else 6
                            App.font = App.createFont(App.height)
                            App.screencol = 0
                        elif e.key == pg.K_r:
                            App.game.stop()
                            App.game = PyBoy('pokered.gb', window_type='headless')
                        elif e.key == pg.K_s:
                            App.saving = True
                        elif e.key == pg.K_o:
                            App.loading = True
                        elif e.key == pg.K_n:
                            App.code = ''
                            App.cursorcol = 0
                            App.cursorline = 0
                            App.filename = 'new.asm'
                        continue
                    if (App.saving or App.loading) and App.mode == 'code':
                        if e.key == pg.K_BACKSPACE:
                            if len(App.filename)>0:
                                App.filename = App.filename[:-1]
                        elif e.key in [pg.K_DELETE, pg.K_LEFT, pg.K_RIGHT, pg.K_UP,
                                       pg.K_DOWN, pg.K_HOME, pg.K_END]:
                            continue
                        elif e.key == pg.K_RETURN:
                            if App.loading:
                                try:
                                    with open(App.filename, 'r') as file:
                                        App.code = file.read()
                                        file.close()
                                    App.cursorline = 0
                                    App.cursorcol = 0
                                except:
                                    pass
                                App.loading = False
                            elif App.saving:
                                try:
                                    with open(App.filename, 'w') as file:
                                        file.write(App.code)
                                        file.close()
                                except:
                                    pass
                                App.saving = False
                        elif e.mod & pg.KMOD_CTRL and e.key == pg.K_C:
                            App.loading = False
                            App.saving = False
                        elif e.unicode:
                            App.filename += e.unicode
                        continue
                    if e.key == pg.K_BACKSPACE:
                        if len(App.code)>0:
                            splitted = App.code.split('\n')
                            #print(repr(splitted[App.cursorline]))
                            if splitted[App.cursorline] and App.cursorcol>0:
                                #print('ok')
                                #print(repr(splitted[App.cursorline][:App.cursorcol-1]))
                                #print(repr(splitted[App.cursorline][App.cursorcol:]))
                                splitted[App.cursorline] = splitted[App.cursorline][:App.cursorcol-1] + splitted[App.cursorline][App.cursorcol:]
                                #print(repr(splitted[App.cursorline]))
                                App.cursorcol -= 1
                            else:
                                if App.cursorcol>0:
                                    splitted[App.cursorline] = splitted[App.cursorline][:App.cursorcol-1] + splitted.pop(App.cursorline)
                                    App.cursorcol = len(splitted[App.cursorline])
                                else:
                                    App.cursorline -= 1
                                    App.cursorcol = len(splitted[App.cursorline])
                                    splitted[App.cursorline] += splitted.pop(App.cursorline+1)
                            App.code = '\n'.join(splitted)
                        continue
                    if e.key == pg.K_DELETE:
                        if len(App.code)>0:
                            splitted = App.code.split('\n')
                            if splitted[App.cursorline][App.cursorcol:]:
                                splitted[App.cursorline] = splitted[App.cursorline][:App.cursorcol] + splitted[App.cursorline][App.cursorcol+1:]
                            elif App.cursorline+1<len(splitted):
                                #print(splitted, App.cursorline)
                                App.cursorcol = len(splitted[App.cursorline])
                                splitted[App.cursorline] += splitted.pop(App.cursorline+1)
                            App.code = '\n'.join(splitted)
                    elif e.key == pg.K_UP:
                        if App.cursorline>0:
                            App.cursorline -= 1
                            App.cursorcol = min(len(App.code.split('\n')[App.cursorline]), App.cursorcol)
                    elif e.key == pg.K_DOWN:
                        if App.cursorline<App.code.count('\n'):
                            App.cursorline += 1
                            App.cursorcol = min(len(App.code.split('\n')[App.cursorline]), App.cursorcol)
                    elif e.key == pg.K_LEFT:
                        if App.cursorcol>0:
                            App.cursorcol -= 1
                        else:
                            if App.cursorline>0:
                                App.cursorline -= 1
                                App.cursorcol = len(App.code.split('\n')[App.cursorline])
                            else:
                                App.cursorline = App.code.count('\n')
                                App.cursorcol = len(App.code.split('\n')[App.cursorline])
                    elif e.key == pg.K_RIGHT:
                        if App.cursorcol<len(App.code.split('\n')[App.cursorline]):
                            App.cursorcol += 1
                        else:
                            App.cursorcol = 0
                            if App.cursorline<App.code.count('\n'):
                                App.cursorline += 1
                            else:
                                App.cursorline = 0
                    elif e.key == pg.K_END:
                        App.cursorcol = len(App.code.split('\n')[App.cursorline])
                    elif e.key == pg.K_HOME:
                        App.cursorcol = 0
                    elif e.key == pg.K_RETURN:
                        splitted = App.code.split('\n')
                        splitted[App.cursorline] = splitted[App.cursorline][:App.cursorcol] + '\n' + splitted[App.cursorline][App.cursorcol:]
                        App.code = '\n'.join(splitted)
                        App.cursorline += 1
                        App.cursorcol = 0
                    elif e.unicode:
                        splitted = App.code.split('\n')
                        line = splitted[App.cursorline]
                        splitted[App.cursorline] = line[:App.cursorcol] + e.unicode + line[App.cursorcol:]
                        App.cursorcol += 1
                        App.code = '\n'.join(splitted)
            selectedcol = (0, 162, 232)
            unselectedcol = (48, 51, 163)
            bgcol = (63, 72, 204)
            pg.draw.rect(App.window, bgcol, pg.Rect((0, 0), (640, height*3)))
            codecolor = selectedcol if App.mode=='code' else unselectedcol
            mapcolor = selectedcol if App.mode=='map' else unselectedcol
            muscolor = selectedcol if App.mode=='music' else unselectedcol
            emucolor = selectedcol if App.mode=='emulator' else unselectedcol
            App.window.blit(App.font.render('Code', False, (255, 255, 255), codecolor), (height, height))
            App.window.blit(App.font.render('Map', False, (255, 255, 255), mapcolor), (height+App.font.size('Code ')[0], height))
            App.window.blit(App.font.render('Music', False, (255, 255, 255), muscolor), (height+App.font.size('Code Map ')[0], height))
            App.window.blit(App.font.render('Emulator', False, (255, 255, 255), emucolor), (height+App.font.size('Code Map Music ')[0], height))
            #if App.cursorcol>App.screencol+App.ratio/width:
            #    App.screencol = int(App.cursorcol-App.ratio/width)
            #if App.cursorcol<App.screencol-App.ratio/width:
            #    App.screencol = max(0, int(App.cursorcol+App.ratio/width))
            if App.mode == 'code':
                for i, line in enumerate(App.code.split('\n')):
                    #print(line)
                    rect = App.window.blit(App.font.render(line, False, (255, 255, 255), (0, 0, 0)), (width*(4-App.screencol), height*(4+i)))
                    if not App.saving and App.total % 1 > 0.5 and i==App.cursorline:
                        cursor = pg.Rect((0, 0), (width+2, height+2))
                        cursor.bottomleft = rect.bottomleft
                        cursor.left += App.font.size(line[:App.cursorcol])[0]-(width*App.screencol)
                        pg.draw.rect(App.window, (255, 255, 255), cursor)
                pg.draw.rect(App.window, (32, 32, 32), pg.Rect((0, height*3), (height*3, 480)))
                for i in range(App.code.count('\n')+1):
                    center = 1-len(str(i+1))//2
                    App.window.blit(App.font.render(str(i+1), False, (255, 255, 255), (32, 32, 32)), (width*center, height*(4+i)))
                pg.draw.rect(App.window, (255, 255, 255), pg.Rect((0, 480-height), (640, height)))
                App.window.blit(App.font.render('line {}/{} col {}'.format(App.cursorline+1, App.code.count('\n')+1, App.cursorcol+1), False, (0, 0, 0), (255, 255, 255)), (0, 480-height))
                App.window.blit(App.font.render(App.filename, False, (0, 0, 0), (255, 255, 255)), (640-App.font.size(App.filename)[0], 480-height))
                if App.saving or App.loading:
                    pos = (320-height*10, 240-height*2)
                    center = (320-height*9, 240)
                    pg.draw.rect(App.window, unselectedcol, pg.Rect(pos, (20*height, 4*height)))
                    pg.draw.rect(App.window, bgcol, pg.Rect(pos, (20*height, height)))
                    pg.draw.rect(App.window, (0, 0, 0), pg.Rect(center, (18*height, height)))
                    App.window.blit(App.font.render('Save As' if App.saving else 'Load', False, (255, 255, 255), bgcol), pos)
                    App.window.blit(App.font.render(App.filename, False, (255, 255, 255), (0, 0, 0)), center)
            if App.mode == 'emulator':
                scrn = App.game.botsupport_manager().screen()
                form = scrn.raw_screen_buffer_format()
                dims = scrn.raw_screen_buffer_dims()
                buff = scrn.raw_screen_buffer()
                surf = pg.image.frombuffer(buff, dims, form)
                surf = pg.transform.scale(surf, (320, 288))
                App.window.blit(surf, (160, 96))
                App.game.tick()
            pg.display.update()
        pg.quit()
if __name__=='__main__':
    import threading
    global app
    app = App()
    debug = False
    if debug:
        threading.Thread(target=app.run_wrap, daemon=True).start()
    else:
        app.run_wrap()
