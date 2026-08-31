# mine/ — the phrase-library pipeline (round 5)

The instrument's embedded phrase library (`const PHRASES=` inside
`triton-rack.html`) is **mined human playing**, not generated content. This
directory is the complete, re-runnable pipeline that produced it, so the
library can be audited, regenerated, or extended with new open corpora.

## Sources (license-verified before extraction)

| corpus | what it gives | license |
|---|---|---|
| [Groove MIDI Dataset](https://magenta.tensorflow.org/datasets/groove) (Magenta) | 1,150 performances by 10 session drummers on a Roland TD-11 — grooves AND fills, with the players' timing and dynamics | CC-BY 4.0 |
| [OpenScore String Quartets](https://github.com/OpenScore/StringQuartets) | CC0 editions of public-domain scores: cello → bass lines, violin II/viola → counter-lines, violin I → ornament gestures | CC0 1.0 |

Wanted but unreachable from the build bench (network egress blocked
zenodo.org): **FiloBass** (48 professional jazz bass transcriptions, CC-BY 4.0)
and **GuitarSet** (human comping + solos, CC-BY 4.0). The pipeline is
source-agnostic — point an extractor at them when you have network.

Deliberately excluded: Lakh-style scraped dumps (rights unclear), the Sapp
Bach chorale edition and MAESTRO (both CC BY-NC-SA — NC).

## The format (LDRP1)

One phrase = a tiny JSON wrapper + a packed base-36 event string
(`ldrp.js` holds pack/unpack; the artifact embeds only the decoder).

- **drum event (5 chars):** grid step (2) · signed deviation in 1/36-step
  units (1) — *the player's hand, preserved and tempo-independent* ·
  lane (1: `KSXHOPCRBFTt`) · velocity (1, 36 levels)
- **melodic event (6 chars):** grid step (2) · semitones-from-tonic +24 (2)
  — *any key, any scale: degrees re-fit to the target scale at play time* ·
  duration in ¼-steps (1) · velocity (1)

Melodic micro-timing is deliberately NOT stored: at play time lines ride the
drummer's **groove field** (median deviation per step of the drum phrase) —
"quantized to the human played rhythm track."

## Pipeline

```
node extract_drums.js    <groove-root> drum_candidates.json      # SMF → candidates
node extract_quartets.js <osq-scores>  quartet_candidates.json   # MusicXML → candidates
node prefilter.js                                                # structural ranking → shortlist.json
node decode_phrase.js <bucket> <start> <count>                   # human-readable render (what the judges read)
# … curation court (agents or humans) produce court_picks.json …
node assemble_library.js court_picks.json library.json           # dedup, sanitize, re-verify EVERY pick
node inject_library.js library.json ../triton-rack.html          # embed
node verify_phrase.js <selection.json>                           # fidelity gate, runnable any time
```

The fidelity gate (`verify_phrase.js`) re-derives every phrase from its RAW
source file at a rediscovered window offset and requires exact reproduction
within encoder quanta. A phrase that cannot be re-derived is not embedded.

Curation for the shipped library was a 29-agent court: 26 per-bucket judges
(style/mode buckets, producer criteria: pocket, dynamics architecture,
space-for-a-vocalist, loopability) + 3 adversarial auditors attacking the
parsers with constructed inputs. Picks carry names, tags, and reasons.

## data/ — provenance of the shipped library

- `court_picks.json` — the judges' raw verdicts: every pick with its name,
  tags, and one-line reason, plus per-bucket confidence and falsifiers.
- `court_picks_rebound.json` — the same picks re-bound to the corrected
  extraction after the auditors' findings were fixed (189 exact, 33 by
  ≥70% event overlap, 34 dropped where the corrected form diverged).
- `library.json` — the exact 222-phrase library embedded in the artifact
  (116 grooves · 20 fills · 25 bass · 41 counters · 20 licks, 66KB packed),
  all 222 re-verified against raw sources by `verify_phrase.js`.

Auditor findings fixed before assembly: TD-11 note 58 (tom-3 rim) restored
to the lane map; SMF running status no longer poisoned by meta events; the
full representable deviation range kept (exact −½-step hits included);
MusicXML cursor kept in quarter notes (mid-part `divisions` changes safe);
measures end at their farthest voice; `<cue/>` reminder notes excluded;
tie-stops extend only the note whose sounding end aligns; sustained
durations kept to the encodable cap; sub-16th ornament runs excluded from
gestures (they collapse on a 16th grid); minor-mode inference requires a
stronger anchor margin.
