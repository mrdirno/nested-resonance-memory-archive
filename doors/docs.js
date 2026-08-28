/* DOORS & HARDWARE FIELD TOOLKIT — THE WRITE-UP LIBRARY.
 *
 * Shape #4, the DOCS engine (shared/docspec.js). This file is not a form and
 * does not produce a document: it produces the INSTRUCTIONS a man pastes into
 * his own AI once, after which he dictates the mess at the tailgate and gets
 * back something the office can forward. Six documents written for this trade
 * join the shared library every kit inherits.
 *
 * WHAT THIS TRADE'S DOCUMENTS ARE NOT ALLOWED TO SAY, and the reason the
 * refusal list is repeated here rather than trusted to trade.js: this is the
 * one surface that emits FREE PROSE, so it is the one place a rule can be
 * broken without a field to break it in. Every `note` below carries its own
 * half of this, and a later cycle editing a document must carry it forward:
 *   - NO FIRE LABEL VALUE, ever — not a rating, not what a label permits, not
 *     whether a label is intact. A tag in front of him may be QUOTED; what the
 *     quote is worth belongs to the manufacturer and the authority having
 *     jurisdiction;
 *   - NO clearance, gap or undercut as a requirement — only what HIS tape read
 *     at that opening, named as his tape;
 *   - NO closer setting, opening force, or accessibility dimension;
 *   - NO hardware set CONTENTS and no door schedule — an opening number and a
 *     supplier line number ride as ADDRESSES so two people can point at the
 *     same door, and that is the whole of it;
 *   - NO KEYING OR BITTING INFORMATION, in any column, for any reason. The
 *     openings-walk document says so in its own note because that is the one
 *     place somebody would put it;
 *   - NO release verdict: no document here says an opening is complete,
 *     compliant, acceptable, or ready for anybody's inspection.
 * Every document records what HE saw, what HIS tape read, what HIS OWN
 * approved shop drawing, submittal, purchase order and bid scope say, and what
 * he did — and never says which one wins. The engine's two LOCKED toggles
 * ("never invent", "never judge a value") back this at the universal-law
 * level; the notes below carry the doors-specific edge the locks cannot see.
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
  /* "doors and hardware" is what the bid package, the schedule and the truck
     door all say. "We do doors and hardware work" reads wrong, so the emitted
     sentence takes the trade word without the tail: "we do door and hardware
     work". */
  "trade": "door and hardware",

  "docs": [
      {
        "id": "frames-set-wrong",
        "name": "Somebody Else Set My Frames",
        "aka": ["frames out of plumb can't hang", "frame set in wrong opening", "frames not per my shop drawings", "mason set my frames wrong", "wrong hand frame installed", "frame throat wrong size wall", "frames racked and twisted", "frame set before I got there", "hollow metal frames set crooked", "who set these frames"],
        "family": "notice",
        "from": "the installer who has to hang to them",
        "to": "the GC super and our PM",
        "why": "A frame stops being adjustable the minute the grout goes in and the tape goes on. Once the mason fills it solid or the finisher wraps and floats the backbend, three-eighths of rack is no longer a shim job — it is demolition of somebody's finished wall, and the man who set it has rolled off to the next building. The leaves are already coming, factory-machined to a hand and a prep that assume the frame is where the drawing put it. If the out-of-plumb, the wrong hand and the wrong throat are not written down and dated while the frame can still be pulled, then the day the leaf won't close is the day it becomes the door hanger's problem, because he is the last man who touched it.",
        "note": "This is a measurement and a source, twice over: what his own level, tape and square read at the frame, and what his own approved frame elevation or shop drawing shows for that mark. It never says the frame is non-compliant, never says a label is void, damaged or intact, never states a rating or what a label permits, never quotes a required clearance, gap or undercut, and never sets out what anchors or fasteners should have been used — it can say what he found in the wall, and stop. The architect's schedule and the hardware consultant's sets stay theirs; the opening number appears only as an address so somebody can walk to it. Whether the frame is acceptable is the architect's and the GC's call. This document does not make that call — it only makes it possible to make, by putting numbers next to the frame before the grout hides them.",
        "omit": "THE READING, WHERE ON THE FRAME HE TOOK IT, AND THE DRAWING NUMBER SITTING BESIDE IT. Everybody writes \"the frames are out of plumb and the throats are wrong.\" Almost nobody writes \"6-foot level held on the hinge jamb at 212, plumb reads out 3/8 at the head and tight at the floor; tape across the throat at mid-height reads 5-1/8; my approved frame elevation, <sheet and revision in his hand>, shows this mark at 4-7/8 with hinges on the corridor side; the mason grouted it Tuesday.\" The first is a complaint about another man's workmanship, and the mason will say he set them plumb. The second is a dimension, a spot on the frame, and a stamped document with a date on it — and only one of the two is still standing after that argument.",
        "halt": "Only if he has not yet put a level and a tape on the frame — a frame that \"looks off\" is an argument, and ten minutes with a tool turns it into a notice. And if his own crew set the frames, this is not a notice against anybody: it is his own rework, and it belongs in the field log, not in the GC's inbox.",
        "facts": [
          "the openings by number, floor and grid, pinned so somebody can walk to each frame without him",
          "what his level, tape and square read, jamb by jamb, and where on the frame each reading was taken",
          "what his own approved frame elevation or shop drawing shows for that mark, named by sheet, revision and approval date",
          "how far the work has already closed over it — loose, anchored, grouted, wrapped, taped, primed, painted",
          "who set the frames and when, if he knows it, and how he found out",
          "which openings he is standing down on and what that stops downstream"
        ],
        "sections": [
          { "h": "Which openings, and how to find them",
            "r": "The opening numbers as they read on his own tags, cartons and field sheets, plus a second address anybody can follow — floor, grid, stair, and the name the crew actually uses (\"the pair off the east stair landing,\" \"the three on the corridor side of the break room\"), because a door number on a hollow-metal frame is very often written nowhere on the building. Say what each one is: single or pair, hollow metal or wood, welded or knock-down, and which side the crew calls the pull side. Photos listed by what each frame shows — head and floor both in the shot, the level in the picture with the bubble readable, and something fixed in frame such as a room sign, a stair number or a grid stripe — because a photograph of a bare frame in a bare corridor locates nothing at all." },
          { "h": "What I measured, jamb by jamb",
            "r": "Plumb on the hinge jamb and on the strike jamb, read at the head and at the floor, with the tool named — 6-foot level, 4-foot level, dot laser. Square across the head, and corner-to-corner diagonals on a pair. Throat measured at head, mid-height and floor, because a frame can be right at one and wrong at another. The face-to-wall relationship: frame proud of or shy of the finished board, by how much. Rack and twist: hold a straightedge across the two faces and write what it reads. Head height taken off the finished floor, or off the 4-foot control line if the floor isn't in — and say which one, because that single choice is where half of these arguments live. The hand and swing as actually set, in his words (hinges on the corridor side, swings into the room), and every number tied to the tool that produced it." },
          { "h": "What my drawing says, and where the drawing is",
            "r": "His own approved submittal quoted, not paraphrased: frame elevation, shop drawing, or his own field-measured order sheet, named by sheet number, revision and the date it came back approved, with the page attached and only the line that covers those marks — throat, size, hand. Say who stamped it and when. Not the architect's schedule and not the hardware consultant's set: the opening number is an address here, nothing more. If the field and his approved drawing disagree, that disagreement is now two documents standing next to each other instead of one man's opinion, and that is the entire point of the paragraph." },
          { "h": "What's already closed over it",
            "r": "The state of the frame at the hour he wrote this: shipping spreader still in the bottom or cut out, anchors in and what he can see of them, grout placed or not and on what date, board hung, corner bead on, taped and floated, primed, finish-painted, floor poured, tile set. This is the paragraph that decides whether the fix costs an hour or a wall, and it is the first paragraph memory throws away — six weeks later nobody can say whether the grout went in before or after he flagged it. If the mason filled it Tuesday and he found it Thursday, the write-up says Tuesday and it says Thursday." },
          { "h": "What I can't do until somebody answers",
            "r": "Which openings he is holding and which he is proceeding on, stated as a list of numbers rather than a floor. What the leaves are and where they are: factory-machined to a hand and a prep, delivered, tagged to those marks, sitting on a cart that is in somebody's way. What the hold does to the sequence behind him — hardware, closers, the undercut that waits on flooring, the painter who wanted frames done. Then a request for direction with a date on it, not a demand for a remedy: pulling and resetting a frame is somebody's money and somebody's call. If the direction that comes back is \"hang them anyway,\" stop writing this one and send the next document in the library instead." }
        ]
      },
      {
        "id": "hung-under-protest",
        "name": "You Told Me To Hang It",
        "aka": ["told to hang the door anyway", "directed to proceed door install", "hung under protest doors", "hang doors before floor goes in", "frame not grouted hang it anyway", "no power at electrified opening hang it", "install anyway letter doors", "hang it we'll fix it later", "hung doors under direction", "made me install doors early"],
        "family": "notice",
        "from": "the door hanger who flagged it",
        "to": "the GC super and our PM",
        "why": "The minute the leaf is on the hinges and the lock is bored, the opening reads as finished work with exactly one trade's name on it. Everything that made it wrong is still underneath and still invisible: the slab that has another inch of build-up coming, the frame that was never grouted and will move when it is, the raceway with no wire past the box, the wet mud on the jamb the painter will scrape off with a five-in-one. A bored door does not un-bore. In April, when the leaf drags on the new tile or the strike walks out of line or the mag lock has no power, nobody remembers there was a conversation about it in November — unless the conversation carries a date from before the leaf went up.",
        "note": "This records three things and nothing else: what he could still see, what his own tape read, and who told him to proceed, in their words. It never says the opening is non-conforming, never says a label is void or intact, never states a rating or what a label permits, never states a required clearance, gap, undercut, opening force or closer setting, never says whether the opening will pass anybody's inspection, and never calls an opening complete. The opening number is an address. Whether the installation is acceptable is precisely the question this document refuses to answer, and that refusal is what makes it hold up when somebody reads it out loud a year later.",
        "omit": "THE MEASUREMENT TAKEN AGAINST THE THING THAT ISN'T THERE YET. Everybody writes \"the floor wasn't in when they made us hang.\" Almost nobody writes \"my tape reads 1-1/2 from the bottom of the leaf to the bare slab at 118; the flooring foreman standing next to me, <name and company>, said his mud and tile are coming in around 3/4; I showed the super at 7:20 and was told to hang them and come back later.\" The first is a condition anybody can wave off. The second is his own number, a second number with a man's name attached to it, and a time — and the whole fight in April is about what the floor was going to add, which is exactly the number nobody thinks to write down while the slab is still bare.",
        "halt": "Only if there is no statement of who directed the work to proceed — without the direction this is just a condition report, and the frame notice and the lost-day write-up already exist for that. A note that says the floor wasn't in but never says who said go is a note that proves he knew and hung it anyway.",
        "facts": [
          "the openings by number, pinned so somebody can find them after the building is finished",
          "the condition, in the hanger's own words, while it could still be seen",
          "what his own tape read, and what the trade that owns the missing work said their work would add",
          "who directed the work to proceed, how, and the words they used",
          "exactly what was installed and what was deliberately held back",
          "the return work he can already see coming, named as return work"
        ],
        "sections": [
          { "h": "The openings, and what was still missing",
            "r": "Opening numbers plus an address a stranger can follow a year from now. Then the condition in plain hanger's words while it was still visible: bare slab with the tile stacked in the corridor, frame anchors dry and the grout crew two floors down, an electrified frame with a raceway and a box and nothing pulled past it, mud still soft on the backbend, the wall unprimed so the paint is coming after the hardware, ceiling grid not in where the closer arm has to live. Photos listed by what each frame shows, shot with something fixed in the picture — a room number, a stair sign, a grid stripe, the pallet tag — because a photograph of a bare frame in a bare corridor could be any floor of any building." },
          { "h": "What my tape read, and what the other trade told me",
            "r": "The measurements he took himself before anything went up, each with the tool named: bottom of the leaf to the slab, head height off the slab or off the 4-foot line, plumb on both jambs, throat, and the gap at the strike edge with the leaf held to. Then the second source: what the trade that owns the missing work says their work adds or changes, quoted with a name and a company — the flooring foreman's build-up, the electrician's date for pulling wire, the mason's grout schedule. Two numbers from two sources beat one man's opinion every single time. If he does not know the second number, he writes that he does not know it and who he asked; an honest gap is a fact, an invented number is a hole in the whole document." },
          { "h": "Who I told, and what came back",
            "r": "Who was shown or told, by name and company, when, and how — at the opening, by text, on the phone, in the morning huddle. The words that came back as close to verbatim as memory allows, quoted and never characterised: \"hang them, we're walking it Friday, come back after the floor\" is a quote with a promise inside it; \"he blew me off\" is an argument he will lose. If it came by text or email, say so and attach it, because the timestamp does work no memory can do. Note anybody else who was standing there — a witness with a company name beside it outweighs three more adjectives." },
          { "h": "What I did after that",
            "r": "Exactly what went in and exactly what was held: leaf hung with hardware still boxed, leaf hung and everything set, leaf machined in the field or arrived factory-machined, closers and thresholds deliberately left off, protective wrap left on, strike screws left loose, silencers in or out. Which openings this covers, by number, and which ones it does not. A note that covers \"the third floor\" is worth a fraction of a note that lists eight numbers, because in six months the argument will be about one opening, not about a floor." },
          { "h": "What I'll be back for",
            "r": "The return work he can already see from where he is standing: pulling leaves to trim after the floor covering goes down, resetting strikes once the frames are grouted and have moved, terminating at the frame when the wire finally shows, touching up hardware the painter is about to work around, rehanging after somebody else's finish. Write it as expected return work with the reason attached, not as a price — the ticket for the money is a different document in this library, and this note is the thing that makes that ticket believable when it lands three months from now." }
        ]
      },
      {
        "id": "delivery-came-up-short",
        "name": "The Truck Was Short",
        "aka": ["door delivery came up short", "hollow metal frames damaged in shipping", "wrong doors delivered to jobsite", "hardware missing from shipment", "short shipment doors claim", "freight damage door delivery", "supplier shipped wrong hand", "doors delivered wrong size", "concealed damage door cartons", "delivery ticket short doors"],
        "family": "incident",
        "from": "the installer who took the delivery",
        "to": "the distributor's inside man and our PM — and the carrier, if it happened on the truck",
        "why": "Two clocks start when the truck backs in, and neither one waits for him to get around to it. The driver leaves with the bill of lading, and a delivery signed clean makes the dent his dent. Then the replacement clock: a frame, a special-size leaf or a finish-matched piece is weeks out of the factory, not days, and that clock started the morning the material was supposed to be on site, not the morning somebody noticed it wasn't. Once the banding is cut and the cartons are spread across four floors and three storage rooms, nobody on earth can prove the missing leaf was never on the truck rather than walked off the job.",
        "note": "This is a count and a source: what physically came off the truck, counted and photographed against the packing list and against his own purchase order or approved submittal, both named. It does not reproduce the hardware consultant's sets or the architect's schedule — cartons are identified by opening number and by the supplier's own line number as printed on the tag, never by contents copied out of somebody else's document, and no keying information appears anywhere in it. It says nothing about fire ratings, nothing about what a label permits, and nothing about whether any label is intact or acceptable. If a label is gouged, painted over or missing, the document photographs it, names it as an observed condition and stops there, because what that condition means belongs to the manufacturer and the authority having jurisdiction, not to the man unloading a trailer at six in the morning.",
        "omit": "THE COUNT AT THE TAILGATE, WRITTEN ON THE PAPER THE DRIVER TAKES WITH HIM. Everybody writes \"the order came in short and a couple frames were beat up.\" Almost nobody writes \"counted 22 frames against 26 on packing list <number>, line 4; marks 214, 216, 218 and 220 were not on the truck; the crate for the pair at 101 had a crushed hinge jamb, photographed on the trailer before it came off; I wrote 'short 4 frames, 1 crate damaged, subject to inspection' on the delivery receipt and the driver signed it at 6:55 — his name and my copy are attached.\" One is a phone call nobody can find later. The other is a count, a document number and a signature from the only man in the story who cannot later say he wasn't there.",
        "halt": "Only if the material was never actually counted against a named document — a load he eyeballed at quitting time is a feeling, not a shortage, and sending it burns the credibility he is going to need on the next four trucks. Count it, photograph it, then write it. And if the shortage traces back to his own order, this stops being a claim and becomes a purchasing correction that goes to his PM alone.",
        "facts": [
          "the delivery itself: date, time, carrier, trailer or BOL number, packing list number, who signed and what he wrote on it",
          "the physical count against the packing list, line by line — what came, what didn't, what came that he never ordered",
          "what his own purchase order or approved submittal says was ordered, named by number and date",
          "the physical condition of what arrived, photographed on the truck where that was possible",
          "where the material is stacked now and how it is protected and secured",
          "the first date the schedule actually feels it, stated as a date"
        ],
        "sections": [
          { "h": "The truck, and the paper that came with it",
            "r": "Date, time on site, carrier, driver's name if he'll give it, trailer or BOL number, packing list number, and how the load was made up — crated, banded to skids, or loose stacked with blankets. Whether he had the men and the minutes to count before signing, and exactly what he wrote on the delivery receipt before the driver pulled the gate down: \"received short 4 frames, 1 crate damaged, subject to inspection\" is a fact with a signature under it, and \"I told the driver about it\" is not. If he signed clean because somebody told him to keep the truck moving, say who told him and when — that sentence is worth more than the rest of the page." },
          { "h": "What I counted, against what",
            "r": "The count line by line: opening marks and supplier line numbers exactly as printed on the cartons and tags, how many came, how many didn't, and anything that came which he never ordered. Wrong material described physically and measured with his own tape — a leaf 3'-0\" wide where his own order sheet says 2'-10\", a frame hinged on the wrong side for that opening, a finish that doesn't match what the order calls out, a knock-down where a welded frame was ordered. His own purchase order and his own approved submittal are the two documents he gets to hold up; the architect's schedule and anybody's hardware set stay out of it, and the opening number is only ever an address." },
          { "h": "What was broken, and what it looked like",
            "r": "Damage described by where it sits and how big it is: a dent in the face at the strike, a crushed corner at the head, rust bloom coming through the prime, a bowed or twisted leaf, a blown-out mortise, edge banding lifting, factory finish scratched through to metal. Say whether it was visible on the truck or found after the wrap came off, and say what day the wrap came off — damage photographed on the trailer and concealed damage found on day nine are two entirely different conversations with two different people paying. Photos with the mark tag and a tape laid in the shot so the size reads. Physical condition only; what any of it means for anything stamped on the material is not his call and does not appear here." },
          { "h": "Where it is now, and how it's covered",
            "r": "Where the good material is stacked — flat, off the deck, blocked, covered, indoors or under a tarp — and whether the damaged pieces have been pulled aside and marked so no one installs them by accident on a Friday afternoon. Who has access to that room and whether it locks, because the argument that always follows \"it came short\" is \"it came, and somebody on your crew moved it.\" If the supplier wants the damaged material back for a claim, say what he is holding, where it is, and how long he can keep it out of the way of everybody else's work." },
          { "h": "What it costs the schedule",
            "r": "The openings that cannot proceed, by number, and the crew days already sequenced against them. Whether there is a workaround and what the workaround actually costs him — hanging out of sequence, coming back to a finished floor a second time, leaving hardware off and making a third trip, remobilising a two-man crew for eight openings. The replacement ship date, who gave it to him and on what day. Then the first date the general schedule genuinely feels it, written as a date rather than as \"this is going to set us back.\" Ask for the ship date and the tracking in writing, and let the paper argue it later so he doesn't have to." }
        ]
      },
      {
        "id": "not-in-my-number",
        "name": "That Wasn't In My Number",
        "aka": ["extra work doors not in contract", "door hardware change order narrative", "scope not in my bid doors", "added openings extra cost", "field change doors extra", "cor narrative doors and frames", "out of scope frame work", "t and m ticket door install", "rework not in my scope doors", "who is paying for these doors"],
        "family": "notice",
        "from": "the installer who found it in the field",
        "to": "our PM — and through him, the GC's project manager",
        "why": "Extra work on an opening disappears into the opening. A leaf machined twice, a frame pulled and reset, a strike moved and the first mortise filled and dressed — once the paint dries every one of them looks exactly like an opening that was in the bid. There is no photograph of a labor hour, and there is no way to un-hang a door to prove it was hung twice. Worse, work performed without a word in writing reads to everybody downstream as work that was always included, which is why the narrative has to be written while the old prep is still open, the shims are still on the floor and the two men who did it are still standing in the corridor.",
        "note": "This narrates work and cause. It quotes his own bid scope, exclusion list or approved submittal for what was included, named by document and date, and describes what the field actually required in physical terms — never the architect's schedule, never a hardware consultant's set contents, never keying of any kind. It never argues that the original design was wrong, unsafe or non-compliant, and it never leans on a rating, a required clearance, an undercut, an opening force or a closer setting as the reason the work grew. It says what showed up, who directed it, what the crew did about it, and what it took in men, hours and material. The entitlement argument belongs to the PM and to the contract; this document exists so that he has one to make.",
        "omit": "THE ORIGINAL SCOPE LINE, QUOTED, SITTING RIGHT NEXT TO WHAT HE ACTUALLY DID. Everybody writes \"this is extra, it wasn't in my bid.\" Almost nobody writes \"my proposal dated <date>, scope line 4, reads 'furnish and install frames and leaves at the openings shown on the <date> bid set — 84 openings'; the bulletin dated <date> added openings 341 through 348; my crew set 8 frames and hung 8 leaves on the 6th and 7th, two men, fourteen hours, and here are the two daily reports with both men's names on them.\" The first is a position, and positions get negotiated to nothing. The second is a document, a date, a delta and two men's hours, and there is nothing in it left to negotiate.",
        "halt": "Only if he cannot name the document that says what was included — a claim that opens with \"it wasn't in my number\" and never produces the number is a mood, and it teaches the PM to discount the next one that is real. And if the work has already been directed in writing and priced, this is no longer a narrative: it is an invoice, and it goes out as one.",
        "facts": [
          "the openings affected, by number, and where they are in the building",
          "what his own bid or approved submittal says was included, quoted, with document name and date",
          "what the field actually required, described physically and measured with his own tape",
          "what changed it — a bulletin, an RFI answer, a revised submittal, a field direction, or a condition nobody drew",
          "what the crew actually did: names, dates, hours, opening by opening, and the material consumed",
          "what is still ahead of him because of it, and what he needs decided before he does any more"
        ],
        "sections": [
          { "h": "What I was carrying",
            "r": "The exact language he priced, quoted out of his own proposal, scope letter, exclusion list or approved submittal, with the document name, revision and date, and the plan set it was priced from named by issue date. Include the exclusions he wrote, word for word — the \"by others\" lines are where this argument usually lives, and the exclusion nobody reads is worth more than the inclusion everybody does. Attach the page rather than paraphrasing it; a scope line retyped from memory in the office is the first thing a PM on the other side will take apart." },
          { "h": "What was actually there",
            "r": "The field condition in physical terms, measured with his own tape and the tool named: a masonry opening a half inch narrow at the head; a frame welded for one throat standing in a wall that framed out deeper; an existing frame that has to come out rather than get reused; an opening drawn as a single and built as a pair; leaves that arrived factory-prepped for one lock function and openings that now take another; a wall that never got framed at the opening at all. Describe what he found, not what somebody should have done — the moment the paragraph turns into an accusation it stops being evidence and starts being a fight." },
          { "h": "Who changed it, and how I found out",
            "r": "The instrument, if there is one: bulletin, supplemental drawing, RFI answer or revised submittal, named by number and date. Or the person, if it came across a corridor: name, company, time, and the words quoted. If nothing was formally changed and the condition simply existed in the building, say that plainly — a differing site condition is a real category and it does not need a villain to be true. Say when he first knew, because the gap between the day he knew and the day he wrote is the first thing anybody attacks, and a short honest gap beats a long unexplained one." },
          { "h": "What the crew actually did",
            "r": "Men by name, dates, hours, opening by opening: set 8 frames, hung 8 leaves, field-machined 6 leaves for a changed function, filled and dressed 6 abandoned preps, pulled and reset 3 frames, made two trips to a floor that was sequenced for one. Then the material burned: frames, leaves, filler and reinforcing plates, shims, grout, anchors, screws, blades, bits, touch-up. Tie every line to a daily report, a timesheet or a T&M ticket that already exists with a name or a signature on it. An hour reconstructed in the office three weeks later is worth a fraction of the same hour written on a ticket that afternoon, and everybody who reads claims for a living knows it." },
          { "h": "What's still in front of me",
            "r": "The work this change is still dragging behind it: leaves left to machine, hardware still to order and its lead time, openings that cannot close out until somebody answers, and the other openings whose sequence just moved because of it. State what he needs decided and by when, and state plainly what he is doing in the meantime — proceeding under direction, holding, or working around it at a cost. The price goes in the change order the PM writes; this is the narrative he writes it from, and it stays a narrative. The moment a number lands at the bottom of it, everybody reads the number and nobody reads the facts." }
        ]
      },
      {
        "id": "the-day-i-couldnt-hang",
        "name": "The Day I Couldn't Hang",
        "aka": ["lost day door crew", "door crew stood down all day", "couldn't hang doors delay notice", "idle crew write up doors", "openings not ready lost the day", "sent my guys home doors", "impact write up door installer", "non productive day doors", "other trades blocked my openings", "delay letter doors and frames"],
        "family": "notice",
        "from": "the foreman who had the crew on site",
        "to": "our PM, and the GC super the same day",
        "why": "A lost day cannot be photographed after it is over. Whatever stopped him gets fixed — the pallets in the corridor get moved, the slab dries, the electrician finally pulls the wire, the lift goes back downstairs — and inside forty-eight hours there is nothing left standing in the building that says his crew stood there. All that survives is payroll, and payroll on its own proves men were paid, not that they were prevented. A day written up that same afternoon, with the condition photographed while it still existed and the super told while he could still walk to it, is evidence. The same day reconstructed from timesheets at the end of the month is arithmetic, and arithmetic loses.",
        "note": "This records a condition, a notification and the disposition of hours. It names the work that wasn't ready in factual terms — \"the slab in corridor 2 was poured that morning and taped off\" — and never says a trade is behind, never assigns fault, never claims the schedule is unachievable, and never says any opening is or is not compliant, complete or ready for anybody's inspection. No ratings, no clearances, no closer settings, no forces: none of that is what a lost day is about. There are no dollars in it either. It quotes what people said instead of characterising it, because the version with quotation marks in it is the version that survives being read aloud in a room.",
        "omit": "WHAT THE MEN ACTUALLY DID WITH THE HOURS. Everybody writes \"lost the day, four men, eight hours.\" Almost nobody writes \"four men on site 6:30; came to hang 118 through 131; corridor 2 poured and taped at 6:40 by <name, company>; told the super at 6:50 and again by text at 7:05; held the crew to 8:15 staging hardware in the storage room, 1.5 hours productive; sent two men home at 8:30; kept two on three punching openings that were ready, 3 hours productive; 26 man-hours on the clock against 4.5 productive.\" The first is a number a GC talks down to zero by lunch. The second is a ledger — and the mitigation inside it, the honest admission that some of the hours got used, is exactly the thing that makes nobody bother attacking the rest.",
        "halt": "Only if the crew was never actually on site. A day he chose not to man because he heard the floor wasn't going in is a scheduling decision, not an impact, and dressing it up as one is how a contractor loses the next three that are real. If he stayed home, the write-up he owes is a heads-up about the condition, not a claim about a day.",
        "facts": [
          "the date, the crew by name and count, and the hours on the clock",
          "the openings they came to work that day, by number, and where the plan to work them came from",
          "the condition that stopped them, observed and photographed while it still existed",
          "who was told, at what time, by what means, and what came back in their words",
          "what work was found instead, and how many hours were genuinely productive",
          "which openings slid, and into whose week they landed"
        ],
        "sections": [
          { "h": "Who was here, and what we came to do",
            "r": "Date, day of the week, weather if weather mattered, the crew by name and classification, time on site and time off. The openings they were sequenced to work that day by number and floor, and where that sequence came from — his own three-week look-ahead, the GC's schedule by activity name and ID, or a direction from the super with a date on it. A crew that shows up with a written plan and gets stopped is a completely different story from a crew that shows up and wanders, and the plan is the only thing that makes the first story provable after the fact." },
          { "h": "What stopped us",
            "r": "The condition in physical terms and in the crew's own words: slab poured that morning and taped off, corridor stacked with somebody's duct so a 4-foot leaf cannot make the turn, frames not grouted, no power at the electrified openings, grid hung where the closer arm has to go, floor covering not down so nothing could be fitted to a finished floor, leaves locked in a container nobody had a key to, hoist down, no elevator window, another trade working overhead with the area barricaded. Photographed with a timestamp and something fixed in the shot — room number, stair sign, pallet tag — because a picture of an empty corridor proves nothing about which corridor or which morning." },
          { "h": "Who I told, and when",
            "r": "The super by name and company, the time, and the means: face to face at the opening, text, the seven o'clock huddle, an email the same morning. What came back, quoted: \"give me till after lunch and I'll get the pallets moved\" is a quote with a promise and a clock in it; \"he said he'd take care of it\" is a memory that evaporates. If the notice was verbal, put a text behind it inside the hour so the timestamp lives somewhere outside his own head. Note anyone else standing there — a witness with a company name beside it is worth more than another paragraph of adjectives." },
          { "h": "What we did with the time",
            "r": "The honest ledger. Hours held on site, hours released, who went home and at what time, and every scrap of productive work that was found instead: staging and sorting hardware, tagging leaves to marks, pre-fitting in the lay-down area, punching a floor that was ready, cleaning grout off frames, cutting protective wrap. Man-hours on the clock stated against man-hours actually productive, both numbers written out. This is the paragraph that costs him a little and buys him the whole document: a write-up admitting four of twenty-six hours got used is a write-up nobody bothers to attack, and a write-up claiming all twenty-six is one somebody will spend a week attacking." },
          { "h": "What it moves",
            "r": "Which openings slid and where they land now, whether the crew can absorb it inside the same week or the sequence has to be re-planned, and what it does to the people behind him — the painter waiting on frames, the inspector's walk, the owner's move-in on that floor. Then what he needs: the condition cleared, a date to come back, somewhere to work in the meantime. Ask for the date in writing. There are no dollars in this document; there is a day. And when days stack up, it is the stack of individually dated write-ups that carries the argument, never the total at the bottom of a summary written in month three." }
        ]
      },
      {
        "id": "openings-walk-before-theirs",
        "name": "My Own Walk, Before Theirs",
        "aka": ["pre punch door openings", "punch my own doors before the walk", "self punch list doors and hardware", "door walk before the architect", "openings checklist before punch walk", "pre walk doors frames hardware", "find my punch before they do", "door installer self inspection", "walk the openings before the owner", "punch list prep doors and hardware"],
        "family": "verification",
        "from": "the door and hardware foreman",
        "to": "his own crew first, and our PM — nobody outside the company",
        "why": "Everything about fixing an opening gets more expensive the second somebody else writes it down. A strike that takes four minutes to move today takes a badge, an escort, an after-hours window and half a day once that floor is turned over and occupied — and by then the painter, the mason, the drywall crew and the lift operator are all off the job, so the frame they dented and the wall they never patched become his to eat. A punch item found on his own list is work. The same item found on the architect's list is a defect with his company's name beside it, sitting in the closeout file, attached to his retention and to the reference call somebody makes about him next year.",
        "note": "This is a work list, not a certificate, and it is written as one from the first line. It never says an opening is complete, compliant, finished or ready for anybody's inspection. It never states or implies a fire rating or what a label permits, and it never says a label is intact. It records no clearance, gap, undercut, closer setting or opening force as a requirement or a finding, and it contains no keying or bitting information in any column, for any reason, ever. Where a dimension matters he writes what his own tape read and says it was his tape. Openings appear by number as addresses only. What an opening is or is not permitted to be is the judgment of the architect, the hardware consultant and the authority having jurisdiction — this document exists so that when they come to make it, there is nothing of his left on the floor for them to find.",
        "omit": "THE DAMAGE SOMEBODY ELSE DID TO HIS WORK, LOGGED ON THE SAME WALK, WITH A DATE ON IT. Everybody writes their own half — \"adjust the closer at 214, touch up 216, screw missing at 301.\" Almost nobody writes the other half: \"frame at 218, dent in the strike jamb about 18 inches off the floor, size of a lift tire, was not there when I set it on 5/12, photographed 6/03, showed the super the same morning; frame at 221 painted over the hinge leaves and the strike; leaf at 230 scarred by a drywall cart after somebody pulled the protective wrap.\" Six weeks later every one of those lands on the architect's punch list as a door item with his name against it, and the lift operator, the painter and the board crew are long gone. The line with a date and a photograph on it is the only one that ever goes back where it came from.",
        "halt": "Only if the openings have not actually been walked — a list built at a desk out of the schedule is a plan, not a punch, and the eleven items it quietly skips are the eleven the architect will write. And it never leaves the company: the moment a self-punch is handed to the architect or the owner it stops being his working list and becomes a written inventory of his own defects, and every honest line in it turns into a contract item.",
        "facts": [
          "the date of the walk, who walked it, and which openings were walked — plus which were skipped and why",
          "each item tied to an opening number and described physically, the way one man describes it to another",
          "whose item it is: his own crew, another trade, or waiting on somebody else's work",
          "what his own tape read wherever a dimension is the issue, named as his tape",
          "the fix on every line, with a name and a date against it and a blank column for the day it closed",
          "the two or three that will not close without a decision from above"
        ],
        "sections": [
          { "h": "How the walk was run",
            "r": "Date, who walked it, which floors and which openings by number, in what order, and what was carried — tape, level, screwdrivers, a bag of screws and silencers, touch-up, a camera. Then the openings that were not walked and the reason: no access, tenant space locked, floor not turned over, leaves not hung yet, area barricaded for overhead work. A punch that claims a whole floor and quietly skips eleven openings is precisely the punch that gets one of those eleven written up by somebody else. Walk both sides of every opening, both leaves of every pair — half the items only exist from the push side, and nobody finds them standing in the corridor." },
          { "h": "What I found, opening by opening",
            "r": "One line per item, each tied to an opening number and described so the man who fixes it never has to come back and ask a question: hinge screws stripped at the top hinge, leaf binding on the strike jamb at the top corner, latch not catching the strike, closer arm fouling the grid, lockset loose on the rose, silencers missing, kick plate short of the edge, threshold not bedded, gasketing pinched at the head, protective wrap still on, grout not cleaned off the frame face, backbend loose, shipping spreader still sitting in the bottom of a frame. Where a dimension is the issue, write what his own tape read and say it was his own tape. No conclusions anywhere about what any of it means for anything stamped on the material." },
          { "h": "Whose item it is",
            "r": "Three buckets, and a name in every one. His own crew's work. Another trade's damage or unfinished work. And items he cannot close until somebody else finishes — power at an electrified opening, a floor that hasn't been laid, paint that was never cut in, a wall never patched around a frame. For the second bucket, date it, photograph it and tell the GC super the same day, by name and with a time: an item logged and reported the day it is found goes back to its owner, and the identical item raised for the first time at final punch goes on his tab, every time, without exception. For the third, name what he needs and who he needs it from." },
          { "h": "What gets done, by who, by when",
            "r": "The disposition on every line: fixed now off what is on the truck, fixed on the return trip, or needs material — and if it needs material, what it is, what the lead time is and whether the order is actually placed or just talked about. A name on every line, a date on every line, and a blank column for the day it closed with the initials of the man who closed it. A punch list with no closer column is a wish list. The closed column is the artifact that proves the work happened, and it is the thing he holds up six weeks later when the formal walk turns up the one item he did miss and somebody starts asking what else he missed." },
          { "h": "What I'm handing my own PM",
            "r": "The short summary he owes his own office and nobody else: openings walked, items open, items sitting on other trades, and the two or three that will not close without a decision from above — a frame that has to come out, a leaf that has to be reordered with the lead time written next to it, an opening where the field and the approved drawing disagree and somebody upstairs has to answer which one wins. Say what he needs from his PM and by when. Keep the whole thing inside the company: this list is honest because it is internal, and the day it stops being internal is the day it stops being honest." }
        ]
      }
    ],

  /* What this trade dictates that a phone gets wrong. Only real corrections —
     the creative entry recorded 19 pairs that corrected nothing under a
     heading claiming they did, and that is the failure to avoid here. */
  "vocab": [
    "mull -> mullion",
    "astral -> astragal",
    "hollow mental -> hollow metal",
    "hollowmetal -> hollow metal",
    "night latch -> nightlatch",
    "panic bar -> exit device",
    "door closer arm -> closer arm",
    "strike plate -> strike",
    "hinge but -> hinge butt",
    "jam -> jamb",
    "jams -> jambs",
    "cylinder core -> core",
    "l h r -> LHR",
    "r h r -> RHR",
    "hm frame -> hollow metal frame",
    "k d frame -> knock-down frame"
  ],

  /* Trigger-only nudges. They fire when the dictation touches the thing and
     stay silent otherwise. */
  "reminders": [
    { "when": "label", "say": "You can quote what a tag in front of you reads. Do not say what the rating means, whether the label is intact, or what the assembly is worth — that call belongs to the manufacturer and the authority having jurisdiction, and a write-up that makes it is worse than one that doesn't mention it." },
    { "when": "keying", "say": "Keying direction is an ASK with a date on it. Do not write out keyed-alike groups, masters or bitting anywhere in this document — that schedule is somebody else's and a second copy of it on a phone is the problem, not the fix." },
    { "when": "clearance", "say": "Write what your tape read and where on the opening you read it. Do not write what the gap is allowed to be — that belongs to the standard and the inspector, and the number you half-remember is the one that gets quoted back at you." },
    { "when": "hand", "say": "Say the hand you actually found at the frame, and say where you were standing when you called it. The hand is the most expensive thing on a door job to get wrong, and the argument is always about who read it and when." },
    { "when": "closer", "say": "Say what the closer is doing — slamming, not latching, arm fouling something. Do not write a spring size or an adjustment setting; what it should be set to is the manufacturer's, not yours." }
  ]
};
