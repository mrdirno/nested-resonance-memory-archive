/* MASONRY FIELD TOOLKIT — THE TRADE'S VOCABULARY DATA.
 *
 * The boundary this file exists to hold (av/AV_SOCIETY.md §TRADE EXPANSION):
 *   trade.js  = IDENTITY + COPY
 *   tools.js  = REGISTRY
 *   items.js  = the trade's VOCABULARY DATA  <- you are here
 * Categories, option lists, ladders and the words a mason actually says live
 * here. A page that hand-writes any of them is a fork with extra steps.
 *
 * ── THE WORDS, AND THEY ARE NOT DECORATION ───────────────────────────────
 * MUD IS MORTAR. Not joint compound (the taper's), not concrete (the
 * finisher's), not thinset (the tile setter's), not wet dirt (the dirt hand's).
 * MORTAR AND GROUT ARE DIFFERENT MATERIALS ON DIFFERENT DAYS — mortar is the
 * bed between units, grout is the fluid fill poured into the cells, and the
 * electrician's live ask in the shipped electrical kit is literally "Don't
 * grout the cell I'm in." Swap those two words anywhere in this file and the
 * kit contradicts the ask it was built to answer.
 * CELL, never core. CUBE, never pallet. BLOCK or CMU, never cinder block. A
 * WYTHE is one vertical thickness. A LEAD is the corner built up first that the
 * line runs from; a TWIG holds the line off a long run. Joints are HEAD
 * (vertical) and BED (horizontal), struck and tooled at the thumbprint. The
 * TENDER mixes and keeps the layers stocked — he is not a helper and he is not
 * an apprentice.
 * AND HE SCHEDULES BY COURSE AND LIFT, NOT BY DATE. "The wall's at eight foot
 * Thursday" is the native sentence, which is why every ask, every answer and
 * the whole wall-state page carry a COURSE where the other ten kits carry a
 * date. A date does not help a man whose box is at ten foot and whose wall is
 * at four.
 *
 * ── WHAT IS NOT IN THIS FILE, AND WILL NOT BE ────────────────────────────
 * Decided before a line was written, the way concrete killed its seventeen
 * admixture dose fields. Nothing here rates, sizes, doses, spaces, times or
 * grades anything: no mortar TYPE (M/S/N/O) as a value, a default or a
 * placeholder digit · no ASTM designation or proportion · no grout lift height,
 * consolidation timing or cleanout rule stated as code · no rebar size, lap,
 * spacing, cover or dowel embedment · no lintel bearing length · no joint
 * reinforcement, tie or anchor spacing · no control-joint or expansion-joint
 * location · no cold-weather protection temperature or duration · no cure time
 * · no rated-assembly or UL number · no silica exposure figure presented as a
 * control plan · and above all NO CONSTRUCTION-PHASE BRACING IN ANY FORM — no
 * height, no spacing, no wind figure, no restricted-zone distance, no duration,
 * no release criterion, no "safe to work under". That one is engineered, it is
 * the thing on this job that kills people, and a bracing field on a phone is a
 * bracing design. A wall may be flagged unbraced only as a COME-ASK-ME with a
 * handback, never as a dimension and never as a permission.
 * No brand as a thing to write down, either: Speedy, Sakrete, Quikrete,
 * Dur-O-Wal and Lull are words people SAY. A trademark printed as the item puts
 * a trademark on somebody's purchase order (the electrical/items.js precedent).
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};

/* ── THE EXTRA WORK TAG (shape #2 — shared/note.js) ────────────────────────
 * Who directed it, what came up, why it is outside the contract, and the line
 * everybody argues about later: what is NOT in this tag. Counts only — men,
 * hours and material as quantities. No rates, no totals, and no signature line,
 * because a copy-paste block cannot be signed and a mason spots it instantly.
 */
