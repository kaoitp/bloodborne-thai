import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


root = Path(__file__).parent
ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
with zipfile.ZipFile(root.parent / 'Bloodborne-Thai-English-Updated.xlsx') as workbook:
    strings = [''.join(s.itertext()) for s in ET.fromstring(workbook.read('xl/sharedStrings.xml'))]

    def read_sheet(index):
        sheet = ET.fromstring(workbook.read(f'xl/worksheets/sheet{index}.xml'))
        return [[strings[int(v)] if c.get('t') == 's' else v
                 for c in row if (v := c.findtext(ns + 'v')) is not None]
                for row in sheet.iter(ns + 'row')]

    changed = read_sheet(1)
    full = read_sheet(2)

columns = full[0]
latest = [columns + ['ไทยก่อนตรวจทาน']]
translated = {}
old_by_key = {row[2]: row for row in changed[1:]}
base = [changed[0]]
for file in Path('th').glob('*.json'):
    values = json.loads(file.read_text(encoding='utf-8'))
    source = json.loads(Path('source/en', file.name).read_text(encoding='utf-8'))
    translated.update({f'{file.stem}/{k}': (v, source[k]) for k, v in values.items()})

assert len(translated) == len(full) - 1
for row in full[1:]:
    previous, english, key = row
    thai, source = translated[key]
    assert english == source, key
    row[0] = thai
    if thai != previous:
        latest.append(row + [previous])
    if key in old_by_key:
        saved = old_by_key[key]
        assert saved[:3] == [previous, english, key], key
        base.append(row + saved[3:])
    elif thai != previous:
        base.append(row + [previous, 'ปรับสำนวน/แก้คำแปล'])
root.joinpath('review-rows.json').write_text(
    json.dumps([latest, base, full], ensure_ascii=False), encoding='utf-8')
print('Rows:', [len(sheet) - 1 for sheet in (latest, base, full)])
