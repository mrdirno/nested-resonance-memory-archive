# HANDOFF — TRITON-Rack × LuckyDreamer

**For:** the next build session (Claude Code internal), iterating toward accurate
instrument mapping and a 4U LuckyDreamer face.
**From:** the chat session of 2026-08-30 (rings 2–8 in `triton-rack.html`).
**Rule zero:** both HTML files carry append-only ring/history blocks at their very
end. **Read the rings first.** Never edit or delete a ring; append a new one per
session. The combined file uses the BUILD·BRANCH·BAN·BREAK·SHIP schema; the donor
uses its own dense log format at its tail. Both survive; that is the merge law
(Ring 5).

---

## 1. What is in this package

| file | what it is |
|---|---|
| `triton-rack.html` | The combined organism (~220 KB, self-contained). Korg TRITON-Rack recreation: 128 programs, 16 combis, Web MIDI in, DecentSampler export, EXB-LDR rhythm board (51 grafted figures), Dream Conductor v2 (auto-band), producer dock (play / dice / WAV record), rings 1–8 at tail. |
| `luckydreamer_3.html` | The donor, byte-identical to the user's upload (~2.9 MB). A complete generative-drums organism with its own instrument physics, style blocks, figure catalog, and history log at its tail. **Do not modify it.** It is the reference and the ground truth. |
| `extracted-data.json` | One JSON, three keys. `percussion`: `KIT_SLOTS`, `PERC_SLOTS`, `PERC_SAG`, `PERC_RECIPE` eval'd out of the donor (not retyped) — 25 instruments with fundamentals, body types, decay, shell and slap parameters. `figures`: the donor's 51-figure catalog (`FIG`), same data embedded in `triton-rack.html` as `LDR_FIG`. `sambaStyleExcerpt`: a verbatim style-block excerpt showing how the donor itself assigns figures to instruments (the pattern to follow for P0). |
| `tests.js` | One self-contained runner: syntax gate + all four suites (bank schema, figure graft, conductor, WAV recorder). It slices `triton-rack.html` itself — no side files. Run before and after every change. |

---

## 2. Anatomy of `triton-rack.html`

Five `<script>` blocks, in order:

1. **Data + engine** — `PROGRAMS[128]`, `COMBIS[16]`, riffs, `BLOCK_INFO`,
   Web Audio graph (`buildGraph`), voice engine (`spawnVoice` — note the optional
   6th arg `dest` for per-part panning), `drumHit(note,vel,when,kit)` with three
   kits (`std`/`ana`/`perc`), `applyFX()` / `applyFXP(prog)`.
2. **UI** — LCD renderer, modes/pages, dial/knobs, on-screen keys (per-note
   voice **stacks** in `keysDown` — polyphonic retrigger law, do not regress),
   arp (incl. `CHORD` pattern), audition, power/test, `quickBoot()`, `fit()`.
3. **I/O** — Web MIDI in (bend/mod/sustain), latency readout, DecentSampler
   export (offline renders, zip/wav writers).
4. **EXB-LDR** — `LDR_FIG` (the grafted catalog), `ldrBase()` (handles `+N` and
   `-N` rotations), **`ldrLane(id,f,i)` ← the function P0 replaces**, manual
   rhythm tab, slot-1 install visuals.
