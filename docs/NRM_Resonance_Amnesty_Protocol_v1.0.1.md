# **NRM Resonance Amnesty Protocol (RAP): Complete White Paper**

**Version 1.0.1 — November 2025**  
Public-facing alias: Negative-Space Commons (NSC)  
Technical codename: NRM Resonance Amnesty Protocol (RAP)

## **0\) Pain Points → Design Responses**

* **File-drawer drag (buried failures, repeated dead-ends):**  
  * **Response:** RAP creates a synchronized commit-reveal window and a machine-readable Negative-Space Index of “beautiful failures,” cutting duplication.  
* **No one wants to go first (initiation risk):**  
  * **Response:** A Genesis Round where founding members disclose older (2+ years), low-sensitivity failures to seed liquidity and trust.  
* **Low-value spam (trivial “we tried it too” uploads):**  
  * **Response:** Quality gating via Surprise Quotient (SQ) and replication tickets; the G-Score is impact- and size-normalized.  
* **Info hazards (capability lift, exploits) & legal/IP risk:**  
  * **Response:** Risk bands (L1–L4), a redaction ladder, an Independent Risk Board, C2PA attestation, export-control screens, a defensive-publication license, and antitrust safe-harbor.  
* **Adoption inertia (no CFO-visible ROI):**  
  * **Response:** Compute/$/CO₂e saved metrics, procurement & grant preference points, and public leaderboards.  
* **Staleness (architecture shifts, obsolescence):**  
  * **Response:** Temporal versioning: valid\_until \+ decay functions and refresh triggers for bounds tied to paradigm changes.

## **1\) Executive Summary**

The current R\&D equilibrium privatizes wins and buries losses, producing a **file-drawer drag**: repeated dead-ends, wasted compute, and slower safety learning. The **Resonance Amnesty Protocol (RAP)** creates a synchronized, safe-harbor exchange of **beautiful failures** and their **emergent side-effects**, mapped into a machine-readable **Negative-Space Index**.  
RAP operationalizes **Non-Equilibrium Resonance Matching (NRM)**: we “ping” the solution space, record **instability boundaries**, and share **attested** Failure Cards through a commit-reveal window under legal shields. Incentives (the **Generativity Score**) reward contributions that **save others compute** or **spawn new lines**.  
Result: less duplication, faster pivots, safer exploration. This paper sets out the theory (Sec. 2), protocol (Sec. 3), incentives (Sec. 4), data standard (Sec. 5), trust layer (Sec. 6), KPIs (Sec. 7), and a 90-day pilot (Sec. 8), plus a dashboard spec (Sec. 9\) and governance (Sec. 10).

## **2\) Foundational Mathematics & Physics for NRM**

**State space.** Let the solution manifold be a high-dimensional state space ($\\mathcal{S}$). A point ($\\theta \\in \\mathcal{S}$) parameterizes a system (architecture, hyperparameters, data regime).  
**Potential landscape.** Each ($\\theta$) has potential ($L(\\theta)$) (loss). We seek low-potential regions; **failures** are dynamic instabilities—walls/cliffs in practice.  
**Dynamics.**

* Equilibrium (overdamped GD):  
  $$\\dot{\\theta} \= \-\\eta \\nabla L(\\theta)$$  
* Non-equilibrium (NRM, Langevin-style):  
  $$m \\ddot{\\theta} \+ \\gamma \\dot{\\theta} \= \-\\nabla L(\\theta) \+ \\sqrt{2\\gamma k\_B T}\\xi(t)$$

  Momentum ($m\\ddot{\\theta}$) enables barrier crossing; ($\\gamma \\dot{\\theta}$) is friction/latency; ($T$) captures exploratory noise (batching, augmentation).