window.TOOLKIT_ITEMS.tag = {
  roles: [
    "GC superintendent",
    "Our own general super",
    "Another trade's foreman working in our wall",
    "GC project manager",
    "Our PM or the office",
    "Builder's field super (tract or custom home)",
    "Homeowner",
    "Owner's rep",
    "Property manager or building engineer",
    "Jurisdiction inspector on site"
  ],
  how: [
    { v: "Face to face at the wall" },
    { v: "Text message" },
    { v: "Phone call" },
    { v: "Told to me at the morning huddle" },
    { v: "Radio on the site channel" },
    { v: "Email" },
    { v: "Marked-up set handed to me in the field" },
    { v: "Paint or keel marks changed on the wall" },
    { v: "Note left on the stage" },
    { v: "A different trade told me he'd cleared it" }
  ],
  /* WHY IT IS OUTSIDE THE CONTRACT. Every line is a CONDITION he picks, not a
     characterisation of anybody, and not one of them puts a price, a cause or a
     verdict on the page. */
  "why": [
    {
      "name": "Footing or dowels not as shown",
      "sub": "Top of footing high, low or out of line, or dowels out of the cells. Told to lay it anyway, or told to stand while somebody sorted it."
    },
    {
      "name": "Standing while another trade got out of our wall",
      "sub": "Crew, mud and material on the ground, waiting on somebody else to finish in the wall we were manned for."
    },
    {
      "name": "Boxes, sleeves or stubs late or wrong",
      "sub": "Somebody else's rough-in showed up after we had laid past it, or did not match what we were marked to. Wall opened back up."
    },
    {
      "name": "Opening moved after we laid to it",
      "sub": "A door, a window, a louvre or a knockout landed somewhere else after we built to the first set."
    },
    {
      "name": "Layout or a control line moved",
      "sub": "Lines, offsets or elevations changed after we set leads to the first ones."
    },
    {
      "name": "Frames, lintels or precast not on site",
      "sub": "Could not lay past the opening. Crew moved, stood, or came back to it as a second trip."
    },
    {
      "name": "Told to cut in something that isn't on our drawings",
      "sub": "An opening, a chase, a pocket or a knockout added at the wall after the lift was laid."
    },
    {
      "name": "Broke out and re-laid work we had already built",
      "sub": "Wall we laid came back out on somebody's say-so — not because of anything wrong with the laying."
    },
    {
      "name": "Old work nobody told us about",
      "sub": "Existing wall, footing, lintel or fill in our line that was not on anything we bid."
    },
    {
      "name": "Told to work the weather",
      "sub": "Keep laying, cover it, uncover it, or come back on a day we had called off."
    },
    {
      "name": "Babysitting protection somebody else called for",
      "sub": "Cover, blankets, plastic, heat or barricade we put on, kept checking and pulled on somebody's say-so."
    },
    {
      "name": "Couldn't get material or the stage to it",
      "sub": "Hand-carried, re-stacked, or one lift turned into two because access or hoisting changed after we set up."
    },
    {
      "name": "Cleanup or re-washing behind somebody else",
      "sub": "Mud, slurry, overspray, tracking or staining left on a face we had already washed."
    },
    {
      "name": "Told to hold the wall for somebody else's look",
      "sub": "Stopped short of a course, or left a lift open, so another party could inspect, photograph or work in it."
    }
  ],
  /* WHAT IS NOT IN THIS TAG. The line everybody argues about later, and the
     reason the tag survives being read by an office: it says out loud what it is
     not, so nobody can read it as something bigger than it is. */
  "notin": [
    {
      "name": "Not a price",
      "sub": "Hours, counts and conditions only. No rate, no total, no dollar figure anywhere on it."
    },
    {
      "name": "Not a change order and not a claim",
      "sub": "This says we were directed and what it took. It becomes a change when the offices paper it, and entitlement is their letter, not the foreman's."
    },
    {
      "name": "Not a question for the engineer, and not a design change",
      "sub": "Anything about the design goes up through the GC on their form. Nothing here approves moving steel, changing a bearing, cutting a wall or leaving the set in hand."
    },
    {
      "name": "Not a bracing decision and not a release",
      "sub": "Nothing on this tag braces a wall, releases one, or says one is safe to load, backfill against or work under. That is engineered and it is somebody else's call."
    },
    {
      "name": "Not the supplier's ticket or the testing agency's report",
      "sub": "We attach them by the numbers already printed on them. We never retype what's on them."
    },
    {
      "name": "Not the special inspector's record",
      "sub": "He writes his own and numbers it. We write what our crew was told and what our crew did."
    },
    {
      "name": "Not the GC's daily",
      "sub": "They keep theirs and number it. This is ours and it stands on its own."
    },
    {
      "name": "Not a finding of cause",
      "sub": "We write what we laid and what we saw. Why something cracked, spalled or stained is a call other people make."
    },
    {
      "name": "Not a safety or incident report",
      "sub": "Injuries, near misses and equipment go on their own paper, right then, through the proper channel."
    },
    {
      "name": "Not turnover or acceptance",
      "sub": "Signing that you were told isn't accepting the work, releasing anybody, or agreeing it's done."
    }
  ],
  /* THE CLASSIFICATIONS. TENDER is on this list and it is not a courtesy — he is
     a classification on the crew, not a helper and not an apprentice, and a tag
     that cannot name him cannot count the man who actually stood. */
  "classes": [
    "— class",
    "JOURNEYMAN",
    "APPRENTICE",
    "FOREMAN",
    "TENDER",
    "OPERATOR"
  ],
  "pics": [
    {
      "v": "In this message — shot before we laid past it"
    },
    {
      "v": "None"
    }
  ]
};

/* ── BEFORE IT GOES UP (shape #3 — shared/rowlog.js) ───────────────────────
 * THE ASK HALF OF THE BOUNDARY, and the honest note about this trade: it is
 * receiver-heavy and ask-light. A mason is chased by everybody and chases
 * comparatively few people back. So this list is deliberately shorter than
 * concrete's fourteen, and every rung on it is a thing that actually stops a
 * crew from getting on a wall — not a rung invented to match another kit's
 * length. The milestones are COURSES AND LIFTS, which is the whole difference
 * between this kit and its siblings.
 */
