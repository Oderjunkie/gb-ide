import pygame as pg
from menu import Menu
import struct

class Module:
    class Instrument:
        def __init__(self, raw):
            self.name = raw[:22].decode('cp437').rstrip('\x00')
            self.len, self.finetune, self.volume, self.loopstart, self.loopend\
                = struct.unpack('>HbB2H', raw[22:30])
            self.len *= 2
            self.loopstart *= 2
            self.loopend *= 2
        def createRaw(self):
            name = self.name
            if len(name)<22:
                name += '\x00'*(22-len(name))
            name = name.encode('cp437')
            length = struct.pack('>H', int(self.len / 2))
            finetune = struct.pack('>b', self.finetune)
            volume = struct.pack('>B', self.volume)
            loopstart = struct.pack('>H', int(self.loopstart / 2))
            loopend = struct.pack('>H', int(self.loopend / 2))
            return name+length+finetune+volume+loopstart+loopend
    class Sample:
        def __init__(self, raw):
            self.data = struct.unpack('{}b'.format(len(raw)), raw)
        def createRaw(self):
            return struct.pack('{}b'.format(len(self.data)), *self.data)
    class Pattern:
        class Row:
            class Note:
                conversiontable = {
                    0:   '---',
                    856: 'C-1',
                    808: 'C#1',
                    762: 'D-1',
                    720: 'D#1',
                    678: 'E-1',
                    640: 'F-1',
                    604: 'F#1',
                    570: 'G-1',
                    538: 'G#1',
                    508: 'A-1',
                    480: 'A#1',
                    453: 'B-1',
                    428: 'C-2',
                    404: 'C#2',
                    381: 'D-2',
                    360: 'D#2',
                    339: 'E-2',
                    320: 'F-2',
                    302: 'F#2',
                    285: 'G-2',
                    269: 'G#2',
                    254: 'A-2',
                    240: 'A#2',
                    226: 'B-2',
                    214: 'C-3',
                    202: 'C#3',
                    190: 'D-3',
                    180: 'D#3',
                    170: 'E-3',
                    160: 'F-3',
                    151: 'F#3',
                    143: 'G-3',
                    135: 'G#3',
                    127: 'A-3',
                    120: 'A#3',
                    113: 'B-3'
                }
                def __init__(self, raw):
                    samplehi        = (raw                ) >> 28
                    self.noteperiod = (raw & 0x0_FFF_0_000) >> 16
                    samplelo        = (raw & 0x0_000_F_000) >> 12
                    self.effects    = (raw & 0x0_000_0_FFF)
                    self.sample     = (samplehi << 4) | samplelo
                def createRaw(self):
                    #print(self.raw)
                    samplelo = self.sample & 0x0F
                    samplehi = self.sample >> 4
                    samplehi = samplehi << 28
                    samplelo = samplelo << 12
                    effects  = self.effects
                    noteperiod = self.noteperiod << 16
                    raw = samplehi | noteperiod | samplelo | effects
                    return struct.pack('>L', raw)
                def __repr__(self):
                    sample = self.sample
                    effects = self.effects
                    noteperiod = self.noteperiod
                    sample = '--' if sample==0 else '{0:2X}'.format(sample).replace(' ', '0')
                    effects = '---' if effects==0 else '{0:3X}'.format(effects).replace(' ', '0')
                    return '{}{}{}'.format(self.conversiontable[noteperiod], sample, effects)
                def getnote(self):
                    noteperiod = self.noteperiod
                    return self.conversiontable[noteperiod]
                def getsample(self):
                    sample = self.sample
                    sample = '--' if sample==0 else '{0:2X}'.format(sample).replace(' ', '0')
                    return sample
                def geteffect(self):
                    effects = self.effects
                    effects = '---' if effects==0 else '{0:3X}'.format(effects).replace(' ', '0')
                    return effects
            def __init__(self, unpacked):
                self.cells = [self.Note(note) for note in unpacked]
            def createRaw(self):
                cells = b''.join([cell.createRaw() for cell in self.cells])
                #print(cells)
                return cells
            def __repr__(self):
                return '  '.join(map(repr, self.cells))
        def __init__(self, raw):
            self.rows = [self.Row(struct.unpack('>4L', raw[_*16:_*16+16])) for _ in range(len(raw)//16)]
        def createRaw(self):
            raw = []
            for row in self.rows:
                raw.append(row.createRaw())
            raw = b''.join(raw)
            return raw
        def __repr__(self):
            return '\n'.join(map(repr, self.rows))
    def __init__(self, raw):
        self.sig = raw[1080:1084].decode('cp437')
        assert self.sig in ['M.K.', 'M!K!', '4CHN', '6CHN', '8CHN', 'FLT4', 'FLT8']
        self.title = raw[:20].decode('cp437').rstrip('\x00')
        self.insts = []
        for _ in range(31):
            self.insts.append(self.Instrument(raw[20+_*30:50+_*30]))
        self.length, self.looping = struct.unpack('BB', raw[950:952])
        self.order = list(struct.unpack('128B', raw[952:1080]))[:self.length]
        self.sig = raw[1080:1084].decode('cp437')
        lengthofpatterns = max(self.order)
        self.patterns = []
        for _ in range(lengthofpatterns+1):
            #print(1084+_*1024, 2108+_*1024)
            self.patterns.append(self.Pattern(raw[1084+_*1024:2108+_*1024]))
        nextbyte = 2108+lengthofpatterns*1024
        self.samples = []
        for desc in self.insts:
            self.samples.append(self.Sample(raw[nextbyte:nextbyte+desc.len]))
            nextbyte += desc.len            
    def createRaw(self):
        title = self.title
        if len(title)<20:
            title += '\x00'*(20-len(title))
        title = title.encode('cp437')
        sig = self.sig.encode('cp437')
        insts = b''.join([inst.createRaw() for inst in self.insts])
        lengthloop = struct.pack('2B', self.length, self.looping)
        order = struct.pack('{}B'.format(len(self.order)), *self.order)+b'\x00'*(128-len(self.order))
        patterns = b''.join([pattern.createRaw() for pattern in self.patterns])
        samples = b''.join([sample.createRaw() for sample in self.samples])
        return title+insts+lengthloop+order+sig+patterns+samples
    def play(self, mixer):
        sounds = [mixer.Sound(sample.createRaw()) for sample in self.samples]
        return sounds
class ExtendedModule:
    def __init__(self, raw):
        assert raw[:17].decode('cp437') == 'Extended Module: '
        assert raw[37] == b'\x1a'
        assert raw[58:60] == b'\x04\x01'
        name = raw[17:20].decode('cp437').rstrip('\x00')

class MusicMenu(Menu):
    def __init__(self, font):
        super().__init__(font)
        self.filename = 'new.mod'
        self.data = None
        self.trackerrow = 0
        self.selectedrow = 0
    def event(self, e):
        if e.mod & pg.KMOD_CTRL:
            if e.key == pg.K_s:
                self.saving = True
                self.loading = False
            elif e.key == pg.K_o:
                self.saving = False
                self.loading = True
            elif e.key == pg.K_n:
                self.data = None
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
                            try:
                                self.data = Module(file.read())
                                file.close()
                            except AssertionError:
                                self.data = ExtendedModule(file.read())
                                file.close()
                    except Exception as e:
                        print(e)
                    self.loading = False
                elif self.saving:
                    try:
                        with open(self.filename, 'wb') as file:
                            file.write(self.data.createRaw())
                            file.close()
                    except Exception as e:
                        print(e)
                    self.mussaving = False
            elif e.mod & pg.KMOD_CTRL and e.key == pg.K_c:
                self.loading = False
                self.saving = False
            elif e.unicode not in '':
                self.filename += e.unicode
        elif e.key == pg.K_DOWN:
            self.selectedrow += 1
            if self.selectedrow>self.trackerrow+21:
                if self.trackerrow<42:
                    self.trackerrow += 1
                else:
                    self.selectedrow = self.trackerrow+21
        elif e.key == pg.K_UP:
            self.selectedrow -= 1
            if self.selectedrow<self.trackerrow:
                if self.trackerrow>0:
                    self.trackerrow -= 1
                else:
                    self.selectedrow = 0
    def draw(self, window, total, selectedcol, unselectedcol, bgcol):
        width, height = self.font.size('M')
        if self.data:
            down = 0
            tmp = self.selectedrow - self.trackerrow
            for rownum, row in enumerate(self.data.patterns[self.data.order[0]-1].rows[self.trackerrow:self.trackerrow+22]):
                selected = rownum == tmp
                cells = row.cells
                width  = self.DisplayNote(cells[0], (0, height*3+down), selected, window)[0]
                width += self.DisplayNote(cells[1], (width, height*3+down), selected, window)[0]
                width += self.DisplayNote(cells[2], (width, height*3+down), selected, window)[0]
                down  += self.DisplayNote(cells[3], (width, height*3+down), selected, window)[1]
        else:
            message = 'can i haz mukik?'
            width, height = self.font.size(message)
            window.blit(self.font.render(message, False, (40, 40, 60), (0, 0, 0)), ((window.get_width()-width)//2, (window.get_height()-height)//2))
        if self.saving or self.loading:
            pos = (window.get_width()//2-height*10, (window.get_height()//2)-80-height*2)
            center = (window.get_width()//2-height*9, (window.get_height()//2)-80)
            pg.draw.rect(window, unselectedcol, pg.Rect(pos, (20*height, 4*height)))
            pg.draw.rect(window, bgcol, pg.Rect(pos, (20*height, height)))
            pg.draw.rect(window, (0, 0, 0), pg.Rect(center, (18*height, height)))
            window.blit(self.font.render('Save As' if self.saving else 'Load', False, (255, 255, 255), bgcol), pos)
            window.blit(self.font.render(self.filename, False, (255, 255, 255), (0, 0, 0)), center)
    def DisplayNote(self, noteobj, pos, selected, window):
        col = (64,64,64) if selected else (0,0,0)
        note, sample, effect = noteobj.getnote(), noteobj.getsample(), noteobj.geteffect()
        window.blit(self.font.render(note, False, (0, 255, 0), col), (pos[0], pos[1]))
        window.blit(self.font.render(sample, False, (255, 255, 0), col), (pos[0]+self.font.size(note)[0], pos[1]))
        window.blit(self.font.render(effect, False, (0, 0, 255), col), (pos[0]+self.font.size(note+sample)[0], pos[1]))
        return self.font.size(note+sample+effect+' ')
