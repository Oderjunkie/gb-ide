import pygame as pg
from menu import Menu

class asbits:
    def __init__(self, val):
        self.val = val
        self.iters = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.iters == 8:
            raise StopIteration
        returned = self.val&1
        self.val >>= 1
        self.iters += 1
        return returned

class TilesetMenu(Menu):
    def __init__(self, font):
        super().__init__(font)
        self.filename = 'new.2bpp'
        self.tiledata = b''
        self.tilesurf = None
        self.tilex = 0
        self.tiley = 0
        self.tilepixelx = 0
        self.tilepixely = 0
    def decodetiles(self):
        tileset = pg.Surface((128, 128), flags=0)
        tile = pg.Surface((8, 8), flags=0)
        bp1 = pg.surfarray.array2d(pg.Surface((8, 8), flags=0))
        bp2 = pg.surfarray.array2d(pg.Surface((8, 8), flags=0))
        realtilex = 0
        tilex = 0
        tiley = 0
        row = 0
        bitplane = 1
        vals = self.gettileset()
        modulos = 0
        #print(vals)
        try:
            for val in vals:
                #print('BITPLANE {}'.format(bitplane))
                bp = bp1 if bitplane==1 else bp2
                #print(asbits(val))
                for col, bit in enumerate(asbits(val)):
                    bp[row][col] = bit
                if bitplane==1:
                    bp1 = bp
                else:
                    bp2 = bp
                #print(val)
                #print(bp)
                bitplane += 1
                if bitplane==3:
                    bitplane = 1
                    #modulos += 1
                    #if modulos<=8:
                    #    continue
                    #modulos = 0
                    for rownum, [row1, row2] in enumerate(zip(bp1, bp2)):
                        for colnum, [col1, col2] in enumerate(zip(row1, row2)):
                            #print(col1, col2)
                            #tile[rownum][colnum] = (col2<<1+col1)*(0x0F0F0F*0xFF/6)
                            tile.set_at([7-colnum, rownum], [0xFF-((col2<<1)+col1)*(0xFF/3)]*3)
                    #print(tile)
                    row += 1
                    #realtile = pg.surfarray.make_surface(tile)
                    tilex += 8
                    if tilex==64:
                        tileset.blit(tile, pg.Rect((realtilex, tiley), (8, 8)))
                        realtilex += 8
                        tilex = 0
                        if realtilex==128:
                            realtilex = 0
                            tiley += 8
                    if row==8:
                        row = 0
        except Exception as e:
            print(e.__traceback__.tb_lineno, e)
        return tileset
    def loadtileset(self, data):
        self.tilex = 0
        self.tiley = 0
        self.tiledata = data
        self.tilesurf = self.decodetiles()
    def gettileset(self):
        return self.tiledata
    def serializetileset(self):
        final = b''
        bp1byte = 0
        bp2byte = 0
        try:
            for row in range(16):
                for col in range(16):
                    for tiley in range(8):
                        for tilex in range(8):
                            gray = self.tilesurf.get_at([col*8+tilex, row*8+tiley])[0]
                            value = int((0xFF-gray)//(0xFF/3))
                            bp1byte = (bp1byte<<1)|(value&1)
                            bp2byte = (bp2byte<<1)|(value>>1)
                        #print(bp1byte, bp2byte)
                        final += bytes([bp1byte, bp2byte])
                        bp1byte = 0
                        bp2byte = 0
            return final
        except Exception as e:
            print(e, type(e), e.__traceback__.tb_lineno)
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
                        with open(self.filename, 'rb') as file:
                            self.loadtileset(file.read())
                            file.close()
                    except Exception as e:
                        print(e)
                    self.loading = False
                elif self.saving:
                    try:
                        with open(self.filename, 'wb') as file:
                            file.write(self.serializetileset())
                            file.close()
                    except Exception as e:
                        print(e)
                    self.saving = False
            elif e.mod & pg.KMOD_CTRL and e.key == pg.K_c:
                self.loading = False
                self.saving = False
            elif e.unicode not in '':
                self.filename += e.unicode
        elif e.mod & pg.KMOD_CTRL:
            if e.key == pg.K_RIGHT and self.tilex<15:
                self.tilex += 1
            if e.key == pg.K_LEFT and self.tilex>0:
                self.tilex -= 1
            if e.key == pg.K_DOWN and self.tiley<15:
                self.tiley += 1
            if e.key == pg.K_UP and self.tiley>0:
                self.tiley -= 1
            elif e.key == pg.K_s:
                self.saving = True
            elif e.key == pg.K_o:
                self.loading = True
        elif e.key in [pg.K_RIGHT, pg.K_LEFT, pg.K_DOWN, pg.K_UP]:
            if e.key == pg.K_RIGHT and self.tilepixelx<7:
                self.tilepixelx += 1
            if e.key == pg.K_LEFT and self.tilepixelx>0:
                self.tilepixelx -= 1
            if e.key == pg.K_DOWN and self.tilepixely<7:
                self.tilepixely += 1
            if e.key == pg.K_UP and self.tilepixely>0:
                self.tilepixely -= 1
        elif e.key in [pg.K_1, pg.K_2, pg.K_3, pg.K_4]:
            tilepos = (self.tilex*8+self.tilepixelx, self.tiley*8+self.tilepixely)
            value = [pg.K_1, pg.K_2, pg.K_3, pg.K_4].index(e.key)
            color = [0xFF-(value)*(0xFF/3)]*3
            self.tilesurf.set_at(tilepos, color)
    def draw(self, window, total, selectedcol, unselectedcol, bgcol):
        width, height = self.font.size('M')
        if self.tilesurf:
            #offset = window.get_width()/3-128
            offset = 100
            topleft = (window.get_width()-256-offset, ((window.get_height()-height*3-256)//2)+height*3)
            window.blit(pg.transform.scale(self.tilesurf, (256, 256)), pg.Rect(topleft, (64, 64)))
            pg.draw.rect(window, (255, 255, 255), pg.Rect((topleft[0]-2, topleft[1]-2), (259, 259)), 2)
            topleftedit = (offset, topleft[1])
            pg.draw.rect(window, (255, 255, 255), pg.Rect((topleftedit[0]-2, topleftedit[1]-2), (259, 259)), 2)
            real_rect = pg.Rect((self.tilex*8, self.tiley*8), (8, 8))
            drawn_rect = pg.Rect((topleft[0]+self.tilex*16, topleft[1]+self.tiley*16), (16, 16))
            tile = self.tilesurf.subsurface(real_rect)
            edit_drawn_rect = pg.Rect((topleftedit[0]+self.tilepixelx*32, topleftedit[1]+self.tilepixely*32), (32, 32))
            window.blit(pg.transform.scale(pg.transform.scale(tile, (256, 256)), (256, 256)), pg.Rect(topleftedit, (64, 64)))
            pg.draw.rect(window, (255, 255, 255) if total % 0.5 > 0.25 else (0, 0, 0), drawn_rect, 2)
            pg.draw.rect(window, (255, 255, 255) if total % 0.5 > 0.25 else (0, 0, 0), edit_drawn_rect, 4)
        if self.saving or self.loading:
            pos = (window.get_width()//2-height*10, window.get_height()//2-height*2)
            center = (window.get_width()//2-height*9, window.get_height()//2)
            pg.draw.rect(window, unselectedcol, pg.Rect(pos, (20*height, 4*height)))
            pg.draw.rect(window, bgcol, pg.Rect(pos, (20*height, height)))
            pg.draw.rect(window, (0, 0, 0), pg.Rect(center, (18*height, height)))
            window.blit(self.font.render('Save As' if self.saving else 'Load', False, (255, 255, 255), bgcol), pos)
            window.blit(self.font.render(self.filename, False, (255, 255, 255), (0, 0, 0)), center)
        elif not self.tilesurf:
            message = 'can i haz tileset?'
            width, height = self.font.size(message)
            window.blit(self.font.render(message, False, (40, 40, 60), (0, 0, 0)), ((window.get_width()-width)//2, (window.get_height()-height)//2))