window.TOOLKIT_ROUGHIN = {
  toolName: "Before It Goes Up",
  eyebrow: "Masonry · you → everybody who owes you something in this wall",
  lede: "Everything that has to be marked, delivered, moved or decided before you get on the wall — and before you cap it. Who owes it, where it is, and the course it has to beat. One walk, one message each.",
  docSubject: "Before it goes up — what I need out of your trade",
  docSubjectWith: "Before it goes up — what I need from {to}",
  closing: "That's my list for this wall. If a line on here is wrong, or you've got something going in it that I didn't put on the list, hit me back today and we'll walk it — I can build anything in as I lay, and none of it after we grout.",
  warn: "<b>Double-check it before you send it.</b> Every line on here is what <i>you</i> picked off <i>your</i> set. This page sizes nothing, specs nothing and locates nothing &mdash; no bar size, no lap, no cover, no bearing length, no joint spacing, no mortar type, no bracing &mdash; and it doesn't know what the structural drawings, the approved submittals, the engineer of record or the AHJ require. Verify all of it against your own approved set. It's an ask, not an approved detail, and <b>nothing on it authorizes anybody to do extra work.</b>",
  offHint: "The structural sheet, the wall section and its revision is the whole argument — naming what you took it off is the difference between a request the other foreman works to and one he re-walks with you the morning of the lift.",
  phJob: "Riverside MOB",
  phOff: "S-301 rev 2",
  phFrom: "Dave K — Kerrigan Masonry",
  phArea: "East elevation, grid 4 to 9",
  areaLabel: "Wall / elevation / gridline",
  who: [
    { v: "gc", label: "GC super" },
    { v: "elec", label: "Electrician" },
    { v: "plumb", label: "Plumber" },
    { v: "conc", label: "Concrete / footings" },
    { v: "rebar", label: "Rebar foreman" },
    { v: "steel", label: "Steel / misc metals" },
    { v: "hm", label: "Hollow metal / door supplier" },
    { v: "precast", label: "Precast / cut stone supplier" },
    { v: "survey", label: "Surveyor / layout" },
    { v: "framer", label: "Framer" },
    { v: "roofer", label: "Roofer" },
    { v: "yard", label: "Yard / material supplier" },
    { v: "owner", label: "Owner / homeowner" }
  ],
  /* THE LADDER IS COURSES, NOT DAYS. Two served kits already count down to
     rungs on this ladder in their own words — electrical's "Before CMU caps
     out" and plumbing's "Before block goes up". */
  milestones: [
    { v: "layout", label: "Before we lay out" },
    { v: "leads", label: "Before the leads go up" },
    { v: "firstlift", label: "Before the first lift" },
    { v: "bondbeam", label: "Before the bond beam" },
    { v: "headcourse", label: "Before the head course" },
    { v: "cmucap", label: "Before we cap out" },
    { v: "grout", label: "Before grout day" },
    { v: "veneer", label: "Before the veneer goes up" },
    { v: "stagedown", label: "Before the stage comes down" },
    { v: "wash", label: "Before we wash it down" }
  ],
  asks: [
    { v: "control", label: "Layout and a control line", who: "survey", by: "layout", specs: [
      "Give me the control line and the benchmark you want me working off, and tell me which set they came from.",
      "I need the face of the wall called out — face of block or face of finish. They are not the same line and the argument only shows up at the veneer.",
      "If the line moved on the last set, tell me before I chalk it, not after I have leads on it.",
      "Anything on this wall that is dimensioned to something not built yet, flag it now."
    ] },
    { v: "footing", label: "The footing and the top of it", who: "conc", by: "leads", specs: [
      "Footing at grade and clean before I set leads — I am not shimming a wall up out of a bird bath.",
      "Tell me where it is out, and by how much, before I find it with a story pole.",
      "Anything left on top of it — form stakes, snap ties, wire, mud — gone before we start.",
      "If there is a cold joint or a step I do not have on my set, walk it with me."
    ] },
    { v: "dowels", label: "Dowels where the cells are", who: "rebar", by: "leads", specs: [
      "The dowels have to land in a cell, not on a web and not out of the wall line.",
      "If they came up bent or out of place, tell me now — I am not the man who gets to decide what happens to a dowel.",
      "Tell me who is calling the engineer if any of them have to move, because it will not be me on my own.",
      "Call me the morning you are tying, and I will show you where my cells fall."
    ] },
    { v: "boxes", label: "Your boxes and stubs, marked on the wall", who: "elec", by: "firstlift", specs: [
      "Paint or keel your marks on the footing and on the line before I get off the ground.",
      "Tell me the height you want them at as a course, not a dimension I have to convert while I am on the stage.",
      "Tell me which cells you need left open above them and how far up — I will keep them open and out of the grout.",
      "Be here the morning of the lift they land on. I will build anything in as I lay it and none of it after.",
      "Anything that shows up after we cap out is a core bit through grout and steel, and on this wall that is a phone call to the engineer first."
    ] },
    { v: "sleeves", label: "Sleeves, chases and stacks", who: "plumb", by: "firstlift", specs: [
      "Mark the sleeve and I will lay it in as I go up — that is free, and cutting it in afterwards is not.",
      "If you need a chase, tell me before the leads go up so I can lay it out rather than break it in.",
      "Tell me which cells stay open and say it in writing before grout day. A nod at the mixer is not a record.",
      "Give me the course. A date does not help me and a height does not help you."
    ] },
    { v: "lintels", label: "Loose lintels and angle on site", who: "steel", by: "headcourse", specs: [
      "I need them on the ground at the wall before I reach the head course, not on a truck that ships that week.",
      "Tell me what is actually on the truck, by mark, and what is still at the shop.",
      "If one is short or the wrong mark, I need to know at the head course, not standing on the stage with a lift of block behind me.",
      "Tell me who is setting it and with what, because that changes what I need in the way."
    ] },
    { v: "embeds", label: "Embeds, plates and anchor bolts", who: "steel", by: "bondbeam", specs: [
      "Give me the locations off your approved set and I will build them in as I lay.",
      "Anything that has to be in the bond beam, I need before we get to that course — after it grouts it is not an adjustment.",
      "Tell me if you are welding to it, because that changes what I leave open around it.",
      "If a location on your set does not agree with mine, we settle it before the lift, not on it."
    ] },
    { v: "frames", label: "Hollow metal frames on site", who: "hm", by: "headcourse", specs: [
      "Frames on site and staged before I reach that opening. I cannot lay past an opening that is not there.",
      "Tell me what is actually delivered by mark — 'it ships Friday' is not a frame on the ground.",
      "Who is setting them and bracing them, and when — if it is us, I need that on paper before we build them in.",
      "Any frame with a hardware prep I have to work around, tell me at the head course, not at the jamb."
    ] },
    { v: "precast", label: "Sills, caps, coping and cut stone", who: "precast", by: "cmucap", specs: [
      "On site and staged where the crane or the forklift can reach it before we cap out.",
      "Tell me what came damaged and what is short — I would rather lose a piece off the ground than off the top course.",
      "Tell me the piece marks and where they land, because the truck never comes marked the way the drawing is.",
      "If anything got substituted, I need it standing next to the panel before it goes on the wall."
    ] },
    { v: "access", label: "Access, hoisting and where the cube lands", who: "gc", by: "layout", specs: [
      "Tell me where I can set cubes and boards and where the truck comes in — say the elevation and the side.",
      "Say forks or boom, because a cube dropped wherever the truck stopped is a day of a tender's life moving it.",
      "Tell me who else is working under or over us that week so we are not both there.",
      "I need water I can reach and somewhere to put the mixer that is not moving every day."
    ] },
    { v: "stage", label: "The stage, and who moves it", who: "gc", by: "firstlift", specs: [
      "Tell me who is erecting it, who inspects it, and who is allowed to alter it once it is up.",
      "Nobody takes a plank, a tie or a brace off it but the man who owns that call.",
      "If another trade needs an aisle through it, that comes to me first and not to whoever is nearest.",
      "Tell me when you want it down, because everything I still owe on that wall has to happen before it goes."
    ] },
    { v: "panel", label: "The panel signed off", who: "gc", by: "layout", specs: [
      "I want everybody who gets a vote standing at the panel in daylight, once, before we start the job.",
      "Colour, blend, joint profile and how it gets cleaned — settle all of it there.",
      "Whatever is agreed, it stays up and it stays protected for the length of the job. It is the only thing anybody can point at later.",
      "If it is signed off, say who signed it and when, and send it to me in writing."
    ] },
    { v: "throughwall", label: "Flashing, weeps and who ties into what", who: "roofer", by: "veneer", specs: [
      "Tell me where your work stops and mine starts, and who laps over whom.",
      "Anything terminating into my wall, I need to know at what course before the veneer goes up in front of it.",
      "If it has to be sequenced with your crew on site, tell me which week, because it is a one-shot on a scaffold.",
      "Send me a photo of your side of the detail before we cover it. That is the only look anybody gets."
    ] },
    { v: "groutday", label: "Grout day and who else has to be done", who: "gc", by: "grout", specs: [
      "Everybody with something going in this wall has to be done and off it before we grout — say it to them, not to me.",
      "Tell me who is calling the inspection and when, so I am not the one who finds out that morning.",
      "I need access for the truck or the pump and somewhere it can wash out that you are okay with.",
      "Once it is grouted, every one of their asks is a core bit through grout and rebar. Say that out loud at the huddle."
    ] }
  ]
};

