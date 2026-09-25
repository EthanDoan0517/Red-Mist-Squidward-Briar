# Red Mist Squidward Briar

## Current checkpoint — C09 frequent laughter; purchase unresolved, 2026-09-20

**VOICE OFFLINE VALIDATED — AWAITING C09 GAMEPLAY. PURCHASE BLOCKED ON RUNTIME SOUND IDENTIFICATION.** Candidate: `skin versions/RedMist-Squidward-Briar-C09.fantome`, 7,529,683 bytes. SHA256 `5515644ea707b2048af95d240e1a486affe8b4135f97b2741fda49f3b290ce15`. User reports C08 purchases still play the normal shop sound in Summoner's Rift Practice Tool using CSLoL Manager, and requests much more laughter in attacks/movement.

Voice: attack pool now12/15 laughter and3/15 existing screams (80/20 nominal eligible choices); standard movement17/17 laughter, long movement11/11 laughter. All previously silent slots in these pools replaced with the existing full6.122s Squidward laugh1 recording. Native weights/shuffle/avoid-repeat, command timing and max1/killNewest concurrency remain unchanged: eligibility is not every hit/footstep, and another line may block a new one. Future laugh emote and all other VO slots preserved. Only38Sound media-size fields and38WPK payloads change; source media reused with C08 decode evidence. Original Briar voices remain muted outside custom replacements. E, footsteps, death, all visuals and Common purchase banks are byte-identical C08.

Purchase diagnosis: installed mod, actual saved-profile overlay, and isolated CLI overlay all contain exact C08 HUD bank bytes. Saved profile enables only C08; filtered latest patcher log confirms Common was verified AND redirected. This disproves a missing Common override/manager-conflict hypothesis. Known seven purchase events are routed; cached UI/other bank scan found only an additional debt-specific route, not a general explanation. No further purchase change justified. Do not repeat guessed routing, gain or codec changes. Need a short recording buying one named basic item with the audible original sound to identify actual runtime sound/hook (and distinguish a click from the buy effect). Evidence: `evidence/c09_purchase_runtime_audit.json`, `c09_purchase_alternative_strings.json`. Isolated CSLoL compilation also propagates Common HUD overrides into Map30; earlier blanket Arena noncoverage assumption was too strong. No actual manager/profile/game mutations were made.

Validation: 164WPK spans, exact voice-object/media scope and exclusive playlist consumers, independent wwiser parse; existing decoded laugh reused. Final package CRC,20WAD entries (16base,2voice,2Common), exact native hashes and all extracted payload equality pass. Base Briar and Common entire payloads verified unchanged. Evidence: `evidence/c09_voice_validation.json`, `c09_package_validation.json`.

Immediate next action: user enables only C09 and checks increased attack/movement laughter. For purchase work, provide a short recording of buying a named basic item, with sound audible. Pause purchase experiments until that or another materially new diagnostic finding; keep completed voice work. Follow skill validation-checkpoints rule after repeated failed attempts. Stop for gameplay feedback; do not call purchase fixed.

Reproduce: bundled Python `scripts/build_c09_voice.py`, then `scripts/package_c09.py`; voice stage `work/c09-voice`, final stage `work/candidate-c09`. Delivered candidates preserved.

## Previous checkpoint — C08 E onset, purchase/laugh repair and new VO

**OFFLINE VALIDATED — AWAITING C08 GAMEPLAY.** Candidate: `skin versions/RedMist-Squidward-Briar-C08.fantome`, 4,922,960 bytes. SHA256 `6b52108c2cce5b3ca13b27735f2c737986a658e2a6ae834aabd85e80cb105856`. User confirms C07 custom footsteps and death violin BOTH work; preserve these runtime-confirmed subsystems. E audible at release but requested at charge onset. C07 purchase and laugh failed; no general visual acceptance inferred.

E: native registered OnCast action26936025 now targets the existing one-shot custom E container261100005. Release event retains only its native old-charge stop action, removing shout playback at release. Original E audio bytes retained. Full shout starts with charge; release does not replay it. Native charge timing remains to be confirmed in game.

