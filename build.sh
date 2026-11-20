#!/usr/bin/env bash
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
    echo "Run build.sh on Linux x86-64. On Windows, use build.ps1." >&2
    exit 1
fi

python=python3.13
if [[ -x .venv-linux/bin/python ]]; then
    python=.venv-linux/bin/python
fi

"$python" tools/package_notices.py out/linux-notices/licenses

# The installer only reads ZIP archives and does not use TLS, readline or ctypes.
"$python" -m PyInstaller --noconfirm --onefile --noupx --name bloodborne-thai \
    --exclude-module ssl --exclude-module _hashlib --exclude-module readline \
    --exclude-module bz2 --exclude-module lzma --exclude-module ctypes \
    --add-data "$PWD/th:th" --add-data "$PWD/fonts:fonts" \
    --workpath out/pyinstaller-linux --specpath out/linux --distpath out/linux tools/install.py

archive=out/bloodborne-thai-linux-x64.tar.gz
tar -czf "$archive" -C "$PWD/out/linux" bloodborne-thai \
    -C "$PWD" README.md VERSION LICENSE -C "$PWD/fonts" OFL.txt \
    -C "$PWD/out/linux-notices" licenses
printf '%s\n' "$PWD/$archive"
