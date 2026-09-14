# ANIMATION EXPANSION PLAN — Origin Kit Intake into the Mini-Run Catalog

**Brief for the implementing agent.** Read this fully before writing code. Sources are authoritative; this plan governs scope, porting doctrine, batching, and acceptance. The auditor will check every item.

**Mission:** expand the mini-run kinetic text catalog from 65 → ~77 presets by porting the Origin Kit animation set (plus one Framer-Motion reference) into Remotion-native renderer branches, registered in the Python selection catalog.

## Sources (authoritative — read the reference implementations COMPLETELY before porting each preset)

| Source | Path | Contents |
|---|---|---|
| S1 | `C:\Users\HomePC\Downloads\ORIGIN KIT ANIMATIONS, LET US INCREASE THIS MOOTHER FUCKER.txt` | 14 Origin Kit components, ~20 preset variants (5,127 lines) |
| S2 | `C:\Users\HomePC\popcorn-text.tsx` | Popcorn char-burst (Framer Motion spring) |
| S3 | `mini_run_pipeline/typography.py` | Current catalog: `ANIMA_RUNTIME_TREATMENTS` (65 ids), family sets, intrinsic-duration map |

## Porting doctrine — non-negotiable

Remotion is deterministic and frame-based. The source files are browser-runtime components. You are porting **kinematics**, not code:

1. **Forbidden in renderer code:** `requestAnimationFrame`, `setTimeout`, `IntersectionObserver`, `document.fonts`, `hover/scroll/click` triggers, unseeded `Math.random`. Any of these in a committed branch fails audit.
2. **Port to:** `interpolate(frame, [...], [...], {easing})`, `spring({frame, fps, config})`, and `random(\`seed-${wIdx}-${frame}\`)` from `remotion`. Every "random" in the sources (popcorn's random rotation, FuzzyText's row displacement, flicker letter selection) becomes seeded and frame-deterministic.
3. **Canvas preset (FuzzyText):** offscreen text rasterized once (`useMemo`), per-frame row displacement drawn deterministically with displacement seeded by `(frame, row)`. The rAF loop becomes the frame itself.
4. **GSAP preset (InkdropSpread):** GSAP `stagger: {from: "center"}` becomes word-index distance-from-center × per-word delay in frames. No GSAP dependency may be added.
5. **Framer Motion preset (popcorn):** spring config `{stiffness: 350, damping: 14, mass: 1}` ports to Remotion `spring()` physics. `useAnimate`/`motion.span` do not port — plain spans + frame math.
6. **Entrances obey mention-sync** (`wordEntranceFrames`, lead ≤130ms — the existing contract at PrometheusMinRun.tsx:1036). Overlay presets run on the hold window **after** the entrance completes.
7. **No hardcoded demo colors.** `waveColor`, gradient ends, stroke colors derive from `layer.color` / chunk palette / motif — never `#00FF66`/`#F9731A` literals.
8. Every preset gets an `INTRINSIC_ANIMATION_DURATIONS_MS` entry (perceptibility floor) and obeys the accelerated-exit contract when truncated.

## Intake table — 15 sources → 13 presets