Purchase: independent audit found C07 covered only two legacy routes. Five modern registered basic/component/legendary/mythic/upgrade purchase routes bypassed them. All seven Play actions now target the existing custom purchase Sound1048964796/media41429280. Native instance cap1 kills oldest on a new equal-priority purchase; C07 custom clip bytes retained. Shared Common HUD applies to any champion while enabled. Summoner's Rift/Common coverage; Arena Map30's separate HUD bank is not overridden. Sell/undo/other HUD events preserved. Audit: `evidence/c08_purchase_audit.json`.

Laugh: full 'fuuuutureeee' moved to restored native registered VO Laugh3DGeneral event660848939/media711994501; C07 custom animation start retired. C07 laugh's precise runtime failure cause remains unproven; native registered VO replaces that failed route. Four new full supplied clips added through native VO playlists: three scream files occupy3/15 Attack2DGeneral slots; Squidward laugh1 occupies1/17 standard movement and1/11 long movement slots. Remaining media stay silent. These are occasional command responses, not every hit or footstep. Native shuffle/avoid-repeat and engine cadence retained; nominal eligible selection shares20%,5.88%,9.09%, not fixed time cooldowns. Native VO cap1 rejects incoming lines while an existing line plays, so laugh may not restart/interrupt another voice. Ult voice remains reserved.

Validation: exact SFX3/HUD8/VO10 HIRC-object deltas; six of164voice media replaced, others unchanged silent. SFX/HUD audio banks byte-identical C07; footsteps/death objects retained. Four new full WEM clips independently decode without saturation; three banks independently parse; streamed voice IDs/WPK extents and native schema validated; strict animation BIN sizes/exactEOF. All C07 visual assets, skin BIN, model, props and art remain byte-identical, reusing prior checks. Final20WAD payloads (16base,2en_US,2Common), archiveCRC, path hashes and all re-extracted bytes pass. Evidence: `evidence/c08_audio_validation.json`, `c08_audio_replacement_map.json`, `c08_package_validation.json`.

Immediate next action: enable only C08. Check E at charge start and release (no duplicate), each shop purchase class and rapid buys, laugh emote while no other voice plays, occasional attack/movement voices across multiple commands, and footsteps/death regression. Check volume/long-clip frequency. Stop for gameplay feedback before further changes; do not call untested C08 fixes confirmed. No game/manager interaction.

Reproduce with bundled Python: `scripts/build_c08_audio.py`, `scripts/validate_c08_audio.py`, `scripts/package_c08.py`. Stage `work/candidate-c08/`; native source and prior candidates preserved. Package refuses overwrite.

## Previous checkpoint — C07 large R backdrop, flower and purchase/laugh audio

**OFFLINE VALIDATED — AWAITING C07 GAMEPLAY.** Candidate: `skin versions/RedMist-Squidward-Briar-C07.fantome`, 4,358,796 bytes. SHA256 `4cd12c369b7da9b40e6243f54ba26a58507af29837061d175c80db6b38d23af1`. User screenshot shows C06 background on the small circle and sideways; requested massive ring instead. User explicitly clarified flat ground, artwork upright on screen. No general C06 acceptance inferred.

Visuals: screenshot maps the massive ring to `Briar_Base_R_warning` while Briar is travelling to the marked enemy. Its12visual layers become one Boys Who Cry ground decal using native500unit footprint/host lifecycle and50%peak opacity with original fades. Native texture noise multiplication removed; white RGB preserves artwork. Two small Berserk Target variants now use additive glowing red SpongeBob flower from supplied reference. Ground plane fixed at90degree pitch, UV sampling rotated90degrees to correct screenshot floor-left→floor-bottom, emitter/particle local orientation disabled and angular rates zero. Exact engine screen orientation still needs gameplay confirmation. Arrival AoE burst, burger spin/size and other effects preserved.

