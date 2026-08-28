/* FLOORING FIELD TOOLKIT — DOCUMENT LIBRARY (shape #4: shared/docspec.js).
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = picker VOCABULARY · docs.js = the WRITE-UPS
 * this trade actually has to produce. The engine owns the eleven blocks of the
 * emitted instruction set and every universal law in them; this file owns what
 * is different about a floor and nothing else.
 *
 * WHY THIS FILE EXISTS NOW. Flooring shipped as trade #13 with six tools and no
 * write-up page, and sitework did the same at #12 — the two trades the DOCS axis
 * skipped, named in tools.js's own prune ("THE WRITE-UP LIBRARY ... owed on two
 * trades") and in the private record. This is the flooring half of that debt.
 * The prune also put FOUR panel proposals inside this library rather than on the
 * hub, because a second docspec engine on one rack is the duplication the prune
 * exists to catch: the exclusions-and-clarifications sheet, the prep write-up
 * that becomes the PCO backup, the shading call that is not a defect, and the
 * substrate excluded from warranty when he was directed to proceed anyway. All
 * four are here as documents, none as a page.
 *
 * THE SHARED LIBRARY IS ALREADY ADDRESSED TO A JOBSITE, AND THIS TRADE IS ON ONE.
 * Unlike creative (a one-person shop with no GC and no PM, which had to drop and
 * re-address almost everything), flooring is a sub with a crew, a PM, an office,
 * a GC above it and a dealer beside it. So this file keeps ALL eleven shared
 * documents — `drop: []`, the same as every other construction kit on the rack —
 * and overrides only where a floor genuinely differs: the daily's audible is
 * prep, the delay that is the slab reading wet is a SHIPPED PAGE and this letter
 * must point away from it, and the service write-up is a warranty callback where
 * a cause-of-failure determination is exactly the thing §SAFETY forbids.
 *
 * THE REFUSAL IS THE DESIGN, and it is the same wall trade.js and items.js
 * already built, carried into the one place a document can breach it — the block
 * an AI reads. This file ships NO moisture value (RH, calcium chloride, pH,
 * wood-to-subfloor differential), NO flatness or levelness tolerance (no fraction
 * in ten feet, no FF/FL number), NO acclimation period or temperature range as a
 * value, NO product data (wear layer, DCOF, IIC/STC, expansion gap, fastener
 * schedule, trowel notch, coverage rate, cure hours), NO pass/fail/ready/
 * acceptable/safe-to-install determination, NO appearance or defect ruling from
 * any mill or standard, and NO warranty interpretation. Every document below
 * records what HE measured beside the limit off HIS OWN bucket, what HIS OWN
 * instructions require, and what he did — and never says which one wins. The
 * mill, the adhesive maker, the independent testing agency and the architect own
 * what it is supposed to be. The engine's two LOCKED toggles ("never invent",
 * "never judge a value") back this at the universal-law level; the per-document
 * `note` lines carry the flooring-specific edge the locks cannot see.
 *
 * `trade`     the trade word the emitted instructions use ("we do ___ work"). DECLARED,
 *            never derived from the toolkit name.
 * `docs`      documents specific to this trade (they join the shared library)
 * `overrides` change any field of a SHARED document by id, rather than forking it
 * `drop`      shared document ids this trade genuinely never writes
 * `vocab`     what this trade dictates that a phone gets wrong ("wrong -> Right")
 * `reminders` trigger-only nudges — they fire when relevant and never nag
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TRADE_DOCS = {
  "trade": "flooring",

  "docs": [
    {
      "id": "not-in-my-number",
      "name": "What My Number Doesn't Cover",
      "aka": [
        "exclusions",
        "clarifications",
        "qualifications",
        "assumptions",
        "inclusions and exclusions",
        "my bid excludes",
        "not in my price",
        "not in my scope",
        "scope letter",
        "proposal clarifications"
      ],
      /* VERIFICATION family, and it is the least-wrong of the five. This is not a
         test, but it is a standalone record somebody leans on later where THE
         BOUNDARY IS THE WHOLE VALUE — which is exactly verification's own first
         spine heading — and it must not carry a delta rule, because every bid is
         its own baseline. The explicit sections below override the family spine;
         the family is here for the continuity rule (standalone) and the label. */
      "family": "verification",
      "from": "the person who bid it",
      "to": "the GC, the builder, or whoever is holding my number",
      "why": "The one page that decides, months later, what counts as an extra. Attached to the bid it is a clarification everyone signs off on; produced after the argument starts it is a defense nobody believes. It is the cheapest document in this library and the one that saves the most.",
      "note": "It states what my price is for and what it takes for granted, in plain words. It carries no price — the office owns the number — and it never states another party's spec: the flatness, the moisture limit and the schedule belong to the people who own them, and this sheet only says which ones my number assumed.",
      "omit": "THE ASSUMPTIONS, in the same page as the exclusions. An exclusion list names what I am not doing; the assumptions name what has to be TRUE for my price to hold — the slab ground and flat enough for my system, the room clear, the old goods gone, the building at temperature. It is the half everybody leaves off, and it is the half that turns into a change when the day arrives and none of it is done.",
      "needs": ["notdone"],
      "halt": "Only if no scope of work or bid is described at all.",
      "facts": ["what my number covers", "what it excludes", "what it assumes is already done by others", "where an allowance is carried and what it is based on", "what turns into a change"],
      "sections": [
        {
          "h": "WHAT MY NUMBER COVERS",
          "r": "The work my price is for, in plain words: the areas, the material by the name on the plan, and the prep I am carrying. Say it the way the estimate said it, so this page and the number agree."
        },
        {
          "h": "WHAT IT DOES NOT COVER",
          "r": "The exclusions, one neutral line each — moisture mitigation, grinding or leveling past the skim I carried, demolition of the existing goods, cutback or mastic removal, moving furniture or fixtures, patching the slab to a tolerance somebody else owns. Name it; never price it and never say whose job it is instead unless you actually know."
        },
        {
          "h": "WHAT I'M ASSUMING IS ALREADY DONE",
          "r": "The conditions my number takes for granted, each stated as an assumption and not a demand: the slab is ground and flat to the spec, the room is clear and at temperature, the old flooring is out, the jambs are set, the material is on site. This is the section the exclusion list forgets, and it is the one that protects the price."
        },
        {
          "h": "ALLOWANCES, AND WHAT THEY'RE BASED ON",
          "r": "Where the number carried an allowance — an attic-stock quantity, a square-footage taken off a plan of a certain date, a stair count. State what each one is BASED on, never the dollar. A change to the basis is a change to the price, and this line is how it stays visible."
        },
        {
          "h": "WHAT MAKES THIS A CHANGE",
          "r": "The specific things that, if they show up, are outside this number and become a tag: more area than the plan showed, a substrate that needs work I excluded, a schedule that puts me back in the same room twice. Naming them here is not a threat — it is the map that keeps the extra from becoming an argument."
        }
      ],
      "secondary": ["a one-paragraph version to paste into the bid email", "just the exclusion list on its own, as a short block"]
    },

    {
      "id": "prep-write-up",
      "name": "The Prep Write-Up (What the Substrate Needed)",
      "aka": [
        "prep",
        "floor prep",
        "prep report",
        "what the slab needed",
        "substrate prep",
        "grinding",
        "skim coat",
        "pco backup",
        "potential change order",
        "what i had to do to the floor"
      ],
      /* VERIFICATION family: a record of what was done to a condition found, leaned
         on later, non-delta. It is the NARRATIVE, and it coexists with the shipped
         Extra Work Tag (tm-tag.html) the way the shared change-request coexists
         with it on every construction kit — the tag is the signed ticket with
         counts, this is the condition story that becomes the backup behind it. */
      "family": "verification",
      "from": "the lead who did the prep",
      "to": "my PM, the GC super, and the dealer who sold the job",
      "why": "Prep is where the whole margin lives and it is the work nobody writes down. This is the record of what the substrate was and what it took to make it installable — the backup behind the tag, written the day you did it. Grind it, skim it or glue over it and the before is demolished; a story told three weeks later is not evidence, and the day's write-up is.",
      "note": "It records what you found and what you did to it. It never states a moisture number, a flatness tolerance or whether the substrate was acceptable. You write the reading you took beside the limit off your own bucket or the mill's printed instructions, and you never say which one wins — that call is the reason this document, and this whole kit, exists.",
      "omit": "WHAT IT WAS LIKE BEFORE YOU TOUCHED IT — the condition of the substrate and the reading you took before anything changed, with where the photos live. Grinding, skimming or gluing over it demolishes the evidence, and the before-value written the same day is the only thing that still exists ninety days later when a bonded floor is somebody else's ninety-day-old mistake that you now own.",
      "needs": ["before", "where"],
      "halt": "Only if no area or substrate is described at all.",
      "facts": ["the date and the area", "what the substrate was when you got there", "what your own instructions require of it", "what you did to it", "what it displaced — hours, schedule, another trade"],
      "sections": [
        {
          "h": "WHAT I WAS STANDING ON",
          "r": "The substrate and its condition when you arrived, area by area. What you saw, what you measured — your reading beside the limit off your own bucket, never which one wins — and where the photos are. Record the number; never record a verdict on it."
        },
        {
          "h": "WHAT MY OWN INSTRUCTIONS REQUIRE",
          "r": "The condition your adhesive's or the mill's printed instructions call for, stated as THEIR requirement and not a number you are supplying. This is the line that says why the prep was necessary without you setting the spec that made it so."
        },
        {
          "h": "WHAT I DID TO IT",
          "r": "The prep in the order you did it — ground, skimmed, patched, pulled cutback, undercut jambs, primed — with the area and roughly how long each took. Counts and areas, never prices; the office prices it off this."
        },
        {
          "h": "WHAT IT COST THE DAY",
          "r": "What the prep displaced: the hours it added, the crew standing while a skim cured, the trade you could not follow because you were still on the floor. This is the impact half the tag turns into money."
        },
        {
          "h": "WHERE THE PROOF IS",
          "r": "The photos, the readings, the bucket labels — by area and date. A description with no photo reference and no date is worth nothing in a back-charge meeting, and once the floor is down there is no second chance to take the picture."
        }
      ],
      "secondary": ["a short cover note to send with the Extra Work Tag", "just the before-condition and photo list, as a record for the file"]
    },

    {
      "id": "shading-note",
      "name": "It Looks Different in That Light (the shading call)",
      "aka": [
        "shading",
        "pile reversal",
        "watermarking",
        "pooling",
        "telegraphing",
        "it looks lighter",
        "looks wrong",
        "they say it's a defect",
        "appearance complaint",
        "color looks off"
      ],
      /* INCIDENT family: a concern raised and observed on a day, documented once,
         read later, non-delta. The whole design constraint is that this document
         gets AHEAD of an appearance complaint WITHOUT the installer making the
         determination §SAFETY forbids — he records what was raised and what he
         actually did, and routes the appearance call to the mill rep in writing. */
      "family": "incident",
      "from": "the installer who laid it",
      "to": "my PM, the dealer, and the GC or customer who raised it",
      "why": "Somebody points at the floor and says it looks wrong — a lighter run, a change where the light hits it, a direction that shows. This is the note that documents what was raised and what you actually did, the same day, so an appearance question does not become an installation-defect claim by silence. You do not grade the look here; you record it and send it to the people who own that call.",
      "note": "It records what was raised and how the floor was installed. It never calls the appearance a defect OR a characteristic, never says it is acceptable, and never quotes a mill's appearance criteria — whether it is a manufacturing trait or a defect is the mill rep's determination, and this document asks for it in writing rather than making it.",
      "omit": "WHEN IT WAS RAISED AND UNDER WHAT LIGHT — the date, the time of day, the lighting and the direction you were standing when it showed. Shading moves with the light and the angle, so a complaint with no conditions on it can be re-staged to look like anything; the record made on the day, under stated light, is the only fixed one.",
      "needs": ["when", "where"],
      "halt": "Only if no floor, area or concern is described at all.",
      "facts": ["the date it was raised and by whom", "what they are seeing and where", "the conditions you observed it under", "how the material was installed", "what you are asking the mill rep for"],
      "sections": [
        {
          "h": "WHAT WAS RAISED, AND BY WHOM",
          "r": "The concern in their words, the area, and the date they raised it. Record what they say they see; never record whether they are right. Neutral, no adjectives of your own."
        },
        {
          "h": "WHAT I SEE, AND UNDER WHAT CONDITIONS",
          "r": "What you observed standing there — the light (daylight, overhead, low sun through a window), the time of day, the direction you were facing. Shading reads differently from every angle, so the conditions ARE the record. State what you see; never state whether it is acceptable."
        },
        {
          "h": "HOW IT WAS INSTALLED",
          "r": "The facts about YOUR work you can stand behind: laid from one run and one dye lot, swept or racked per the layout, seams where the plan put them, direction as specified. This is the half you own, and you can state it plainly without grading the appearance."
        },
        {
          "h": "WHAT THIS ISN'T MINE TO CALL",
          "r": "One plain line: whether this is a manufacturing characteristic or a defect is the mill's determination, not the installer's, and this note does not make it. Saying so is not a dodge — it is the honest boundary that keeps the note credible."
        },
        {
          "h": "WHAT I'M ASKING FOR",
          "r": "The request to the mill rep or dealer, in writing: a site visit, an inspection under stated conditions, or their written determination — by a date — so nobody's floor sits in limbo and nobody's invoice does either."
        }
      ],
      "secondary": ["a short message to the dealer or mill rep requesting the inspection", "a two-line note to the customer saying it has been referred and by when"]
    },

    {
      "id": "directed-to-proceed",
      "name": "You Told Me To Put It In Anyway",
      "aka": [
        "directed to proceed",
        "told to install",
        "proceed anyway",
        "over my objection",
        "install over it",
        "they said go",
        "at your risk",
        "against my recommendation",
        "made me cover it"
      ],
      /* INCIDENT family: a record of a thing that happened — a condition found and
         a direction given over the objection — written once, read years later,
         non-delta. §SAFETY's hardest edge lives here: it must NOT declare a
         warranty void or predict a failure. It states the honest half — what his
         own instructions require and that he was directed to proceed over it. */
      "family": "incident",
      "from": "the installer who raised it",
      "to": "the GC super, my PM, and whoever gave the direction",
      "why": "You looked at what you were told to cover, it was not what your own instructions call for, you said so, and you were told to put it in anyway. This is the record that you raised it and were directed to proceed — written the same day, because once the floor is bonded the thing you covered is gone, and so is the argument, unless this exists.",
      "note": "It records what you found, what your own instructions require, that you raised it, and that you were directed to proceed. It never declares a warranty void, never says the floor will fail, and never grades the substrate. It states the honest half — what your instructions require and what you were told to do over it — which is the half that actually holds up. If the floor is not ready and you want the go-ahead in writing BEFORE you cover it, that is Give Me The Go (give-me-the-go.html) — it owns the not-ready-to-install case and ends in the ask. This is the record for AFTER you were directed to proceed over your objection and covered it anyway, the dated proof when the go will not come in writing. Keep the two apart or the kit has two doors onto one job.",
      "omit": "WHO DIRECTED YOU, WHEN, AND HOW — the name, the date and the channel of the go-ahead, plus the condition as it was before you covered it and where the photos live. \"They told me to\" with no name and no date on it is worth nothing; the direction with a name and a time on it is the whole document.",
      "needs": ["when", "who", "before", "where"],
      "halt": "Only if no condition and no direction to proceed are described at all.",
      "facts": ["the date and area", "the condition you found", "what your own instructions require of it", "who directed you to proceed and how", "what you covered, and where the proof is"],
      "sections": [
        {
          "h": "WHAT I FOUND",
          "r": "The substrate condition, area by area, with your reading beside the limit off your own instructions or bucket. State what you measured; never state whether it passes. Refusing that call alone is the whole reason for this note."
        },
        {
          "h": "WHAT MY INSTRUCTIONS REQUIRE",
          "r": "The condition your adhesive's or the mill's printed instructions call for, stated as THEIR requirement. This is why you raised it, and it is not a number you are supplying."
        },
        {
          "h": "THAT I RAISED IT",
          "r": "When you flagged it, to whom, and how — the exact words if you have them. This is the line that makes the direction a direction rather than a surprise."
        },
        {
          "h": "WHO DIRECTED ME TO PROCEED",
          "r": "The name, the date, and the channel: verbal, call, text, email, in the room. If it was verbal, say so and say this note is the record of it. A direction with no name on it is not one."
        },
        {
          "h": "WHAT I COVERED, AND WHERE THE PROOF IS",
          "r": "What went down over what, the area, and where the photos and readings live. Once it is bonded the substrate is demolished, so the record made today is the only one there will ever be."
        }
      ],
      "secondary": ["a short message asking whoever gave the direction to confirm it in writing", "a note for the file with the photos and readings attached"]
    }
  ],

  /* ── DROPS — none, and that is the finding ────────────────────────────────
   * creative dropped three shared documents because a one-person video shop has
   * no dispatch, no safety department and a shipped tool that already does its
   * change narrative. Flooring is construction: it has a crew, a PM, an office, a
   * GC and a dealer, and it writes every one of the eleven. The Extra Work Tag
   * (tm-tag.html) is a signed TICKET with counts, structurally the same split
   * that lets change-request (the narrative) live beside it on all ten other
   * construction kits — so it stays. The one that had to be argued is
   * service-writeup: a floor callback is where a cause-of-failure determination
   * is most tempting and most forbidden, so it is KEPT but re-cast as a warranty
   * visit whose `note` sends the cause to the mill, rather than dropped.
   */
  "drop": [],

  /* ── OVERRIDES — addressing plus the two that would otherwise collide ──────
   * The shared library is already written to a jobsite and this trade is on one,
   * so most spines and omit lines are untouched. What changes: the daily's
   * audible is prep; the delay letter must point AWAY from Give Me The Go, which
   * is the shipped page that owns the slab-not-ready case (the delay-notice /
   * still-waiting-on split creative recorded, in flooring's own vocabulary); and
   * service-writeup becomes a warranty callback that never rules on cause.
   */
  "overrides": {
    "daily-report": {
      "name": "The Day Report",
      "aka": ["daily", "dfr", "end of day", "eod", "field report", "how the day went"],
      "from": "the lead mechanic on the job",
      "why": "The one your PM forwards, and the only record of what a day on this floor actually cost. Written on the day it is a fact; written on Friday it is a memory, and a memory does not back a change order.",
      "omit": "THE AUDIBLE, and on a floor the audible is almost always prep — the grind nobody scheduled, the skim that ate the morning, the material robbed from another area to keep laying, the hour of overtime to beat a pour. Nobody writes it down the day it happens, and three weeks later there is no paper for why the number moved.",
      "needs": ["change"],
      "secondary": ["a weekly rollup from the dailies in this thread", "a short version for the GC with the internal detail stripped"]
    },

    "damage-found": {
      "name": "How the Slab Was When I Got There",
      "aka": ["damage", "pre-existing", "already cracked", "came in like this", "not us", "prior condition"],
      "to": "the GC super, my PM, and the dealer",
      "why": "You walked in to a substrate that was already wrong — cracked, contaminated, curling, oil-stained, or a slab somebody else poured and left. This is the note that means the condition under your floor is not yours when somebody goes looking for who pays, and you are the trade that seals it.",
      "omit": "THE DATE AND WHERE THE PHOTOS ARE, and the reading you took before anything changed. You are about to cover this, so a description with no photo and no date is your word about a slab nobody can see any more — which settles nothing on the day somebody asks who owns the tear-out.",
      "needs": ["when", "before", "where"],
    },

    "delay-notice": {
      "name": "We're Held Up",
      "aka": ["held up", "stopped", "cant start", "date is moving", "impact", "delay"],
      "to": "the GC and my PM",
      "why": "One thing has actually stopped the work and the date is going to move. Sent warm and early it moves the thing; sent late it only explains why you are late.",
      "note": "The letter for a slab that reads wet, or heat that never ran, is Give Me The Go — that page owns the not-ready-to-install case and ends in the go-ahead. This is any OTHER hold: a backordered material, a room that never got cleared, an approval you are waiting on, another trade that has not finished. Keep the two apart or the kit has two doors onto one job."
    },

    "change-request": {
      "to": "the GC, my PM, and the dealer who sold it",
      "note": "This is the NARRATIVE only — no prices, no rates, no hours priced out; the office owns the number. The signed ticket with the counts on it is the Extra Work Tag (tm-tag.html); this is the story that says why it is outside the number, which is the part that gets argued. For prep specifically, the fuller record is the Prep Write-Up."
    },

    "service-writeup": {
      "name": "Warranty / Callback Write-Up",
      "aka": ["callback", "warranty", "warranty call", "went back", "come back", "lifted seam", "hollow spot", "gap opened up"],
      "from": "the mechanic who went back",
      "to": "my PM, the dealer, and the customer",
      "why": "You went back to a floor that is already down and somebody is unhappy with — a lifted seam, a hollow spot, a plank that has moved, a gap that opened. This is the record of what you found and what you did about it, honest and complete.",
      "note": "It records what you found and what you did. It NEVER states the cause and never calls it a defect — whether a lifted seam is adhesive, substrate, the material or the site is the mill's and the testing agency's call, not the man on his knees, and \"caused by\" is a claim a callback note is not allowed to make. Route the cause to the mill; record the condition.",
      "omit": "WHAT YOU DID NOT DO AND WHY, and the condition it was in when you got there before you touched it. The part you could not fix on this visit, the thing outside this callback, the reading from before — left out, you own it by silence, and on a floor already down there is no second look.",
      "needs": ["before", "notdone"],
    },

    "site-walk": {
      "name": "Pre-Install Walk",
      "aka": ["walk", "site visit", "survey", "pre-install walk", "went and looked", "field measure"],
      "to": "the office, estimating, and the dealer",
      "why": "Everything you noticed standing on the substrate, written so somebody who was not there can price it, schedule it and order the right material for it.",
      "omit": "ACCESS, THE SUBSTRATE AND THE ROOM'S STATE — where a twelve-foot roll can actually get in, the freight lift and who holds the key, whether the room will be clear and at temperature, and what the slab looks like today. It never makes the notes and it is the thing that blows the day, because a floor van cannot improvise its way past a locked dock.",
      "needs": ["who", "before", "where"],
    },

    "handover": {
      "name": "Turnover / Closeout",
      "aka": ["handover", "turnover", "closeout", "punch complete", "hand off", "done"],
      "to": "the GC, the owner, and their facilities people",
      "why": "The last document anyone reads and the first one they blame. Written well it ends the job; sent as \"floors are done\" it brings you back for free on every scuff that was there when you left.",
      "omit": "THE ATTIC STOCK AND THE MAINTENANCE HANDOFF, alongside the open items. Where the leftover material and the spares physically are, what cleaner and what pad the floor takes, and what is still open with an owner and a date. A closeout that reads finished turns every future mark into your warranty.",
      "needs": ["when", "who", "where", "notdone"],
      /* `facts` re-addressed too, not just the row-level fields — the shared list
         names "keys, codes, manuals" and "what was tested and by whom", which are
         a systems turnover, not a floor closeout. It only feeds the VALIDATION
         checklist, but a floor hand told to check his notes for keys and codes is
         reading a checklist built for another trade. */
      "facts": ["what area or floor is being handed over", "what was verified and by whom", "what is still open", "the attic stock and spares left, and where they are", "the care and cleaning info, and who to call"]
    },

    "look-ahead": {
      "name": "Look-Ahead / What Has To Be Ready",
      "aka": ["look ahead", "lookahead", "two week", "next week", "whats coming", "plan"],
      "to": "the GC and my PM",
      "why": "The one that stops the crew standing in a corridor next week. It is a request wearing a schedule — the dates below only hold if the rooms underneath them are ready.",
      "omit": "WHAT HAS TO BE TRUE BEFORE EACH AREA CAN START — the slab ground and dry enough, the room cleared, the heat on, the other trades out, the material on site and conditioned. A look-ahead with no preconditions on it is a wish list, and the date slips with nobody having agreed to it.",
      "needs": ["notdone"],
    }
  },

  /* ── VOCAB — what a floor crew dictates that a phone gets wrong ────────────
   * Spoken-to-written only. Every pair CORRECTS something — the engine emits this
   * under "the ones my phone gets wrong", so an identity pair ("dye lot -> dye
   * lot") reads as a broken instruction to both the model and the man. No brand
   * names (items.js §THE REFUSAL), and nothing here is a value or a requirement:
   * RH PROBE and CALCIUM CHLORIDE are the TOOL and the TEST, never a number.
   * US dialect throughout, held with the rest of the kit.
   */
  "vocab": [
    "el vee tee -> LVT",
    "el vee pee -> LVP",
    "vee see tee -> VCT",
    "ess pee see -> SPC",
    "double stick -> double-stick",
    "self leveler -> self-leveler",
    "self levelling -> self-leveling",
    "levelling -> leveling",
    "cut back -> cutback",
    "under layment -> underlayment",
    "sub floor -> subfloor",
    "notch trowel -> notched trowel",
    "float floor -> floating floor",
    "click lock -> click-lock",
    "tongue and groove -> tongue-and-groove",
    "tee and gee -> T&G",
    "tee molding -> T-molding",
    "t molding -> T-molding",
    "quarter round -> quarter-round",
    "shoe mould -> shoe molding",
    "thresh hold -> threshold",
    "under cut -> undercut",
    "in situ -> in-situ",
    "cal chloride -> calcium chloride",
    "rh probe -> RH probe",
    "colour -> color"
  ],

  /* ── REMINDERS — trigger-only, never nagging ──────────────────────────────
   * The block is what talks to the AI, and an AI asked to write a moisture
   * paragraph or a callback note is exactly where an invented limit or a "caused
   * by" walks in. items.js keeps the numbers off the page; these keep them, and
   * the determinations, out of the document.
   */
  "reminders": [
    "When a moisture reading, RH, calcium chloride, pH or a meter comes up -> remind them to record the number they measured and, beside it, the limit off their OWN adhesive bucket or the mill's printed instructions, and where the reading was taken and by which probe. Never let the document say whether the reading is acceptable, and never let it supply a limit — one adhesive's maximum is not the next one's, and the write-up that asserts a number is the one that gets quoted back.",
    "When flatness, levelness, a low spot, a straightedge or FF/FL comes up -> remind them to describe what they found and where, and to state the tolerance as the one on THEIR contract or the mill's instructions if they have it, marked <MISSING> if they do not. Never let the document supply a fraction in ten feet; that is the concrete sub's ASTM record and the architect's spec, not the floor layer's to set.",
    "When acclimation, conditioning, temperature or \"operational and conditioned\" comes up -> remind them to record the conditions they observed and the dates, not a required range. What the material needs is in the box; this document reports what was, never what should be.",
    "When a substrate condition, grinding, a skim, a patch or cutback comes up -> remind them to write the BEFORE — what it was and what they measured before they touched it, with where the photos live. Once it is ground, skimmed or covered the evidence is demolished, and the before written the same day is the only record that survives.",
    "When somebody directs them to install over a condition they flagged -> remind them to record who directed it, when, and by what channel, and to state what their own instructions require — never that the warranty is void or that the floor will fail. The name and the date on the direction is the whole protection; the determination is not theirs to make.",
    "When an appearance concern comes up — shading, pile reversal, watermarking, telegraphing, a lighter run -> remind them to record what was raised, the light and the direction they observed it under, and how it was installed, and to route the determination to the mill rep in writing. Never let the document call it a defect OR a characteristic; that call belongs to whoever owns the material.",
    "When extra work, prep, a change or \"one more room\" comes up -> remind them to name who asked, when, and how it was authorized, and to keep every price out of it. The record made on the day is what makes it a change rather than a favor; the office owns the number."
  ]
};