/* ── WHAT I'LL BUILD IN (shape #3 — the RETURN LEG) ────────────────────────
 * The mirror. Two served kits ship a page that sends this crew a list; this is
 * the page he answers it on. The one field that makes it this trade's rather
 * than a reskin is the WHEN: a yes on this document carries a COURSE.
 */
window.TOOLKIT_ANSWER = {
  toolName: "What I'll Build In",
  eyebrow: "Masonry · them → you → back",
  lede: "The electrician or the plumber sent you a list of what has to be in this wall — boxes, sleeves, stubs, embeds, a marked-up plan typed out. Line it up, give each one a yes, a no or a question, and put the COURSE on every yes. Then send back one answer he can work to.",
  docSubject: "what I'll build in",
  closing: "That's the yes, the no, and the course. Anything I flagged I need a location or a height on before we get to it — I can build any of it in as I lay, and none of it after we grout. Tell me the course and I'll build it in.",
  phJob: "Riverside MOB",
  phTo: "Danny — EC foreman",
  phFrom: "Dave K — Kerrigan Masonry",
  phOff: "E-201 rev 4",
  paste: "Riverside MOB — east elevation CMU — Aug 14\n\nJob: Riverside MOB\nFrom: Danny — EC foreman\n\nGrid 5 · 2 boxes at switch height, marked in orange on the footing\nGrid 4 to 9 · conduit up the cell from each box — leave those cells open\nGrid 7 · pull box above the door, needs the cell open above it\nGrid 9 · don't grout the cell at the corner, our feed comes up it"
};

/* ── WHERE THE WALL'S AT (shape #3 — the pinned tool) ──────────────────────
 * THE ONE DOCUMENT ON THIS JOB NOBODY ELSE CAN WRITE. electrical/items.js and
 * plumbing/items.js have been telling two other trades to count down to "Before
 * CMU caps out" and "Before block goes up" since those kits shipped, and
 * nothing anywhere publishes the number they are counting to. This does.
 *
 * THE INVERSE-CLAIM GUARD is the one genuinely new thing on this page. A list
 * that names the walls nobody may touch will be read as clearing the walls it
 * did not name. So the `touch` axis has NO "it's fine" value — a blank means he
 * said nothing — and the document footer says so in words that are not
 * configurable from here.
 */
window.TOOLKIT_WALLSTATE = {
  toolName: "Where The Wall's At",
  eyebrow: "Masonry · you → the super, the EC and the plumber",
  lede: "Wall by wall at quitting time: the course it got to, what's holding it, and what nobody touches. Tap each wall up the ladder and send one message. Two other trades have been counting down to your cap out for months — this is the first page that gives them the number.",
  docSubject: "where the wall's at",

  /* THE LADDER. Build order, and it does NOT wrap: a wall does not go back to
     not-laid-out, and the pencil sheet is the correction path. "Struck and
     pointed" sits AFTER grouted on purpose — it is not the thumbprint tooling
     he does as he lays, which is continuous and is not a milestone. */
  states: [
    { v: "notout", label: "Not laid out" },
    { v: "laidout", label: "Laid out" },
    { v: "leads", label: "Leads up" },
    { v: "onwall", label: "On the wall" },
    { v: "capped", label: "Capped out" },
    { v: "grouted", label: "Grouted" },
    { v: "pointed", label: "Struck and pointed" },
    { v: "washed", label: "Washed down" },
    { v: "off", label: "Off it" }
  ],
  /* OPEN CELLS runs from LEADS UP to short of GROUTED — there is wall standing
     and its cells are not all full. That is what the EC and the plumber are
     actually racing, and it is declared here ONCE, by value, so the header
     count, the filter and the footer call-out can never disagree. */
  openFrom: "leads",
  openTo: "grouted",

  holds: [
    { v: "going", label: "Nothing — we're going" },
    { v: "material", label: "Material short at the yard" },
    { v: "mud", label: "Mud, sand or cement" },
    { v: "frames", label: "Hollow metal frames" },
    { v: "lintels", label: "Loose lintels or angle" },
    { v: "precast", label: "Precast — sills, caps, coping" },
    { v: "embeds", label: "Embeds, plates or anchor bolts" },
    { v: "roughin", label: "Another trade's rough-in" },
    { v: "footing", label: "The footing or the dowels" },
    { v: "dim", label: "A dimension nobody's answered" },
    { v: "layout", label: "Layout or a control line" },
    { v: "access", label: "Access, hoisting or the stage" },
    { v: "grout", label: "The pump / grout day" },
    { v: "weather", label: "Weather" },
    { v: "men", label: "Manpower" },
    { v: "panel", label: "Panel not signed off" }
  ],

  /* WHAT NOBODY TOUCHES. Every value is a NOTICE WITH A HANDBACK and not one of
     them is a dimension, a spacing, a height, a wind figure, a duration or a
     permission. THERE IS DELIBERATELY NO "it's fine" VALUE ON THIS AXIS — if a
     later cycle adds one, that is the defect this page was designed around and
     not a tidy-up. */
  touches: [
    { v: "green", label: "Green — don't load it" },
    { v: "backfill", label: "Don't backfill against it" },
    { v: "stack", label: "Don't stack against it" },
    { v: "hang", label: "Nothing hangs off it" },
    { v: "brace", label: "Not braced yet, come see me" },
    { v: "ours", label: "Braces are ours, call before anybody moves one" },
    { v: "cells", label: "Cells still open above my line" },
    { v: "stage", label: "Leave the stage where it is" },
    { v: "cut", label: "Don't cut it, call me first" }
  ],

  nexts: [
    { v: "up", label: "Carry on up" },
    { v: "grout", label: "Grout it next" },
    { v: "cap", label: "Cap it out" },
    { v: "point", label: "Strike, tool and point up" },
    { v: "wash", label: "Wash it down" },
    { v: "trade", label: "Waiting on another trade" },
    { v: "mat", label: "Waiting on material" },
    { v: "none", label: "Nothing on it tomorrow" }
  ],

  flags: ["Come see me on this one", "Nobody goes near it"],

  phJob: "Building B",
  phFrom: "Dave — Kerrigan Masonry",
  phNum: "(503) 555-0147",
  phWall: "Grid C 4 to 9",
  phCourse: "the way you'd say it out loud",
  phNote: "anything the man reading this at seven in the morning needs",

  closing: "That's where the wall got to today, in my words. Anything listed as held is stopped on somebody else — ring me and I'll give you the course it stops at, because a date doesn't help a man whose wall is at four foot and whose box is at ten.",
  cells: "Anything that has to be in one of those walls — a box, a stub, a sleeve, an anchor — tell me the course and tell me before we grout. After the grout it's a core bit through grout and rebar.",
  /* NOT CONFIGURABLE IN SPIRIT: the second sentence is the inverse-claim guard
     and the third is the money/quantity refusal. Both print on every document. */
  warn: "<b>Nothing on this page braces a wall, rates a wall, or says a wall is safe to load, to backfill against or to work under.</b> A wall not named here is a wall I have said nothing about. No count on it is a quantity in place, a percent complete or a price — the course is my own words about where the wall got to, and it is nobody's pay application."
};