Audio: full9.845s 'becauseimalloutofmoney' clip on shared HUD Store_Buy and Store_Upgrade, replacing their shared media41429280. Repeated purchases stop previous buy/upgrade voice before playing; original-13dB makeup gain removed. **Common.wad.client override affects purchases on any champion while enabled**, while sell/undo/open and115other HUD media stay unchanged. Full14.694s 'fuuuutureeee' clip on Briar laugh via isolated custom event; repeated laugh restarts, running/death/respawn stop it. All442existing C06 SFX HIRC objects and112media remain byte-identical; C06 en_US silence inherited. Original motion tracks untouched. Replacement IDs: `evidence/c07_audio_replacement_map.json`.

Validation: independent visual expected-value audit confirms exactly3skinBIN entries changed/61untouched,50%peak alpha, flat-world orientation flags and flower mips. Original C06 model/body/eye/prop/HUD textures preserved byte-for-byte, so prior pose evidence reused. Audio native-bank/DIDX/HIRC extents, wwiser parse and Init-backed event simulations pass; fullclips independently decoded with no saturation; actualdeath clip stop asserted. Final archive CRC,16base+2locale+2Common entries, native hashes, strict SKN/BIN and all re-extracted payload bytes pass. Evidence: `evidence/c07_r_validation.json`, `c07_independent_visual_validation.json`, `c07_flower_validation.json`, `c07_audio_validation.json`, `c07_package_validation.json`. Flower source/edit provenance: `evidence/c07_flower_imagegen.txt`.

Immediate next action: enable only C07 and test R from several directions. Confirm massive background upright on ground at50%opacity, small red flower, lifecycle/cleanup. Buy components/completed items/consumables/upgrades including rapid purchases; test laugh/repeat/move/death. Check earlier eye/death fixes if still unconfirmed. Stop for gameplay feedback before further refinement. No game or manager control performed.

Reproduce: `scripts/build_c07_r.py`, `encode_c07_flower.py`, `validate_c07_visuals.py`, `build_c07_audio.py`, `validate_c07_audio.py`, `package_c07.py`. Bundled Python; native tools reused. Stage: `work/candidate-c07/`; previous candidates preserved.

## Previous checkpoint — C06 eye/death fixes, audio silence and R backdrop

**OFFLINE VALIDATED — AWAITING C06 GAMEPLAY.** Candidate: `skin versions/RedMist-Squidward-Briar-C06.fantome`, 2,116,851 bytes. SHA256 `12e95c792497acc12023b2ef1b97669ef16e468c304c50a6f6eccf08baa3b9e6`. User reported C05 eyes black and death song not working; these subsystems were not accepted. C02 remains explicitly load-confirmed rollback.

Implemented: clarinets corrected to **2.5x C04**, 5/6 of C05 size; burger stays at C05 size and rotates about vertical Y at 180degrees/sec (one revolution/2sec), preserving level orientation. Both post-hit `Briar_Base_R_Berserk_Target` detail variants use one neutral, alpha-blended ground circle with the reconstructed Boys Who Cry background. Two supplied frames used, Squidward removed, original green curtain/yellow eyes/tear/floor retained. Prearrival warning and arrival burst remain separate native cues. Native target-size binding and lifecycle retained.

Eye cause verified: C05 colored eye and blood triangles had inward winding, hidden by engine culling but visible in Blender's double-sided preview. C06 corrects facing, removes dark pupil/iris overlays, centers white inside red, and adds a native skinned bloom material cloned from Briar Skin20's Hair_Frenzy_Fresnel_Bloom_inst. Custom R/G mask gives red and white eye emission; black sockets and blood are zero-mask. Body texture and all original body vertex fields unchanged. New preview explicitly handles backfaces; Blender emission is an appearance approximation, not the native shader or proof of gameplay bloom.

