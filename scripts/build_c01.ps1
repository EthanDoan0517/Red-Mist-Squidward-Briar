$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$taskPython = 'C:/Users/etqdo/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$taskBlender = 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
$taskModTools = 'C:/Users/etqdo/Downloads/cslol-go/cslol-tools/mod-tools.exe'
if (Test-Path 'output/RedMist-Squidward-Briar-C01.fantome') { throw 'C01 already exists. Preserve this gameplay checkpoint; create a new version for changed inputs.' }
& $taskPython scripts/verify_export.py
if ($LASTEXITCODE) { throw 'Export verification failed' }
& $taskBlender --background --python scripts/build_model.py
if ($LASTEXITCODE) { throw 'Model build failed' }
& $taskBlender --background --python scripts/validate_poses.py
if ($LASTEXITCODE) { throw 'Pose validation failed' }
& $taskPython scripts/prepare_package.py
if ($LASTEXITCODE) { throw 'Texture staging failed' }
& $taskModTools addwad work/candidate-c01/Briar.wad.client work/candidate-c01/mod '--game:C:/Riot Games/League of Legends/Game' --noTFT
if ($LASTEXITCODE) { throw 'WAD build failed' }
& $taskModTools export work/candidate-c01/mod output/RedMist-Squidward-Briar-C01.fantome '--game:C:/Riot Games/League of Legends/Game' --noTFT
if ($LASTEXITCODE) { throw 'Fantome export failed' }
& $taskPython scripts/validate_package.py
if ($LASTEXITCODE) { throw 'Package validation failed' }
