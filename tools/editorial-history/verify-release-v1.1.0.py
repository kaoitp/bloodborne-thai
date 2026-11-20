import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import zipfile

sys.path.insert(0, str(Path('tools').resolve()))
from fmgtool import Bnd4, Fmg, dcx_read
from install import FILES, copy_files
from thaifont import shape_text


assets = Path(sys.argv[1]).resolve()
windows = 'bloodborne-thai-windows-x64.zip'
linux = 'bloodborne-thai-linux-x64.tar.gz'
manifest = {}
for line in (assets / 'SHA256SUMS.txt').read_text(encoding='ascii').splitlines():
    digest, filename = line.split()
    assert filename not in manifest
    manifest[filename] = digest
assert set(manifest) == {linux, windows}
for name, digest in manifest.items():
    with (assets / name).open('rb') as asset:
        assert hashlib.file_digest(asset, 'sha256').hexdigest() == digest, name
    print(f'{name}: SHA-256 matched')

version = Path('VERSION').read_bytes().strip()
with tarfile.open(assets / linux, 'r:gz') as package:
    assert set(package.getnames()) == {'bloodborne-thai', 'README.md', 'VERSION', 'OFL.txt'}
    assert package.getmember('bloodborne-thai').mode & 0o111
    assert package.extractfile('VERSION').read().strip() == version
    assert package.extractfile('bloodborne-thai').read(4) == b'\x7fELF'
print('Linux archive contains version, executable, README and font license')

original = Path(sys.argv[2])
with tempfile.TemporaryDirectory(prefix='release-smoke-', dir=assets) as scratch:
    scratch = Path(scratch)
    with zipfile.ZipFile(assets / windows) as package:
        assert package.testzip() is None
        assert set(package.namelist()) == {
            'bloodborne-thai.exe', 'Install Thai.bat', 'README.md', 'VERSION', 'OFL.txt'
        }
        assert package.read('VERSION').strip() == version
        binary = scratch / 'bloodborne-thai.exe'
        binary.write_bytes(package.read(binary.name))
    game = scratch / 'Game copy'
    target = game / 'dvdroot_ps4'
    copy_files(original, target)
    subprocess.run([str(binary), 'install', str(game)], check=True)
    subprocess.run([str(binary), 'install', str(game)], check=True)
    verified = 0
    for relative in FILES[:2]:
        family = relative.name.split('.')[0]
        rebuilt = Bnd4(dcx_read((target / relative).read_bytes()))
        for source in Path('th').glob(f'{family}.*.json'):
            index = int(source.stem.split('.')[1])
            values = Fmg(rebuilt.files[index]).strings
            expected = json.loads(source.read_text(encoding='utf-8'))
            assert all(values[int(key)] == shape_text(value) for key, value in expected.items()), source
            verified += len(expected)
    subprocess.run([str(binary), 'restore', str(game)], check=True)
    assert all((target / name).read_bytes() == (original / name).read_bytes() for name in FILES)
    print(f'Windows package install, update, readback of {verified:,} translations, and restore passed')
