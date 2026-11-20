"""Thai glyphs for the game font, and the text pre-shaping that goes with them.

The game's text renderer draws one glyph per character with no OpenType shaping, so Thai
marks are added as zero-width glyphs with their position baked into the outline. Each mark
gets variants (shifted left for tall consonants, raised above an upper vowel, lowered under
a consonant with a tail) at private-use code points; shape_text() picks the variant.
"""
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont

from gfxfont import Glyph, encode_shape

CONSONANTS = range(0x0E01, 0x0E2F)
UPPER_VOWELS = (0x0E31, 0x0E34, 0x0E35, 0x0E36, 0x0E37, 0x0E47, 0x0E4D, 0x0E4E)
TONES = (0x0E48, 0x0E49, 0x0E4A, 0x0E4B, 0x0E4C)
LOWER = (0x0E38, 0x0E39, 0x0E3A)
MARKS = UPPER_VOWELS + TONES + LOWER
TALL = {0x0E1B, 0x0E1D, 0x0E1F, 0x0E2C}       # ป ฝ ฟ ฬ: marks move left
TAILED = {0x0E0E, 0x0E0F}                      # ฎ ฏ: lower vowels move down
SARA_AA, SARA_AM, NIKHAHIT = 0x0E32, 0x0E33, 0x0E4D
PUA = 0xF700


def variant(mark, left=False, alt=False):
    """Code point of a positioned mark. alt = raised (tones) or lowered (lower vowels)."""
    if not (left or alt):
        return mark
    return PUA + MARKS.index(mark) * 4 + (2 if left else 0) + (1 if alt else 0)


def shape_text(text):
    out = []
    base, has_upper = None, False
    chars = [ord(c) for c in text]
    i = 0
    while i < len(chars):
        c = chars[i]
        left = base in TALL
        if c in CONSONANTS:
            base, has_upper = c, False
            out.append(c)
        elif base is None:
            out.append(c)
        elif c in TONES and i + 1 < len(chars) and chars[i + 1] == SARA_AM:
            out += [variant(NIKHAHIT, left), variant(c, left, True), SARA_AA]
            base, i = None, i + 1
        elif c == SARA_AM:
            out += [variant(NIKHAHIT, left), SARA_AA]
            base = None
        elif c in UPPER_VOWELS:
            out.append(variant(c, left))
            has_upper = True
        elif c in TONES:
            out.append(variant(c, left, has_upper))
        elif c in LOWER:
            out.append(variant(c, False, base in TAILED))
        else:
            base = None
            out.append(c)
        i += 1
    return ''.join(map(chr, out))


class _ContourPen(BasePen):
    def __init__(self, glyph_set):
        super().__init__(glyph_set)
        self.contours = []

    def _moveTo(self, pt):
        self.contours.append([pt])

    def _lineTo(self, pt):
        self.contours[-1].append(('line', *pt))

    def _qCurveToOne(self, control, pt):
        self.contours[-1].append(('curve', *control, *pt))

    def _curveToOne(self, *_):
        raise ValueError('cubic outlines are not supported: use a TrueType font')


class ThaiSource:
    def __init__(self, path, base_height, font_number=0):
        """base_height: height of ก (a plain consonant) in the game font's glyph units."""
        self.font = TTFont(path, fontNumber=font_number)
        self.glyph_set = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.hmtx = self.font['hmtx']
        (_, _, _, top) = self._bbox(self._contours(0x0E01))
        self.scale = base_height / top
        self.base_top = top

    def _contours(self, code):
        pen = _ContourPen(self.glyph_set)
        self.glyph_set[self.cmap[code]].draw(pen)
        return pen.contours

    @staticmethod
    def _bbox(contours):
        xs, ys = [], []
        for contour in contours:
            xs.append(contour[0][0])
            ys.append(contour[0][1])
            for segment in contour[1:]:
                xs += segment[1::2]
                ys += segment[2::2]
        return min(xs), max(xs), min(ys), max(ys)

    def _glyph(self, code, source, dx=0.0, dy=0.0, advance=None):
        s = self.scale

        def point(x, y):
            return round((x + dx) * s), round(-(y + dy) * s)

        contours = []
        for contour in self._contours(source):
            out = [point(*contour[0])]
            for segment in contour[1:]:
                if segment[0] == 'line':
                    out.append(('line', *point(segment[1], segment[2])))
                else:
                    out.append(('curve', *point(segment[1], segment[2]), *point(segment[3], segment[4])))
            contours.append(out)
        if advance is None:
            advance = round(self.hmtx[self.cmap[source]][0] * s)
        return Glyph(code, encode_shape(contours), advance, (0, 0, 0, 0))

    def glyphs(self):
        """Every Thai glyph to add: plain characters, then the positioned mark variants."""
        out = []
        for code in range(0x0E01, 0x0E5C):
            if code not in self.cmap:
                continue
            if code in MARKS:
                out += self._mark_variants(code)
            else:
                out.append(self._glyph(code, code))
        return out

    def _mark_variants(self, mark):
        units = self.font['head'].unitsPerEm
        xmin, xmax, ymin, ymax = self._bbox(self._contours(mark))
        # Marks sit to the left of the pen position (after the consonant); nothing may advance.
        dx = min(0.0, -0.03 * units - xmax)
        shift_left = -0.19 * units
        gap = 0.05 * units
        _, _, vowel_bottom, vowel_top = self._bbox(self._contours(0x0E34))
        out = []
        if mark in LOWER:
            _, _, _, lower_top = self._bbox(self._contours(0x0E38))
            base_dy = min(0.0, -gap - lower_top) if mark != 0x0E3A else min(0.0, -gap - ymax)
            for alt in (False, True):
                out.append(self._glyph(variant(mark, False, alt), mark, dx, base_dy - (0.22 * units if alt else 0), 0))
            return out
        if mark in TONES:
            low_dy = (self.base_top + gap) - ymin
            high_dy = (vowel_top + gap) - ymin
        else:
            low_dy = high_dy = max(0.0, (self.base_top + gap) - ymin) if ymin < self.base_top else 0.0
        for left in (False, True):
            for alt in ((False, True) if mark in TONES else (False,)):
                out.append(self._glyph(variant(mark, left, alt), mark, dx + (shift_left if left else 0),
                                       high_dy if alt else low_dy, 0))
        return out