/* ── GETTING IN (shape #2) ─────────────────────────────────────────────────
 * The one boundary in the program where the receiver is not another trade, and
 * the only one where being wrong leaves a crew and a load standing at a locked
 * gate. Every heads-up option ends in a QUESTION aimed back at whoever owns the
 * process — they are handbacks, not statuses. If a later cycle rewrites one
 * into "hot work permit obtained", that is the defect, not a tidy-up.
 */
window.TOOLKIT_GETIN = {
  toolName: "Getting In",
  eyebrow: "Masonry · you → whoever holds the keys",
  lede: "You need a boom truck, a lift of block and a stage onto a property somebody else locks — and then you need them to stay there for a fortnight. Send the ask that gets a yes before the yard loads it: the route in, where the cubes land, who's coming, and the heads-up that keeps a truck sitting at a gate with a full load on the forks.",
  docName: "ACCESS REQUEST",

  run: [
    { v: "Just that day" },
    { v: "A couple of days" },
    { v: "Nights all week" },
    { v: "Ongoing — I'll flag changes" }
  ],

  need: [
    { name: "Gate unlocked", sub: "nobody has to stay" },
    { name: "Somebody to let us in", sub: "meet us, open it, done" },
    { name: "An escort the whole time" },
    { name: "Badges at the desk", sub: "for the names below" },
    { name: "The route in", sub: "wide enough for a boom truck, clear overhead for the forks" },
    { name: "Where the cubes land", sub: "somewhere they can sit for the length of the job, on the right side of the building" },
    { name: "Room for the mixer and the boards", sub: "and somewhere the sand pile can stay put" },
    { name: "Water on site", sub: "a spigot or a hose bib we can reach" },
    { name: "The stage stays up", sub: "tell me now if anything has to come through where it goes" },
    { name: "Somewhere to wash out", sub: "a spot you're okay with, and who hauls it off" },
    { name: "Nobody there — we'll lock up behind us" },
    { name: "Us off the alarm for the window", sub: "a truck and a lift moving in before anyone's normally there" },
    { name: "Tell me who gets our COI", sub: "if it isn't already on file" }
  ],

  heads: [
    { name: "It'll be loud", sub: "a mixer, a saw and a truck on the forks — say the word and we'll move the window" },
    { name: "Cutting and grinding makes dust", sub: "we run it wet or on a vac — tell me what barrier you want up and where your intakes are" },
    { name: "A truck and a lift staging early", sub: "before your gate's normally open — tell me if that's a problem" },
    { name: "The stage goes up and stays up", sub: "it blocks whatever it stands in front of for the length of the job — tell me what has to stay reachable" },
    { name: "We're washing the wall down at the end", sub: "water runs where the ground takes it — tell me what's below and what you want protected" },
    { name: "There'll be a wall standing that isn't finished", sub: "nobody loads it, backfills against it or works under it without asking me first — who do you want that told to?" },
    { name: "We might set off the alarm", sub: "a truck and gear moving near the doors — who puts it on test? We don't" },
    { name: "We may need a sprinkler head or a detector covered", sub: "who does that and takes it off after? It isn't us" },
    { name: "There may be hot work", sub: "cutting or grinding near anything that watches for it — tell me who issues that and how you want it run" },
    { name: "Something may need powering down", sub: "tell me who owns that switch and what notice they need" },
    { name: "We'll be in and out of a public way", sub: "tell me who owns the closure and the permit for it — that's yours to number, not ours" }
  ],

  phSite: "Bishop Ranch 3",
  phRoom: "East elevation, grid 4 to 9",
  phHow: "south gate, past the loading dock, forks come round the back",
  phScope: "laying the east elevation CMU — stage up, cubes on the ground",
  phLoud: "mixer and saw from 7am, done mid-afternoon",
  phTo: "Ray — property manager",
  phMe: "Dave K — 503-555-0147",
  phCo: "Kerrigan Masonry",

  closing: [
    "This is an ask, not a booking — nobody rolls until you reply. Wrong day? Tell me which one works and we'll take it.",
    "Saying yes: tell me the window you're actually giving us and who's meeting us — and if nobody is, how we get in and how we lock up behind us."
  ],

  warn: "<b>It's a request, not a permit and not a booking.</b> Anything on the heads-up list that needs a permit, a panel on test, a fire watch or a lane closure is theirs to issue and theirs to number — this page just tells them it's coming and asks how they want it run. And check your contract before you send it: plenty of them say you don't talk to the building direct. If yours does, send this to your GC and let him forward it — same words, right chain."
};


