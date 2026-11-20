from pathlib import Path
import os
import subprocess
import tempfile
from textwrap import dedent
import zipfile

workflow = Path('.github/workflows/release.yml').read_text(encoding='utf-8')

def shell_step(name):
    block = workflow.split(f'      - name: {name}\n', 1)[1].split('\n      - ', 1)[0]
    return dedent(block.split('        run: |\n', 1)[1])

version = Path('VERSION').read_bytes()
with zipfile.ZipFile('out/bloodborne-thai-windows-x64.zip') as archive:
    assert archive.testzip() is None
    assert archive.read('VERSION') == version
    assert set(archive.namelist()) == {'Install Thai.bat','bloodborne-thai.exe','README.md','VERSION','OFL.txt'}
    with tempfile.TemporaryDirectory(dir=Path('out').resolve()) as temp:
        installer = Path(temp, 'bloodborne-thai.exe')
        installer.write_bytes(archive.read(installer.name))
        subprocess.run([str(installer)], input='\n', text=True, check=True)
print('Windows ZIP includes matching VERSION and its installer starts.')

if '--bash' not in __import__('sys').argv:
    raise SystemExit

bash = os.environ.get('BASH', 'bash')
mock = '''
gh() {
    printf '%s %s\\n' "$1" "$2" >> invocations
    case "$1 $2" in
        'api --paginate')
            if [[ "$MOCK_STATE" == unavailable ]]; then return 1; fi
            printf '%s\\n' "$MOCK_STATE" ;;
        'api --method')
            [[ "$3 $4 $5 $6 $7 $8" == "POST repos/example/mod/git/refs -f ref=refs/tags/v1.0.0 -f sha=$GITHUB_SHA" ]] ;;
        'api repos/example/mod/git/matching-refs/tags/v1.0.0') printf '%s\\n' "$MOCK_SHA" ;;
        'release create') [[ "$*" == *'--verify-tag'* && "$3" == v1.0.0 ]] ;;
        'release upload') [[ "$*" == *'--clobber'* && "$3" == v1.0.0 ]] ;;
        'release edit') [[ "$3 $4" == 'v1.0.0 --draft=false' ]] ;;
        *) return 33 ;;
    esac
}
'''
sha = 'a' * 40
with tempfile.TemporaryDirectory(dir=Path('out').resolve()) as temp:
    root = Path(temp)
    steps = {'version': shell_step('Check release version'), 'publish': shell_step('Publish installers and checksums')}
    for name, content in steps.items():
        (root / f'{name}.sh').write_text(mock + '\n' + content, encoding='utf-8', newline='\n')
        subprocess.run([bash, '--noprofile','--norc','-n',f'{name}.sh'], cwd=root, check=True)
    (root / 'VERSION').write_bytes(version)
    (root / 'bloodborne-thai-windows-x64.zip').write_bytes(b'windows test')
    (root / 'bloodborne-thai-linux-x64.tar.gz').write_bytes(b'linux test')

    def check(step, state, tag_sha, calls, exit_code=0):
        (root / 'invocations').write_text('')
        (root / 'output').write_text('')
        env = dict(os.environ, GH_REPO='example/mod', GITHUB_OUTPUT='output', GITHUB_SHA=sha, TAG='v1.0.0', RELEASE_STATE=state, MOCK_STATE=state, MOCK_SHA=tag_sha)
        result = subprocess.run([bash, '--noprofile','--norc','-euo','pipefail',f'{step}.sh'], cwd=root, env=env, text=True, capture_output=True)
        actual_calls = (root / 'invocations').read_text().splitlines()
        assert result.returncode == exit_code and actual_calls == calls, (step, state, result.returncode, actual_calls, result.stderr)
        return (root / 'output').read_text().splitlines()

    assert check('version', '', '', ['api --paginate']) == ['tag=v1.0.0', 'state=']
    assert check('version', 'published', sha, ['api --paginate']) == []
    assert check('version', 'draft', sha, ['api --paginate']) == ['tag=v1.0.0', 'state=draft']
    assert check('version', 'manual', sha, ['api --paginate'], 1) == []
    assert check('version', 'unavailable', '', ['api --paginate'], 1) == []
    (root / 'VERSION').write_text('1.0.bad')
    assert check('version', '', '', [], 1) == []

    tag_lookup = 'api repos/example/mod/git/matching-refs/tags/v1.0.0'
    check('publish', '', '', [tag_lookup, 'api --method', 'release create'])
    check('publish', '', sha, [tag_lookup, 'release create'])
    check('publish', 'draft', sha, [tag_lookup, 'release upload', 'release edit'])
    check('publish', '', 'b' * 40, [tag_lookup], 1)
    check('publish', 'draft', '', [tag_lookup], 1)
    assert len((root / 'SHA256SUMS.txt').read_text().splitlines()) == 2
print('Release Bash steps passed syntax and 11 mocked scenarios.')
