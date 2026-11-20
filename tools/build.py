"""Thai translation mod for the Bloodborne port.

  python tools/build.py export GAME_FOLDER   write the English text to source/en/
  python tools/build.py build GAME_FOLDER    build from th/ and install into the game folder
  python tools/build.py restore GAME_FOLDER  put the original files back

GAME_FOLDER can be the folder holding dvdroot_ps4, or dvdroot_ps4 itself.

The port's mods folder is not used: its link overlay made the game fail at startup here, so the
three files are replaced in the game folder itself and the originals are kept in original/.

Translation files map string id -> Thai text; ids without a translation stay in English.
"""
import json
from pathlib import Path
import shutil
import sys

from fmgtool import Bnd4, Fmg, dcx_read, dcx_write
from gfxfont import FontFile
from thaifont import ThaiSource, shape_text

PROJECT = Path(__file__).resolve().parent.parent
GAME = None
ORIGINAL = PROJECT / 'original'
LANGUAGE = 'enggb'      # the language slot that is replaced (this EU dump shows enggb for English)
ARCHIVES = ('item', 'menu')
THAI_FONT = Path('fonts') / 'Anuphan[wght].ttf'
THAI_BASE_HEIGHT = 11200    # height of a plain Thai consonant in font units (Latin x-height is ~11000)


def archive_path(root, name):
    return root / 'msg' / LANGUAGE / f'{name}.msgbnd.dcx'


def original(relative):
    """The untouched game file, saved to original/ the first time it is asked for."""
    backup = ORIGINAL / relative
    if not backup.is_file():
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(GAME / relative, backup)
    return backup


def restore():
    for backup in ORIGINAL.rglob('*'):
        if backup.is_file():
            shutil.copy2(backup, GAME / backup.relative_to(ORIGINAL))
            print('restored', backup.relative_to(ORIGINAL))


def export():
    out = PROJECT / 'source' / 'en'
    out.mkdir(parents=True, exist_ok=True)
    for name in ARCHIVES:
        bnd = Bnd4(dcx_read(original(archive_path(Path(), name)).read_bytes()))
        for file_id, content in bnd.files.items():
            strings = {str(k): v for k, v in Fmg(content).strings.items() if v and v.strip()}
            (out / f'{name}.{file_id}.json').write_text(
                json.dumps({'table': bnd.name(file_id), 'strings': strings}, ensure_ascii=False, indent=1),
                encoding='utf-8')
            print(f'{name}.{file_id}  {bnd.name(file_id)}  {len(strings)} strings')


def build():
    thai_font = PROJECT / THAI_FONT
    glyphs = ThaiSource(thai_font, THAI_BASE_HEIGHT).glyphs()

    translated = 0
    for name in ARCHIVES:
        raw = original(archive_path(Path(), name)).read_bytes()
        bnd = Bnd4(dcx_read(raw))
        for file_id in list(bnd.files):
            path = PROJECT / 'th' / f'{name}.{file_id}.json'
            if not path.is_file():
                continue
            fmg = Fmg(bnd.files[file_id])
            for key, text in json.loads(path.read_text(encoding='utf-8')).items():
                if int(key) not in fmg.strings:
                    raise KeyError(f'{path.name}: no string {key}')
                fmg.strings[int(key)] = shape_text(text)
                translated += 1
            bnd.files[file_id] = fmg.build()
        archive_path(GAME, name).write_bytes(dcx_write(raw, bnd.build()))

    font_path = Path('menu') / LANGUAGE / 'font.gfx'
    font = FontFile(original(font_path).read_bytes())
    for glyph in glyphs:
        font.add(glyph)
    (GAME / font_path).write_bytes(font.build())
    print(f'{translated} strings translated, {len(glyphs)} Thai glyphs added -> {GAME}')


if __name__ == '__main__':
    commands = {'export': export, 'build': build, 'restore': restore}
    if len(sys.argv) != 3 or sys.argv[1] not in commands:
        sys.exit('Usage: python tools/build.py {export|build|restore} GAME_FOLDER')
    GAME = Path(sys.argv[2]).resolve()
    if GAME.name.lower() != 'dvdroot_ps4':
        GAME /= 'dvdroot_ps4'
    if not archive_path(GAME, 'item').is_file():
        sys.exit(f'no game text found under {GAME}')
    commands[sys.argv[1]]()