Audio: 109 original base SFX slots silenced, 164 base en_US VO clips silenced and 53VO events disabled; custom E and footstep media retained byte-for-byte. Death violin gets an isolated direct event on death animation frame1, bypassing native death container's -20dB MakeupGain; respawn stop retargeted to new violin Sound. Original motion tracks untouched. Installed locale is en_US; global map/item/summoner/UI sounds and other locales are outside Briar-owned coverage. Editable native/custom replacement slots: `evidence/c06_audio_replacement_map.json`.

Validation: strict SKN footer/material/index ranges, outward colored triangles, unchanged original body, nine finite frenzy pose samples and inspected closeup/idle/attack previews; strict skin and animation BIN size/EOF checks; target-circle and rotation scope; native TEX roundtrip and alpha; independent audio bank/WPK parsing, silence decode, custom media identity and event simulation. Final Fantome has15base+2locale payloads; CRC, all native hashes and re-extracted bytes pass. Evidence: `c06_visual_build.json`, `c06_pose_validation.json`, `c06_r_validation.json`, `c06_textures.json`, `c06_audio_validation.json`, `c06_package_validation.json` under evidence/. Image prompt/provenance: `evidence/c06_circle_imagegen.txt`.

Immediate next action: enable only C06 on base Briar. Check red/white eyes in normal/frenzy states; clarified clarinet scale; burger's level two-second rotation; Boys Who Cry circle on an R-marked enemy and cleanup; absence of native voice/ability sounds; E/steps; death violin then respawn stop. Stop for feedback before dependent refinement. No game/manager interaction performed.

Independent review passed: `evidence/c06_independent_review.json` and reproducible `scripts/review_c06_visuals.py`. All surviving face triangles agree with outward normals;424 reversed,128 dark-center triangles removed,66 white-center vertices translated. Original body/index payload preserved. Native donor material LINK, techniques/macros/states and both samplers validated; R baseline unchanged beyond face override/new material. Global shader720ce467 is inherited from native donor; its runtime resolution/bloom strength remain gameplay checks.

Reproduction: bundled Python `encode_c06_textures.py`; `build_c06_r.py`; Blender `build_c06_visuals.py`; audio `build_c06_audio.py` and `validate_c06_audio.py`; Blender `validate_c03_visuals.py -- c06`; bundled Python `package_c06.py`. Scripts live in scripts/. Package preserves delivered checkpoints. C06 working staging: `work/candidate-c06/` with base and en_US WAD folders.

## Previous checkpoint — C05 reference face, larger props and audio

**OFFLINE VALIDATED — AWAITING C05 GAMEPLAY.** Candidate: `skin versions/RedMist-Squidward-Briar-C05.fantome`, 3,245,887 bytes; SHA256 `4d18231d76578447cdd98191efedc05a678e45a9c1d6b93e144bdccf2fa81704`. C02 remains the explicitly load-confirmed rollback. C04 received further-change feedback; no broad acceptance inferred.

Implemented: clarinets 3x C04 (5.25x original C03) about existing hand grips; burger 2x C04 around established center, maintaining bun-up world orientation and burger-only missile. Cleared 64 emitters in seven native frenzy-dagger/R back-jet systems to remove weapon flares. Other particle entries and R flight timing/binding remain unchanged. Gray body atlas targets #CAC6CF with original shading; source UVs/geometry retained. `References/ref image squidward.png` guides large black eye sockets, red/white eyes with brown iris/black pupil/highlight, and six cheek-following blood trails. Native face palette stores exact #FE4E4A, #EE6054, #650021. Existing portrait/loading art retained. Preview colors depend on lighting; runtime appearance remains unconfirmed.

All three supplied audio files integrated: E release shout (2.547s, native 200ms delay retained); death violin (9.6s, explicit stop on respawn); 0.24s footstep accents sampled from walking clip, triggered at run contacts. Footsteps use isolated event/action/sound objects; original W foley preserved. Two native SFX banks and sound-only animation graph events added; original skeleton and ANM motion files untouched. Full walking clip is not played repeatedly on each footstep.

