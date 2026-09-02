/* LANDSCAPE & IRRIGATION FIELD TOOLKIT — THE WRITE-UP LIBRARY.
 *
 * Shape #4, the DOCS engine (shared/docspec.js). This file is not a form and
 * does not produce a document: it produces the INSTRUCTIONS a man pastes into
 * his own AI once, after which he dictates the mess off the tailgate and gets
 * back something the office can forward. Seven documents written for the
 * INSTALL crew — trencher, valve boxes, mainline and laterals, soil, grade,
 * plants, sod, the clock — join the shared library every kit inherits. The
 * maintenance route is not in here and never will be. This is the outfit that
 * puts it in the ground, runs it once, and hands the water to somebody else.
 *
 * WHAT THIS TRADE'S DOCUMENTS ARE NOT ALLOWED TO SAY, repeated here rather
 * than trusted to trade.js because this is the one surface in the kit that
 * emits FREE PROSE — the one place a rule can be broken without a field to
 * break it in. Every `note` below carries its own slice of it, and a later
 * cycle editing a document carries it forward:
 *   - NO RATE AND NO RUN TIME. No precipitation or application rate, no flow
 *     figure, no minutes on a zone — not as a value, a default or a "typical".
 *     The clock says only what HE states he set it to, copied off its own face.
 *   - NO watering schedule, no ET, no water budget, no seasonal figure, no
 *     "how long to run it" — not as advice and not as a starting point.
 *   - NO SIZING AND NO DESIGN: no pipe, valve, wire or sleeve size, no
 *     pressure-loss or velocity arithmetic, no head spacing, arc, radius,
 *     nozzle or coverage layout. The design is a sheet he RECEIVES, and it
 *     rides here as an ADDRESS — sheet and revision — so two people can point
 *     at one line.
 *   - NO BACKFLOW value, result or certification. The certified tester fills
 *     the water purveyor's own numbered form; nothing here is shaped like it.
 *   - NO AUDIT: no distribution uniformity, no catch-can result, no
 *     water-efficiency finding, no compliance call.
 *   - NO SPRAY RECORD OF ANY KIND. No pesticide, herbicide, fungicide or
 *     fertiliser product, rate or interval, on any document, in any column,
 *     ever. That record is the licensed applicator's, filed with the state.
 *   - NO soil prescription: no amendment rate, no pH, salinity or infiltration
 *     threshold, no import spec, no reading of anybody's lab report.
 *   - NO PLANTING SPECIFICATION AND NO PLANT VERDICT: no depth, spacing,
 *     staking, backfill mix or pruning call; no suitability, hardiness or
 *     substitution verdict; no nursery grading standard. He types what is ON
 *     THE TAG, and the tag is quoted rather than judged.
 *   - NO TREE VERDICT: no protection zone, no critical-root dimension, no
 *     health or hazard assessment, no removal call. The arborist's report and
 *     the city's permit own every one of those.
 *   - NO grading or drainage engineering: no slope minimum, no swale or
 *     detention sizing, no erosion-control selection, no stormwater form and
 *     no rain-event log.
 *   - NO cover depth, trench depth or separation distance, and no locate
 *     ticket — a ticket number rides as an address and nothing more.
 *   - NO property line, setback or easement determination. The pin is the
 *     surveyor's sealed record and it is not ours to read.
 *   - NO RELEASE VERDICT AND NO CAUSE OF DEATH. No document here says planting
 *     is complete, established, accepted or warrantable, or that a bond may be
 *     released — and none says WHY a plant died. What he saw, what the clock
 *     was doing that week, and who was holding it, all dated: that is the whole
 *     record, and it is worth more than a verdict.
 * And the word twelve other kits on this rack use for a fire-suppression head
 * is not this trade's word. It appears exactly once in this file, down in the
 * dictation list, being corrected. Ours are HEADS, VALVES, MAINLINE, LATERALS,
 * DRIP, THE CLOCK, ZONES, THE POC, THE BACKFLOW.
 *
 * Where a number belongs it is HIS — his laser, his tape, his shovel, his
 * count at the tailgate, his own controller face — and it is named as his on
 * the page. The engine's two LOCKED toggles ("never invent", "never judge a
 * value") back that at the universal-law level; the notes below carry the
 * landscape edge the locks cannot see.
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
  /* Two trades in one hat, and the bid package, the sub agreement and the
     truck door all say both. "We do landscape and irrigation work" is the
     sentence the super would use about him, so the block takes it whole. */
  "trade": "landscape and irrigation",

  "docs": [
      {
        "id": "ground-i-was-handed",
        "name": "The Ground I Was Handed",
        "aka": ["finish grade not to plan landscape", "rock and debris in the planting beds", "subgrade compacted cannot plant", "no topsoil delivered to my beds", "beds will not drain grade too high", "ground handed over not ready to plant", "gc never brought the beds to grade", "spoil and base rock buried in the beds", "grade sits high against the walk", "what i found when i took the ground", "landscape notice bad subgrade"],
        "family": "notice",
        "from": "the landscape foreman taking the ground over",
        "to": "the GC super and our PM",
        "why": "Ground gets accepted by working it. The morning his crew tills, rakes and sets the first plant, everything underneath becomes his: the rock he tilled under is his rock, the pan a winter of loaded trucks put under the bed is why his plants sit in water, and the lip where the bed runs high against the walk is his grade. Nobody digs a finished bed back up to find out what was in it. The half day he spends with a laser and a spade before anything goes in is the only day the ground can still be described by the man who did not make it.",
        "note": "This is a reading and a source, twice over: what HIS laser, level, tape or string line read at a spot he names, and what the sheet HE was issued shows at that same spot, cited by number, revision and issue date. It never states a slope minimum, never sizes a swale or a drain, never says the ground will not drain as a conclusion, never names a soil class, and never gives an amendment, a pH or an infiltration figure. It does not say the grade is out of tolerance or that the beds are unplantable. It describes what a man found with his own tools on a dated morning, beside the drawing he was handed, and lets the architect decide which one moves.",
        "omit": "HIS OWN READING, THE SPOT HE TOOK IT, AND THE SHEET BESIDE IT. Everybody writes \"the grade is off and the beds are full of rock.\" Almost nobody writes \"my laser off the bench at the northeast walk corner reads 0.4 low in the bed against the walk; the sheet I was issued, <number and revision, with its issue date>, gives the bed at that corner; I cut four holes across the island with a spade and three came out with base rock and broken block, photographed with the tape in the hole.\" The first is a complaint about another man's dirt, and the dirt contractor will say he shot it good. The second is a number, a place, a document and four holes he can point at.",
        "needs": ["ref", "count", "where"],
        "halt": "Only if he has not yet put a tool on the ground or a spade in a bed — ground that looks wrong is an opinion, and half an hour with a laser and a shovel turns it into a notice. And if his own crew did the rough grade or hauled the import, this is not a notice against anybody: it is his own rework, and it belongs in the field log rather than in the GC's inbox.",
        "facts": [
          "the areas by the names the crew uses, pinned so a stranger can walk to each one",
          "what his own laser, level, tape or string line read, and the exact spot he read it",
          "the sheet he read the elevation off, by number, revision and issue date",
          "what came out of his own spade holes, hole by hole and bed by bed",
          "how long the ground has sat in that state and who has been driving on it",
          "which beds he is standing down on, and what that stops behind him"
        ],
        "sections": [
          { "h": "The ground, and how to find it again",
            "r": "The areas by the name the crew actually uses — the entry islands, the strip along the drive, the courtyard beds, the south lawn — and a second address anybody can follow after the fences come down: building corner, gridline, curb return, light pole, door number. Say what each is meant to become, in his words: bed, lawn, sod, hydroseed, DG path, tree pits in the walk. Then the photographs, listed by what each frame shows, with something fixed in every one — a stair, a bollard, a room sign — because a picture of dirt in a field of dirt locates nothing a month on, when every bed looks alike." },
          { "h": "What my tool read, and where I stood",
            "r": "The tool named on every number: rotary laser off a stated bench, dot laser, six-foot level, string line and hand level, tape off the top of the walk. Say what he took as his reference and where it is, because half of every grade argument is two men off two different benches. Then reading by reading with the place attached — in the bed against the walk, at the curb return, at the low corner of the island, at the door threshold. Say whether he read against a walk already poured or against a line somebody staked. Every number here is his, taken with a named tool, at a named spot." },
          { "h": "What my sheet says, and where the sheet is",
            "r": "The drawing HE was issued, quoted rather than summarised: sheet number, revision, issue date, and the note or spot elevation covering the area he is standing in. Attach the page and mark the spot. If the plant schedule or the irrigation legend matters here, they ride as addresses only — sheet, key, line as their own document numbers them — never retyped. Say who issued it and whether he has been told of a newer revision he has not been given. If the ground and the sheet disagree, that disagreement is now two documents standing next to each other instead of one man's opinion." },
          { "h": "What came out of the holes",
            "r": "Cut holes with a spade across every bed, not one at the gate, and log them: how many, where, and what came out of each. Describe what he pulled up — spoil off the building pad, base rock, broken block, chunks of the flatwork, form stakes, banding, wire, wet clay that balls in the hand, dry pan a spade will not enter. Photograph every hole with a tape standing in it. Then topsoil: whether there is any at all, what his spade found cutting through it, whether there is import on site and whose pile it is. Describe the material and stop. What it is called belongs to the geotech." },
          { "h": "How long it has been like this, and who has had it",
            "r": "The history that gets forgotten first. When was he told the ground would be his, in writing or in the huddle, and by whom. What has run across it since: haul trucks, the pumps, the mason's forklift, trade parking, a laydown for the steel, a stockpile that sat all winter. Whether it has been rained on and driven while wet. Who has had the beds before he showed up, by company. This is the paragraph that decides whether the fix is a ripper and a day or a re-import, and it is the first one memory throws away — six weeks on, nobody can say when the trucks came off." },
          { "h": "What I cannot do until somebody answers",
            "r": "Which beds he is holding and which he is proceeding on, as a list of areas rather than a wave at the site. What is already on the ground or on order against them — trees on a rack, sod cut and coming, one-gallons and flats that will not hold in a laydown. What the hold does behind him: the trench that goes in before topsoil, the sod that cannot be laid on a bed running high, the walk-through on somebody's calendar. Then a request for direction with a date on it, not a demand for a remedy. How this gets fixed and who pays is the GC's call, and the letter exists so he can make it with numbers in front of him." }
        ]
      },
      {
        "id": "sleeves-never-went-in",
        "name": "Nobody Put My Sleeves In",
        "aka": ["sleeves not installed before the pour", "concrete poured over my irrigation crossing", "no sleeve under the walk for my mainline", "have to bore under the drive now", "core drill through finished flatwork irrigation", "nobody set my sleeves i sent the list", "crossing list ignored before the pour", "walk poured with no sleeve for wire", "mainline cannot get under the curb", "sleeve missing under paving notice", "saw cut the walk to get my pipe across"],
        "family": "notice",
        "from": "the irrigation foreman who sent the crossing list",
        "to": "the GC super and our PM, copied to concrete and paving",
        "why": "A sleeve is the one thing on a job with no drawing, no line item and no owner until somebody pays for a core drill. Before the pour it is a length of pipe, two caps and twenty minutes. After the pour it is a bore under finished flatwork, a core through a curb, a saw cut and a patch that will always be a patch, or a re-route that buries fittings under somebody else's warranty. And flatwork does not reopen — it gets demolished. He wrote the crossings down and sent them to a named man on a dated morning precisely so this could not happen, and it happened anyway. That message is the entire document.",
        "note": "This is a message and two dates. It quotes the crossing list HE sent, in his own words off his own submittal, and sets it beside the day the concrete or the base went over it. It never gives a sleeve size, a pipe or wire size, a trench or cover depth, or a separation distance; it never specifies a boring or coring method; and it never says the pour was defective or that anybody breached a spec. The crossing is named the way HE named it, and the irrigation sheet rides as an address. There is no price in it either: what getting through the concrete costs is a ticket, written once this one has established who knew what, and when.",
        "omit": "THE DATE HE SENT THE LIST AND THE MAN HE SENT IT TO, BESIDE THE DATE OF THE POUR. Everybody writes \"my sleeves never went in and now the walk is poured.\" Almost nobody writes \"I sent the crossing list to <name, company> by text on <date> and again by email on <date> — here is the message — and it reads 'crossings 4, 5 and 6 cross the east entry walk, mainline and valve wire, before you set forms'; the east walk was poured on <date>; three of my twelve are under it.\" The first is a grievance, and grievances get split down the middle. The second is a timestamp with a man's name on it beside a pour date, and there is nothing left to negotiate.",
        "needs": ["when", "who"],
        "halt": "Only if he cannot produce the crossing list he actually sent — a sleeve he meant to mention over coffee is not a notice, and sending one without the message behind it teaches the super to discount the next one, which will be the expensive one. The message, its date and the name it went to come first; the letter is built on top of them.",
        "facts": [
          "the crossings by his own names for them, and what was to go through each",
          "the date he sent the crossing list, to whom, and by what means",
          "the date the concrete, base or paving went over it, and who placed it",
          "which crossings are buried now and which are still open",
          "what getting through it takes, stated as work rather than as money",
          "the direction he needs, and the date he needs it by"
        ],
        "sections": [
          { "h": "What I sent, and who I sent it to",
            "r": "The crossing list quoted as it went out, not summarised: the date, the time if the phone shows it, the means — text, email, a photo of a marked-up sheet, a printout handed across at the huddle — and the man it went to, by name and company. Attach the message. A timestamp does work no memory can do, and it is the single fact this letter stands on. If it went to more than one person, name them all. If it went out more than once, list every date: a list sent twice and ignored twice reads very differently from one sent once. If it was also walked, say who walked it and where the pins were." },
          { "h": "What went over it, and when",
            "r": "The date the forms went in, the date of the pour, the date the base was rolled or the paving laid, and who placed it, by company. How he found out and when — arrived to a finished walk, watched the trucks come in, got a photo from his own man. Then say plainly whether the sleeve was never installed, was installed by his crew and covered without being marked, or was set and then pulled or driven flat before the pour. Those are three stories with three different owners, and the letter is worth nothing if it blurs them. Name who was on site for his outfit that week." },
          { "h": "What is under there now, crossing by crossing",
            "r": "One line per crossing, using the same names the list used, so the two documents read against each other without a translation. What was to go through each: mainline, a lateral, a drip feed, valve wire, the common, low-voltage lighting, a drain line. What it is under now: drive, walk, curb, patio, paving, a wall footing, the flatwork at the entry. Which crossings survived and are still open and capped, and where their ends are marked — the ones that are fine belong in this record as much as the ones that are not. Photograph each buried crossing from a fixed point." },
          { "h": "What it takes to get through now",
            "r": "Stated as work and sequence, never as a price. A bore from pit to pit, where the pits have to go, and what has to be dug up on either side to get them. A core through a curb or a wall, and who owns the finish it comes out of. A saw cut and patch across finished flatwork, and the fact that a patch is permanent and visible. A re-route the long way with the added fittings and where they end up buried. Then what each does to his own schedule: a trench that stays open, a crew that comes back, an area he cannot backfill, a grade he cannot finish." },
          { "h": "What I need, and by when",
            "r": "One ask with a date on it. Direction in writing on how each buried crossing gets made: bore it, core it, cut it, or re-route it and where. Whose scope it lands in and who is arranging it, because the man with the saw is not on his payroll. What he is doing in the meantime — proceeding on the crossings that are open, holding the mainline at the last valve box, standing the trencher down. And what happens to the dates behind him if the answer is late, stated as a date rather than a warning. Ask for it by email so it lands somewhere other than a corridor, and close there." }
        ]
      },
      {
        "id": "the-day-i-couldnt-plant",
        "name": "The Day I Couldn't Plant",
        "aka": ["lost day landscape crew", "sent my guys home no water on site", "crew stood down could not plant", "beds not ready lost the day", "idle landscape crew write up", "delay letter landscape install", "trades parked in my beds all day", "showed up to plant and the ground was not ready", "no water at the point of connection lost day", "non productive day irrigation crew", "landscape impact write up lost hours"],
        "family": "notice",
        "from": "the foreman who had the crew on site",
        "to": "our PM, and the GC super the same day",
        "why": "A lost day cannot be photographed after it is over. Whatever stopped him gets fixed inside forty-eight hours — the trucks come off the beds, the ground dries, the plumber charges the POC, the gate gets unlocked — and nothing is left standing in the dirt that says five men stood in it. All that survives is payroll, and payroll proves men were paid, not that they were prevented. Worse than on most trades, what was on the ground that morning was alive and on a clock nobody stops. A day written up that afternoon, photographed, with the super told while he could still walk to it, is evidence. The same day rebuilt from timesheets in month three is arithmetic, and arithmetic loses.",
        "note": "This records a condition, a notification and the disposition of hours. It names what was not ready in flat physical terms — \"no water at the POC and the beds still stacked with forms\" — and never says a trade is behind, never assigns fault, never says the schedule is unachievable, and never rules on whether the ground was plantable. It gives no watering instruction, no run time and no schedule anywhere, including in the paragraph on keeping the stock alive, where what he did is stated in his own words as what he did. There are no dollars in it. It quotes what people said instead of characterising them, because the version with quotation marks survives being read out loud.",
        "omit": "WHAT THE MEN ACTUALLY DID WITH THE HOURS. Everybody writes \"lost the day, five men, eight hours.\" Almost nobody writes \"five men on site 6:30; came to plant the entry islands; no water at the POC and the beds still stacked with the concrete crew's forms; told <name> at 6:45 and by text at 7:10; held the crew to 8:30 pulling the 15-gallons off the truck onto blocks and hand-watering the rack, two hours productive; sent three home at 8:40; kept two cutting sod on the south lawn, four hours productive; 40 man-hours on the clock against 6 productive.\" The first is a number a GC talks to zero by lunch. The second is a ledger, and its honest half is what stops anybody attacking the rest.",
        "needs": ["when", "count", "notdone"],
        "halt": "Only if the crew was never actually on site. A day he chose not to man because he heard the water was still off is a scheduling call, not an impact, and dressing it up as one is how a man loses the next three that are real. If he stayed home, what he owes is a heads-up about the condition and a date he is coming, which is a different letter in this library.",
        "facts": [
          "the date, the crew by name and count, and the hours on the clock",
          "the areas they came to plant, and where that day's plan came from",
          "the condition that stopped them, photographed while it still existed",
          "who was told, at what time, by what means, and what came back in their words",
          "what work was found instead, and how many hours were genuinely productive",
          "what was standing on the ground waiting, and who kept it alive"
        ],
        "sections": [
          { "h": "Who was here, and what we came to do",
            "r": "Date, day of the week, weather if weather is part of it, the crew by name and classification, time on and time off. The areas they were sequenced to plant or trench that day, by the names the crew uses, and where the sequence came from: his own look-ahead, the GC's schedule by activity name, a direction from the super with a date on it, or a delivery booked that morning. A crew that turns up with a written plan and gets stopped is a different story from a crew that turns up and wanders, and the plan is the only thing that makes the first one provable once the day is gone." },
          { "h": "What stopped us",
            "r": "The condition in physical terms and in the crew's own words. Beds still stacked with forms, pallets and trade parking. No water on site and nothing to fill a tank off. The POC not live, the meter not set, the backflow not in. No power at the clock. Ground soaked and gumbo, or frozen. Rock and spoil never picked, finish grade never brought in. Sleeves never set and the flatwork already poured. Gate locked, no badge, no escort. Nowhere to dump the sod cut. No answer on the substitution. Photograph every one with a timestamp and something fixed in the frame, because a picture of an empty bed proves nothing about which bed or which morning." },
          { "h": "Who I told, and when",
            "r": "The super by name and company, the time, and the means: face to face at the bed, a text, the seven o'clock huddle, an email that morning. What came back, quoted rather than characterised — \"give me an hour and I will get the forms moved\" is a quote with a promise and a clock inside it; \"he blew me off\" is an argument he loses. If the notice was verbal, put a text behind it inside the hour so the timestamp lives outside his own head. Note anyone else standing there, with a company beside the name. One witness with a company name beats another paragraph of adjectives." },
          { "h": "What we did with the time",
            "r": "The honest ledger, and the paragraph that buys the document. Hours held on site, hours released, who went home and at what time. Then every scrap of work genuinely found instead: pulling stock off the truck onto blocks and into shade, hand-watering the rack, staging by area, laying out heads and boxes, cutting sod on a piece that was ready, hauling spoil, servicing the trencher. Man-hours on the clock stated against man-hours actually productive, both written out. A write-up admitting six of forty hours got used is one nobody attacks; one claiming all forty is one somebody attacks for a week." },
          { "h": "What was standing on the ground while we waited",
            "r": "The half of a lost day only this trade has. Material on site is alive and on a clock nobody stops: B&B with the rootballs out in the sun, one-gallons and flats on a pallet with nobody on them over a weekend, sod cut two days ago and stacked hot in the middle of the pallet, trees leaning on a rack in the wind. Say what was there, by kind and count and where it stood, and what his crew actually did to keep it alive that day and who did it, in his own words. Say whether anything was already turning. This paragraph is what makes the next document in this library believable if any of it dies." },
          { "h": "What it moves",
            "r": "Which areas slid and where they land now. Whether the crew absorbs it inside the same week or the sequence has to be rebuilt, and what it does to the people behind him: the paving that wanted his trench closed, the walk-through on somebody's calendar, the owner's opening on that end of the building, a delivery already booked against a bed that is not ready. Then the ask: the condition cleared, a date to come back, somewhere to work meanwhile. Ask for the date in writing. There are no dollars in this document; there is a day, and it is the stack of dated days that carries an argument, never a total written in month three." }
        ]
      },
      {
        "id": "why-they-died",
        "name": "What I Found When They Died",
        "aka": ["plants died on the job write up", "trees died who turned the water off", "dead plants on the job record", "lost the shrubs in the island", "plant loss record with photos", "somebody shut the controller off and they died", "found the clock in off and the plants dead", "sod died before we handed it over", "plant material dying on site notice", "replacements who pays for the dead plants", "trees browning out after we planted"],
        "family": "incident",
        "from": "the foreman who planted them",
        "to": "our PM, the GC super, and whoever holds the controller",
        "why": "A dead plant is the one defect on a job that everybody already has an opinion about, and it is always the same opinion: the landscaper planted it wrong. The plant gets pulled, replaced and hauled off inside a week, so the evidence disappears faster than on any other trade. What would actually answer the question is not in the hole at all — it is on a controller face in somebody else's building, behind a door he has not had a key to since handover. Written on the day, with the rootball open and the clock photographed as found, it is a record. Written at the end of the establishment period, it is his word against a line in somebody's contract.",
        "note": "This document never says why anything died, and that refusal is the whole of its value. No horticultural verdict, no warranty verdict, no cause stated as a conclusion, not even a likely one. No suitability, hardiness or substitution call, no planting depth, spacing, staking or backfill specification, no soil interpretation, no watering recommendation, no run time and no schedule anywhere in it. It records four things: what he found when he opened the ground, what the controller face read when he opened the door, who has held that controller since he left, and who was told and when. If the record is thin it stays thin and says so. A cause written into it is the sentence read back to him.",
        "omit": "WHAT THE CLOCK WAS DOING THAT WEEK, AND WHO HAD IT, WITH A NAME. Everybody writes \"we lost four of the 24-inch box in the entry island.\" Almost nobody writes \"the clock in the garage was in OFF when I opened the door on <date>, photographed as found; zone 3 is the entry island; <name, company> told me on <date> that he shut it down for the paint crew and did not put it back on; nobody had been in that room since we left on <date>.\" The first is a loss with one company's name on it and no other facts in the room. The second puts a dated clock and a named man beside it, and never says what killed anything.",
        "needs": ["when", "who"],
        "halt": "Only if he cannot say when the plants went in — a loss with no planting date sits inside nobody's period and cannot be placed against anybody's contract, and that date is already on a delivery slip and a daily he wrote. Everything else in this document can come back <MISSING> and it is still worth sending the same day.",
        "facts": [
          "the plants by kind and by the size as the tag reads, counted, and where each stood",
          "the date they went in, the date he last worked them, and the date he found them",
          "what he found when he opened the ground, described physically and photographed",
          "what the controller face read when he opened the door, and who has held it since",
          "who was told, when, and in whose words",
          "what is still standing that is going the same way"
        ],
        "sections": [
          { "h": "What died, and where it stood",
            "r": "Kind and size exactly as the tag reads, not as anybody would classify it — the name on the tag, the size on the tag, the grower if it is still on the plant. Count them. Locate each one by area name and by a second address a stranger can walk to: the third tree in from the curb return, the row along the east face, the island at the loading dock. Photograph on the day, wide enough to place it and close enough to show it, with something fixed in every frame. If a tag has been pulled or faded, say so rather than filling it in from the schedule — the schedule is somebody else's document and no evidence of what was in that hole." },
          { "h": "The dates that bracket it",
            "r": "Five of them, and they do work no adjective can. The date it was planted. The date it was watered in and by whom. The last day his own crew was on that area. The day he first saw it turning, if he saw it. The day he found it dead. Write the gap between the last two rather than leaving it to be counted, and what he was doing on site in between, or that he was not there and since when. If there were weeks he had no access, say which and who had the key. This paragraph decides whose period the loss falls in, and it cannot be rebuilt later." },
          { "h": "What I found when I opened the ground",
            "r": "Dig one back and describe it physically, with a tape and a camera. The rootball dry through, or wet and sour, or intact and firm. The hole standing in water or dry at the bottom. What the ground around it does when a spade goes in. Roots as they came out of the can. The wrap, the basket, the twine, still on or off. Then the surface: mower scars on the trunk, tire tracks across the bed, a stake down, a head buried under mulch, a dripline cut, an emitter pulled off, a basin flattened. Photograph every one with a tape in the frame. Describe it and stop. No conclusion appears in this paragraph, ever." },
          { "h": "What the clock was doing, and who had it",
            "r": "The controller face photographed as found, before anybody touches a dial. What the door says it is. What position it was in — running, off, in a delay, in a mode he did not leave it in. Whether the panel was live and the breaker on. What the face shows zone by zone, transcribed exactly as it displays. Whether a rain sensor is there and what state it was in. Then the water: the POC on or off, the backflow shut, a valve found closed, a restriction the owner was told about. And the people: who has held that controller since handover, by name, company and date, and what each told him, quoted. Never a run time and never a schedule." },
          { "h": "Who I told, and when",
            "r": "Who was told the day he found it, by name and company, at what time, and by what means. What came back, in quotation marks. The GC super, the property manager, whoever holds the clock, his own PM. If the owner's rep has already said something about it — that the water was off for a paint crew, that a restriction came in, that the mowing contractor started last month — write it in their words with a date, because a sentence somebody volunteers on the first morning is worth ten paragraphs written after everybody has had a week to think about their position." },
          { "h": "What is still standing",
            "r": "The rest of the same material, the same zone, the same bed — what he is watching and why. Anything else showing the same thing, by kind and count and location. What he has asked for and from whom: the clock back on, a name who waters the days his crew is not there, access to the controller room, an answer on who is paying for replacements and under whose direction they go in. Say what he is doing meanwhile and under whose direction. Ask for a decision with a date. Do not price replacements here — that is a ticket, and this is what makes the ticket believable." }
        ]
      },
      {
        "id": "nursery-came-up-short",
        "name": "The Truck Came Up Short",
        "aka": ["nursery delivery came up short", "wrong size on the plant tag delivered", "trees came off the truck dry", "short count on my plant order", "sod delivered hot on the pallet", "material not on my packing slip", "rootball broken on delivery", "the yard sent the wrong plants", "count the truck before i sign for it", "damaged stock off the truck write up", "plants delivered rootbound in the can"],
        "family": "incident",
        "from": "the foreman who took the delivery",
        "to": "the yard's inside man and our PM, and the grower if it came off their truck",
        "why": "Two clocks start when the truck backs in, and neither waits for him to get around to it. The driver leaves with the delivery receipt, and a load signed clean makes the short count his short count. Then the replacement clock: a size that is not sitting in a yard within a day's drive is not a re-order, it is a substitution letter and a wait, and that clock started the morning the material was supposed to be in the ground. Once it is spread across four beds and a laydown and the tags are off, nobody alive can prove the six that are missing were never on the trailer instead of walking off the job on a Saturday.",
        "note": "This is a count and a source: what physically came off the truck, counted in the unit he counted in, against the packing slip by its own number and against his own order by document and date. It never converts between units. It never states a caliper, rootball or height standard, never grades anything to anybody's nursery standard, and never rules on whether the material is the right plant for the job — that answer belongs to the landscape architect and lives in a different letter. Condition is what he could see and photograph, described and never judged: it does not say the stock is unacceptable and it does not say anything will or will not survive. Counts, never dollars. The tag's words, never a standard.",
        "omit": "THE COUNT AGAINST A NAMED SLIP, ON THE PAPER THE DRIVER TAKES WITH HIM. Everybody writes \"the truck came in short and some of it was rough.\" Almost nobody writes \"counted 34 five-gallons against 40 on packing slip <number>, line 6 — six short; the tag on the flowering pear reads 15-gal and my order line 3 reads 24-inch box; three came off with the rootballs pulling away from the can, photographed on the trailer; I wrote 'short 6, three dry, subject to inspection' on the delivery receipt and the driver signed it at 7:05.\" One is a phone call nobody can find. The other is a count, a document number and a signature from the one man in the story who cannot say he was not there.",
        "needs": ["ref", "count", "when"],
        "halt": "Only if nothing was actually counted against a named document — a load eyeballed at quitting time is a feeling and not a shortage, and sending it burns the credit he is going to need on the next four trucks. Count it against the slip, photograph it, then write it. And if the shortage traces back to his own order, this becomes a purchasing correction that goes to his PM alone.",
        "facts": [
          "the delivery: date, time, yard or grower, driver, and the packing slip number",
          "the count against the slip, line by line, in the unit he counted in",
          "what the tags read, set against what his own order says he bought",
          "the condition as he could see it, photographed before it came off the truck",
          "what he wrote on the delivery receipt and who signed it",
          "where it was set down, and how it is being kept alive"
        ],
        "sections": [
          { "h": "The truck, and the paper that came with it",
            "r": "Date, time on site, the yard or grower, the driver's name if he gives it, the trailer or ticket number, and the packing slip number. How the load was made up: racked, on the deck, B&B standing on the floor, flats stacked, sod on pallets with the cut date on the tag, pipe and boxes loose in the nose. Whether he had the men and the minutes to count before signing. Then exactly what he wrote on the delivery receipt before the driver dropped the gate, word for word. \"I told the driver\" is not a fact. A line in his own handwriting with a signature under it is, and it is the cheapest thing in this document to produce." },
          { "h": "What I counted, against what",
            "r": "Line by line, in the unit he counted in and never converted: each, cans, flats, rolls, pallets, bundles, yards, feet. The slip's line number beside his own order's line number, so two people can point at one row. What came, what did not, and anything that came that he never ordered or that belongs to another job. Trees counted by trunk, not by rack. Sod counted by roll or by pallet with the cut date read off the tag. Soil and mulch by what the ticket says was loaded against what he took. If the count could not be finished before the truck left, say how far he got." },
          { "h": "What the tag says, against what I ordered",
            "r": "Copy the tag, verbatim and photographed: the name on it, the size on it, the grower, the block or lot number if it carries one. Then his own order line quoted, by document and date. Where they disagree, that disagreement is now two documents standing next to each other rather than one man's memory — the tag reads one size, the order reads another, and both are attached. Do not translate a tag into anybody's grading language and do not decide which plant is right for the bed. Whether a substitution is acceptable is the architect's answer under their own number, and asking for it is a different letter." },
          { "h": "What it looked like coming off",
            "r": "Physical description only, photographed before it came down where possible. Rootball loose in the wrap or broken, burlap torn, basket snapped, twine cut. The can dry through, the plant wilted, leaves burned from the ride. Broken leader, scarred trunk, limbs snapped in the strapping, roots circling out of the can. Sod hot in the middle of the pallet. Mulch steaming. Pipe with the ends open and full of road grit, valve box lids cracked, a controller carton crushed. Say whether he saw it on the trailer or after it came off, and say what day the wrap came off — those are two different conversations with two different people paying." },
          { "h": "Where it is, and how it is being kept alive",
            "r": "Where the good material was set down: shaded or in the open, blocked off the ground or standing on hot asphalt, racked, heeled in, tarped, inside a fence or in a corner anybody can drive to. Who is watering it and how often, in his own words as what he is doing rather than as anybody's recommendation. Whether the damaged or wrong stock has been pulled aside and marked so nobody plants it on a Friday afternoon, and where it is held if the yard wants it back. Who has access and whether it locks — the sentence that always follows a short count is \"it came, and somebody on your crew moved it.\"" },
          { "h": "What it moves",
            "r": "The areas that cannot go in, by name, and the crew days already sequenced against them. Whether there is a workaround and what the workaround actually costs him in work: planting out of sequence, coming back to a finished bed a second time, holding a trench open, re-mobilising two men for eight trees. The replacement or re-delivery date, who gave it to him and on what day. Then the first date the general schedule genuinely feels it, written as a date rather than a worry. Ask for the ship date in writing, and let the paper carry the argument so he does not carry it on the phone." }
        ]
      },
      {
        "id": "what-i-left-running",
        "name": "What I Left Running",
        "aka": ["irrigation turnover record what i ran", "handed over the system zones i ran", "what i set the clock to at turnover", "who has the controller after we leave", "startup record zones i did not run", "walked the zones before handover", "the water is yours from here", "clock settings i left on the face", "which zones are not running yet", "handover note irrigation install", "turned the water over to the owner"],
        "family": "verification",
        "from": "the irrigation foreman handing it over",
        "to": "the owner or property manager, the GC super and our PM",
        "why": "The day he drives off, the water stops being his and the plants do not. Everything that happens to that landscape from then on happens through a controller in somebody else's building, behind a door he no longer has a key to, and the first question in every argument nine weeks later is what was running when he left. This is the record that answers it — and the half that does the real work is not the zones he ran. It is the ones he did not, named by number, because a zone nobody has ever run is a zone nobody should rely on, and the only way anybody learns that is if he wrote it down on the day.",
        "note": "This is a transcription and a boundary, and it makes no recommendation of any kind. No run time, no watering schedule, no seasonal figure, no ET, no water budget, no rate, no coverage or uniformity finding, no audit result, no backflow value or certification, and no verdict on whether the system is complete, balanced, accepted or compliant. What is on the controller face is copied off it in its own words and named as what HE set on that date — never as what it should be, and never as advice to whoever holds it next. THE DOOR CODE AND THE ACCOUNT PASSWORD DO NOT GO IN THIS DOCUMENT. They go by phone to a named person, and the document records that they went by phone, to whom, and when.",
        "omit": "WHAT WAS NOT RUN, AND WHY. Everybody writes \"walked the system, all zones running.\" Almost nobody writes \"ran zones 1 through 7 and stood and watched every one of them from the box to the far end; did NOT run 8, 9 and 10 — the drip in the north beds is stubbed and capped because those beds are not planted — and did not run 11, the parkway strip the paving crew still has closed; nobody has run those four and nobody should say they work.\" The first sentence is the one quoted back at him when a zone fails in August. The second gives away nothing and hands him the only defence there is: he wrote down what he had not seen.",
        "needs": ["notdone"],
        "halt": "Only if he cannot say which zones he personally stood and watched — a handover written off a controller screen without walking the zone is the one version of this document that can hurt him, because it puts his name on something he never actually saw run. If he ran none of them, that is a real answer and the document is still worth writing.",
        "facts": [
          "the date, who ran it, and who else was standing there",
          "which zones he ran, and what he watched happen at each one",
          "which zones he did NOT run, by number, and the reason for each",
          "what he set the clock to, copied off the face in its own words",
          "who has the controller, where it is, and who waters when the clock is off"
        ],
        "sections": [
          { "h": "What I ran, and what I watched",
            "r": "Zone by zone, by the number as it reads on the controller face and on the valve box lid, and say if those two disagree. For each, what he stood there and saw: heads came up and went back down, the drip pressurised and the emitters wet the ground, a bubbler filled the basin, the valve opened off the clock and by hand at the solenoid, the far end came on. Say where he stood when he watched it, because a zone run from the garage is not a zone anybody watched. Say what he found and fixed on the spot, and what he found and left. No coverage judgement, no uniformity finding, no verdict on whether it waters what it is meant to." },
          { "h": "What I did NOT run, and why",
            "r": "The section that protects him, and it goes in even when it is empty — \"none\" is an answer worth writing. Every zone he did not run, by number, with a reason beside each: stubbed and capped because the bed is not planted, under an area another trade has closed, no wire pulled to the valve, no power at the clock, could not reach the far end, drip he could not see under mulch, a zone the owner asked him to leave off. Then one plain sentence saying nobody has run these and nobody should rely on them until somebody does. Name who he told about each one, and when." },
          { "h": "What I set the clock to, in its own words",
            "r": "A transcription, not a recommendation. Copy what is on the face as the face displays it and say plainly that this is what HE set on that date and nothing more. The make and model as it reads on the door. Program letters, zone numbers, start times and days exactly as shown. Whether the dial is in run or off, and which he left it in. Whether a rain sensor is fitted and what state it is in. Whatever the face shows for a seasonal adjustment, copied as it displays. Photograph the face. Nothing here says what any of it ought to be, and a man who wants it different asks whoever holds it now." },
          { "h": "Who has it, and how to get to it",
            "r": "Where the controller physically is — building, room, wall, whether it locks and who holds that key. Who is on the water account and who holds the app if there is one. Where the POC, the master valve, the backflow and the valve boxes are, described so somebody can find them without him. Then the line that matters: THE CODE AND THE PASSWORD GO BY PHONE, to a named person, and this document records only that they went by phone, to whom, and when. Nothing that opens a controller or an account is written on a page that gets forwarded, printed and left on a desk." },
          { "h": "What the water still needs from somebody",
            "r": "The asks, each with a name and a date against it. Nobody kills the water without telling him. Nobody changes the clock without telling him, and if they do, he wants to know what changed and who changed it. Tell him the day it goes off for a freeze, a repair or a restriction, and the day it comes back. Name the person who waters on the days his crew is not there, and write what they say they are doing in their own words. Keep trucks and trades off the beds. And the date the maintenance or establishment period starts, quoted off the owner's own contract in its own words — never restated, never interpreted here." }
        ]
      },
      {
        "id": "they-drove-on-it",
        "name": "They Drove On It",
        "aka": ["somebody drove through my beds", "damage to finished sod by another trade", "heads broken off by a lift", "ruts across the island after handover", "not mine punch item landscape damage", "trades parked on my finished grade", "who wrecked the plants on the job", "vehicle damage to landscape write up", "valve box crushed by a truck", "mower hit my trees record", "tracks through the beds after we finished"],
        "family": "incident",
        "from": "the foreman whose finished work it was",
        "to": "the GC super the same day, and our PM",
        "why": "This is the evidence behind the words \"not mine\" on a punch list, and without it those words are just a position. Damage to finished landscape heals into the record faster than any other trade's: the rut fills in, the sod knits or dies and gets replaced, the head gets a new nozzle, the mulch gets raked back over, and by the punch walk there is a line on a list with his company beside it and nothing left to point at. The outfit that did it has usually rolled off the job by then. A photograph taken the same morning, with a date on it and a name in the caption, is the only thing that ever sends one of these back where it came from.",
        "note": "This describes damage physically and does nothing else. It never states a cause beyond what he saw or what somebody told him in their own words, and it never says another company is at fault as a matter of contract — a company name appears as an observed fact, off the door or off the tag, and no further. It gives no dollars and no repair method as a specification. It does not rule on whether damaged plants or sod will live, because that is a verdict this trade makes on no document here. And it does not say the area was complete or accepted: it says the date it was his and finished, which is a different claim and a stronger one.",
        "omit": "THE DATE HE HANDED THE AREA OVER, BESIDE THE DATE HE FOUND IT. Everybody writes \"somebody drove through the island and wrecked the sod.\" Almost nobody writes \"the east island went in on <date> and I photographed it finished that afternoon; on <date> at 7:15 I found tracks across it from the loading dock to the entry, two heads sheared at the swing joint and ruts the depth of my hand the length of the bed; the lift parked at the end of it was tagged <company>; I showed <name> the same morning at 7:30.\" The first is an accusation with no clock in it. The second is two dates with a photograph under each, and the whole argument lives in the space between them.",
        "needs": ["when", "who"],
        "halt": "Only if he cannot say when the area was his and finished — damage with no handover or completion date is a condition report and not a claim, and both dates sitting side by side are the entire mechanism of this document. Everything else in it can be thin and it still works, so write it the same day with whatever he has.",
        "facts": [
          "what was damaged, described physically, and where it is",
          "the date the work went in or was handed over, and the date he found it",
          "who did it, by name and company, if he knows and how he knows",
          "the photographs, taken the same day, and what is in each frame",
          "who was told, at what time, and what came back in their words"
        ],
        "sections": [
          { "h": "What was damaged, and where",
            "r": "Physically, and by area name plus a second address a stranger can walk to. Tracks and ruts across a finished bed, and how deep by his own tape or by something in the frame. Sod torn, churned or lifted at the seams. A tree rubbed, snapped or leaning where it was plumb. A rootball shoved sideways. Heads sheared at the swing joint or buried under pushed dirt. A valve box lid cracked or the box crushed flat. A lateral or dripline cut, mainline pulled, wire snagged out of a splice. Bed edge gone, grade pushed out, mulch scattered, a stake down. No verdict on whether anything lives — that is a different document on a different date." },
          { "h": "When it was mine, and when I found it",
            "r": "The two dates that carry the whole page. The date the area went in or was handed over, and how he can show it — a daily with the crew on it, a photo set from that afternoon, a delivery slip, a handover note. Then the date and time he found the damage, and what he was doing there. Describe what it looked like when he left it, in a sentence: that is the before-state nobody thinks to write. If there were days in between when other people had the area and his crew was gone, say which days and who had it. If he cannot fix the handover date exactly, say how close he can get and off what record." },
          { "h": "Who did it, and how I know",
            "r": "The vehicle or machine by what he actually saw: a scissor lift, a boom, a telehandler, a concrete truck, a pickup, a mower, a skid steer. The company name off the door, the tag or the rental sticker, as an observed fact and never as an accusation. The tyre or track pattern if that is all there is, and where it comes from and goes to. Anybody who saw it, by name with a company beside it. And if he does not know who did it, he writes that, and writes who he asked and what they said. An honest gap holds up fine. A guessed name loses the whole document." },
          { "h": "The photographs",
            "r": "Taken the same day, timestamped, with something fixed in every frame: a light pole, a curb return, the building corner, a stair, a door number, a pallet tag. A wide shot that places the damage in the building and a close one that shows it with a tape laid in the picture so the size reads. Shoot the machine and its company name if it is still standing there. Shoot the undamaged half of the same bed in the same frame where he can — the contrast is the argument. Say where the files live and who took them. A photograph of a rut in an anonymous bed proves nothing about which bed or which week." },
          { "h": "Who I told, and what I need",
            "r": "The super by name and company, the time, and the means — at the bed, by text, at the huddle, by email the same morning. What came back, quoted. Copy his own PM the same day so it exists in two places. Then the asks: traffic kept off, an access route that is not across his beds, barricade or fence he is putting in and who owns keeping it there, and direction on the repair with a date. Say what he is doing to stop it getting worse — taping it off, staking a line, hauling the long way round. No price here. The ticket is a separate document, and this is what makes it stand up." }
        ]
      }
    ],

  /* What this trade dictates that a phone gets wrong. Only real corrections —
     a pair that corrects nothing under a heading claiming it does is the
     failure to avoid, so this list is held to words that actually come back
     mangled off a tailgate in the wind. The last line is the only place in this
     file the fire-suppression word appears, and it appears being fixed. */
  "vocab": [
    "main line -> mainline",
    "back flow -> backflow",
    "drip line -> dripline",
    "root ball -> rootball",
    "top soil -> topsoil",
    "sub grade -> subgrade",
    "back fill -> backfill",
    "flat work -> flatwork",
    "stub up -> stub-up",
    "pop up -> pop-up",
    "quick coupler -> quick-coupler",
    "b and b -> B&B",
    "p v c -> PVC",
    "d g -> DG",
    "pee oh see -> POC",
    "sprinkler head -> head"
  ],

  /* Trigger-only nudges. They fire when the dictation touches the thing and
     stay silent otherwise. Six of them, and every one guards a place where an
     AI writing fluent prose would supply a number, a schedule or a cause that
     this trade is not allowed to state. */
  "reminders": [
    { "when": "rate", "say": "There is no rate in this kit and there never will be. No precipitation rate, no application rate, no flow figure — not as a value, a typical or a placeholder. If a number about water belongs on the page it is one HE read off his own gauge, named as his reading, with the day and the place he took it." },
    { "when": "schedule", "say": "Write what he says he set the clock to, copied off the face in its own words, and say it is what he set on that date. Never write how long a zone should run and never suggest an adjustment. What the water ought to do is the owner's call through whoever holds the controller — the moment we recommend it, the next dead plant is ours." },
    { "when": "backflow", "say": "The assembly may be named and located as a thing he can see. Nothing else. No test value, no result, no certification, no statement that it passed or is due — the certified tester fills the water purveyor's own numbered form. Say who is pulling the permit and who is testing it, by name, and stop there." },
    { "when": "spray", "say": "Stop. Nothing that goes in a tank belongs in any document this kit produces — no product, no rate, no interval, no re-entry, not even in passing. That record is the licensed applicator's and it is filed with the state. Name the date and the company as a fact he observed, and let their record carry the rest." },
    { "when": "dead", "say": "Record what he saw when he opened the ground, what the controller face read when he opened the door, and who has been holding that clock — names and dates on all three. Never write why anything died, not as a conclusion and not as a likely cause. A plant loss here is a dated record, never a verdict." },
    { "when": "grade", "say": "Give the reading, the tool that took it, the spot he stood, and the sheet and revision he read the plan elevation off. Never write a slope minimum, never size a swale or a drain, and never say the ground will not drain as a conclusion — say the water stood there on a date and how long it stayed." }
  ]
};
