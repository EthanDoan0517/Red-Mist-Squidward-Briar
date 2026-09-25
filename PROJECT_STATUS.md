# Red Mist Squidward Briar project status

Snapshot: 2026-09-25. **Read [STATUS.md](STATUS.md) for the authoritative implementation history and current checkpoint**, then [AGENTS.md](AGENTS.md). Update this summary when the checkpoint changes; do not create a competing detailed log.

## Current stage
C09 voice changes are OFFLINE VALIDATED; gameplay pending. Purchase sound remains unresolved. C02 loads; C07 footsteps and death audio were confirmed by the user.

## Current working files
`References/`, `work/c06-preview.blend` (latest saved visual scene), earlier `work/*-preview.blend`, `work/redmist_candidate.blend`, `work/clarinets-only.blend`, `scripts/build_c09_voice.py`, `scripts/package_c09.py`. C09 is an audio iteration; there is no C09 Blender scene.

## Completed work
Model, clarinets, burger projectile, artwork, effects and custom audio iterations C01-C09; independent layout and package checks. See STATUS.md for subsystem acceptance.

## Current tasks
Test C09 laughter frequency. Obtain a recording buying a named basic item before further purchase-hook changes; preserve existing working audio and visual work.

## Known issues
Gameplay gates remain as recorded in STATUS.md. Build scripts contain absolute desktop tool paths and depend on ignored extracted game data, local tools, and prior candidate stages. A source clone is ready for editing but is not a self-contained clean build environment. See BUILD_SETUP.md.

## Important technical decisions
Preserve native skeleton and motions. Newer Squidward source is clarinet-only. Shared shop audio overrides affect other champions while enabled. Do not infer that the purchase issue is fixed.

Each skin has an independent Git repository with Git LFS for binary sources. Work/output editable scenes are explicitly retained despite their historical location. Keep source references immutable. Do not sync working directories through cloud-drive clients. Existing Red Mist public repository visibility/history is preserved; Queen is public by explicit request.

## Build/package information
Use the version-specific reproduction sequence in STATUS.md. Builds must preserve delivered candidates and use a new version or separate working copy. `.fantome` files are excluded from Git and distributed as GitHub Release assets. RELEASE_MANIFEST.json records the preserved local packages, hashes and sizes. Offline validation is not gameplay acceptance. User performs game/mod-manager installation and tests.