Validation: strict SKN 4.1 footer/layout; valid weights/indices/UVs; nine finite native frenzy pose samples and inspected idle/attack/face/burger renders; native TEX roundtrips; strict skin/animation BIN declared sizes and exact EOF; independent audio decoding, bank parsing and event-to-media simulation; no decoded audio clipping. Fantome CRC, all 13 native WAD hashes and final extracted byte equality pass. Evidence: `evidence/c05_visual_build.json`, `c05_pose_validation.json`, `c05_textures.json`, `c05_audio_validation.json`, `c05_package_validation.json`. Source and prior packages preserved. No game or manager interaction.

Previews: `evidence/c05_face_closeup.png`, `c05_idle_frenzy.png`, `c05_attack1_frenzy.png`, `c05_spell2_attack.png`, `c05_burger_preview.png`. Body ImageGen prompt/provenance: `evidence/c05_imagegen_prompt.txt`. Clarinets are intentionally much larger than the body at the requested multiplier. Four-leg overlap remains a known gameplay-feedback issue.

Independent helper review passed: `evidence/c05_independent_visual_review.json` verifies exact requested prop multipliers, unchanged original body vertex fields, 1,044 appended Head-weighted face vertices, SKN completeness/material ranges, face path hash, and only eight intended skin-BIN entries changed (55 untouched). Seven complete dedicated dagger/jet emitter arrays were cleared. Gameplay must assess large-prop occlusion and flare removal.

Immediate next action: enable only C05 on base Briar and test loading, W size/hand alignment/visibility, R burger scale/orientation and absent weapon flares, eye/body colors, E shout, walking timing and violin stopping on respawn. Stop for gameplay feedback before dependent refinement. Report C05 plus action/state and a clip for defects.

Reproduction: Blender `scripts/build_c05_visuals.py`; bundled Python `scripts/encode_c05_textures.py`; Blender `scripts/validate_c03_visuals.py -- c05`; audio `scripts/build_c05_audio.py` and `scripts/validate_c05_audio.py`; bundled Python `scripts/package_c05.py` (requires fresh staging without merged audio, refuses overwrite). Final stage `work/candidate-c05/Briar.wad.client`.

## Previous checkpoint — C04 larger clarinets, level burger-only flight

**OFFLINE VALIDATED — AWAITING C04 GAMEPLAY.** User requested larger visible clarinets, R burger oriented normally as though resting on the ground (like a Teemo mushroom), and removal of other flying R effects.

Candidate: `skin versions/RedMist-Squidward-Briar-C04.fantome`, 1,326,886 bytes. SHA256 `dfe77d4743608c03bfb4f80e0d9ba2ac698a14fcbd5dd444c1302bfc4bb2a4f6`.

Changes from C03: clarinets uniformly enlarged **1.75x** about their existing hand grips; only the 492 prop vertex positions and model bounds changed. R missile now contains exactly **one emitter: burger**; all remaining 21 native projectile smoke, trails, fire skirts, glow, stones and hitbox visual emitters removed. Constant scale replaces native gem squashing. Burger geometry is already Y-up with buns parallel to X/Z; `isLocalOrientation=false` and `isRotationEnabled=false` request stable world-upright appearance rather than inherited missile orientation. Actual engine orientation must be confirmed in game. Native projectile trajectory/binding/position/lifetime and separate R cast/impact/buff systems retained; removal applies to the flying projectile.

Validation: only SKN and R-containing BIN differ from C03. Body geometry/indices, all weights/UVs/normals, burger mesh, textures, portrait/loading artwork unchanged. Nine sampled frenzy poses remain finite; enlarged idle/attack renders inspected with stable hand attachment. Strict SKN footer and 17,030 independent BIN size checks/exact EOF pass. All 62 other BIN entries unchanged. Final Fantome CRC, nine WAD payloads, decoded byte roundtrip, and custom mesh/texture references pass. Evidence: `evidence/c04_build.json`, `c04_validation.json`, `c04_pose_validation.json`, `c04_package_validation.json`. Preview: `evidence/c04_idle_frenzy.png` and `c04_attack1_frenzy.png`. No new runtime acceptance claimed.

