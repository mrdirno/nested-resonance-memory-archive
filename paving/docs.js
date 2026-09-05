/* PAVING & STRIPING FIELD TOOLKIT — THE WRITE-UP LIBRARY.
 *
 * Shape #4, the DOCS engine (shared/docspec.js). This file is not a form and
 * does not produce a document: it produces the INSTRUCTIONS a man pastes into
 * his own AI once, after which he dictates the mess off the tailgate and gets
 * back something the office can forward. Seven documents written for the
 * PAVING crew and the SEALCOAT & STRIPING outfit — the base he was handed, the
 * iron and the sleeves under it, the plant order, the layout against the sheet,
 * the car that came through the cones, the lobby floor, the morning the cones
 * came off — join the shared library every kit inherits. The highway side is
 * not in here and never will be: bonded, inspected, numbered by the agency, it
 * writes on the agency's own forms. The maintenance route on the striper's
 * side, a customer list at street addresses, is scoped out the same way. This
 * is the outfit that is on the job LAST, after everybody else's trench, and on
 * an occupied lot is the man whose cones decide where two hundred people park
 * tonight.
 *
 * WHAT THIS TRADE'S DOCUMENTS ARE NOT ALLOWED TO SAY, repeated here rather
 * than trusted to trade.js because this is the one surface in the kit that
 * emits FREE PROSE — the one place a rule can be broken without a field to
 * break it in. Every `note` below carries its own slice of it, and a later
 * cycle editing a document carries it forward:
 *   - NO MIX AND NO NUMBER ON THE MAT. No mix design, no mix, lay-down or
 *     compaction temperature, no density, no compaction percentage, no
 *     thickness, no lift, no tonnage-per-area arithmetic — not as a value, a
 *     default or a "typical". The lab and the plant own those; the ticket and
 *     the lab's report ride here as ADDRESSES, by number, so two people can
 *     point at one line.
 *   - NO ADA AND NO STALL TABLE. No accessible-stall count, no stall or aisle
 *     dimension, no slope limit, no sign height, no symbol spec, no count
 *     table of any kind. The page quotes what the SHEET draws — sheet, rev,
 *     quoted — and says what HIS TAPE found, and asks the civil and the owner
 *     which one goes.
 *   - NO FIRE LANE. No determination, length, width or marking spec — the fire
 *     marshal's. No MUTCD or traffic-sign spec.
 *   - NO TRAFFIC-CONTROL PLAN, flagger plan, lane closure or detour: an
 *     engineered, permitted document. We ask WHO holds it and stop.
 *   - NO CURE TIME, no open-to-traffic time, no sealcoat product, no
 *     application rate, no paint spec, no dry time and no "how long to keep
 *     cars off". The manufacturer's sheet and his own spec sheet own that;
 *     the page carries what HE states, in his words, copied off his sheet.
 *   - NO TICKET OF OURS, no load count turned into a yield or a "short load"
 *     verdict, no invoice, no unit price. Loads are counted as trucks he
 *     watched come in, never as tons against an area.
 *   - NO VERDICT that a subgrade, a base or a lift passed, failed or is "to
 *     spec": the lab's numbered report, the civil's call.
 *   - NO PROOF-ROLL VERDICT. "I watched it, here is what I saw where the truck
 *     sat" is the whole of what a paragraph may say.
 *   - NO TOW AUTHORIZATION, no license-plate list, no tenant roster, no
 *     customer address list. A car is described as he saw it, off the door
 *     and the colour, and the plate stays off the page.
 *   - NO WEATHER THRESHOLD, no air or surface temperature minimum. "I'm not
 *     paving today, here's what I saw" in his words, with the time he called it.
 *   - NO DRAINAGE OR GRADE ENGINEERING. A birdbath is a place he saw water
 *     sit, named and dated; there is no slope number of ours anywhere.
 *   - NO RELEASE VERDICT, EVER. Nothing here says the lot is accepted,
 *     complete, finished or warrantable. The cones came off at a time, a
 *     named person was told, and the photo shows what it looked like — that
 *     is the whole record, and it is worth more than a verdict.
 * And the word the mason uses for his brick is not this trade's word. "Pavers"
 * on this rack is the hardscape crew's block on a sand bed. The machine is
 * "the paver" only inside a sentence that makes it a machine; the work is
 * PAVING, the surface is THE MAT, the plan side is THE LAYOUT, and the people
 * are THE PAVING CREW and THE STRIPER. It appears once in this file, down in
 * the dictation list, being corrected.
 *
 * Where a number belongs it is HIS — his string line off the top of the curb,
 * his straightedge, his tape, his measuring wheel, his count of trucks at the
 * gate, his chalk on the mat — and it is named as his on the page. The
 * engine's two LOCKED toggles ("never invent", "never judge a value") back
 * that at the universal-law level; the notes below carry the paving edge the
 * locks cannot see.
 *
 * `trade`     the trade word the emitted instructions use ("we do ___ work"). DECLARED,
 *            never derived from the toolkit name.
 * `docs`      documents specific to this trade (they join the shared library)
 * `drop`      shared document ids this trade genuinely never writes
 * `vocab`     what this trade dictates that a phone gets wrong ("wrong -> Right")
 * `reminders` trigger-only nudges — they fire when relevant and never nag
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
window.TRADE_DOCS = {
  /* Two hats, often two companies, and the rack has them as one chip. The sub
     agreement and the truck door say both. "We do paving and striping work"
     is the sentence the super would use about him, so the block takes it
     whole. */
  "trade": "paving and striping",

  "docs": [
      {
        "id": "the-base-i-was-handed",
        "name": "The Base I Was Handed",
        "aka": ["base not to grade against the curb", "base pumps under the truck", "soft spots in the base before we pave", "string line off the curb reads the base high", "subgrade soft cannot pave on it", "base handed over not ready to pave", "sitework left the base rough", "birdbath in the base before the mat", "what i found when i took the base", "paving notice bad base", "lip at the walk before we pave"],
        "family": "notice",
        "from": "the paving foreman taking the base over",
        "to": "the GC super and our PM, copied to sitework",
        "why": "A base gets accepted by paving it. The morning the first truck backs into the paver, everything under the mat becomes his: the soft spot he watched pump under the water truck is his soft spot when the mat cracks over it in March, the base that sat high against the gutter is his lip, and the low corner where the water stood all week is his birdbath. Nobody saw-cuts a finished mat to find out what was under it. The half hour he spends with a string line and a straightedge before the plant's first truck rolls is the only half hour the base can still be described by the man who did not build it.",
        "note": "This is a reading and a source, twice over: what HIS string line, straightedge, tape or level read at a spot he names, and what the sheet HE was issued shows at that same spot, cited by number, revision and issue date. It never states a density, a compaction figure, a thickness or a lift, never says the base passed or failed or is out of tolerance, never gives a slope number and never says the lot will not drain as a conclusion — a birdbath is a place he saw water sit, dated. Where a truck crossed it, the paragraph says what he watched where the wheels sat and stops; a proof-roll verdict is the lab's, under the lab's own numbered report, and the civil's call. It describes what a man found with his own tools on a dated morning, beside the drawing he was handed, and lets the super decide which one moves.",
        "omit": "HIS OWN STRING LINE, THE SPOT HE PULLED IT, AND THE SHEET BESIDE IT. Everybody writes \"the base is off and it's soft at the dock.\" Almost nobody writes \"my string line off the top of curb at the northeast return reads the base high against the gutter for thirty feet, the reading off my tape, photographed with the tape on it; the sheet I was issued, <number and revision, with its issue date>, gives the finish at that curb; I stood at the dock aisle at 6:40 and watched the water truck cross it and the base pumped under both rear axles for two truck lengths, photographed with a cone standing in it.\" The first is a complaint about another man's dirt, and the dirt contractor will say he shot it good. The second is a reading, a place, a document and a truck he watched, and there is nothing in it to argue with.",
        "needs": ["where", "when"],
        "halt": "Only if he has not yet pulled a string, laid a straightedge on it or stood and watched a loaded truck cross it — a base that looks soft is an opinion, and twenty minutes with a string line and one water truck turns it into a notice. And if his own outfit placed the base or hauled the rock, this is not a notice against anybody: it is his own rework, and it belongs in the field log rather than in the super's inbox.",
        "facts": [
          "the sections by the names the crew uses, pinned so a stranger can walk to each one",
          "what his own string line, straightedge, tape or level read, and the exact spot he read it",
          "the sheet he read the finish off, by number, revision and issue date",
          "where he watched it pump, under which truck, and what he saw where the wheels sat",
          "where water stood, on which date, and how long it stayed",
          "how long the base has sat in that state and who has been driving on it",
          "which sections he is standing down on, and what that stops behind him"
        ],
        "sections": [
          { "h": "The base, and how to find it again",
            "r": "The sections by the name the crew actually uses — the north lot, the drive to the dock, the strip along the building, the entrance off Pell — and a second address anybody can follow once the cones are gone: curb return, light pole, catch basin, building corner, door number. Say what each is meant to become, in his words: full-depth, overlay, a patch, the drive aisle, the row by the pharmacy. Then the photographs, listed by what each frame shows, with something fixed in every one — a hydrant, a pole base, a sign post — because a picture of base rock in a field of base rock locates nothing a month on, when every section looks alike." },
          { "h": "What my string line read, and where I stood",
            "r": "The tool named on every number: string line and line level off the top of curb, a ten-foot straightedge laid across the aisle, a tape off the gutter lip, a rotary laser off a stated bench, a level on the walk. Say what he took as his reference and where it is, because half of every grade argument is two men off two different curbs. Then reading by reading with the place attached — against the gutter at the northeast return, across the aisle at the dock, at the low corner of the island, at the walk by door B. Say whether he read against a curb already poured or against a stake somebody set. Every number here is his, taken with a named tool, at a named spot, and none of them is a thickness or a lift." },
          { "h": "What my sheet says, and where the sheet is",
            "r": "The drawing HE was issued, quoted rather than summarised: sheet number, revision, issue date, and the note or spot elevation covering the section he is standing in. Attach the page and mark the spot. If the section detail or the striping sheet matters here, they ride as addresses only — sheet, detail, rev, as their own document numbers them — never retyped and never reduced to a thickness. Say who issued it and whether he has been told of a newer revision he has not been given. If the base and the sheet disagree, that disagreement is now two documents standing next to each other instead of one man's opinion." },
          { "h": "Where it pumped, and what I watched",
            "r": "Only what he stood and saw, with the truck named. The water truck, a loaded ten-wheeler, the roller, the paver on its own tracks — which one, where it crossed, and what the base did under the wheels: moved, rutted, pumped, held. Where the ruts are and how deep by his own tape, photographed with the tape in the rut. Whether anybody from the lab was standing there and what they were doing, by name and company. Describe it and stop. Whether the base passed a proof roll is a sentence that lives in the lab's numbered report and nowhere else, and the day he writes it himself is the day it becomes his." },
          { "h": "Where the water sat",
            "r": "Every low spot as a place, not a slope: where the water stood, which morning, how long it stayed, and what it looked like when it left — a film of fines, a soft ring, a rut full. Photograph each one from a fixed point with something in the frame that will still be there when the argument happens. Say whether the sheet draws a drain, a swale or a curb cut there and whether it is in. Say which way he saw the water go when it went. No slope number of his appears in this paragraph; a birdbath is a place with a date on it." },
          { "h": "How long it has been like this, and who has had it",
            "r": "The history that gets forgotten first. When was he told the base would be his, in writing or in the huddle, and by whom. What has run across it since: the concrete trucks for the curb, the mason's forklift, trade parking, a laydown for the steel, the conex somebody dragged across it. Whether it has been rained on and driven while wet. Who has had the section before he showed up, by company. This is the paragraph that decides whether the fix is a grader and a morning or a rip-out and a re-import, and it is the first one memory throws away." },
          { "h": "What I cannot do until somebody answers",
            "r": "Which sections he is holding and which he is proceeding on, as a list of sections rather than a wave at the lot. What is already ordered against them — the plant order by its number and time, the trucks, the crew called for the morning — and when the plant wants a cancel by, in his words. What the hold does behind him: the striper lined up for Thursday, the owner's opening on that end, the tenant notice already sent. Then a request for direction with a date on it, not a demand for a remedy. How this gets fixed and who pays is the GC's call, and the letter exists so he can make it with a string line reading in front of him." }
        ]
      },
      {
        "id": "under-my-mat-now",
        "name": "What's Under My Mat Now",
        "aka": ["valve box under the mat nobody raised", "sleeve i was never told about under the paving", "lid paved over who told me", "crossing list against what i found", "iron not raised before we paved", "the base rolled over somebody's conduit", "found a cleanout under the mat", "sleeves and lids under my base notice", "who owns the box under my asphalt", "paved over a monument", "landscaper's sleeve never marked"],
        "family": "notice",
        "from": "the paving foreman who walked the crossing lists",
        "to": "the GC super and our PM, copied to whoever's iron or pipe it is",
        "why": "He is the last trade in, and everything anybody else left under the base is his the minute the mat goes over it. Before the base rolls, a lid is a riser and ten minutes and a sleeve is a length of pipe with two caps somebody marks past the edge. After the mat it is a saw cut, a patch that will always be a patch, and an argument about whose day it costs. He asked for the crossing lists, walked them, painted every lid he could find, and rolled the base on a dated morning — and something still came up under his rake. This letter sets what he was told against what he found, with the day the base rolled sitting between them.",
        "note": "This is two lists and a date. It quotes the crossing lists and lid counts HE was handed, in their own words, by the man who sent each one and the day it came, and sets them beside what his crew found and the date the base rolled and the mat went down. It never gives a cover depth, a separation, a sleeve size or a riser detail; it never says who should have raised what as a matter of contract; and it never says the mat is defective over any of it. A box under the mat is named the way HE found it — where, how, with what — and the utility sheet rides as an address. There is no price in it either: what a saw cut and a patch cost is a ticket, written once this one has established who knew what, and when.",
        "omit": "THE LIST HE WAS HANDED, WITH ITS DATE AND THE MAN'S NAME, BESIDE THE DAY THE BASE ROLLED. Everybody writes \"there's a valve box under the mat and the landscaper never told me about his sleeve.\" Almost nobody writes \"Ray T., <company>, texted me his crossing list on <date>, four sleeves, and walked three of them with me on <date> — the fourth he said was 'by the sign' and nobody flagged it; the water valve box at the drive entrance was on nobody's list; the base rolled on <date> and the mat went down on <date>; I found the lid under the mat with my own rake at <time>, photographed with the rake in the picture.\" The first is a grievance, and grievances get split down the middle. The second is a message with a name on it beside a roll date, and there is nothing left to negotiate.",
        "needs": ["when", "who"],
        "halt": "Only if he cannot produce the lists he was actually sent, or say he asked for one and got nothing — a sleeve somebody mentioned at the gate is not a crossing list, and a letter without the message behind it teaches the super to discount the next one, which will be the expensive one. The lists, their dates and the names they came from go first; the letter is built on top of them. If nobody sent him anything, that is a real answer and it goes in the first paragraph.",
        "facts": [
          "every crossing list and lid count he was handed: who sent it, when, and by what means, quoted",
          "the date he walked each one and with whom, and what he painted on the base",
          "the date the base rolled and the date the mat went down, section by section",
          "what came up that was on no list, where, and how he found it",
          "what is under the mat now and what is still open, item by item",
          "the direction he needs, and the date he needs it by"
        ],
        "sections": [
          { "h": "What I was told, and who told me",
            "r": "Every list quoted as it came in, not summarised: the date, the time if the phone shows it, the means — a text, an email, a photo of a marked-up sheet, a printout handed across at the huddle, a walk with a can of paint — and the man it came from, by name and company. Attach each one. Landscape's sleeves, the electrician's conduit to the pole bases, low-voltage's pipe to the gate, the plumber's cleanouts, the water company's valve boxes, the surveyor's monuments. A list that came twice and a list that never came read very differently, so say which. If a trade said 'nothing of mine in your section', write that down with the name too — it is the most useful sentence in the letter." },
          { "h": "What I walked, and what I painted",
            "r": "The date his crew walked each list and who from the other outfit walked it with him. What he found at each spot: the sleeve end sticking out past the base edge and capped, a lid at grade, a lid low, a stub-up, nothing where the list said. What he painted on the base and photographed before the roller went over it — the paint is the record, and a photo of it with a pole in the frame is the only proof the mark was ever there. Say which items he raised himself, which he was told not to touch, and which he flagged to the super, by name and date, as not his to raise." },
          { "h": "The day the base rolled, and the day the mat went down",
            "r": "Two dates per section, and who was standing there for the other outfits when it happened. The date the base was fine-graded and rolled, the date the tack went down, the date the mat was laid. Whether anybody came out that morning to check their iron. Whether anybody called him after the roll to say they had something in there. The gap between the last list he got and the roll date is the space this letter lives in, so write it out as days rather than leaving somebody else to count it." },
          { "h": "What came up, and how I found it",
            "r": "Item by item, using the same names the lists used, so the two read against each other without a translation. A lid under the mat found with a rake, a magnet, a probe, a sunk spot after the roller. A sleeve end found under the base edge by the laborer setting the string. A box crushed by the roller. Conduit turned up by the grader. Where each one is, by section and by a second address, and what it looks like now, photographed with the tool that found it in the frame. Say plainly which were on a list and missed, which were on no list at all, and which were marked and driven over by somebody after he marked them. Those are three stories with three different owners, and the letter is worth nothing if it blurs them." },
          { "h": "What is under there now, and what is still open",
            "r": "One line per item. What it is, whose it is by company as he understands it, whether it is under base, under tack or under mat, and whether it is still reachable. Which lids he can still raise before the mat and which are gone under it. What it takes to get at each one, stated as work and never as money: a core for a lid, a saw cut and patch for a box, a riser set before the mat goes over, a bore for a sleeve that never went in. Then what each one does to his own day: a section he cannot pave, a striper he cannot bring in, a patch that will always be a patch on an owner's front lot." },
          { "h": "What I need, and by when",
            "r": "One ask with a date on it. Direction in writing on each item: raise it, cut it, core it, leave it and note it on the record. Whose scope it lands in and who is doing it, because the man with the riser is not on his payroll. What he is doing meanwhile — paving the sections that are clear, holding the drive, keeping the roller off the box. And what the plant order does if the answer is late, as a date and a time the plant wants a cancel by, rather than a warning. Ask for it by email so it lands somewhere other than a corridor, and close there." }
        ]
      },
      {
        "id": "the-day-we-couldnt-pave",
        "name": "The Day We Couldn't Pave",
        "aka": ["rained out paving crew lost day", "cancelled the plant order sent the crew home", "loads on the road when we called it", "paving crew stood down base not ready", "idle paving crew write up", "showed up to pave and the lot was full of cars", "trucks could not get in lost the day", "plant order cancelled who called it", "non productive day paving crew", "lost paving day the base was wet", "crew and paver sat all morning"],
        "family": "notice",
        "from": "the paving foreman who had the crew and the order",
        "to": "our PM, and the GC super the same day",
        "why": "A lost paving day is the most expensive lost day on the rack and the fastest to disappear. The crew, two rollers and the paver were on site at dawn, the plant had an order with a time on it, and somebody — him, the super, the sky — called it. By noon the cars are back on the lot, the base has dried, and the only thing standing that says six men and a plant order stood there is a cancel he made by phone. Worse than on most trades, the plant does not stop its clock when he stops his: two trucks were loaded and rolling when he called, and the plant's paper says so. A day written up that afternoon, with the plant's name in it and the super told while he could still walk to the base, is evidence. The same day rebuilt from timesheets in month three is arithmetic, and arithmetic loses.",
        "note": "This records a condition, a call, a notification and the disposition of hours and trucks. It names what stopped him in flat physical terms — \"standing water the length of the dock aisle and cars in rows A and B\" — and never states a weather threshold, a surface temperature or an air temperature minimum: the call was HIS, in his words, at a time. It never says a trade is behind, never assigns fault, never says the base was unpaveable as a verdict. Loads are counted as trucks he watched come in and go back, by ticket number as an address, and never turned into tonnage against an area or a short-load claim. There are no dollars in it. It quotes what people said instead of characterising them, because the version with quotation marks survives being read out loud.",
        "omit": "WHO CALLED IT, AT WHAT TIME, AND WHAT THE PLANT WAS TOLD. Everybody writes \"rained out, lost the day, six men.\" Almost nobody writes \"crew of six on site 5:45 with the paver and both rollers; plant order <number> for 6 a.m.; standing water the length of the dock aisle when I walked it at 5:50, photographed with a cone in it; I called it at 6:05 — my call, my words — and phoned the plant at 6:10, spoke to <name>, cancelled the order with two trucks already loaded; those two came in and we dumped them at the stockpile, tickets <numbers>; told <name, GC> at 6:15 by text; held four to 8:00 sweeping and setting iron, released two; 28 hours on the clock against 10 productive.\" The first is a number a GC talks to zero by lunch. The second is a ledger with the plant's name in it, and its honest half is what stops anybody attacking the rest.",
        "needs": ["when", "who"],
        "halt": "Only if the crew was never actually on site and the plant never held an order — a day he chose not to man because he heard the base was wet is a scheduling call, not an impact, and dressing it up as one is how a man loses the next three that are real. If he stayed home, what he owes is a heads-up about the condition and a date he is coming, which is a different letter in this library.",
        "facts": [
          "the date, the crew by name and count, the machines on site, and the hours on the clock",
          "the plant order by its number and time, and who placed it",
          "the condition that stopped them, photographed while it still existed",
          "who called it, at what time, in whose words — and who at the plant was told, when",
          "the trucks that came anyway, by ticket number, and where they went",
          "what work was found instead, and how many hours were genuinely productive"
        ],
        "sections": [
          { "h": "Who was here, and what we came to lay",
            "r": "Date, day of the week, the crew by name and classification, time on and time off, and the iron on site: the paver, the rollers, the skid steer, the water truck, the tack truck. The sections they were sequenced to pave that day, by the names the crew uses, and where the sequence came from: his own look-ahead, the GC's schedule by activity name, a direction from the super with a date on it. Then the plant: the order number, the time it was called for, who placed it and when. A crew that turns up with a written plan and a plant order and gets stopped is a different story from a crew that turns up and wanders, and the order is the only thing that makes the first one provable once the day is gone." },
          { "h": "What stopped us",
            "r": "The condition in physical terms and in the crew's own words. Water standing the length of the aisle. Base still soft where the water truck crossed it yesterday. Rain on the radar and the sky black over the plant — his call, his words, no number of his about the temperature or the surface. Cars in rows A and B and a conex on the drive. The haul route blocked by the mason's boom. No lab on site and the super wanting one. Curb not cured, the crew not allowed against it. Lids not raised. No set at the right rev. Photograph every one with a timestamp and something fixed in the frame, because a picture of wet base proves nothing about which section or which morning." },
          { "h": "Who called it, and when",
            "r": "The single most important sentence in the document, written plainly: who made the call to stop, at what time, and how he said it. If it was him, say so — \"my call, at 6:05, base too wet to pave, in my words\" — and never dress it up as anybody's threshold. If it was the super, the owner, the lab or the plant, name them and quote them. If it was the sky, say what the sky was doing and who was standing there when he said it. Then the plant: who he spoke to, at what time, what he said, what they said back, and whether trucks were already loaded. The plant's own paper carries a time, and his has to match it." },
          { "h": "Who I told, and what came back",
            "r": "The super by name and company, the time, and the means: at the base, by text, at the seven o'clock huddle, by email that morning. What came back, quoted rather than characterised — \"get the cars off and we'll try after lunch\" is a quote with a promise and a clock inside it; \"he shrugged\" is an argument he loses. If the notice was verbal, put a text behind it inside the hour so the timestamp lives outside his own head. Note anyone else standing there, with a company beside the name." },
          { "h": "The trucks, and where they went",
            "r": "Every truck that was on the road when he called it, by ticket number and by the plant's time stamp, and what happened to each: turned around at the plant, came in and dumped at a stockpile he names, sent to another job, laid as a patch somewhere useful. Say who authorised the stockpile and where it is. Tickets ride as addresses and nothing more — no tons against an area, no short-load claim, no yield arithmetic. Say whether the plant said anything about a charge in their words, and stop there; what the plant bills is the office's conversation, and this is what makes that conversation short." },
          { "h": "What we did with the time",
            "r": "The honest ledger, and the paragraph that buys the document. Hours held on site, hours released, who went home and at what time. Then every scrap of work genuinely found instead: sweeping the base, setting risers, painting lids, stringing the curb, moving cones, pulling the striping layout on the section that was dry, servicing the paver. Man-hours on the clock stated against man-hours actually productive, both written out. A write-up admitting ten of twenty-eight hours got used is one nobody attacks; one claiming all twenty-eight is one somebody attacks for a week." },
          { "h": "What it moves",
            "r": "Which sections slid and where they land now. Whether the crew absorbs it inside the same week or the sequence has to be rebuilt around the plant's calendar, and what it does to the people behind him: the striper lined up against a mat that is not there, the owner's opening on that end, the tenant notice already out for a closure that will not happen. Then the ask: the condition cleared, a date to come back with a plant order behind it, somewhere to work meanwhile. Ask for the date in writing. There are no dollars in this document; there is a day, and it is the stack of dated days that carries an argument." }
        ]
      },
      {
        "id": "laid-out-doesnt-fit",
        "name": "Laid Out, Doesn't Fit",
        "aka": ["stalls don't fit the sheet", "layout does not match the striping plan", "stall count off from the drawing", "accessible pair does not fit where drawn", "pole base in the middle of a stall", "chalked it both ways who decided", "striping sheet against my tape", "the run is short one stall", "painted it as the civil told me", "layout discrepancy record striping", "sheet says fourteen tape says thirteen"],
        "family": "verification",
        "from": "the striper who laid it out",
        "to": "the GC super, the civil and the owner's rep, copied to our PM",
        "why": "Paint is the one thing on a lot that everybody can count. The day the sheet says fourteen and the curb has room for thirteen, whoever holds the striper is about to make a decision that belongs to the civil and the owner, and the moment the paint is down it is his decision — the grind-out is his, the re-paint is his, and the accessible pair that ended up where his rake put it instead of where the sheet put it is a conversation with somebody in a suit. The chalk is cheap and the paint is not. This is the record of what the sheet drew, what his tape found, what he chalked, and who told him which one to paint, written before the first stall and finished after the last.",
        "note": "This is the sheet quoted and the tape reported, section by section, and the name of the man who decided. It never states an accessible-stall count of its own, a stall or aisle dimension, a slope, a sign height or a symbol spec, and it carries no count table: what the sheet draws is quoted by sheet, revision and issue date, what his tape found is stated as his, and the difference is handed to the civil and the owner as a question. It never says a layout complies or does not, never says the lot has enough of anything, and never says who was wrong. Where the accessible pair does not fit as drawn, it says so and stops until a named person answers. The fire lane, if the sheet draws one, is quoted the same way and the fire marshal's word rides as a name, never as ours.",
        "omit": "WHICH ONE THEY PICKED, WHO PICKED IT, AND HOW HE HAS IT. Everybody writes \"the stalls didn't fit so we adjusted.\" Almost nobody writes \"C-201 rev 3, issued <date>, draws 14 stalls along the north curb with the accessible pair at the east end; my tape off the curb return reads room for 13 at the width the sheet gives — the pole base eats one; I chalked it both ways and photographed the chalk at 7:20; <name, civil> came out at 9:10 and said 'shift the run west and drop the last stall, leave the pair where it's drawn,' and I have that in his text at 9:14; painted it as he said it, starting at 10:30.\" The first sentence makes the layout his. The second puts a sheet, a tape, a name and a text in front of the paint, and he is the man who painted what he was told.",
        "needs": ["where", "who"],
        "halt": "Only if he has not yet put a tape on the curb and the sheet side by side — a run that looks short is a feeling, and ten minutes with a wheel and a chalk box turns it into a question somebody can answer. And if nobody has answered yet, this is not the document: it is an ask for a decision before paint, which is the pinned page in this kit, and this record is what he writes once the answer is in and the paint is down.",
        "facts": [
          "the sheet he laid out off, by number, revision and issue date, and who issued it",
          "section by section: what the sheet draws there, quoted, and what his tape found",
          "what is in the way at each spot, named — a pole base, a lid, a hydrant, a lip",
          "what he chalked, photographed before paint, and when",
          "who decided, in their words, by what means, and at what time",
          "what he painted, when, and what is still not painted waiting on an answer"
        ],
        "sections": [
          { "h": "The sheet, and where the sheet is",
            "r": "The drawing HE laid out off, quoted rather than summarised: sheet number, revision, issue date, and who handed it to him. Attach it. Say whether he was told of a newer revision and whether he has it. If a stall count, an accessible pair, an arrow, a crosswalk or a fire lane is drawn on it, it is quoted as the sheet draws it — never restated, never counted up into a table, never compared to anything but his tape. Whatever the sheet is silent on, say it is silent. Two men can point at one line on a numbered sheet; nobody can point at a summary." },
          { "h": "What my tape found, section by section",
            "r": "One run at a time, by the names the crew uses — the north curb, the row by the pharmacy, the drive aisle to the dock, the end cap at the island. For each: what the sheet draws there, quoted; what his tape, wheel or string found, as his reading; and where he measured from, because a run measured from the curb return and a run measured from the pole base are two different runs. Say what is in the way at each spot, physically: a light pole base, a hydrant, a lid, a curb return that came in wider than drawn, a lip at the walk, water sitting where the aisle goes. Photograph the tape on the curb at each one. No dimension of his appears as a rule; every number is what the sheet gives or what he measured." },
          { "h": "The accessible pair",
            "r": "Its own paragraph, because it is the one place the page stops and waits. What the sheet draws for it — where, how many, with what beside it — quoted. What his tape found at that spot and what is in the way. Whether the pair fits as drawn, in his words, and if it does not, what he asked and of whom, with the time. He states nothing about how many the lot needs, how wide anything must be, what the slope may be or what the sign says; those answers have a stamp on them and a name under the stamp. If the answer came, quote it with the name and the means. If it has not come, this paragraph ends with the question and the date he asked it, and the paint waits." },
          { "h": "What I chalked, and when",
            "r": "The chalk is the record. What he laid out in chalk, both ways where he laid it both ways, photographed from a point he names before any paint, with the time on the photo and something fixed in the frame. Which version the super, the civil or the owner walked, by name and time. The chalk photograph is the one piece of evidence in the whole document that exists only because he thought to take it; a week later the paint has covered it and the argument is about paint." },
          { "h": "Who decided, and how I have it",
            "r": "By name and company, at what time, by what means — at the curb, by text, by email, a marked-up sheet handed back. Quoted rather than characterised: \"shift it west and drop the last one\" is an instruction with a name on it; \"he said it was fine\" is nothing. If it came verbally, the text he sent back inside the hour confirming it in his words, attached. If the answer was \"paint it as drawn\", say so and say who said it, because that sentence is the one he needs in writing more than any other. If more than one person answered and they disagreed, quote both and say whose he followed and why." },
          { "h": "What I painted, and what is waiting",
            "r": "Section by section: painted as drawn, painted as answered, or not painted. The date and time paint started on each run and who was on the striper. What is chalked and waiting on an answer, by run, and who owes the answer. What that hold does behind him: a lot that opens Monday with a row unpainted, a tenant notice already out, a second night on the closure. Then the ask with a date on it. Nothing here says the layout is right, complete or compliant; it says what the sheet drew, what his tape found, who decided, and what is on the mat tonight." }
        ]
      },
      {
        "id": "cars-on-my-section",
        "name": "Cars On My Section",
        "aka": ["car drove through the fresh seal", "somebody moved my cone and drove in", "tracks through the new sealcoat", "tenant parked on wet paint", "drove on the mat before it cooled", "cones moved on the closed lot", "vehicle on fresh striping write up", "who let the car in tonight", "tire marks across the closed section", "night man moved the tape", "fresh seal tracked by a car"],
        "family": "incident",
        "from": "the foreman whose section it was",
        "to": "the property manager or GC super the same night, and our office",
        "why": "On an occupied lot the cones are the contract. He closed a section, told a named person, photographed the tape across both entrances, and at some point in the night a cone was on the island, the tape was on the ground and a car had driven two rows across fresh seal to the door somebody always uses. By morning the tracks are in the finish, the car is gone, and whoever moved the cone is the one person who will never say so. The only thing that separates \"your seal job is streaked\" from \"a car came through your closure\" is a photograph of the closure standing, with a time on it, taken before the car.",
        "note": "This describes what he set out, what he found and what he was told, and does nothing else. It never records a license plate, never names a tenant off a roster, never authorises or requests a tow, and never says anybody is liable — the car is described as he saw it, by colour and kind off the door, and the person who moved a cone is a quote, not an accusation. It gives no cure time, no dry time and no statement of when the seal or the paint would have been ready: what he told them about keeping off is quoted from his own spec sheet in his own words. It does not say the section was finished or accepted, and it does not price the re-do; it says the closure stood at a time and a photograph shows it.",
        "omit": "WHAT THE CLOSURE LOOKED LIKE BEFORE THE CAR, PHOTOGRAPHED, WITH THE TIME. Everybody writes \"somebody drove through the fresh seal and tracked it.\" Almost nobody writes \"cones and tape across both entrances to the north half at 6:40 p.m., photographed from the drive with the pharmacy sign in the frame; at 9:25 p.m. a silver SUV came in past the east entrance — the cone was on the island and the tape was down — and drove two rows to the door by the pharmacy; tracks from the entrance to row C, photographed at 9:30 with my wheel in the frame; the building's night man <name> told me at 9:40 'somebody moves that cone every night to get to the pharmacy door'; I re-set the cones and texted <name, property manager> at 9:45.\" The first is a complaint about a streak. The second is a before, a time, a track and a quote, and it never once needed a plate.",
        "needs": ["before", "when"],
        "halt": "Only if he has no record of the closure standing before the car — no photo, no text to a named person saying the section was coned, nothing with a time on it. Without a before, this is a condition report about streaks in his own seal, and it belongs in his own field log until he has something that shows the cones were up. If he has even a text at 6:40 saying \"north half closed, cones up\", write it tonight with that.",
        "facts": [
          "the section, by name and by a second address, and what was on it — seal, paint, a mat still warm",
          "the closure as he set it: cones, tape, signs, which entrances, photographed, with the time",
          "what he found: the cone, the tape, the tracks, where they run, photographed with the time",
          "the vehicle as he saw it, by colour and kind — never a plate",
          "who moved what and who said what, by name, quoted, with the time",
          "who was told that night, at what time, and what came back in their words"
        ],
        "sections": [
          { "h": "The section, and what was on it",
            "r": "Which part of the lot, by the names the crew and the tenants both use, and a second address a stranger can walk to — the rows by the pharmacy, the north half from the drive to the fence, the aisle to the dock. What was on it and when it went down: seal, the second coat, layout paint, a mat that was still warm. What he told the property manager about keeping off, quoted from his own sheet in his own words, and when he told them. Nothing here says how long anything needs; it says what he said." },
          { "h": "The closure as I set it",
            "r": "The before, and the whole document rests on it. Cones, tape, barricade stands, signs, which entrances and which doors, and how many of each. The time he finished setting it and the photographs from a fixed point with something in the frame that proves which lot and which evening — a sign, a storefront, a light pole. Who he told it was closed, by name, at what time, by what means, and what they said back. Whether the tenants were told and by whom. If a door had to stay open for somebody, say which one, who asked, and what he set to protect it." },
          { "h": "What I found, and when",
            "r": "The time he found it and what he was doing there — a walk at the end of the shift, a call from the building, the morning check. Then physically: which cone was moved and where it was sitting, whether the tape was down or cut, which entrance the tracks come in from, which rows they cross, where they end, and whether the car was still there. Photograph the tracks from the entrance and from the end with his wheel or a cone in the frame so the run reads, and photograph the moved cone where it sits before he touches it. Describe the finish where the tires went — pulled, streaked, printed — and stop. No verdict on what it needs; that is the next document." },
          { "h": "The car, and who I talked to",
            "r": "The vehicle as he actually saw it: colour, kind, a company name off the door if there is one, where it was parked, whether the driver was there. The plate stays off this page — a plate is the property manager's business and the tow list is theirs, and a document with a plate on it gets forwarded to places he does not want his name. Then everybody he talked to that night, by name and company: the night man, the security guard, the tenant at the door, the driver if he found him. Quoted, with the time. \"Somebody parks by the pharmacy door every night\" is a sentence somebody volunteered, and it is worth ten paragraphs written after everybody has had a week to think." },
          { "h": "Who I told, and what I did",
            "r": "The property manager or the super by name, the time, the means — a text with the photos attached is the right one, because the timestamp lives outside his phone. What came back, quoted. Then what he did on the spot: re-set the cones, doubled the tape at that entrance, put a stand in the door, sat a man on it, left it. What he is asking for, each with a name: the tenants told again by somebody with authority, the door people actually use covered, a name who moves a car at seven in the morning, nobody pulling a cone before he says. No price for the re-do here. The ticket is a separate document, and this is what makes it stand up." }
        ]
      },
      {
        "id": "tracked-inside",
        "name": "Tracked Inside",
        "aka": ["sealcoat tracked into the lobby", "black footprints in the building", "paint tracked in on their shoes", "seal on the lobby floor who walked it", "tracked seal into the elevator", "cleaning crew walked through the seal", "tenant tracked it into the store", "footprints from my section into the door", "seal on the carpet write up", "the door we coned got used", "sealer inside the building record"],
        "family": "incident",
        "from": "the foreman who closed the section",
        "to": "the property manager and the tenant contact the same morning, and our office",
        "why": "A lobby floor is the one piece of the job he never bid and can lose in a night. Somebody — the cleaning crew at five, a tenant with a key, the delivery driver who always uses that door — walked across fresh seal, through the door he coned, and left a line of black prints from the mat to the elevator car. By eight the building engineer has photographed it, the tenant has an opinion about the carpet, and the only question anybody is asking is what it costs. Whether that floor was clean when his crew arrived, whether that door was coned, and who walked it with him before anybody touched a print — those three facts decide whose morning it is, and all three are gone by nine.",
        "note": "This records the floor as it was before his crew opened a bucket, the closure at that door, what he found, who walked it with him, and what he did — and nothing else. It never names a cleaning product, a method or a result as a specification: what he used and what it did is stated in his own words as what he did, off the can, never as advice. It never says the floor is ruined or restored, never says who is liable, never quotes a price and never records a plate or a tenant off a roster. The person who came through the door is a quote from whoever saw them, by name, and no more. It does not say the section was finished or the seal was ready; it says what his sheet told him and when he told them.",
        "omit": "THE FLOOR BEFORE HIS CREW SHOWED UP, PHOTOGRAPHED, AND WHO WALKED IT WITH HIM. Everybody writes \"some seal got tracked into the lobby and we cleaned it up.\" Almost nobody writes \"the B lobby floor photographed at 5:50 p.m. before we opened a bucket, with the mat at the door and the two old scuffs by the elevator in the frame; at 7:05 a.m. <name, building engineer> called me to the B lobby — six black prints from the door to the elevator and one in the car; I walked it with him at 7:20 and we photographed each one before anybody touched it; the door had been coned and the tape was on the ground; <name> said 'the cleaning crew came in through that door at five'; I had <crew name> on it by 7:45 with <what he used, off the can>, and the door mat went in my truck.\" The first is a floor everybody now owns. The second is a before-picture, a name beside him, and a quote, and it was all gone by nine.",
        "needs": ["before", "who"],
        "halt": "Only if nobody from the building walked it with him before anything was touched and he has no before-picture of the floor — a lobby he cleaned alone at six with no witness and no before is a floor he now owns, and writing it up as anything else teaches the property manager to discount the next one. If he has the before-picture and no witness, write it with that and say so plainly; an honest gap holds up fine.",
        "facts": [
          "the door and the floor, by name, and what they looked like before his crew arrived, photographed with the time",
          "how that door was coned and taped, and who was told it was closed",
          "what he found: the prints, where they run, how many, photographed before anybody touched one",
          "who walked it with him, by name and company, and at what time",
          "who came through, as somebody said it, quoted with the name",
          "what he did, in his own words, and what he is asking for"
        ],
        "sections": [
          { "h": "The door, and the floor before we started",
            "r": "Which door, by the name people use for it — the B entrance, the pharmacy side door, the loading dock man-door — and what is inside it: tile, carpet, a mat, an elevator car, a stair. What it looked like before his crew opened a bucket, photographed with the time and something fixed in the frame, the old scuffs and the existing stains included, because the one thing a property manager remembers a week later is that the floor was perfect. If he did not take a before-picture, say so, and say what the floor looked like in a sentence; that honest sentence is worth more than a guess." },
          { "h": "How that door was closed",
            "r": "Cones, tape, a stand in the door, a sign, a man — what he set at that door, when, photographed. Who he told that door was closed, by name and time, and what they said back. Whether anybody asked for that door to stay open and who. Whether the cleaning crew, the night security or the delivery route was named to him as using that door, by whom, and what he did about it. The sentence that decides this document is whether the people who use that door were told by somebody with the authority to tell them, and whether he has that in writing." },
          { "h": "What I found, and who walked it with me",
            "r": "The time he was called and by whom. Then the prints: how many, from where to where, which surfaces — tile, carpet, the elevator floor, a stair tread — photographed one by one before anybody touched them, with the time on the photos and the door in the first frame. Who walked it with him, by name and company, at what time: the building engineer, the property manager, the tenant's manager, the janitorial lead. What each of them said, quoted. A print photographed with the building engineer standing beside it is a record; a print he photographed alone after cleaning half of them is a story." },
          { "h": "Who came through, as somebody said it",
            "r": "Only what he was told and by whom, quoted with the name and the time — \"the cleaning crew comes in that door at five\", \"the pharmacy manager has a key\", \"the bread truck always uses the B side\". If the building has a camera and somebody offered to look, say who and when; do not say what it shows unless he saw it with them. No plate, no tenant off a roster, no name of a person he did not talk to. An honest \"nobody knows who came through\" holds up. A guessed name loses the document." },
          { "h": "What I did, and what I need",
            "r": "In his own words as what he did: who he put on it, at what time, what he used off the can, what came up and what did not, what he pulled — the door mat, a runner — and where it is. Never as a method anybody should follow and never as a verdict on the floor. Then who he told when he was done and what they said, quoted. The asks, each with a name: the door covered tonight by somebody who can tell the people who use it, a walk with the property manager before the tenants open, a name for whoever decides what happens to the carpet. No price here; the ticket, if there is one, is a separate document, and this is what makes it stand up." }
        ]
      },
      {
        "id": "the-lot-i-handed-back",
        "name": "The Lot I Handed Back",
        "aka": ["cones off what i told them", "cars back on the lot when i said", "reopened the section record", "closure lifted who i told", "north half back to them in my words", "what i told the property manager when the cones came off", "pulled the cones this morning", "handed the lot back after the seal", "keep the sweeper off it what i said", "lot back to the tenants note", "cones came off at six"],
        "family": "verification",
        "from": "the foreman opening the section back up",
        "to": "the property manager or GC super, the tenant contact, and our office",
        "why": "The cones come off at six and by seven the lot is theirs — the sweeper, the delivery trucks, the dumpster truck with its outriggers, the tenant who parks in the same spot every day. Everything that happens to that surface from then on happens under somebody else's keys, and the first question in every argument in October is what he told them when he handed it back. Not what the can says; what HE said, off his own sheet, to a named person, at a time, with a photograph of the rows before the first car. The half of this record that does the work is the list of what he asked them to keep off it and for how long in his own words — because a lot nobody was told about is a lot with tire prints in it by lunch and his name on the callback.",
        "note": "This is a time, a name, a photograph and his own words, and it makes no promise about the surface. The cones came off at a stated time. A named person was told, by a stated means, and what they were told about keeping trucks, the sweeper and the cars off is quoted from HIS spec sheet in his words — never a cure time, a dry time, a product's open-to-traffic figure or a manufacturer's number restated as ours; the manufacturer's time is theirs to state. It never says the lot is accepted, complete, finished or warrantable, never says the work is done, never says the striping complies with anything, and never declares the fire lane or the accessible pair to be anything but where the sheet drew them and the civil answered. What is still coned and why is listed. It is the record of a hand-back, not a release.",
        "omit": "THE TIME THE CONES CAME OFF, WHO HE TOLD, AND WHAT HE TOLD THEM IN HIS OWN WORDS OFF HIS SHEET. Everybody writes \"lot's open.\" Almost nobody writes \"pulled the cones off the north half at 6:10 a.m. on <date> and photographed rows A through D from the drive with the pharmacy sign in the frame before the first car; texted <name, property manager> at 6:12: 'north half is yours; per my spec sheet I'm asking you to keep the sweeper and the trucks off it through <what my sheet says, in my words>; rows A–D striped and dry to the touch when I walked them at 6:00'; the east entrance stays coned until <name> moves the dumpster; <name> told the tenants at <time>, her text attached.\" The first is two words nobody can hold. The second is a time, a name and his own sentence, and nothing in it says the lot is accepted.",
        "needs": ["when", "who"],
        "halt": "Only if he cannot say who he told and when — a lot handed back to nobody in particular is a lot he still owns, and the text to a named person at a stated time is the entire mechanism of this document. If he has the text, everything else in it can be thin and it still works, so write it the same morning with whatever he has.",
        "facts": [
          "the date and the time the cones came off, section by section, and who pulled them",
          "who he told, by name and company, at what time, by what means, and what came back",
          "what he told them about keeping off, quoted from his own sheet in his own words",
          "the photographs of the surface before the first car, from a point he names",
          "what is still coned, why, and who owes the thing that clears it",
          "what he walked and what he did NOT walk, by row"
        ],
        "sections": [
          { "h": "What came off, and when",
            "r": "Section by section, by the names the crew and the tenants use: the north half, rows A through D, the drive to the dock, the east entrance. The time the cones and tape came off each one and who pulled them, by name. The order he opened them in and why — the entrance first so the delivery could come, the rows by the pharmacy last. The photographs from a fixed point before the first car, with the time on them and something in the frame that says which lot and which morning. A photograph of clean rows at 6:10 is the only evidence there will ever be that the first tire print was not his." },
          { "h": "What I told them, in my own words",
            "r": "Quoted, because this is the sentence that comes back in October. What he asked them to keep off the surface and for how long — the sweeper, the dumpster truck and its outriggers, delivery trucks, power steering in a tight spot, a car parked in one place with the wheel cranked — stated as HIS ask off HIS spec sheet, in his words, and never as the manufacturer's figure restated as ours. If he told them he would text when something changed, say so. If his sheet says something he cannot say in his own words, attach the sheet and say the sheet says it. Nothing here is a cure time or a dry time of ours; it is what he said." },
          { "h": "Who I told, and what came back",
            "r": "By name and company, the time, the means — a text with the photographs in it is the right one, because the timestamp lives outside his phone. What came back, quoted. Whether the tenants were told, by whom, at what time, and whether he has that message; a hand-back the tenants never heard about is a hand-back to nobody. If the super, the owner's rep or the building engineer walked it with him, say who and when and what they said in their words. If nobody came, say so — it is a fact worth more than an adjective." },
          { "h": "What I walked, and what I did NOT",
            "r": "The section that protects him, and it goes in even when it is short. Row by row, what he walked that morning and what he saw: dry to the touch, tacky at the island, a wheel print at the east entrance from the dumpster truck at 5:50 before the cones were off, a stall the striper missed on the end cap. Then what he did not walk and why — the drive by the dock still coned, the rows he could not see in the dark, the section his crew finished after he left. One plain sentence saying nobody has walked those and nobody should say they are ready until somebody does. No verdict on the surface anywhere in this paragraph; what he saw, where, at what time." },
          { "h": "What is still coned, and why",
            "r": "Every cone still standing, by place, with the reason beside it and the name of whoever owes the thing that clears it: the east entrance until the dumpster moves, the accessible pair until the civil answers on the sign post, the drive until the second night's seal, a patch the plant's last truck did not cover. Say what he needs from each name and by when. Say who he told about each one. What the fire lane is and what it needs is the fire marshal's; if the sheet draws one, it is quoted, and the marshal's contact rides as a name he was given, never as a call of ours." },
          { "h": "What the lot still needs from somebody",
            "r": "The asks, each with a name and a date against it. Nobody pulls a cone he left without telling him. Somebody with authority tells the tenants, again, on the day the second section opens. Tell him the day the sweeper comes back so he can say what his sheet says about it. A name who calls him if a truck sits on it. Then the date the owner's own contract says the maintenance or warranty period starts, quoted off the owner's document in its own words and never restated here. Nothing in this paragraph says the lot is accepted, complete or warrantable. It says who has it now, what they were asked, and how to reach him." }
        ]
      }
    ],

  "drop": [],

  /* What this trade dictates that a phone gets wrong. Only real corrections —
     a pair that corrects nothing under a heading claiming it does is the
     failure to avoid, so this list is held to words that actually come back
     mangled off a tailgate next to a running roller. The last pair is the
     only place in this file the mason's word appears, and it appears being
     fixed: the brick is his, the work is ours. */
  "vocab": [
    "seal coat -> sealcoat",
    "sub grade -> subgrade",
    "straight edge -> straightedge",
    "bird bath -> birdbath",
    "tack cote -> tack coat",
    "loot -> lute",
    "matt -> mat",
    "clean out -> cleanout",
    "stub up -> stub-up",
    "hair pin -> hairpin",
    "pot hole -> pothole",
    "over lay -> overlay",
    "blue tops -> blue-tops",
    "ravelling -> raveling",
    "a d a -> ADA",
    "f d c -> FDC",
    "pavers -> paving"
  ],

  /* Trigger-only nudges. They fire when the dictation touches the thing and
     stay silent otherwise. Nine of them, and every one guards a place where an
     AI writing fluent prose would supply a number, a plan or a verdict that
     this trade is not allowed to state. */
  "reminders": [
    { "when": "the mix, a temperature, a density or a thickness", "say": "There is no number on the mat in this kit and there never will be. No mix design, no mix or lay-down temperature, no density, no compaction figure, no thickness, no lift, no tons against an area — not as a value, a typical or a placeholder. The plant ticket and the lab's report ride as numbers on a piece of paper he names, and what they say inside is theirs. Write who called the lab and who was standing there, and stop." },
    { "when": "accessible stalls, the ADA, a stall count or a stall width", "say": "Quote the sheet — number, revision, issue date — for what it draws, and give his tape for what he found at a spot he names. Never write a count the lot needs, a stall or aisle dimension, a slope, a sign height or a symbol; never say the layout complies or does not. Where the two disagree, the sentence is a question to the civil and the owner with a date on it, and the paint waits for the answer." },
    { "when": "the fire lane, a traffic plan, a lane closure or a detour", "say": "The fire lane is the fire marshal's — no length, no width, no marking, no determination of ours; quote the sheet if it draws one and name the marshal's contact he was given. A traffic-control plan, a flagger plan or a detour is an engineered, permitted document: write who holds it, by name, and stop. Nothing here describes one." },
    { "when": "cure time, dry time, or when the cars can come back", "say": "Write what HE told them, in his own words off his own spec sheet, to a named person at a stated time. Never write how long seal, paint or a mat needs, never restate a manufacturer's figure as ours, never suggest a window. The manufacturer's time is theirs to state, and the moment we recommend one the next tire print is ours." },
    { "when": "a proof roll, or whether the base passed", "say": "What he watched, where the truck sat, what the base did under the wheels, photographed — that is the whole paragraph. Never write that a subgrade, a base or a lift passed, failed, proof-rolled or is to spec. That sentence lives in the lab's numbered report and the civil's call, and it never lives here." },
    { "when": "a tow, a plate or a tenant", "say": "No license plate, no tow call and no tenant off a roster, on any document, ever. The car is the colour and the kind he saw and a company name off the door if there is one. The tow list is the property manager's and the plate is their business; write the name of the person who owns that decision and what they said, quoted." },
    { "when": "the weather", "say": "There is no air or surface temperature minimum in this kit. If he did not pave, write \"my call, my words\" with the time he called it, what he saw where he stood, photographed, and who at the plant he told and when. Never write a threshold and never say the day was or was not paveable as a rule." },
    { "when": "a birdbath, a low spot or drainage", "say": "A birdbath is a place he saw water sit — where, on what date, how long it stayed, photographed from a fixed point. Never a slope number, never a drain or swale sized, never a sentence saying the lot will not drain as a conclusion. Say what the sheet draws there and whether it is in." },
    { "when": "the lot being open, done, finished or accepted", "say": "Never a release verdict. The cones came off at a time, a named person was told, the photograph shows the rows before the first car, and what he asked them to keep off it is quoted in his words. Nothing in this kit says a lot is accepted, complete, warrantable or compliant, and the day a document here says it is the day it is his." }
  ]
};