| # | Proposed id | Source (S1 lines) | Kinematics | Dedup verdict vs current 65 | Family / energy | Class |
|---|---|---|---|---|---|---|
| 1 | `origin_wave_color_sweep` | S1:1-241, 2385-2797 | Char-level wave-color→base transition, blur-in, stagger; drop-from-above variant (startY -500, 1.15s cubic[0.44,0,0.56,1]) | Distinct from `horizontal_gradient_sweep_fade` (word-level) | FLUID / 0.45 | entrance, multi-word |
| 2 | `origin_inkdrop_spread` | S1:804-948 | Words scale(0)+blur(4px), stagger radiating FROM CENTER | Distinct from `stagger_blur_word_reveal` (linear, not radial) | FLUID / 0.40 | entrance, multi-word |
| 3 | `origin_fuzzy_noise_overlay` | S1:953-1338 | Canvas row-displacement fuzz; glitch bursts; optional gradient | **NO conflict — new overlay class** | overlay / n/a | **overlay** (post-entrance hold) |
| 4 | `origin_outline_flicker_fill` | S1:1345-2043 | Outline→fill flicker sequence, stroke-position modes, letter-flicker, optional shake | No conflict (old flicker presets were pruned) | POP / 0.70 | entrance, multi-word |
| 5 | `origin_matrix_letter_rain` | S1:2044-2205 | Column decode rain | Related to `cyber_matrix_text_scramble` but distinct kinematics — own branch required | POP / 0.75 | entrance |
| 6 | `origin_reveal_wipe` | S1:2206-2384 | Directional wipe with soft edge | Conditional: implement ONLY if kinematics differ materially from `cinematic_viewport_mask_sweep` — state the diff in the commit | FLUID / 0.45 | entrance |
| 7 | `origin_typewriter_reveal` | S1:2640-2905 | Char-by-char + caret | **SKIP** — `typewriter_cursor` + `typewriter_ghost_cursor` already own this space | — | — |
| 8 | `origin_staggered_rise` | S1:2906-3064 | Letters rise on stagger | **SKIP** — `dynamic_staggered_character_cascade` + `top_down_staggered_character_drop` own it; a third letter-stagger cannibalizes | — | — |
| 9 | `origin_spotlight_reveal` | S1:3065-3483 | Radial spotlight mask sweeping across glyphs | No conflict — new | SPECIAL / 0.50 | entrance/hold |
| 10 | `origin_spiral_in` | S1:3484-3980 | Chars spiral along arc into place | No conflict — new | POP / 0.65 | entrance |
| 11 | `origin_domino_cascade` | S1:3981-4981 | Chars fall with chained rotation/bounce | No conflict — new | POP / 0.70 | entrance |
| 12 | `origin_splitflap_board` | S1:4982-5166 | Split-flap mechanical char flip | Distinct (`word_by_word_3d_flip` was pruned) | POP / 0.60 | entrance |
| 13 | `origin_shiny_pill` | S1:5167-5392 | Pill badge + specular shine sweep | Badge class, sibling of `vercel_kinetic_highlight_box` | editorial / 0.45 | entrance |
| 14 | `origin_ripple_wave` | S1:5393-5127 | Continuous per-char sine y-wave (idle motion during hold) | No conflict — new **hold-idle** class | FLUID / 0.50 | hold-idle |
| 15 | `popcorn_char_burst` | S2 (all) | Chars pop from scale 0 with seeded random rotation, spring 350/14/14 mass, stagger 0.04 | Distinct from existing letter drops (random rotation axis) | POP / 0.68 | entrance |

**Net: 13 new presets (2 skips, 1 conditional may add a 14th). Catalog target: 65 → 78.**

Class note: this intake introduces **two new treatment classes** the selector must support — `overlay` (joins `ANIMA_OVERLAY_TREATMENTS`, applied to the finished lockup during hold) and `hold-idle` (runs during the hold window, composed AFTER the entrance fx, never replacing it). Wire both into selection so overlays/idles compose with entrances rather than competing with them.

## Premium promotion & routing (the "use them a ton" mandate)

New presets must not merely exist in the catalog — they must carry a visible share of every render. Mechanism:

1. **Premium tier flag**: each of the 13 new entries gets `tier: "premium_new"` in its `ANIMA_RUNTIME_TREATMENTS` entry.
2. **Promotion multiplier**: premium-tier treatments receive a **×2.5 selection multiplier** on top of their family boost, active until the preset accumulates **3 lifetime selections** (tracked in the existing `preset_usage_counts`), after which it decays to normal weighting. This is a launch-rotation: heavy early presence, no permanent artificial inflation.
3. **Per-video quota**: every render must draw **≥25% of its treatment events from the premium_new set** (while it has eligible candidates). Quota is a selection-time constraint, checked in the same pass as the existing fatigue caps.
4. **Hard limits still apply** (non-negotiable — "a ton" must not become "the same three every chunk"):
   - Existing cognitive-fatigue caps and the recent-window dedup (`recent_primary_fx`) bind premium presets exactly like all others.
   - No premium preset may appear twice within any 4-chunk window.
   - Word-fit rules, behind-subject exclusion, and tall-stack contracts bind premium presets identically.