**Resonance failure.** The Hessian ($\\mathbf{H}=\\nabla^2 L(\\theta)$) defines local curvature; large eigenvalues ($\\lambda\_{\\max}$) set effective “natural frequencies.” Instability arises when update cadence **resonates** with high curvature:  
$$\\text{heuristic stability: }\\quad \\eta \\lesssim \\frac{c}{\\lambda\_{\\max}(\\mathbf{H})} $$RAP’s \`Failure Cards\` empirically map these \*\*dynamic stability boundaries\*\* ($\\mathcal{F}(\\theta,\\dot{\\theta},\\eta,T,\\ldots)$). \*Stability footnote.\* In convex L-smooth regions, GD is stable for ($\\eta\<2/L$). The resonance framing generalizes the intuition to non-convex, non-equilibrium regimes and is used operationally, not as a global proof. \#\# 3\\) Core Protocol Mechanics \* \*\*Simultaneous Window (24h).\*\* Pre-announced; \`commit-reveal\` prevents opportunistic timing (hash now, disclose in-window). \* \*\*Failure Cards (standardized).\*\* Machine-readable disclosures (Sec. 5), including \`emergent side-effects\`. \* \*\*Negative-Space Index.\*\* Graph database of \`do-not-waste-time zones\` and \`productive edges\` (where failure birthed new lines). \* \*\*Reciprocity Gate.\*\* Read access requires contributing \`1–3%\` of annual experiments. \* \*\*Safe Harbor.\*\* Legal wrapper: defensive publication, IP carve-outs, antitrust guardrails, export-control screening. \* \*\*Integrity & privacy primitives.\*\* \* \*\*TEEs\*\* (SEV/TDX) for confidential pre-window triage. \* \*\*ZK option\*\* to prove schema conformance (domain, hazard band, attestation) pre-reveal. \* \*\*C2PA\*\* for artifact provenance \+ \*\*OpenTimestamps\*\* (or equivalent) for immutable timing. \* \*\*Genesis Round (catalyst).\*\* Founders simultaneously release \`older (≥24 months)\` failures with high instructional value and low present sensitivity to seed the Index and set disclosure norms. \#\# 4\\) The Economic Engine: Incentive Design \* \*\*Generativity Score (G) — impact- & size-normalized.\*\* $$  
$$G \= \\\\frac{\\\\alpha \\\\cdot \\\\text{unique\\\_citations}\*{12m} \+ \\\\beta \\\\cdot \\\\text{forks}\*{12m} \+ \\\\gamma \\\\cdot \\\\text{new\\\_lines}\\\_{12m}}{\\\\sqrt{\\\\text{annual\\\_experiments}}}

$$  
$$Default weights: ($\\alpha=1.0,\\ \\beta=0.5,\\ \\gamma=2.0$). Calibration published each window.

* Surprise Quotient (SQ) — quality gating.  
  Operationalize “violates strong priors”:$$ \\\\ SQ \\equiv \-\\log P(\\text{obs} \\mid \\text{prior}) \\approx \\mathrm{KL}(\\text{posterior} , \\Vert , \\text{prior}) $$  
  $$$$High-SQ failures score bonus G-points; damp trivial “me-too” uploads.  
* **Temporal versioning & decay.**  
  * Each card includes valid\_until and decay (e.g., exponential) after paradigm shifts (new arch class, optimizer family, data regime).  
  * Refresh triggers: card prompts “re-probe” when upstream shifts occur.  
* **Access tiers & status.**  
  * Deeper analytics, priority replication compute, and early feature access unlock with cumulative, verified G.  
  * Procurement & grants preference for high-G contributors.  
* **Compute/$/CO₂e savings (CFO-visible).**  
  * $\\text{GPU-hours saved} \= \\sum (\\text{planned} \- \\text{actual})$  
  * $\\text{\\$ saved} \= \\text{GPU-hours} \\times \\text{blended hourly rate (published per window)}$  
  * $\\text{CO}\_2\\text{e saved} \= \\text{GPU-hours} \\times (\\text{kWh/GPU-h}) \\times (\\text{grid gCO}\_2\\text{/kWh}), \\text{PUE-adjusted}$  
* **Bounties & recognition.** Annual “Top 10 Generative Failures,” plus cross-domain breakthrough awards.

## **5\) Data Standard: Failure Card Schema (v1.0.1)**

{  
  "$schema": "\[https://json-schema.org/draft-07/schema\#\](https://json-schema.org/draft-07/schema\#)",  
  "title": "RAP Failure Card",  
  "type": "object",  
  "version": "1.0.1",  
  "description": "Standardized record of a failed experiment and its emergent properties.",  
  "properties": {  
    "title": { "type": "string" },  
    "domain": {  
      "type": "array",  
      "items": { "type": "string", "enum": \["algorithmic","data","hardware","systems","socio-technical","governance"\] }  
    },  
    "hypothesis": { "type": "string" },  
    "setup": {  
      "type": "object",  
      "properties": {  
        "model": { "type": "string" },  
        "model\_card\_uri": { "type": "string", "format": "uri" },  
        "data": { "type": "string" },  
        "scale\_hw": { "type": "string" },  
        "scale\_cost\_usd": { "type": "number" },  
        "scale\_time\_hrs": { "type": "number" }  
      },  
      "required": \["model","data","scale\_hw"\]  
    },  
    "observations": { "type": "array", "items": { "type": "string" } },  
    "emergent\_side\_effects": { "type": "array", "items": { "type": "string" } },  
    "failure\_class": {  
      "type": "array",  
      "items": { "type": "string", "enum": \[  
        "scaling-break","instability","alignment-regression","latency-cliff",  
        "energy-blowup","ops-brittleness","non-replicable","ops-incident","other"  
      \] }  
    },  
    "repro\_window": { "type": "string" },  
    "negative\_bounds": { "type": "array", "items": { "type": "string" } },  
    "next\_directions": { "type": "array", "items": { "type": "string" } },  
    "artifacts": { "type": "array", "items": { "type": "string", "format": "uri" } },

    "temporal": {  
      "type": "object",  
      "properties": {  
        "valid\_until": { "type": "string", "format": "date" },  
        "decay": { "type": "string", "enum": \["none","step","exponential"\] },  
        "refresh\_triggers": { "type": "array", "items": { "type": "string" } }  
      }  
    },

    "risk": {  
      "type": "object",  
      "properties": {  
        "hazard\_score": { "type": "number", "minimum": 0.0, "maximum": 1.0 },  
        "band": { "type": "string", "enum": \["L1-public","L2-restricted","L3-delayed","L4-withheld"\] },  
        "export\_control": { "type": "boolean" },  
        "antitrust\_sensitive": { "type": "boolean" }  
      }  
    },

    "metrics": {  
      "type": "object",  
      "properties": {  
        "surprise\_quotient": { "type": "number" },  
        "g\_score\_snapshot": { "type": "number" }  
      }  
    },

    "redactions": { "type": "array", "items": { "type": "string" } },

    "attestation": {  
      "type": "object",  
      "properties": {  
        "org": { "type": "string" },  
        "timestamp": { "type": "string", "format": "date-time" },  
        "c2pa\_signature": { "type": "string" },  
        "commit\_hash": { "type": "string" },  
        "conflicts\_of\_interest": { "type": "array", "items": { "type": "string" } }  
      },  
      "required": \["org","timestamp"\]  
    },

    "license": {  
      "type": "object",  
      "properties": {  
        "type": { "type": "string", "enum": \["defensive-publication"\] },  
        "terms\_uri": { "type": "string", "format": "uri" }  
      }  
    }  
  },  
  "required": \["title","domain","hypothesis","setup","observations","failure\_class","negative\_bounds","attestation"\]  
}

**Release policy (bound to risk.band).**

* **L1-public:** full in-window publication.  
* **L2-restricted:** redacted specifics to cohort; full params time-delayed (≥30 days).  
* **L3-delayed:** boundary “shape” at T0; details at T0+90.  
* **L4-withheld:** metadata only (title/domain/failure\_class); no content.

## **6\) The Trust Layer: Safety & Operations Security**

* **Triage.** Internal pre-window review to exclude capability-lifting content, active vulns, or export-controlled material.  
* **Redaction ladder.**  
  * **Level 1 (Public):** boundary shapes & side-effect classes.  
  * **Level 2 (Restricted):** key parameters/logs to high-trust partners or time-delayed.  
  * **Level 3 (Private):** sensitive specifiers never published.  
* **Attestation & integrity.** C2PA for provenance; commit-reveal; optional ZK checks; TEEs for hazard scoring prior to reveal.  
* **Independent Risk Board.** Cross-lab safety/security/policy/engineering; quorum rules, recusal for conflicts, rapid arbitration (≤72h).  
* **Threat model & anti-poisoning.**  
  * **Sybil resistance:** org-level verification, invite/onboarding, per-window rate limits.  
  * **Replication tickets:** high-impact bounds require ≥1 external replication for verified status.  
  * **Penalty regime:** falsified/low-integrity cards lose access next window; repeat → multi-window suspension.  
  * **Anomaly scoring:** embedding-based novelty & consistency checks to flag coordinated poisoning.  
* **Legal wrappers.**  
  * **Antitrust safe-harbor:** no pricing, capacity, market timing, customer lists, or commercial roadmaps; artifacts limited to experimental failure boundaries and attested metadata.  
  * **IP:** submissions licensed as defensive publications; contributors retain background IP.  
  * **Export-control & sanctions:** flagged content routed to L3/L4 or excluded.

## **7\) Measuring Success: KPIs (with formulas)**

* **Coverage:**$$ \\\\ \\text{Coverage} \= \\frac{\\text{unique (domain, failure\\\_class, regime) tuples with mapped bounds}}{\\text{tracked tuples}}$$  
  $$$$  
* **Redundancy cut:**$$ \\\\ \\text{Redundancy Cut} \= 1 \- \\frac{\\text{repeat runs on bounded regimes}\*{\\text{post}}}{\\text{repeat runs}\*{\\text{pre}}} \\text{ (over 12–24 months)}$$  
  $$$$  
* **Time-to-pivot:**$$ \\\\ \\text{Time-to-Pivot} \= \\text{median days from card } (t\\\_0) \\to \\text{first } \\textit{verified} \\text{ follow-up}$$  
  $$$$  
* **Energy saved:** Standardized GPU-hours saved (Sec. 4\) with confidence intervals.  
* **Cross-pollination:** Count of verified edges crossing domain labels per window.  
* **Surprise yield:** Median SQ of top-quartile G-Score cards per window.  
* **Obsolescence rate:** Share of cards hitting valid\_until without refresh; target ↓ over time.

## **8\) Implementation Roadmap: 90-Day Pilot (with Genesis Round)**

* **T-30 → T0 (Genesis Round).** Founders prep 3–5 older failures each; stand up governance, legal, infra.  
* **Phase 1 (T0–T30) Setup.**  
  * Freeze schema v1.0.1; seat Risk Board (quorum/recusal).  
  * Deploy commit-reveal, ingestion pipeline, Index v0.1; enable TEEs, C2PA, timestamps.  
  * Participants privately commit (hash) initial cards.  
* **Phase 2 (T30–T60) Dry Run.**  
  * Submit sanitized historical failures; tune hazard thresholds & redaction policies.  
  * Validate query utility; test replication tickets workflow.  
* **Phase 3 (T60–T90) Live Fire.**  
  * First 24h commit-reveal window; ingest all new cards.  
  * Cohort-wide analysis; assign replication tickets for high-impact bounds.  
* **Day 91 Report.**  
  * Publish RAP Map v0.1 (negative-space graph \+ cohort leaderboard).  
  * KPIs: energy/CO₂e saved, redundancy cut, time-to-pivot, surprise yield.  
  * Open registration for Cohort-2; schedule next window.  
* **Pilot guardrails.**  
  * **Quorum:** ≥5 orgs; no org \>40% of contributions.  
  * **Safety gate:** L3/L4 require two-person approval (risk \+ domain).  
  * **Public artifact:** anonymized methods \+ metrics reproducible from logs.

## **9\) Dashboard Specification (v1.0.0)**

* **Views.**  
  * **Index Explorer (default):** full-text search; filters (domain, failure\_class, org, time); sort by G, SQ, recency. Card view \+ Graph view (nodes sized by G, colored by domain; edges \= citations/forks).  
  * **My Contributions:** pipeline (Draft → Triage → Ready-to-Commit → Published), G trend, top cards, access tier.  
  * **Network Leaderboard:** Top Orgs (G), Contribution %, Top Cards (G, SQ), network KPIs, countdown to next window.  
* **Key actions.**  
  * Cited-By, Fork/Cite, Request Replication, Report Hazard, Refresh Trigger.

## **10\) Governance**

* **Risk Board:** 7–11 members; simple majority quorum; supermajority (⅔) for L3/L4 disputes; 12-month terms; conflict recusal.  
* **Standards WG:** Maintains schema, decay rules, KPI definitions; semantic-versioned releases.  
* **Access & Enforcement:** Tiering by verified G; sanctions for poisoning or antitrust violations.  
* **Change management:** Windowed RFCs; deprecations with ≥1 window notice.

## **11\) Glossary**

* **Beautiful failure:** Instructive negative result with emergent side-effects.  
* **Negative-Space Index:** Graph of mapped instability/inefficiency bounds and generative edges.  
* **Generativity Score (G):** Impact- and size-normalized credit for avoided runs and new lines.  
* **Surprise Quotient (SQ):** Measure of prior-violating unexpectedness (Bayesian surprise).  
* **Risk bands (L1–L4):** Publication/access timing policy by hazard.  
* **Replication ticket:** Assignment for independent verification.  
* **Genesis Round:** Older, low-sensitivity disclosures to seed trust/liquidity.

## **12\) Appendices**

### **12.1 Antitrust & Legal Boilerplate (Template)**

* Participants must not disclose or coordinate on pricing, capacity allocation, hiring, market timing, customer lists, or commercial roadmaps.  
* Shared artifacts are limited to experimental failure boundaries, safety-relevant side-effects, and attested metadata per the schema.  
* Submissions use a defensive-publication license; contributors retain background IP.  
* Export-controlled content is screened and routed to L3/L4 or excluded.

### **12.2 Sample Failure Card (abbreviated)**

{  
  "title": "LR \>2.5e-4 triggers curvature resonance in 70B decoder",  
  "domain": \["algorithmic","systems"\],  
  "hypothesis": "Higher LR at batch 4M would cut time-to-loss by 15%.",  
  "setup": {  
    "model": "Decoder-Only 70B (arch family X)",  
    "model\_card\_uri": "\[https://example.org/modelcards/decoder70b\](https://example.org/modelcards/decoder70b)",  
    "data": "CCMix-v6 \+ CodeMix-v3",  
    "scale\_hw": "256x H100",  
    "scale\_cost\_usd": 185000,  
    "scale\_time\_hrs": 72  
  },  
  "observations": \[  
    "Loss diverged at step \~35k; gradient norms exploded.",  
    "Instability sensitive to tokenizer variant."  
  \],  
  "emergent\_side\_effects": \[  
    "Alignment regression on safety eval S\* during divergence.",  
    "IO queueing spikes preceded divergence by \~800 steps."  
  \],  
  "failure\_class": \["instability","alignment-regression","ops-brittleness"\],  
  "repro\_window": "Likely applies to autoregressive decoders \>50B with optimizer family O",  
  "negative\_bounds": \["lr \> 2.5e-4 at batch 4M unstable for arch X"\],  
  "next\_directions": \["Try lr warmup to 1.8e-4; clip grad-norm at 0.6", "Swap tokenizer T2"\],  
  "artifacts": \["\[https://example.org/artifacts/plot123.png\](https://example.org/artifacts/plot123.png)"\],  
  "temporal": {   
    "valid\_until": "2026-12-31",   
    "decay": "exponential",   
    "refresh\_triggers": \["optimizer:O→O2","arch:X→Y"\]   
  },  
  "risk": {   
    "hazard\_score": 0.22,   
    "band": "L2-restricted",   
    "export\_control": false,   
    "antitrust\_sensitive": false   
  },  
  "metrics": { "surprise\_quotient": 2.7, "g\_score\_snapshot": 0.0 },  
  "redactions": \["exact tokenizer hash"\],  
  "attestation": {  
    "org": "OrgA",  
    "timestamp": "2025-11-05T19:21:07Z",  
    "c2pa\_signature": "c2pa:...sig...",  
    "commit\_hash": "sha256:...abc"  
  },  
  "license": {   
    "type": "defensive-publication",   
    "terms\_uri": "\[https://example.org/rap/license/v1\](https://example.org/rap/license/v1)"   
  }  
}

### **12.3 Operational Checklists**

**Go/No-Go (per window).**

* \[ \] Antitrust/IP/export boilerplate in force.  
* \[ \] Risk bands wired to release timing/access tiers.  
* \[ \] G-Score normalization \+ SQ scoring live.  
* \[ \] Commit-reveal \+ C2PA \+ timestamps active; TEE triage enabled.  
* \[ \] Replication tickets configured; anomaly scoring on.  
* \[ \] KPI pipelines reproducible from logs.

**Thesis in one line:** Map the negative space together—share the boundaries, not the secrets. The field advances by learning where not to go.