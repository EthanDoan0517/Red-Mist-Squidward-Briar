#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
git lfs install --local
git config --local pull.ff only
git config --local core.longpaths true
git lfs pull
printf 'Git/LFS ready. Pull before work; commit and push afterward.\n'
