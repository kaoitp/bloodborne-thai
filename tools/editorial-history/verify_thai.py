import collections
import json
from pathlib import Path
import re
import sys
import subprocess
import tempfile
import zipfile

sys.path.insert(0, 'tools')
from fmgtool import Bnd4, Fmg, dcx_read
from gfxfont import FontFile
from install import FILES, copy_files
from thaifont import shape_text
from review import load


def parse_pairs(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), 'Duplicate JSON keys'
    return result


def bank(raw):
    return Bnd4(dcx_read(raw))


def tables(bnd):
    return {table: Fmg(raw).strings for table, raw in bnd.files.items()}


original = Path(sys.argv[1])
originals = {path: (original / path).read_bytes() for path in FILES}
original_tables = {path.name.split('.')[0]: tables(bank(originals[path])) for path in FILES[:2]}
old = {}
new = {}
counts = collections.Counter()
format_token = re.compile(r'<[^>\n]+>|%(?:[0-9]+\$)?[-+ #0]*[0-9]*(?:\.[0-9]+)?[a-zA-Z%]|\{[^{}\n]+\}|\[\[[^\n]+?\]\]|\$[A-Za-z0-9_]+\$|\\n')
number = re.compile(r'[-+]?[0-9]+(?:\.[0-9]+)?%?')
for path in sorted(Path('th').glob('*.json')):
    table = path.stem
    family, table_id = table.split('.')
    source = original_tables[family][int(table_id)]
    old[table] = json.loads(subprocess.check_output(['git','show',f'HEAD:{path.as_posix()}']), object_pairs_hook=parse_pairs)
    new[table] = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=parse_pairs)
    assert list(old[table]) == [k for k in new[table] if k in old[table]], table
    for k, text in new[table].items():
        assert k == str(int(k)) and source[int(k)].strip() and text.strip(), (table, k)
        before = old[table].get(k)
        if before == text:
            continue
        counts[table] += 1
        assert format_token.findall(source[int(k)]) == format_token.findall(text), (table, k, source[int(k)], text)
        for control in ('\t','\r','\ufeff','\x00','\ufffd'):
            assert control not in text, (table, k, control)
        if table in {'menu.35','menu.200','menu.204','menu.32','menu.33'}:
            assert number.findall(source[int(k)]) == number.findall(text), (table, k, source[int(k)], text)

for low, high in [(1510, 1512), (1513, 1515), (1516, 1518), (1519, 1521)]:
    assert len({original_tables['item'][24][i].strip() for i in range(low, high+1) if i in original_tables['item'][24]}) == 1
assert new['menu.1']['2800003'] == new['menu.30']['14000210']
assert 'ฝันร้ายของนักล่า' in new['item.24']['4017']
assert 'ผู้เสพติดเสียงสะท้อนโลหิต' in new['item.24']['704']
assert 'โลหิตซีด' in new['menu.30']['10012000'] and 'โลหิตซีด' in new['menu.3']['900400']
print(f'{sum(map(len,new.values())):,} translations in {len(new)} tables inspected, {counts.total():,} changed across {len(counts)} tables')
print('ID order, source membership, template variables and selected numeric modifiers passed')
print('Changes by table:', dict(counts))

if '--package' not in sys.argv:
    sys.exit()

with tempfile.TemporaryDirectory(prefix='thai-review-', dir=Path('out').resolve()) as scratch:
    scratch = Path(scratch)
    with zipfile.ZipFile(Path('out/bloodborne-thai-windows-x64.zip')) as package:
        assert package.testzip() is None
        assert set(package.namelist()) == {'bloodborne-thai.exe','Install Thai.bat','OFL.txt','README.md'}
        executable = scratch / 'bloodborne-thai.exe'
        executable.write_bytes(package.read(executable.name))
    game = scratch / 'Game copy'
    target = game / 'dvdroot_ps4'
    backup = game / 'bloodborne-thai-backup'
    copy_files(original, target)
    subprocess.run([str(executable), 'install', str(game)], check=True)
    font_codes = FontFile((target / FILES[2]).read_bytes()).codes()
    assert font_codes >= FontFile(originals[FILES[2]]).codes()
    expected_thai = set()
    for relative in FILES[:2]:
        family = relative.name.split('.')[0]
        rebuilt = tables(bank((target / relative).read_bytes()))
        assert rebuilt.keys() == original_tables[family].keys()
        for table_id, source in original_tables[family].items():
            translation = new.get(f'{family}.{table_id}', {})
            assert rebuilt[table_id].keys() == source.keys(), (family, table_id)
            for key, value in source.items():
                changed = translation.get(str(key))
                expected = value if changed is None else shape_text(changed)
                assert rebuilt[table_id][key] == expected, (family, table_id, key)
                if changed is not None:
                    expected_thai.update(ord(char) for char in expected if 0x0E00 <= ord(char) <= 0x0E7F or 0xF700 <= ord(char) < 0xF800)
    assert expected_thai <= font_codes, sorted(expected_thai - font_codes)
    assert all((backup / p).read_bytes() == raw for p, raw in originals.items())
    subprocess.run([str(executable), 'restore', str(target)], check=True)
    assert all((target / p).read_bytes() == raw for p, raw in originals.items())
    assert not backup.exists()
    assert not (game / 'bloodborne-thai-work').exists()
    assert all((original / p).read_bytes() == raw for p, raw in originals.items())
    print(f'Windows ZIP install/readback, {len(expected_thai)} Thai glyph codes, and byte-for-byte restore passed')