5. **Config, not hardcode**: the multiplier (2.5), lifetime threshold (3), and quota (25%) live as named constants at the top of `typography.py` — tunable without touching selection logic.

## Integration contract (exact touchpoints)

1. `mini_run_pipeline/typography.py`
   - `ANIMA_RUNTIME_TREATMENTS`: one entry per preset with `styles` + `energy` per the table.
   - Family sets: presets 1, 2, 14 → `FLUID_FAMILY`; 4, 5, 10, 11, 12, 15 → `POP_FAMILY`; 9, 13 → `SPECIAL_OPS_FAMILY`.
   - `INTRINSIC_ANIMATION_DURATIONS_MS`: one entry each (measure the ported timeline; floor 750ms).
   - `ANIMA_OVERLAY_TREATMENTS`: add preset 3.
2. `remotion-app/src/compositions/PrometheusMinRun.tsx`
   - One dedicated branch per preset (follow the "Dedicated B/F/G" branch pattern), registered in `RUNTIME_TREATMENT_IDS`, `normalizeRuntimePreset` passthrough.
3. `remotion-app/src/compositions/__tests__/PrometheusMinRun.test.ts`
   - Passthrough test per id; render test per preset at frame 0 / mid / hold — must not throw; **two-seed determinism**: same props + different seeds → identical output except where the seed is the intended input (popcorn rotation, fuzz displacement), and identical output for the same seed across two renders.
4. `mini_run_pipeline/typography.py` catalog count test: update expected count 65 → 78 (or actual net).
5. `typography_animations_inspector.html`: add each preset so a human can preview it. Inspector is documentation, not runtime.

## Batching (RULE 7 — one fix, one commit, one test)

- **Commit 0 (infra):** overlay/hold-idle class support in selection, **premium-tier flag + promotion multiplier + per-video quota machinery**, shared seeded-PRNG + char/word-split helpers, catalog-count test update. ≤5 files.
- **Commits 1–13:** one preset per commit (renderer branch + registration + duration entry + its vitest tests + inspector entry). Hard cap 5 files / 500 lines each — the FuzzyText canvas port may need audit sign-off to exceed; request it in advance, do not assume.
- **Commit N (variance proof):** a 30-seed selection histogram proving every new id is selected ≥1× on eligible chunks and no new id dominates. Zero-selection presets are dead presets and fail audit.
- Commit messages reference plan ids: `feat(mini-run): origin_wave_color_sweep (expansion plan #1)`.
- Skips (#7, #8) and the conditional (#6) must be stated in the final report with the dedup reasoning — silence is not a verdict.

## Acceptance criteria (what the auditor runs)

1. Full battery green: vitest (all files, `NODE_OPTIONS=--max-old-space-size=4096`), `python -m unittest discover -s tests -p "test_mini_run_*.py"`, reference-frame suite.
2. Catalog count matches the plan; `normalizeRuntimePreset` passes all new ids.
3. Per-preset: no forbidden browser APIs (grep gate), intrinsic duration present, determinism test passes.
4. 30-seed variance histogram attached to the final report (claim → evidence, RULE 5). Upgraded thresholds: every new preset selected **≥3×** (not merely ≥1×), aggregate premium_new share **≥25%** of treatment events, and no preset — new or old — above 15% share (dominance gate).
5. Inspector renders every new preset for human review.

## Out of scope

Selection weight retuning beyond family membership; catalog pruning; any file outside `mini_run_pipeline/`, `remotion-app/src/compositions/`, `remotion-app/src/compositions/__tests__/`, `typography_animations_inspector.html`; macro-section or landscape files (RULE 10).