5. **Dream Conductor v2** — `figAnalysis` (skeleton + response slots),
   `voiceLead`, `makeMotif` (melody in the figure's gaps), section machine,
   quantized `dreamDice`, `startWith/applyDream`, ScriptProcessor take recorder
   (`wavStereo24`), floating dock wiring.

Hidden comment at EOF: rings 1–8. Ring 7 documents conductor musicality; Ring 8
documents this handoff and the prescribed P0 fix.

## 3. Anatomy of `luckydreamer_3.html` (line anchors, current file)

- `KIT_SLOTS` / `PERC_SLOTS` rosters: ~**4430–4438**.
- `PERC_SAG`: ~**4545**; **`PERC_RECIPE`: ~4548–4578** — the physics table.
  Body types: `drumhead`, `wood`, `glock`, `metal`, `shake`. Fundamentals worth
  memorizing: surdo 62 Hz · dunL/M/S 78/150/225 · congas 190/260/340 ·
  bongos 430/620 · timbales 300/420 · agogo 560/780 · cowbell 540 ·
  clave 1250 · woodblock 900 · triangle 3200.
- `PercKit.prototype.setPatch`: ~**4595** — patches tune the SET (one pitch
  offset, one decay scale, one drive), not per-voice. Mirror this discipline.
- Style blocks (figure→instrument assignments by the donor's own hand):
  ~**11170–11850**. Example, samba (~11835+): kick lane runs pattern `surdo1`,
  snare is the caixa with wire accents, perc rows name `'surdo'` explicitly.
  Batucada part patterns (`surdo1/2/3`): ~**11461**.
- Figure catalog `FIG`: **12559–15091**; `figCheck()` load-time audit: 15092+.
- Instrument synth sections (ANALOG/FM/TINE/TONEWHEEL/STATION/SOLINA/VOXA/
  PLUCK/BOWED/MALLET/WIND, tuned-drum voice): ~2458–4420.
- History log: tail of file. Its own open debts are listed there (tongues'
  voicing, anticipated bass with no call site, near-Nyquist aliasing).

---

## 4. P0 — instrument-to-instrument mapping (the accuracy fix)

**Problem.** `ldrLane()` in the combined file maps figure→drum-lane by id
substrings and role fallbacks. Two passes of heuristics have both been judged
wrong by ear. Names are addresses, not sounds.

**Method (three steps, in order):**

1. **Figure → donor instrument.** For every id in `extracted-data.json` (`figures` key), determine
   which donor instrument voices it, using (in priority order): (a) the donor's
   STYLE blocks (~11170–11850) where assignments are explicit; (b) the figure's
   `role` + the donor's drums-module commentary (11170–12550) — e.g. bell
   `tone` rows are two-pitch bells → `agogoL`/`agogoH`; (c) the physics table
   itself when a name is unambiguous (surdo, clave, ganzá→shaker, caixa→wired
   snare, martillo→bongos, cáscara→timbale shell, palitos→woodblock).
   **Ambiguities to resolve by reading, not guessing:** tamborim (the 6" drum)
   vs `tamb` (tambourine, metal 5200 Hz) — the samba style block decides;
   cuíca (donor may voice via `talking` or its own section — search "cuica");
   quinto (djembeS vs congaH — check the guaguancó/rumba style block);
   twelve-pulse ensembles (dunun family `dunL/M/S` exists precisely for them).
   Output: `figure-instrument-map.json` — `{figId: {inst, note?}}` — committed
   into the package and cited in the next ring.
2. **Donor instrument → TRITON voice.** Do **not** translate to the nearest
   existing lane. Port the numbers: extend `drumHit` (or add `drumHitP(recipe)`)
   to synthesize directly from a `PERC_RECIPE` entry — sine/partial at `hz`
   (body-dependent partial set: drumhead = fundamental + sagging pitch (see
   `PERC_SAG`), wood/glock = stiff partials, shake = the donor's rebound
   envelope), shell resonance at `shellHz`, slap transient at `slapHz`. The
   engine already builds every needed node type. Embed the 25-entry recipe
   table (it is 7.6 KB as JSON). Then mapping accuracy is *inherited*, not
   re-approximated, and the `kit` selector becomes "TRITON kits" vs
   "LuckyDreamer physics".
3. **Verify per figure, donor vs graft.** Same figure, both engines, A/B by ear
   first, then measure: per-hit fundamental (FFT peak) and decay time within
   tolerance of the recipe. Add a `tests/mapping-test` that walks all 51
   figures and asserts every hit resolves to a recipe entry (no fallbacks
   fire). A silent fallback is how the current inaccuracy survived two passes.

**Definition of done:** the user plays Rio Sunrise and hears surdos, not toms;
Bembé's bell row lands on two agogô pitches; Son's campana is a bell, its
martillo is bongo skin. Ring the mapping table's provenance.

## 5. P1 — the 4U LuckyDreamer unit

The 1U's on-unit controls scale with the rack (`fit()`), so on a 380 px phone a
64 px design button renders ~25 px — under any touch standard. The floating dock
was the stopgap; the fix is a **4U face**:

- Design canvas **960 × 540** (TRITON is 960 × 270; "similar size or larger"
  per the user — 4U reads as the flagship). Same ears/screws/scale pipeline:
  extend `fit()` exactly as it already handles `#ldru`.
- **Touch law:** every interactive control ≥ **120 design px** in its smallest
  dimension (worst-case scale ≈ 0.375 ⇒ ≥ 45 px physical). PLAY ≥ 160 design px.
- Absorb into the face: PLAY, DICE, RECORD (+ take timer), preset/dream
  selector as large chips (not a `<select>`), the scope (wider, taller), the
  figure browser (the Rhythm tab's chip grid moves home), section/bar/seed
  readout, and per-part activity LEDs (drums/bass/chords/lead) driven from
  `dreamScheduleBar`.
- Keep the floating dock — it is the thumb's home when scrolled elsewhere —
  but the 4U becomes the primary surface. Keep the neon-on-charcoal identity;
  the TRITON below stays period-correct (Ring 6's law: the AI age is the room,
  not paint on the legend).

## 6. Backlog (from the rings, prioritized)

- **P2** — MIDI export of a recorded take (the conductor knows every note it
  schedules; capture alongside the WAV) → the DAW inherits the arrangement.
- **P2** — HALF-DICE: keep rhythm section, re-roll harmony/melody (Ring 7 Q2).
- **P2** — Seed crate: long-press the seed to pin favorites; store the crate
  inside the artifact (no localStorage in this environment — persist by
  writing into the file on the next session, or export/import JSON).
- **P3** — Bank B user WRITE + bank JSON export/import (Ring 4 Q1).
- **P3** — CHORD arp → STRUM (few-ms stagger, Ring 4 Q2); audition improviser
  (Ring 4 Q3); MPE (Ring 2 Q3); reverse graft of the 128 programs into the
  donor (Ring 5 Q1).

## 7. Verification

```
node tests.js                 # from the zip root; expects triton-rack.html beside it
# suites: [0] whole-file syntax · [1] 128 programs / 16 combis schema
#         [2] 51 figures, lanes, ± rotations, ensemble refs
#         [3] figAnalysis, voice-leading smoothness, motifs, 200 surprise seeds, sections
#         [4] stereo 24-bit WAV header + length assertions
```

Green before you start = your baseline. Green after = necessary, not
sufficient — the ear test in §4.3 is the real gate.

## 8. Constraints that must survive every session

Single self-contained HTML per artifact; no CDN, no fetches, no localStorage in
artifacts; no Korg ROM data or firmware ever (all sound synthesized; the file's
honesty notes stay); AudioContext only from a user gesture (quickBoot pattern);
rings append-only, newest last, donor's history stays in the donor; user-facing
reports are one paragraph, process lives in rings.