Immediate next action: user enables only C04, checks bigger clarinets through W attacks, and casts R in several directions to confirm burger remains level with bun up and no flight trails/glow. Stop for feedback before further changes. Preserve C03 and load-confirmed C02 as rollbacks.

Reproduce with Blender background `scripts/build_c04.py`; Blender background `scripts/validate_c03_visuals.py -- c04`; bundled Python `scripts/validate_c04.py`; bundled Python `scripts/package_c03.py c04`. Scripts refuse to overwrite delivered C04. Shared `scripts/strict_prop.py` holds the existing independent BIN validator.

## Previous checkpoint — C03 W/R and artwork

**OFFLINE VALIDATED — AWAITING C03 GAMEPLAY.** User confirmed **C02 loads successfully** and explicitly requested W clarinets, burger R, portrait and loading art. C02 is the load-confirmed rollback; this does not imply full model/animation acceptance.

Candidate: `skin versions/RedMist-Squidward-Briar-C03.fantome`, 1,328,521 bytes. SHA256 `fb3f21f15a1bd9ac510bf92d22d1b612ffc684fb5cfc3fb190751b6b276ec3cc`.

Implemented:
- Two clarinets copied only from the new source's Clarinet mesh, attached to native L_Hand/R_Hand. Original Squidward body vertices, indices and diffuse unchanged. Added 492 vertices/760 triangles in native `FrenzyDaggers` submesh. Supplied `References/textures/clarinet.png` is now available and encoded for the existing weapon material. Clarinets inherit frenzy visibility; native graph explicitly shows them in W recast/E frenzy, but initial W and R berserk timing requires runtime confirmation.
- Supplied Krabby Patty FBX exported as a native SCB and textured from its nine supplied material images. R projectile's main gem core now uses this burger; two crystal surface overlays removed. Other 21 R emitters and 62 non-R BIN entries unchanged. Projectile timing, lifetime, attachment, rotation and scale animation remain native; geometry centered to match scaled gem center. Impact/trails retained.
- Supplied Red Mist artwork cropped into square/circular 128x128 portraits and 308x560 loading image. Native formats and circular alpha retained. No client-wide splash/champion-select override and no audio changes.

Validation: strict SKN footer/layout; original body payload equality; normalized valid weights/influences; nine sampled frenzy poses with three reviewed renders; burger SCB layout/roundtrip and textured preview; texture encoding/mips; artwork dimensions/alpha/decoded previews; semantic BIN scope checks plus independent raw binary validation of 17,538 declared sizes/exact EOF; final Fantome CRC/nine WAD payloads/re-extraction byte equality/custom references. Final evidence is hash bound: `evidence/c03_package_validation.json`, `c03_props_build.json`, `c03_pose_validation.json`, `c03_textures.json`, `c03_art_validation.json`, `c03_bin_validation.json`, `c03_independent_review.json`.

Previews: `evidence/c03_idle_frenzy.png`, `c03_attack1_frenzy.png`, `c03_spell2_attack.png`, `c03_burger_preview.png`, `c03_art_contact_sheet.png`. No geometry from the newer Squidward body was used. Prior four-leg overlap remains a gameplay-feedback issue.

Immediate next action: user disables C02 and enables only C03 on base Briar. Check loading art/portraits; both clarinets appearing on W, hand alignment through attacks/W recast and disappearance on frenzy exit; R burger flight, hit/miss and cleanup. Also note native R berserk weapon visibility. Report C03 plus action/state and clip for defects. Stop for feedback before refinement; do not repeat checks or rebuild unchanged candidate.

Reproduction: Blender background `scripts/build_c03_props.py`; bundled Python `scripts/encode_c03_textures.py` and `scripts/edit_c03_bin.py`; Blender background `scripts/validate_c03_visuals.py`; bundled Python `scripts/review_c03_bin.py` then `scripts/package_c03.py`. Artwork precursor: `scripts/build_c03_art.py`. Packaging refuses to overwrite delivered C03. Staging: `work/candidate-c03/Briar.wad.client`. Game/manager profiles not modified.