/* ── THE YARD CALL (shape #1 — shared/checklist-request.js) ────────────────
 * The vocabulary for yard-call.html, and the rung `masonry/tools.js` shipped
 * naming as the one it was deliberately not building yet. Three independent
 * in-trade panels named the afternoon call to the supply house unprompted; the
 * 20-year prune kept it first. Its own registry comment states the bar it has to
 * clear: "a man who calls in an order off a list that is missing a line stops
 * opening the list."
 *
 *  · THE UNIT OF ISSUE IS THE LINE, not a modifier on it. Block leaves the yard
 *    by the CUBE, mortar by the BAG, sand by the YARD, wire by the ROLL, brick by
 *    the strap, lintels each. "6 block" and "6 cubes of block" are two different
 *    trucks. So every line carries the word the yard sells it in, and the page
 *    attaches that word to a bare number instead of asking him to pick a unit off
 *    a select — which is why the quantity is free text: he already says "six
 *    cube", "a pallet", "half a yard", and a spinner is a desk person's idea of
 *    how a load is counted.
 *  · THE DROP IS ONLY ON WHAT THE FORKS CARRY. Framing puts a drop on every line
 *    because a boom truck sets everything; here the boxed goods go in the gang
 *    box and the argument is about the heavy units — a cube set where the wall is
 *    going, or in the scaffold line, gets moved twice by the crew that was
 *    supposed to be laying.
 *  · THE RUN IS THE ONE THING A SECOND ORDER CANNOT GUESS. Face units come out of
 *    a run and the colour moves run to run. A re-order that does not name what is
 *    already up is how a wall gets a stripe nobody can wash off. It is a FLAG on
 *    the units it applies to and a passthrough field in the header — never a
 *    lookup, because we do not hold anybody's lot numbers.
 *  · NOTHING RATED, and this file's refusal list at the top governs every line
 *    below it. No mortar type as a value (he states it), no proportion, no bar
 *    size or lap, no lintel bearing, no wire or tie spacing, no lift height, no
 *    cold-weather number, no brand as a thing to write down. Where a spec decides
 *    it, the line says so and holds an empty box.
 */
