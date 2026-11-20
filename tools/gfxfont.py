"""Read and rebuild the DefineFont3 tag of Bloodborne's menu/<lang>/font.gfx (Scaleform GFx / SWF).

The file holds one font ("MenuFont_01"). Glyph outlines are kept as opaque SHAPE records; new
glyphs are encoded from outline segments by encode_shape().
"""
import struct

TAG_DEFINE_FONT3 = 75
EM = 1024 * 20      # DefineFont3 glyph units per em


class BitReader:
    def __init__(self, data, pos=0):
        self.data, self.pos, self.bit = data, pos, 0

    def bits(self, n):
        value = 0
        for _ in range(n):
            byte = self.data[self.pos]
            value = (value << 1) | ((byte >> (7 - self.bit)) & 1)
            self.bit += 1
            if self.bit == 8:
                self.bit, self.pos = 0, self.pos + 1
        return value

    def sbits(self, n):
        value = self.bits(n)
        return value - (1 << n) if n and value >> (n - 1) else value

    def align(self):
        if self.bit:
            self.bit, self.pos = 0, self.pos + 1


class BitWriter:
    def __init__(self):
        self.out, self.acc, self.count = bytearray(), 0, 0

    def bits(self, value, n):
        for shift in range(n - 1, -1, -1):
            self.acc = (self.acc << 1) | ((value >> shift) & 1)
            self.count += 1
            if self.count == 8:
                self.out.append(self.acc)
                self.acc = self.count = 0

    def sbits(self, value, n):
        self.bits(value & ((1 << n) - 1), n)

    def done(self):
        if self.count:
            self.out.append(self.acc << (8 - self.count))
            self.acc = self.count = 0
        return bytes(self.out)


def signed_bits(*values):
    need = 0
    for v in values:
        need = max(need, (v.bit_length() if v >= 0 else (~v).bit_length()) + 1)
    return need


def read_rect(data, pos):
    r = BitReader(data, pos)
    n = r.bits(5)
    xmin, xmax, ymin, ymax = (r.sbits(n) for _ in range(4))
    r.align()
    return (xmin, xmax, ymin, ymax), r.pos


def write_rect(xmin, xmax, ymin, ymax):
    w = BitWriter()
    n = max(1, signed_bits(xmin, xmax, ymin, ymax))
    w.bits(n, 5)
    for v in (xmin, xmax, ymin, ymax):
        w.sbits(v, n)
    return w.done()


def decode_shape(data):
    """SHAPE record -> list of ('move', x, y) / ('line', x, y) / ('curve', cx, cy, x, y), absolute."""
    r = BitReader(data)
    fill_bits, line_bits = r.bits(4), r.bits(4)
    x = y = 0
    out = []
    while True:
        if r.bits(1) == 0:
            flags = r.bits(5)
            if flags == 0:
                break
            if flags & 1:
                n = r.bits(5)
                x, y = r.sbits(n), r.sbits(n)
                out.append(('move', x, y))
            if flags & 2:
                out.append(('fill0', r.bits(fill_bits)))
            if flags & 4:
                out.append(('fill1', r.bits(fill_bits)))
            if flags & 8:
                r.bits(line_bits)
            if flags & 16:
                raise ValueError('new styles in a glyph shape')
        elif r.bits(1):
            n = r.bits(4) + 2
            if r.bits(1):
                x, y = x + r.sbits(n), y + r.sbits(n)
            elif r.bits(1):
                y += r.sbits(n)
            else:
                x += r.sbits(n)
            out.append(('line', x, y))
        else:
            n = r.bits(4) + 2
            cx, cy = x + r.sbits(n), y + r.sbits(n)
            x, y = cx + r.sbits(n), cy + r.sbits(n)
            out.append(('curve', cx, cy, x, y))
    return out


def encode_shape(contours, fill='fill0'):
    """contours: list of [(x, y) start, then ('line', x, y) / ('curve', cx, cy, x, y) ...], absolute ints."""
    w = BitWriter()
    w.bits(1, 4)
    w.bits(0, 4)
    first = True
    for contour in contours:
        x, y = contour[0]
        n = max(1, signed_bits(x, y))
        w.bits(0, 1)
        w.bits((1 | (2 if fill == 'fill0' else 4)) if first else 1, 5)
        w.bits(n, 5)
        w.sbits(x, n)
        w.sbits(y, n)
        if first:
            w.bits(1, 1)
            first = False
        for segment in contour[1:]:
            if segment[0] == 'line':
                dx, dy = segment[1] - x, segment[2] - y
                if dx == 0 and dy == 0:
                    continue
                n = max(2, signed_bits(dx, dy))
                w.bits(0b11, 2)
                w.bits(n - 2, 4)
                if dx and dy:
                    w.bits(1, 1)
                    w.sbits(dx, n)
                    w.sbits(dy, n)
                else:
                    w.bits(0, 1)
                    w.bits(1 if dx == 0 else 0, 1)
                    w.sbits(dy if dx == 0 else dx, n)
                x, y = segment[1], segment[2]
            else:
                cdx, cdy = segment[1] - x, segment[2] - y
                adx, ady = segment[3] - segment[1], segment[4] - segment[2]
                n = max(2, signed_bits(cdx, cdy, adx, ady))
                w.bits(0b10, 2)
                w.bits(n - 2, 4)
                for v in (cdx, cdy, adx, ady):
                    w.sbits(v, n)
                x, y = segment[3], segment[4]
    w.bits(0, 6)    # end of shape
    return w.done()