## Previous checkpoint — C02 load repair (load confirmed)

Historical pending labels below are superseded by the user's successful C02 load report above.

**C01 REJECTED: GAMEPLAY BLOCKER — crashes on loading.** User confirms same match loads with C01 disabled. Logs from 12:17:53 and 12:18:04 show a null Briar character record followed by an exception. Read-only inspection of the actual manager overlay found all 1,352 original WAD entries present and only SKN/texture checksums changed. No manager or game interaction was performed.

Concrete defect: C01's v4.1 SKN stops at byte 934,048; the required 12-byte end tab is missing. Local pyRitoFile writer omits it and its reader ignores it, so earlier same-parser and pose checks falsely implied export readiness. Native Briar and LeagueToolkit's independent format implementation require this footer. Source: https://github.com/LeagueToolkit/league-toolkit/blob/main/crates/ltk_mesh/src/skinned/mod.rs (END_TAB_SIZE and end_tab documentation). Runtime confirmation is still required to establish that this fully resolves the reported crash.

**C02 OFFLINE VALIDATED — AWAITING LOAD RETEST.** Candidate `skin versions/RedMist-Squidward-Briar-C02.fantome`, 959,148 bytes, SHA256 `c3f9ce58ef046f377f8010ef80d196c90192c7f127791be676ddea009c59da21`. Only mesh change is appending the 12 native zero bytes. Geometry, weights, UVs, normals, texture, animations and VFX are unchanged. Previous pose evidence is reused for the byte-identical vertex/index data. `evidence/c02_repair_validation.json` records independent layout checks, final package CRC, exact two-entry scope and extracted payload equality. `scripts/skn_layout.py` now guards exports; `scripts/repair_c02.py` reproduces the repair without rebuilding the model. Prior footer-blind export evidence is superseded.

Immediate next action: user disables C01, enables only C02 and tests loading base Briar in Practice Tool. If successful, collect normal/frenzy gameplay feedback before dependent refinements. No accepted playable baseline exists yet.

Clarinet source found: `References/source/squidward_clarinet_final.blend`. **Use only Clarinet and ShootClarinet; do not use its Squidward body.** Isolated props saved as `work/clarinets-only.blend`; evidence `evidence/clarinet_source.json`. Each prop has 384 vertices. Referenced `clarinet.png` is absent and not packed in the source. Request that texture with the next gameplay feedback. W attachment/integration remains pending load confirmation.

## Previous checkpoint — C01 (rejected)

Goal: model-only Squidward replacement for base Briar, bloody eyes and invisible pillory, preserving Briar animations and most VFX. Source references remain unchanged. No prior AGENTS.md or STATUS.md existed.

Candidate: `output/RedMist-Squidward-Briar-C01.fantome` (959,181 bytes).
SHA256: `094ac00f3d5dbdc09caf7414acf85d69db134fadd8cb25058effc453699dc6cf`.

Implemented: supplied Squidward mesh adapted to Briar's existing bind skeleton. Four tentacle legs share Briar's two leg chains. Native Body submesh only; no pillory, crystal, blades or dagger geometry. Bloody eyes use UV assignments to the source atlas's dark red region, with four small head-weighted blood trails. No raster repaint was necessary. 14,969 exported vertices, 25,918 triangles. Original atlas converted to native DXT1, 1024 square, all 11 mips.

Historical offline checks passed but were insufficient: the export parser missed the required footer. Runtime loading FAILED. Never deliver C01 again. Its package is retained under `skin versions/` for diagnosis.

The current C02 next action above supersedes this historical checkpoint.

Known NOTICEABLE limitation: four tentacle legs share two native leg chains and overlap/cross in sampled attack and R poses. The limbs remain attached and deformation is finite; judge silhouette and clipping at normal gameplay zoom before rig changes. Offline lighting/brightness and blood appearance are not proof of runtime appearance.

