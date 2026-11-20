$ErrorActionPreference = 'Stop'

Push-Location $PSScriptRoot
try {
    $python = 'python'
    if (Test-Path -LiteralPath '.venv/Scripts/python.exe') {
        $python = '.venv/Scripts/python.exe'
    }

    & $python tools/package_notices.py out/windows-notices/licenses
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not collect the license notices for the Windows installer.'
    }

    & $python -m PyInstaller --noconfirm --onefile --noupx --name bloodborne-thai `
        --exclude-module ssl --exclude-module _hashlib `
        --add-data "$PSScriptRoot/th:th" --add-data "$PSScriptRoot/fonts:fonts" `
        --workpath out/pyinstaller --specpath out --distpath out/package tools/install.py
    if ($LASTEXITCODE -ne 0) {
        throw 'Build failed. Check the PyInstaller output and the setup instructions in README.md.'
    }

    $zip = 'out/bloodborne-thai-windows-x64.zip'
    Compress-Archive -LiteralPath 'out/package/bloodborne-thai.exe','Install Thai.bat','README.md','VERSION','LICENSE','fonts/OFL.txt','out/windows-notices/licenses' -DestinationPath $zip -Force
    Write-Output (Resolve-Path -LiteralPath $zip).Path
}
finally {
    Pop-Location
}
