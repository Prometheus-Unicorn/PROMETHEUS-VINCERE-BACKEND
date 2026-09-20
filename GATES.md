# Gates: editorial-refinements-and-placement-fixes

OWNS: mini_run_pipeline/subject_placement.py, mini_run_pipeline/typography.py, remotion-app/src/compositions/PrometheusMinRun.tsx, remotion-app/src/compositions/__tests__/PrometheusMinRun.test.ts, tests/test_editorial_placement_refinements.py

Scope: Fix middle-third/companion placement, cranial headroom elevation, companion font styling, and cadence-aware text animation pacing.

- [x] G1: Companion layer in split-layer chunks anchors in middle-third (54%-66% Y), never plunging to 80% Y over microphone
  CHECK: python -m unittest tests/test_editorial_placement_refinements.py -k test_companion_placement_avoids_microphone_deck_plunge
  EXPECT: PASS_G1_COMPANION_OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=37a46e6859108ac99b11f03e566a10599045271ebc31823a11f5f3dcd863d05a; exit=0; EXPECT=matched; output-sha256=57c6dae6d39bbee9a5a01d37523e77b0a24f0fc9ce9000653a4415826b5ad4f2; output-bytes=126; shell=C:\Windows\system32\cmd.exe; cwd=C:\Users\HomePC\Downloads\PROMETHEUS-VINCERE-BACKEND; path=86e75c2a2287/32 entries

- [x] G2: Cranial negative space text elevates into open upper ceiling (under 13.5% Y) when ample headroom exists above head
  CHECK: python -m unittest tests/test_editorial_placement_refinements.py -k test_cranial_negative_space_elevates_into_open_ceiling
  EXPECT: PASS_G2_CRANIAL_OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=24640ea800ebd16a193ef524cd8e0f47899926206dc471a1a70415c5f65d134c; exit=0; EXPECT=matched; output-sha256=5a03f0d332b71e796ce844a8412cb4545ee8b0aeb456fc3a6ef431a892919339; output-bytes=124; shell=C:\Windows\system32\cmd.exe; cwd=C:\Users\HomePC\Downloads\PROMETHEUS-VINCERE-BACKEND; path=86e75c2a2287/32 entries

- [x] G3: Companion and secondary clause typography features refined letter-spacing and styling instead of flat raw unstyled sans-serif
  CHECK: python -m unittest tests/test_editorial_placement_refinements.py -k test_companion_clause_styling_not_flat_generic
  EXPECT: PASS_G3_STYLING_OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=60a218317d28c09dc2456cd9b601984d531ca50aaeb0dfe4cfd7552c2c2c4826; exit=0; EXPECT=matched; output-sha256=198e0ab5c9a354bb8ce3a8dd4b95da787f0c62c45cad6a081d1c22676b6bd93f; output-bytes=124; shell=C:\Windows\system32\cmd.exe; cwd=C:\Users\HomePC\Downloads\PROMETHEUS-VINCERE-BACKEND; path=86e75c2a2287/32 entries

- [x] G4: Text animation entrance duration and word pacing expand with spoken chunk duration instead of 30-frame rush
  CHECK: npx vitest run src/compositions/__tests__/PrometheusMinRun.test.ts -t "resolveChunkEntranceFrame" --no-color
  EXPECT: Test Files  1 passed (1)
  CWD: remotion-app
  EVIDENCE: automatic-evidence=v1; definition-sha256=80cc4c45f229714bb926f4c6ab4f65702db0132abeaa65780332f4c09d9f51f0; exit=0; EXPECT=matched; output-sha256=a0124bc15387fe53a2d29b8cf203cb25cbeb1d7b739165c6a746b6fe27673210; output-bytes=348; shell=C:\Windows\system32\cmd.exe; cwd=C:\Users\HomePC\Downloads\PROMETHEUS-VINCERE-BACKEND\remotion-app; path=86e75c2a2287/32 entries

- [x] G5: Entire test suite for visual helpers, typography, and subject placement passes clean
  CHECK: python scripts/verify-all-editorial.py
  EXPECT: PASS_ALL_EDITORIAL_SUITE_OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=6a5343f291a624f82c1755dc567c6eeb7a05ee55dee1edf54790b97f068a4a7e; exit=0; EXPECT=matched; output-sha256=978a856a65751494fc562e5d6eb16b89263ac2bd45f458f6113ca92ca0ee898a; output-bytes=217; shell=C:\Windows\system32\cmd.exe; cwd=C:\Users\HomePC\Downloads\PROMETHEUS-VINCERE-BACKEND; path=86e75c2a2287/32 entries