## Requested follow-up scope

User requests two clarinets wielded during Briar W. Pending implementation after C01 gameplay feedback; preserve native animation behavior and verify W visibility/attachment lifecycle. User is preparing audio clips; intended triggers and clips are not yet supplied. Preferred authoring handoff: original-quality PCM WAV (48 kHz, 16/24-bit preferred) or lossless FLAC; existing MP3/M4A also usable without user-side conversion. Label one clip per desired trigger and indicate one-shot/loop and source timestamps where relevant. These are source preferences, not verified native bank encoding requirements.

## Evidence and boundaries

- `evidence/export_verification.json`: native SKN semantic read/write/read verified before model adaptation; serializer changes bytes, not parsed fields.
- `evidence/native_paths_and_packaging.json`: paths verified against installed original Briar WAD; supplied SKL matches original exactly. All 74 supplied ANMs match current original (`evidence/original_animation_mapping.json`).
- `evidence/model_build.json`: fitted model counts, bounds, and UV choices.
- `evidence/model_preview.png`: offline exported-mesh preview; not gameplay evidence.
- `evidence/pose_validation.json` and `evidence/pose_contact_sheet.png`: 15 sampled poses across native idle, run, attack, E windup and R cast. Valid weights/influences/indices/UVs/normals; five rendered poses visually inspected. Preview uses the source atlas; encoded final texture separately decoded and validated. Not a full animation sweep or runtime test.
- `evidence/texture_and_staging.json`: complete mip-chain validation and input hashes.
- `evidence/package_validation.json`: final Fantome CRC, exactly two WAD payloads, exact native path hashes, decompressed payload equality after final archive extraction.
- Native model path: `ASSETS/Characters/Briar/Skins/Base/Briar_Base.skn` (hash `9144d26d7f271649`). Texture hash `0e35941cdacaff56`. No BIN, SKL, animation, VFX, audio, or HUD overrides. Native attachment VFX remain and must be judged in gameplay with the absent pillory mesh.

## Reproduction and continuation

`AGENTS.md` is the persistent project-agent entrypoint. Token optimization is the main priority on every request, subject to correctness and gameplay quality. Read this current checkpoint first; do not re-audit unchanged sources. A session helper `/root/project_agent` performed bounded export and validation work; do not depend on its memory across sessions.

Toolchain: Blender 5.2.1 LTS; local LtMAO/pyRitoFile under `C:/Users/etqdo/Documents/maya/LtMAO/src`; bundled Python under `C:/Users/etqdo/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`; cslol-go `cslol-tools/mod-tools.exe`; wadtools 0.5.7. Maya 2027 is installed, but this candidate uses the supplied Blender scene and verified direct native writer.

Scripts: `scripts/verify_export.py`, `scripts/build_model.py`, `scripts/validate_poses.py`, `scripts/prepare_package.py`, `scripts/validate_package.py`. `scripts/build_c01.ps1` records the build sequence and refuses to overwrite the current candidate. Extraction evidence and assets live under `work/original`; final unpacked payloads under `work/final-roundtrip`. Candidate preview scene: `work/redmist_candidate.blend`.

User gameplay gate: install C01 manually for **base Briar**. At normal zoom inspect idle/run and attacks, Q, W frenzy/recast, E, R arrival/berserk, recall, death and respawn. Check both normal and frenzy model visibility, eyes/blood readability, invisible pillory, limb/neck deformation, and retained ability effects. Report candidate C01 plus the action/state and a screenshot or short clip for any defect. Do not change dependent VFX/audio/HUD or refine the rig before feedback. Do not launch/control League or a mod manager.

## Git synchronization checkpoint — 2026-09-25
Independent Git/LFS setup added with source/scene preservation, release-package manifest, PROJECT_STATUS.md summary and clone instructions. No skin assets changed or rebuilt; existing runtime gates remain. Build portability still requires local tools, extracted inputs and prior staging (BUILD_SETUP.md).
