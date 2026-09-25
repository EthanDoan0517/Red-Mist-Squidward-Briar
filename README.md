# Red Mist Squidward Briar

A League of Legends custom skin. Start with [PROJECT_STATUS.md](PROJECT_STATUS.md), [STATUS.md](STATUS.md), and [AGENTS.md](AGENTS.md). C09 voice changes are OFFLINE VALIDATED; gameplay pending. Purchase sound remains unresolved. C02 loads; C07 footsteps and death audio were confirmed by the user.

## Clone on desktop or laptop (Git Bash)
Install Git for Windows with Git LFS, then authenticate to GitHub through Git Credential Manager when prompted. Use a normal local directory outside OneDrive/Google Drive:

```bash
git lfs install
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/EthanDoan0517/Red-Mist-Squidward-Briar.git
cd Red-Mist-Squidward-Briar
bash scripts/setup-git.sh
```

Setup installs the repository LFS hook and uses fast-forward-only pulls to avoid accidental merges. Git LFS downloads binary contents automatically on clone/pull; if downloads were skipped, run `git lfs pull`. Configure your own `git config --global user.name` and `user.email` if not already set. Every computer has its own clone and setup; local Git config does not travel with commits.

## Normal workflow
Before starting (finish/commit any previous changes first):

```bash
git pull
```

After finishing, save/close editing applications, update status when needed, and review the changes:

```bash
git status
git diff --stat
git add .
git commit -m "<description>"
git push
```

Finish pushing on one computer before pulling on the other. Avoid editing the same binary on both computers concurrently: Git cannot merge Blender/audio/image contents. If a fast-forward pull is refused, preserve both sets of changes and resolve the divergent history; do not force-push or discard work. For a safe experiment use `git switch -c codex/experiment-name`; first push with `git push -u origin HEAD`. To undo a published change use `git revert <commit>` and push; for a single old asset use `git restore --source=<commit> -- "path/to/asset"`, then commit it. These preserve history.

## Tracking policy
Git stores scripts, Markdown, maps, manifests and validation evidence. Git LFS stores supplied binary assets (including Blender/FBX, textures, audio projects/recordings, source archives and native-format source references) and retained editable scenes. All listed binary extensions use LFS consistently even when small. XML evidence stays in Git because current audio scripts read it as input.

Ignored: extracted game files, downloaded runtimes/tools, candidate staging, caches, logs, backups, local settings/secrets and generated packages. Explicit exceptions retain `work/*.blend`, diagnostic `work/*.py`, `output/*.blend`, `output/*.png`, and `output/TEST-*.md`. Keep new important source assets under the existing source/reference directories; never hide unique work in an ignored staging directory. No original assets were deleted by this setup.

## Builds and downloads
See [BUILD_SETUP.md](BUILD_SETUP.md) for local build prerequisites and [STATUS.md](STATUS.md) for candidate recipes. Download packages from [GitHub Releases](https://github.com/EthanDoan0517/Red-Mist-Squidward-Briar/releases). Archived candidates are prereleases, not a claim of gameplay acceptance. Package SHA256 values are in [RELEASE_MANIFEST.json](RELEASE_MANIFEST.json). Do not commit each `.fantome` build. Keep local rollback packages until release upload and hashes are verified.

Git/LFS source history starts at this import; earlier candidate stages remain documented and packaged, not invented historical source commits. GitHub LFS storage and downloads depend on the account's available quota.