(function () {
  "use strict";
  /* §THE NEUTRAL — every axis leads with one, written as the QUESTION, and the
   * page drops any value starting with an em-dash. A pre-selected default would
   * be the tool choosing for him; a printed value nobody picked would be the tool
   * putting words in his message. */
  function n(q) { return "— " + q + " —"; }
  function ax(label, opts, wide) {
    return { k: label.toLowerCase().replace(/[^a-z]+/g, ""), label: label, opts: opts, wide: !!wide };
  }
  /* WHERE THE FORKS SET IT. Not a floor — a mason works off the ground and up a
   * stage, so the question is which elevation and how close to the wall. "Not in
   * the scaffold line" is the one every layer has had to say out loud. */
  var DROPS = ["North side", "South side", "East side", "West side",
               "At the leads", "Behind the wall — clear of the scaffold line",
               "By the mixer", "Laydown / yard", "Inside the building", "Split it — see the note"];
  function drop() { return ax("Set it", [n("which side")].concat(DROPS), true); }
  /* Nominal WIDTH is the wall he is already laying, off his own set. It is not a
   * rating, a spacing or a strength, and it is the first thing the yard asks. */
  function width(q) { return ax("Width", [n(q || "which width")].concat(["4 in", "6 in", "8 in", "10 in", "12 in", "Two widths — see the note"])); }
  /* The one flag that repeats: this has to match what is already standing. */
  function matchRun() { return [{ k: "run", label: "Has to match what's already up" }]; }

  window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};

  window.TOOLKIT_ITEMS.yard = {
    drops: DROPS,

    cats: [
      {
        id: "call",
        name: "What are you calling in?",
        docName: "The call",
        hint: "Paste your whole list if you keep one — one line each. Count it the way you say it: 6 cube, a pallet, 4 yard, 2 roll. Then set the heavy stuff below.",
        writein: true,
        items: []
      },

      {
        id: "block",
        name: "Block",
        docName: "Block",
        hint: "By the CUBE. Say the shape — a cube of stretcher where you needed bond beam is a course you can't close.",
        items: [
          { n: "Stretcher", sub: "THE STANDARD UNIT — BY THE CUBE", unit: "cube",
            ax: [width(), drop()] },
          { n: "Half block", sub: "BY THE CUBE — RUN THE BOND OUT AND YOU'RE CUTTING ALL DAY", unit: "cube",
            ax: [width(), drop()] },
          { n: "Bond beam / knockout", sub: "BY THE CUBE — SAY IF YOU WANT THEM KNOCKED OR SOLID-BOTTOM", unit: "cube",
            ax: [width(), drop()] },
          { n: "Lintel block", sub: "BY THE CUBE", unit: "cube",
            ax: [width(), drop()] },
          { n: "Open-end / A-block", sub: "BY THE CUBE — THE ONE THAT DROPS AROUND THE BAR", unit: "cube",
            ax: [width(), drop()] },
          { n: "Sash / jamb block", sub: "BY THE CUBE — SAY WHICH FRAME IT'S GOING AROUND", unit: "cube",
            ax: [width(), drop()] },
          { n: "Bullnose", sub: "BY THE CUBE — SAY SINGLE OR DOUBLE, AND WHICH CORNER", unit: "cube",
            ax: [width(), drop()] },
          /* THE FIRST LINE OF A REAL TAKEOFF, AND THE FIRST DRAFT SHIPPED WITHOUT
             IT. An in-trade read found ten shapes and no corner: every building
             has them, a stretcher cannot run into a 90 and come out with a
             finished end, and a list missing the line a man orders first is the
             list he stops opening (§THE YARD CALL's own bar). */
          { n: "Corner / end block", sub: "BY THE CUBE — THE FINISHED END, FOR CORNERS AND WHERE THE WALL STOPS", unit: "cube",
            ax: [width(), drop()] },
          { n: "Pilaster block", sub: "BY THE CUBE — SAY WHICH ONE OFF YOUR SET", unit: "cube",
            ax: [width(), drop()] },
          { n: "Cap / solid top", sub: "BY THE CUBE", unit: "cube",
            ax: [width(), drop()] },
          { n: "Solid", sub: "BY THE CUBE", unit: "cube",
            ax: [width(), drop()] }
          /* HEADER BLOCK WAS HERE AND WAS CUT, not for safety and not for
             clutter: it keys a brick header course into block backup, which
             veneer ties replaced across this trade decades ago. Shipping it while
             the CORNER was missing had the list exactly backwards. */
        ]
      },

      {
        id: "face",
        name: "Face units",
        docName: "Face units",
        hint: "Anything that stays visible. Tick MATCH on every line that has to line up with what's already standing, and put the run in the header — colour moves run to run and a stripe doesn't wash off.",
        items: [
          { n: "Brick", sub: "BY THE CUBE — SAY IF YOU WANT STRAPS, AND THE SIZE AND COLOUR OFF YOUR SUBMITTAL", unit: "cube",
            flags: matchRun(), notePlaceholder: "size, colour and blend off the approved submittal — and the run if you've got the ticket",
            ax: [drop()] },
          { n: "Split-face", sub: "BY THE CUBE — SAY THE COLOUR AND WHICH FACES ARE SPLIT", unit: "cube",
            flags: matchRun(), notePlaceholder: "colour, and one face or two",
            ax: [width(), drop()] },
          { n: "Ground-face / burnished", sub: "BY THE CUBE — HANDLE IT LIKE GLASS", unit: "cube",
            flags: matchRun(), notePlaceholder: "colour, and say if you want it wrapped",
            ax: [width(), drop()] },
          { n: "Scored", sub: "BY THE CUBE — SAY HOW MANY SCORES", unit: "cube",
            flags: matchRun(), ax: [width(), drop()] },
          { n: "Ribbed / fluted", sub: "BY THE CUBE", unit: "cube",
            flags: matchRun(), ax: [width(), drop()] },
          /* GLAZED IS ITS OWN ORDER AND ITS OWN LEAD TIME, and it was missing
             entirely rather than folded into a neighbour — every school corridor,
             hospital and commercial kitchen runs it. */
          { n: "Glazed block", sub: "BY THE CUBE — SAY THE COLOUR AND WHICH FACES ARE GLAZED", unit: "cube",
            flags: matchRun(), notePlaceholder: "colour off the approved submittal, and one face or two",
            ax: [width(), drop()] },
          { n: "Cast stone / precast trim", sub: "EACH — SILLS, BANDS, CAPS, COPING", unit: "ea",
            flags: matchRun(), notePlaceholder: "which piece, and the length off the shop drawing",
            ax: [drop()] },
          { n: "Stone", sub: "SAY THE TON OR THE PALLET WITH THE COUNT — IT COMES BOTH WAYS",
            flags: matchRun(), notePlaceholder: "what it is, and full bed or veneer",
            ax: [drop()] }
        ]
      },

      {
        id: "mud",
        name: "Mud, sand & grout",
        docName: "Mud, sand & grout",
        hint: "The type is whatever your spec says — type it in, this page won't pick one for you. Sand by the yard. Nobody lays without all three of these.",
        items: [
          { n: "Mortar", sub: "BY THE BAG — SAY THE TYPE OFF YOUR SPEC", unit: "bag",
            notePlaceholder: "the type your spec calls for, in your words — this page doesn't pick one",
            ax: [drop()] },
          { n: "Portland", sub: "BY THE BAG", unit: "bag", ax: [drop()] },
          { n: "Lime", sub: "BY THE BAG", unit: "bag", ax: [drop()] },
          { n: "Coloured mortar", sub: "BY THE BAG — THE COLOUR AND THE LOT BOTH MATTER", unit: "bag",
            flags: matchRun(), notePlaceholder: "colour and the lot already on the wall",
            ax: [drop()] },
          { n: "Sand", sub: "BY THE YARD — SAY IF IT'S GOING IN A PILE OR A BOX", unit: "yd",
            ax: [drop()] },
          /* THE SILO IS HOW MUD ARRIVES ON ANYTHING WITH REAL SQUARE FOOTAGE, and
             the first draft had bags and a portable mixer — which is a house, not
             a commercial job. Half the mud calls a foreman makes are a fill or a
             swap, and there was no line for either. */
          { n: "Silo — fill or swap", sub: "SAY WHICH, AND WHAT'S IN IT NOW",
            notePlaceholder: "fill it, swap it, or pick it up — and the type off your spec",
            ax: [drop()] },
          { n: "Grout — bagged", sub: "BY THE BAG", unit: "bag", ax: [drop()] },
          { n: "Grout — by the truck", sub: "BY THE YARD — SAY THE TIME YOU WANT IT ON SITE", unit: "yd",
            notePlaceholder: "what time, and where he sets up — mix is off your spec, not off this page",
            ax: [drop()] },
          { n: "Admixture", sub: "ONLY THE ONE YOUR SPEC ALLOWS — NAME IT, THIS PAGE WON'T",
            notePlaceholder: "which one your spec allows, and how much is the spec's call — not this page's" },
          { n: "Water — tank or buffalo", sub: "IF THERE'S NO BIB YOU CAN REACH", ax: [drop()] }
        ]
      },

      {
        id: "inwall",
        name: "What goes in the wall",
        docName: "What goes in the wall",
        hint: "Sizes, lengths and spacings come off your approved set — this page carries what you write and specs none of it.",
        items: [
          /* BUNDLE, NOT ROLL, and the first draft hedged in the sub-line ("by the
             roll or the bundle") while the code committed to the wrong one. This
             is welded 9-gauge in rigid straight lengths — coil it and the welds
             are gone. A hedge in the words is a tell that the data is a guess. */
          { n: "Joint reinforcement — ladder", sub: "BY THE BUNDLE", unit: "bundle",
            ax: [width("which wall"), drop()] },
          { n: "Joint reinforcement — truss", sub: "BY THE BUNDLE", unit: "bundle",
            ax: [width("which wall"), drop()] },
          { n: "Veneer ties / anchors", sub: "BY THE BOX", unit: "bx",
            notePlaceholder: "which type off your set — screw-on, dovetail, seismic, adjustable" },
          { n: "Rebar", sub: "SIZE AND LENGTH OFF YOUR SET — THIS PAGE WON'T SIZE IT",
            notePlaceholder: "size and length off your approved set, and how many of each" },
          { n: "Bar positioners", sub: "BY THE BOX", unit: "bx" },
          { n: "Lintels — steel angle", sub: "EACH — SIZE AND LENGTH OFF THE SCHEDULE", unit: "ea",
            notePlaceholder: "the size and length off your schedule — bearing is the engineer's, not this page's",
            ax: [drop()] },
          { n: "Lintels — precast", sub: "EACH — LENGTH OFF THE SCHEDULE", unit: "ea",
            notePlaceholder: "length off your schedule",
            ax: [drop()] },
          { n: "Thru-wall flashing", sub: "BY THE ROLL — THE MATERIAL IS ON YOUR SET", unit: "roll",
            notePlaceholder: "what the set calls for, and the width" },
          { n: "Weeps / vents", sub: "BY THE BOX", unit: "bx" },
          /* "MORTAR NET" WAS HERE AND IT IS A TRADEMARK — the same class as the
             LULL two sections down, caught in the same read. The joint
             reinforcement two lines up was de-branded to ladder/truss and this
             one was not, which is how a brand survives a de-branding pass. */
          { n: "Cavity drainage mat", sub: "BY THE ROLL", unit: "roll" },
          { n: "Control joint key", sub: "BY THE STICK", unit: "stick",
            notePlaceholder: "the profile off your set, and how long" },
          { n: "Grout screen / cleanout covers", sub: "BY THE BOX OR THE BUNDLE — SAY WHICH", 
            notePlaceholder: "which size, off your set" },
          { n: "Insulation — cell fill or board", sub: "SAY WHICH AND HOW MUCH",
            notePlaceholder: "which one your set calls for", ax: [drop()] },
          { n: "Embeds, sleeves, bolts", sub: "SOMEBODY ELSE'S PIECE THAT GOES IN YOUR WALL",
            notePlaceholder: "what it is, whose it is, and who's bringing it" }
        ]
      },

      {
        id: "tender",
        name: "What the tender needs",
        docName: "What the tender needs",
        hint: "Half a yard call is the half nobody writes down. Mud with nothing to mix it in is a morning gone.",
        items: [
          { n: "Mixer", sub: "AND THE FUEL FOR IT — SAY IF YOU NEED IT DELIVERED OR YOU'RE PICKING IT UP",
            ax: [drop()] },
          // "THE LULL" was here in the first draft, in the one file whose own
          // header names that trademark as forbidden — a word people SAY is not a
          // word we PRINT, because printing it puts it on somebody's order.
          { n: "Fuel / propane", sub: "FOR THE MIXER, THE SAW, THE TELEHANDLER" },
          { n: "Mortar boards / pans", sub: "HOW MANY BOARDS", unit: "ea" },
          { n: "Tubs & buckets", sub: "HOW MANY", unit: "ea" },
          { n: "Wheelbarrows", sub: "", unit: "ea" },
          { n: "Shovels, hoes, brushes", sub: "HOW MANY OF EACH" },
          { n: "Scaffold frames & braces", sub: "BY THE SET — YOUR COMPETENT PERSON BUILDS IT, THIS PAGE JUST ORDERS IT", unit: "set",
            notePlaceholder: "how many sets, and how high you're going",
            ax: [drop()] },
          { n: "Plank", sub: "BY THE PIECE — SAY THE LENGTH", unit: "ea", ax: [drop()] },
          { n: "Screw jacks, base plates, guardrail", sub: "COUNTS ONLY", ax: [drop()] },
          { n: "Saw + blades", sub: "SAY WET OR DRY — AND IF IT'S WET, WHO'S BRINGING THE WATER",
            notePlaceholder: "wet or dry, and blade size", ax: [drop()] },
          { n: "Line, blocks, twigs, corner poles", sub: "AND SPARE LINE" },
          { n: "Chalk, pencils, string", sub: "" },
          { n: "Masonry cleaner", sub: "THE ONE YOUR SPEC ALLOWS — NAME IT, THIS PAGE WON'T",
            notePlaceholder: "the one the spec and the unit manufacturer both allow — the wrong cleaner is a warranty argument" },
          { n: "Poly / tarps", sub: "COVER THE TOP OF THE WALL BEFORE YOU LEAVE", ax: [drop()] },
          { n: "Heaters / blankets", sub: "COUNTS ONLY — THE PROTECTION PLAN IS NOT ON THIS PAGE" }
        ]
      },

      {
        id: "forks",
        name: "The forklift, and what goes back",
        docName: "The forklift, and what goes back",
        hint: "The half of the call that's worth money and never gets made. Empties sitting on the job are a deposit you don't get back and a laydown you can't use.",
        items: [
          { n: "Forklift / telehandler", sub: "SAY WHEN YOU NEED IT AND HOW LONG YOU'RE KEEPING IT",
            notePlaceholder: "when it lands, when it leaves, and who's certified on it" },
          { n: "Take the empty cubes back", sub: "SAY ROUGHLY HOW MANY ARE STACKED", unit: "cube" },
          { n: "Take the leftover material back", sub: "SAY WHAT IT IS AND WHETHER IT'S BEEN RAINED ON" },
          { n: "Pick up the mixer / the scaffold", sub: "WHEN YOU'RE DONE WITH IT" }
        ]
      }
    ],

    /* A pasted line gets the same drop as a picked one — a write-in is where the
     * odd heavy item lands ("2 cube of 12 bond beam"), and it is the line most
     * likely to end up in the scaffold line if nobody says where it goes. */
    writeinAx: [drop()]
  };
})();