class Glyph:
    __slots__ = ('code', 'shape', 'advance', 'bounds')

    def __init__(self, code, shape, advance, bounds):
        self.code, self.shape, self.advance, self.bounds = code, shape, advance, bounds


class FontFile:
    """font.gfx split into: bytes before the font tag, the parsed font, bytes after it."""

    def __init__(self, data):
        self.data = data
        nbits = data[8] >> 3
        pos = 8 + (5 + 4 * nbits + 7) // 8 + 4
        while pos < len(data):
            start = pos
            head = struct.unpack_from('<H', data, pos)[0]
            code, length = head >> 6, head & 0x3F
            pos += 2
            if length == 0x3F:
                length = struct.unpack_from('<I', data, pos)[0]
                pos += 4
            if code == TAG_DEFINE_FONT3:
                self.before, self.after = data[:start], data[pos + length:]
                self._parse(data[pos:pos + length])
                return
            pos += length
        raise ValueError('no DefineFont3 tag')

    def _parse(self, body):
        self.font_id, self.flags, self.language, name_len = struct.unpack_from('<HBBB', body, 0)
        if self.flags & 0x8C != 0x8C:
            raise ValueError(f'unexpected font flags {self.flags:#x}')
        self.name = body[5:5 + name_len]
        count = struct.unpack_from('<H', body, 5 + name_len)[0]
        table = 5 + name_len + 2
        offsets = struct.unpack_from(f'<{count + 1}I', body, table)     # last one = code table
        codes = struct.unpack_from(f'<{count}H', body, table + offsets[count])
        pos = table + offsets[count] + 2 * count
        self.ascent, self.descent, self.leading = struct.unpack_from('<HHh', body, pos)
        pos += 6
        advances = struct.unpack_from(f'<{count}h', body, pos)
        pos += 2 * count
        self.glyphs = []
        for i in range(count):
            bounds, pos = read_rect(body, pos)
            shape = body[table + offsets[i]:table + offsets[i + 1]]
            self.glyphs.append(Glyph(codes[i], shape, advances[i], bounds))
        self.kerning = body[pos:]

    def codes(self):
        return {g.code for g in self.glyphs}

    def glyph(self, code):
        return next(g for g in self.glyphs if g.code == code)

    def add(self, glyph):
        self.glyphs = [g for g in self.glyphs if g.code != glyph.code] + [glyph]

    def build(self):
        glyphs = sorted(self.glyphs, key=lambda g: g.code)
        count = len(glyphs)
        shapes = b''.join(g.shape for g in glyphs)
        offsets, pos = [], 4 * (count + 1)
        for g in glyphs:
            offsets.append(pos)
            pos += len(g.shape)
        offsets.append(pos)
        body = bytearray(struct.pack('<HBBB', self.font_id, self.flags, self.language, len(self.name)))
        body += self.name + struct.pack('<H', count)
        body += struct.pack(f'<{count + 1}I', *offsets) + shapes
        body += struct.pack(f'<{count}H', *(g.code for g in glyphs))
        body += struct.pack('<HHh', self.ascent, self.descent, self.leading)
        body += struct.pack(f'<{count}h', *(g.advance for g in glyphs))
        for g in glyphs:
            body += write_rect(*g.bounds)
        body += self.kerning
        tag = struct.pack('<HI', (TAG_DEFINE_FONT3 << 6) | 0x3F, len(body)) + bytes(body)
        out = bytearray(self.before + tag + self.after)
        struct.pack_into('<I', out, 4, len(out))
        return bytes(out)


if __name__ == '__main__':
    import sys
    font = FontFile(open(sys.argv[1], 'rb').read())
    print('name', font.name.decode('utf-8', 'replace'), 'glyphs', len(font.glyphs),
          'ascent', font.ascent, 'descent', font.descent, 'leading', font.leading, 'kerning bytes', len(font.kerning))
    rebuilt = font.build()
    print('rebuild identical:', rebuilt == font.data, len(rebuilt), len(font.data))
    for ch in sys.argv[2:]:
        g = font.glyph(ord(ch))
        ops = decode_shape(g.shape)
        xs = [o[-2] for o in ops if o[0] in ('move', 'line', 'curve')]
        ys = [o[-1] for o in ops if o[0] in ('move', 'line', 'curve')]
        print(repr(ch), 'advance', g.advance, 'bounds', g.bounds, 'shape bytes', len(g.shape), 'x', min(xs), max(xs),
              'y', min(ys), max(ys), 'ops', ops[:5])
        print('   re-encode equal:', encode_shape(
            [[(c[0][1], c[0][2])] + [o for o in c[1:] if o[0] in ('line', 'curve')] for c in _contours(ops)]) == g.shape) \
            if False else None
