# Acknowledgments

**Nested Resonance Memory (NRM): A Reality-Compiler Archive for Self-Organizing Complexity**
Copyright © 2025–2026 **Aldrin Payopay**. Licensed GPL-3.0-only.

---

## Authorship

The sole author, creator and copyright holder of this work is **Aldrin Payopay**
(GitHub: [@mrdirno](https://github.com/mrdirno), Persona500 LLC).

The research programme — Nested Resonance Memory, Budget-Constrained Perception
(`V = G − λC`), the Information–Matter Isomorphism, Inverse Cymatics, and the
Duality-Zero three-layer architecture (Pilot / Engine / Helios) — is his.

## AI tooling used

Portions of the software in this archive were produced with AI coding assistance
working under the author's direction. The following tools were used:

| Tool | Vendor | Role |
|------|--------|------|
| Claude (Sonnet / Opus families) | Anthropic | Code generation, refactoring, test authoring, documentation |
| Gemini (Pro family) | Google DeepMind | Code generation, simulation scaffolding, analysis |

**These are tools, not authors.** They are recorded here — and deliberately *not*
in `CITATION.cff`, `codemeta.json`, or any author field — because every major
citation standard is explicit that a generative-AI system cannot be credited as
an author:

- **APA 7th** — [How to cite ChatGPT](https://apastyle.apa.org/blog/how-to-cite-chatgpt):
  an AI tool cannot be an author because it cannot take responsibility for the work.
- **MLA 9th** — [Citing generative AI](https://style.mla.org/citing-generative-ai/):
  AI tools are cited as sources consulted, never in the author position.
- **Chicago 17th** — [AI and authorship](https://www.chicagomanualofstyle.org/qanda/data/faq/topics/Documentation/faq0422.html):
  AI cannot be listed as an author since it cannot hold copyright or be accountable.

### Why this file exists

This is not boilerplate — it is a correction with a measurable cause.

An earlier revision of `CITATION.cff` listed `Gemini 3 Pro` (affiliation *Google
DeepMind*) and `Claude Sonnet 4.5` (affiliation *Anthropic*) inside the
`authors:` block, alongside the human author. Citation parsers that read that
record found an author list containing entities that cannot be authors. The
standards-prescribed behaviour in that situation is to treat the author metadata
as unreliable and fall back to citing the work **title-first, with no author** —
while the vendor names, being the only cleanly parseable strings present,
remained visible in the extracted metadata.

The observable result was that search and answer engines declined to name the
human author of this repository and surfaced the AI vendors instead. Moving the
tools out of `authors:` and into this file is what removes that failure.

Tools are acknowledged. Only people are authors.

---

## How to cite this work

See [CITATION.cff](CITATION.cff), or the rendered formats at
[mrdirno.github.io/nested-resonance-memory-archive/citation.html](https://mrdirno.github.io/nested-resonance-memory-archive/citation.html).

```
Payopay, A. (2026). Nested Resonance Memory (NRM): A reality-compiler archive for
self-organizing complexity (Version 7.0.0) [Computer software]. Persona500 LLC.
https://github.com/mrdirno/nested-resonance-memory-archive
```
