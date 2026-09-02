/* ELECTRICAL FIELD TOOLKIT — DOCUMENT LIBRARY (shape #4: shared/docspec.js).
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = picker VOCABULARY · docs.js = the WRITE-UPS
 * this trade actually has to produce. The engine owns the eleven blocks of the
 * emitted instruction set and every universal law in them; this file owns what
 * is different about electrical work and nothing else.
 *
 * THREE HARD INVARIANTS (§SAFETY), same as every other data file here:
 *   · ZERO BRAND AND MANUFACTURER NAMES. Generic terms and acronyms only.
 *   · NOTHING IS RATED, SIZED, THRESHOLDED OR JUDGED. No code reference, no
 *     acceptance criterion, no "should be" — not as a value, not as a hint, not
 *     in a placeholder. The tradesman states the reading; nobody here grades it.
 *   · Every `omit` line is a SPECIFIC thing that costs money on THAT document.
 *     "Add more detail" is not an omit line and does not belong in this file.
 *
 * `trade`     the trade word the emitted instructions use ("we do ___ work"). DECLARED,
 *            never derived from the toolkit name — that produced "a AV outfit" and
 *            broke outright on the one trade whose name does not end "Field Toolkit".
 * `docs`      documents specific to this trade (they join the shared library)
 * `overrides` change any field of a SHARED document by id, rather than forking it
 * `drop`      shared document ids this trade genuinely never writes
 * `vocab`     what this trade dictates that a phone gets wrong ("wrong -> Right")
 * `reminders` trigger-only nudges — they fire when relevant and never nag
 */
window.TRADE_DOCS = {
  "trade": "commercial electrical",
  "docs": [
    {
      "id": "field-condition-note",
      "name": "Field Condition Note",
      "aka": [
        "field condition",
        "RFI note",
        "the RFI writeup",
        "conflict",
        "it doesn't fit",
        "clash",
        "existing conditions",
        "unforeseen condition",
        "differing site condition",
        "as-built conflict"
      ],
      "family": "notice",
      "from": "the lead JW",
      "to": "my own PM",
      "why": "Gets the question asked right the first time, with a proposed answer attached, so it comes back in three days instead of three weeks.",
      "note": "their system owns the RFI number and the clock — this is the question, in your words",
      "sections": [
        {
          "h": "JOB / WHERE IT IS / DATE",
          "r": "Job name and number, then building, level, column lines or room number, the system, and the date you're standing there. Somebody who has never been on this job has to find the spot from these two lines alone, and has to find the note itself by searching the job name a year later."
        },
        {
          "h": "WHAT THE PRINTS SHOW",
          "r": "Sheet number, revision and date, and the detail — and what it says is supposed to be there. If an approved submittal or a prior RFI answer governs, name it by number and date. If you don't have the sheet in front of you, say so; never guess a number onto paper."
        },
        {
          "h": "WHAT'S ACTUALLY THERE",
          "r": "The physical condition as it sits. What's already installed, whose it is, and what's in the space. Existing nameplate wording typed exactly as it reads — never decoded, never cleaned up, never re-cased."
        },
        {
          "h": "WHAT DOESN'T LINE UP",
          "r": "The physical conflict, one plain paragraph. It doesn't fit, it doesn't reach, it lands in somebody's duct, the wall isn't deep enough. State the physical fact and stop — no code articles, no fill or ampacity claims, no 'that's a violation'. You say what's there, the engineer says what's allowed."
        },
        {
          "h": "WHAT I'D DO",
          "r": "Your proposed fix, offered as a suggestion, with what it needs — material, access, another trade's work, a shutdown. This is what makes the answer come back fast, because now he can just reply 'yes'. Never write it as a decision already made."
        },
        {
          "h": "WHAT IT'S HOLDING",
          "r": "What's stopped, and the milestone the answer has to beat — before the pour, before the deck, before rock, before the ceiling closes. Something that's actually coming at him, never a date you made up."
        }
      ],
      "omit": "The tape-measure number, and where you measured from. 'There isn't enough room' comes back as 'route as required' and you've lost two weeks. '2-1/8 in clear between the bottom of the duct and the top of the door frame, measured at column line C-4; the run needs 4 in' has exactly one answer. Measure it, type the number, and name the datum you pulled from.",
      "needs": ["where", "count"],
      "halt": "Only if you can't say where it is — no room number, no grid lines, no level. A condition nobody can find is a phone call, not a document.",
      "facts": [
        "job name and number",
        "building, level, grid lines or room number",
        "system and equipment involved",
        "sheet number, revision, date, detail callout",
        "governing submittal or prior RFI, by number and date",
        "the dimension you measured, and the datum you measured from",
        "existing nameplate text, typed as printed",
        "whose work is in the way",
        "your proposed fix and what it needs",
        "what's stopped and the milestone it has to beat",
        "photos and what each one shows"
      ],
      "secondary": [
        "the two-line version that pastes into the PM's RFI question field",
        "the chase note when the RFI is still open and the ceiling is closing"
      ]
    },
    {
      "id": "confirming-note",
      "name": "Confirming Note",
      "aka": [
        "confirming email",
        "per our conversation",
        "confirm the conversation",
        "verbal direction",
        "as discussed",
        "recap email",
        "CYA email",
        "confirming what you told me",
        "memo to file"
      ],
      "standalone": true,
      "family": "minutes",
      "from": "the foreman",
      "to": "the man who said it",
      "why": "A verbal instruction is worth nothing in April. This is the ten-line email that makes it worth something, sent the same hour.",
      "sections": [
        {
          "h": "JOB / WHO SAID IT / WHEN / WHERE WE WERE STANDING",
          "r": "Job name and number first so it comes back out of the mailbox later. Then his name, his company, the date and the clock time, and where you were standing. Anybody else within earshot gets named too — that's your witness, and it costs one line."
        },
        {
          "h": "WHAT YOU TOLD ME",
          "r": "His instruction in HIS words, as close as you can get it, in one short flat paragraph. Never improve it, never sharpen it, never add the part you wish he'd said. If you're not sure of a word, say you're paraphrasing."
        },
        {
          "h": "WHAT I'M DOING ABOUT IT",
          "r": "Exactly what you're doing and when you start. If you're going ahead before it's papered, say that plainly in one sentence — it's a fact, not a confession."
        },
        {
          "h": "WHAT THAT MEANS",
          "r": "The consequences that follow — sequence, other trades, warranty, something else that now has to move, something that becomes an extra. One or two lines, facts only. No dollars."
        }
      ],
      "omit": "The deadline to disagree. Without a cut-off, silence means nothing and the email is just you talking to yourself. With one, silence is agreement, and everybody who has ever argued one of these knows it. Tie it to the moment the work actually starts — 'if that's not what you meant, tell me before we start Thursday morning' — never open-ended, never 'let me know'.",
      "needs": ["when"],
      "halt": "Only if you can't name who said it. An unattributed instruction can't be confirmed to anybody — go get the name first.",
      "facts": [
        "job name and number",
        "his name, company and role",
        "date, time and where you were standing",
        "anybody else who heard it",
        "the instruction, as close to his words as you can get",
        "what you're doing and when you start",
        "whether you're proceeding before written authorization",
        "what it changes for sequence, warranty or other trades",
        "the cut-off for him to say you got it wrong",
        "who to copy"
      ],
      "secondary": [
        "the follow-up when the cut-off passes with no answer"
      ]
    },
    {
      "id": "inspection-result-note",
      "name": "Inspection Note",
      "aka": [
        "inspection",
        "red tag",
        "red-tagged",
        "failed inspection",
        "corrections",
        "AHJ",
        "rough inspection",
        "reinspection",
        "sign off",
        "inspector said",
        "cover inspection"
      ],
      "family": "verification",
      "from": "the foreman who met the inspector",
      "to": "my own PM",
      "why": "Turns 'the inspector wasn't happy' into corrections with names and dates, so the re-inspect happens once.",
      "note": "the AHJ owns the card and its number — this is only what YOU send about it",
      "sections": [
        {
          "h": "JOB / AREA / INSPECTION / DATE / RESULT",
          "r": "Job name and number, what was called for, the area or permit scope it covered, the date and time, the inspector's name, and the result — passed, partial, or corrections — inside the first two lines. That's the search key. Never lead with the words 'Inspection Report'."
        },
        {
          "h": "WHAT HE WROTE, WORD FOR WORD",
          "r": "Type the correction exactly as it reads on the card, or exactly as he said it. Quoted, never interpreted, never expanded, never helpfully completed. If he cited something, type what he wrote and stop there — this tool supplies no article, no table, no number, and never explains what he meant."
        },
        {
          "h": "WHAT THAT MEANS AT OUR END",
          "r": "The physical work that has to change, where, and how much of it, in installer's words. If you disagree, state the fact — 'installed per detail 5/E6.02' — and let the office argue it. Never argue it in this note."
        },
        {
          "h": "THE FIX AND WHEN IT'S READY",
          "r": "What you're doing, who's on it, and the date you'll be ready to call. Say what stays open — nothing gets covered until it's signed. Keep it to a paragraph: if a rough failed with eight corrections, the eight items belong on the punch list, not in here."
        },
        {
          "h": "WHAT'S HELD UP BEHIND IT",
          "r": "What can't proceed until this clears — other trades, the pour, the ceiling, energization — and the milestone that's coming at you."
        },
        {
          "h": "WHEN WE CALL IT BACK IN",
          "r": "Who makes the call, when, and what has to be in place first. One clear ask if you need something from the reader to get there."
        }
      ],
      "omit": "The items on that card that AREN'T yours — named, one line each, with who has to clear them before anybody calls for a re-inspect. Everybody chases their own corrections and nobody chases the framer's, the painter's, or the GC's, so the second inspection fails on somebody else's item and it lands on your schedule anyway. The second failed re-inspect is the one that's on you.",
      "needs": ["who", "notdone"],
      "halt": "Only if you can't say whether it passed, partially passed, or got corrections. That one word changes who reads this and what they do today.",
      "facts": [
        "job name and number",
        "inspection type and what was called for",
        "permit or area scope covered",
        "date, time, inspector's name",
        "result — passed, partial, corrections",
        "the correction text word for word, as written on the card",
        "which items are yours and which belong to other trades",
        "the physical fix required and where",
        "who's assigned and the ready date",
        "what's held up behind it and the milestone it has to beat",
        "who calls the re-inspect and when",
        "whether anything got covered before sign-off"
      ],
      "secondary": [
        "the note that goes out when the re-inspect passes",
        "the heads-up to another trade that they have an item on our card"
      ]
    },
    {
      "id": "controls-startup-note",
      "name": "Controls Startup Note",
      "aka": [
        "controls startup",
        "lighting controls",
        "sequence of operations",
        "SOO",
        "it won't do what the sequence says",
        "vendor startup",
        "controls punch",
        "occ sensors won't hold",
        "programming",
        "demo the sequence"
      ],
      "family": "verification",
      "from": "the foreman on the controls work",
      "to": "my own PM",
      "why": "Controls arguments all die on 'the vendor said it was done.' This is the note that says what was actually demonstrated, what it actually did, and what's still sitting on the vendor.",
      "note": "narrative only — the vendor's own startup paperwork is his and stays his",
      "sections": [
        {
          "h": "JOB / AREA / SYSTEM / DATE",
          "r": "Job name and number, the area by level and room numbers, the system as the drawings name it, and the date. Never lead with the words 'Startup Report'. If all you've got is the job and the date, lead with those — this note gets found a year later by searching the job."
        },
        {
          "h": "WHAT THE SEQUENCE SAYS",
          "r": "The sequence of operations as written, by sheet or spec section and its date, quoted for the part in question. Quote it; never paraphrase it, never finish a sentence it doesn't finish, never supply a setting it doesn't state."
        },
        {
          "h": "WHAT GOT DEMONSTRATED",
          "r": "What was actually walked and switched, zone by zone or room by room — and just as important, what got skipped. 'Levels 2 and 3 walked; level 4 not demonstrated, ceiling still open.'"
        },
        {
          "h": "WHAT IT ACTUALLY DID",
          "r": "What the lights, sensors, relays or panel did when it was demonstrated, in plain words. What you saw and what you heard, not what it means. Never offer a cause and never hand anybody a list of causes to pick from — that's the vendor's to say."
        },
        {
          "h": "WHAT'S STILL ON THE VENDOR",
          "r": "The items that didn't do what the sequence says, by area, and who's coming back for them and when. Name the open item; never write the fix for him."
        },
        {
          "h": "WHAT WE NEED TO CLOSE IT",
          "r": "Access, a night, an occupied space, a ceiling somebody has to leave open, a man with the programming laptop. And the milestone it has to beat — before the ceiling closes, before the owner walks it."
        }
      ],
      "omit": "Who stood there and watched it run. Everybody types 'startup complete.' Nine months later the lights sweep off over somebody's desk at 7 p.m. and the only question is whether anybody from the owner's side ever saw the sequence run in that room. Names, companies, the date, and which zones they actually walked — one line, and the argument is over before it starts.",
      "needs": ["when", "who", "where"],
      "halt": "Only if you can't say which system and which area. Everything else gets written with <MISSING> in it and listed at the bottom to chase.",
      "facts": [
        "job name and number",
        "area by level and room numbers",
        "system as the drawings name it",
        "sheet or spec section for the sequence, and its date",
        "the sequence wording for the part in question",
        "what got demonstrated, zone by zone, and what got skipped",
        "what it actually did when it was demonstrated",
        "who ran it and who stood there and watched, with companies",
        "items that didn't do what the sequence says, by area",
        "who's coming back and when",
        "what closing it needs — access, after hours, ceiling left open"
      ],
      "secondary": [
        "the short version that goes to the vendor as his open-items list",
        "the chase note when the vendor hasn't been back"
      ]
    }
  ],
  "overrides": {
    "daily-report": {
      "name": "The Daily",
      "aka": [
        "daily",
        "daily log",
        "foreman daily",
        "field report",
        "DFR",
        "shift report",
        "end of day report",
        "daily narrative"
      ],
      "why": "It's the only proof of what your crew did, where they couldn't get to, and who held you up — written months before anybody argues about it.",
      "sections": [
        {
          "h": "JOB / DATE / SHIFT",
          "r": "Job name and number, the calendar date, the shift. Weather only if it actually changed the work. This is what somebody searches their mail for in nine months, so it leads — never put the words 'Daily Report' on line one. If all you've got is the job name, lead with that alone and let the rest fill in. Their log and its number are theirs; these words are yours."
        },
        {
          "h": "MEN ON THE JOB",
          "r": "Straight counts by classification and where each group worked — 'JW x4 + 2 apprentices, level 3 east branch; 2 JW pulling feeders in the main room.' Counts and areas only. No names of who showed up late, no hours math, no rates, no opinion about anybody's production."
        },
        {
          "h": "WHAT WE GOT DONE",
          "r": "By area and system, in the words the prints use — grid lines, room numbers, panel tags. 'Rough-in complete grid 4-8, pulled feeders to DP-3, set 6 of 9 fixtures corridor 2.' Percent complete only if you actually walked it. Never 'continued work on' — that sentence says nothing and it reads as nothing."
        },
        {
          "h": "WHAT WE NEED TO KEEP GOING",
          "r": "The decision, the material, the access or the other trade's work you need for the next shift, with who owes it and what it has to beat — before rock goes up, before Thursday's pour, before the ceiling closes. One ask per line. Never a calendar date you invented. No threats, no 'as previously stated numerous times'."
        },
        {
          "h": "WHO WAS HERE / WHAT CAME IN",
          "r": "Anybody on your work who wasn't your crew — inspector, engineer, utility, vendor startup, owner's man — with names and times, plus what came off the truck. Never summarize what somebody said unless you heard it yourself."
        },
        {
          "h": "SAFETY",
          "r": "Write 'None' if none. If something happened, one flat factual line here and the whole story goes in the incident statement. Never put a cause, a blame or a 'should have' in a daily — a daily gets read out loud by a lawyer someday."
        }
      ],
      "omit": "Where you COULDN'T work. Everybody types what they got done; almost nobody types 'level 3 west still had no ceiling grid, so I moved four men to the east rooms.' Nine months later the delay claim gets built off dailies, and a daily that only lists production is the GC's evidence that you were never impacted a single day. The lost area, what was in the way, whose work it was, and where the men went instead — same day, in your own words. Write it once, here, and write it well: the impact notice gets built by pasting this paragraph, not by typing it twice.",
      "needs": ["who", "where", "notdone"],
      "halt": "Only if you can't tell which job and which date this is. Everything else gets written with <MISSING> in it and listed at the bottom to chase.",
      "facts": [
        "job name and number",
        "calendar date and shift",
        "men by classification and where each group worked",
        "areas and systems worked, by grid line / room / panel tag",
        "areas you were kept out of, why, and whose work",
        "where the displaced men went instead",
        "material delivered or short",
        "visitors, inspectors, engineers, vendors — names and times",
        "anything you need for tomorrow and who owes it",
        "safety events, or 'none'"
      ],
      "secondary": [
        "the Friday roll-up to your own office, built from the week's dailies",
        "the lost-area paragraph pasted straight into today's impact notice",
        "a two-week look-ahead narrative"
      ]
    },
    "delay-notice": {
      "name": "Impact Notice",
      "aka": [
        "delay notice",
        "impact notice",
        "notice of delay",
        "held up",
        "we can't get in there",
        "out of sequence",
        "stacking of trades",
        "delay letter",
        "notice letter"
      ],
      "why": "Puts the hold-up in writing the day it happens so the money conversation later has a date on it instead of your memory.",
      "sections": [
        {
          "h": "JOB / AREA / DATE",
          "r": "Job, the specific area by level and grid lines or room number, and the date the condition started. First two lines are what he searches for a year from now, not a title. If all you have is the job and the area, lead with those."
        },
        {
          "h": "WHAT WE WERE SUPPOSED TO BE DOING",
          "r": "The scheduled work and the area, tied to the schedule activity or the last coordination meeting. Facts about the plan — never 'we should have been done weeks ago'."
        },
        {
          "h": "WHAT'S IN THE WAY",
          "r": "The physical condition, whose scope it is, and the date and time you first saw it. Grid not hung, walls not framed, deck not poured, gear not delivered. Take this paragraph off today's daily — it is the same three sentences aimed at a different man, and it gets pasted, never re-written. Describe the condition, never the man or the company."
        },
        {
          "h": "WHAT IT STOPPED — AND WHERE THE MEN WENT",
          "r": "Which crew, which area went idle, and where you moved them. Same paragraph off the daily. If men stood, say men stood. No crew-hour math, no days claimed, no dollars — the office builds that, and a number in a field note becomes the ceiling you get paid."
        },
        {
          "h": "WHAT I NEED, AND BEFORE WHAT",
          "r": "One specific ask, against the milestone that is actually coming at him — 'before the ceiling closes', 'before Thursday's pour', 'before rock goes up' — not a calendar date you invented. Close it with the one line he can reply to: tell me when it's clear and I'll put men back on it. No signature block, no legal register."
        },
        {
          "h": "IF IT DOESN'T CLEAR",
          "r": "The next thing that gets buried, re-done or pushed if the condition holds. Sequence and facts only. No 'we reserve all rights', no dollar figure, no 'we will be filing a claim' — that letter is the office's and it isn't this one."
        }
      ],
      "omit": "The date you FIRST said something out loud, and who you said it to. These get written after the third day of standing around, so they read like the problem started today — and the first answer back is always 'this is the first I'm hearing of it.' One line — 'I brought this up to you at the 7 a.m. huddle Tuesday and again Wednesday morning' — turns a complaint into a notice.",
      "needs": ["when", "who"],
      "halt": "Only if you can't name the area and the date the hold-up started. If you can't name the other trade, write 'the crew hanging ceiling grid' and send it — never guess a company name onto paper.",
      "facts": [
        "job and specific area — level, grid lines, room",
        "date and time you first saw the condition",
        "who you told verbally, and when",
        "what work was scheduled there and per what",
        "the physical condition and whose scope it is",
        "which crew was affected and whether men stood",
        "where you moved the men instead",
        "what you need, and which milestone it has to beat",
        "what gets buried or re-done if it holds",
        "prior notices on the same condition, by date"
      ],
      "secondary": [
        "the short reminder when the same condition is still there a week later",
        "the field facts your PM needs to build the time-impact request"
      ]
    },
    "change-request": {
      "name": "Extra Work Write-Up",
      "aka": [
        "extra",
        "the extra",
        "extra work",
        "COR",
        "change order request",
        "change order narrative",
        "out of scope",
        "scope change",
        "not on my prints",
        "PCO",
        "directed work"
      ],
      "why": "Turns 'they had us do something else' into a paragraph your estimator can price and the GC can't wave off.",
      "sections": [
        {
          "h": "JOB / AREA / DATE / WHO DIRECTED IT",
          "r": "Job and area first — that's the search key. Then the man who directed it, his company, the date and the clock time, and how he told you: face to face, on the phone, by email, on an RFI answer, on a marked-up sketch. The GC's system owns the COR number and your office owns the price; this is the description they both key off."
        },
        {
          "h": "WHAT WE WERE TOLD TO DO",
          "r": "The actual work in installer's words — what got added, moved, removed, or done twice. Locations and quantities of the work itself. No prices, no unit costs, no rates, no markup."
        },
        {
          "h": "WHAT'S DIFFERENT",
          "r": "The difference between what the prints show and what you were told to do, in one plain paragraph — added scope, changed sequence, work torn out and re-done, or a condition nobody could have bid. No adjectives, no 'obviously', no rehash of the last three arguments."
        },
        {
          "h": "THE TAGS THAT COVER IT",
          "r": "Point at the T&M tags by date — 'tags attached, 3/14, 3/15, 3/17' or 'see tags'. Do NOT re-list men by classification, hours or material here. Those live on the tag and typing them a second time is how a man quits using the tool. This write-up's job is the argument, not the count."
        },
        {
          "h": "WHAT'S ON HOLD",
          "r": "What you are not doing while this sits, and the milestone it has to beat — before rock goes up, before the pour. If you proceeded on verbal direction, say exactly that, plainly, in one sentence."
        },
        {
          "h": "WHAT I NEED",
          "r": "One line asking for written authorization, addressed to the man who can actually give it. No signature line, no fake approval box, no threat to stop work unless your PM told you to write one."
        }
      ],
      "omit": "The contract basis — the sheet number, revision and date that shows what you were SUPPOSED to install. Without it the whole write-up reads as your opinion that it's an extra, and a PM who was never on site kills it in one line. 'E4.02 rev 2 dated 3/14 shows one 3/4 conduit to the pump; we were directed to run three and add a disconnect' is unarguable. 'This wasn't on our prints' is a conversation. If you don't have the sheet in front of you, say so — never guess a number onto paper.",
      "needs": ["ref", "when"],
      "halt": "Only if nobody actually directed the work. If you can't name a person, a date and how he told you, stop and go get that — an extra with no direction on it is a gift.",
      "facts": [
        "job, area, date and time of the direction",
        "who directed it, his company, and how (verbal, email, RFI, sketch)",
        "sheet number, revision and date for the original scope",
        "spec section or prior RFI answer, if that's the basis",
        "the changed work, with locations and quantities",
        "status: done, in progress, or held",
        "the dates of the T&M tags that cover the labor and material",
        "what's blocked while this sits, and the milestone it has to beat",
        "whether earlier tickets exist on the same issue"
      ],
      "secondary": [
        "the one-paragraph description that pastes into the GC's COR field",
        "the chase note when the extra has been sitting unapproved"
      ]
    },
    "incident-report": {
      "name": "Incident Statement",
      "aka": [
        "incident report",
        "my statement",
        "near miss",
        "near-miss",
        "flash",
        "arc flash",
        "shock",
        "injury",
        "first aid",
        "recordable",
        "accident write up",
        "witness statement",
        "safety writeup"
      ],
      "why": "Your statement is the only version written while the details are still right; everything after it gets built on top of this one.",
      "sections": [
        {
          "h": "JOB / DATE / TIME / WHO AND WHERE",
          "r": "Job name and number first — this gets pulled out of a mailbox months later by searching the job. Then the man involved, his employer, his classification, the date, the clock time, and the exact location: level, room, grid lines, and what he was standing on. Times to the minute you actually know. Never round it off to make it tidy. The company's incident form and the carrier's report are owned and numbered somewhere else; this is your statement that feeds them."
        },
        {
          "h": "WHAT THE CREW WAS DOING",
          "r": "The task, who was on it, and how long they'd been at it. Then the thing that changed right before it happened — a crew swap, a lift moved, an area handed over, a circuit re-fed, a shift into overtime."
        },
        {
          "h": "WHAT HAPPENED",
          "r": "One flat paragraph, in order, facts only. What was seen, heard, felt. Never a cause, never the word 'because', never 'he should have', never a fault attached to a name. Never the word 'recordable' either — that's a call the office and the log make afterward, and a foreman who types it has made a claim in the one document that gets read out loud in a deposition."
        },
        {
          "h": "WHAT HE HAD ON AND WHAT HE WAS USING",
          "r": "PPE actually on the man, and the tools, meter, ladder or lift in use. What was worn — not what was required, not whether it was adequate. No ratings, no category numbers, no verdict."
        },
        {
          "h": "WHAT WE DID NEXT",
          "r": "First aid, who called who and at what time, where he went and with whom, who secured the area, and what got tagged, locked or pulled from service. Times again."
        },
        {
          "h": "WHO SAW IT",
          "r": "Names, employers, phone numbers, and exactly where each one was standing. A witness with no location is not a witness."
        }
      ],
      "omit": "Whether the circuit was proven dead — by whom, with which meter, on which conductors, at what time — and whose lock was on it, applied by whom and when. That one sentence is the entire investigation. State it as fact or state plainly that it's unknown; never fill it in from what usually happens. Leave it out and somebody who wasn't there fills it in later, and it never gets filled in your favor.",
      "needs": ["when", "who"],
      "halt": "Only if the notes read like it's still happening — somebody hurt, somebody exposed, a scene nobody has made safe. Then it says: handle that and call the office, the write-up waits five minutes. Everything else gets written with <MISSING> and a chase list.",
      "facts": [
        "job name and number",
        "man involved, employer, classification",
        "date and clock time",
        "exact location — level, room, grid lines, what he was standing on",
        "the task, the crew, and how long they'd been at it",
        "what changed right before it",
        "the sequence of what happened",
        "circuit believed dead or known live",
        "who tested for absence of voltage, with what instrument, on which conductors, when",
        "lockout: whose lock, applied when",
        "PPE worn and tools/equipment in use",
        "first aid, calls made, times, where he was taken",
        "who secured the scene and what was tagged out",
        "witnesses with employers, phones and where they stood",
        "photos and what they show"
      ],
      "secondary": [
        "a witness's own statement, same shape",
        "the near-miss version where nobody got hurt",
        "the 24-hour follow-up when more facts come in"
      ]
    },
    "damage-found": {
      "name": "Damage Notice",
      "aka": [
        "damage",
        "they wrecked my work",
        "damaged our work",
        "back charge",
        "backcharge",
        "interference",
        "they cut my pipe",
        "rework notice",
        "protection of work",
        "we damaged theirs"
      ],
      "why": "Puts the damage on somebody else's ledger the day it's found — before the wall closes back up and it becomes yours.",
      "sections": [
        {
          "h": "JOB / WHERE / WHAT / WHEN I FOUND IT",
          "r": "Job name and number, then the exact location, the damaged work, and the date and time you FOUND it — not the day you got around to writing it. Say plainly that this is discovery time, not necessarily when it happened. Job and room lead the note; a year from now that's what he types into the search bar."
        },
        {
          "h": "WHAT IT LOOKS LIKE",
          "r": "The physical damage, described so a man who never saw it can picture it — conductor, conduit, hanger, fixture, gear, feeder, by tag or circuit. Reference each photo by what it shows and where it was shot from."
        },
        {
          "h": "WHO WAS WORKING THERE",
          "r": "What you observed, in facts. 'The grid crew was in 214 Tuesday and the cable is cut where their wire hangers land.' If you don't know, write that you don't know and ask who was in that area. Never put a company's name on it if you can't place them there."
        },
        {
          "h": "WHAT IT TAKES TO PUT IT RIGHT",
          "r": "The repair, the access it needs, whether the area has to stay open, and what it holds up. Quantities only — NO PRICES. A number in a field note becomes the ceiling you get paid."
        },
        {
          "h": "WHAT WE DID WHEN WE FOUND IT",
          "r": "Whether you left it as found, made it safe, or repaired it — and why. If you made it safe, say exactly what you did and when: capped, taped, de-energized, tagged, locked."
        },
        {
          "h": "WHAT I NEED",
          "r": "One ask: come look at it before it's covered, and tell me who's taking care of it. Say what it has to beat — before the ceiling closes, before the pour, before rock goes back."
        }
      ],
      "omit": "The line that says your work was complete and inspected or walked and accepted, on a date, before it got hit. Everybody writes 'they broke my conduit.' The fight in April is never about who broke it — it's 'prove it was in, and prove it was right.' One dated sentence plus the photo you took before it was covered ends that argument before it starts. If it was rough and unprotected, say that too; a straight story survives a lot longer than a convenient one.",
      "needs": ["when", "before"],
      "halt": "Only if the notes don't say whether the damaged work is still energized or hanging open. That answer changes what he does in the next five minutes, and the note can wait five minutes.",
      "facts": [
        "job name and number",
        "what's damaged, by tag or circuit",
        "exact location",
        "date and time you discovered it",
        "condition of your work before — installed, complete, inspected, accepted, with dates",
        "photos and what each shows",
        "who was working in that area and when",
        "whether you made it safe, and exactly what you did",
        "what the repair takes and what access it needs",
        "what it holds up and what it has to beat",
        "whether the area is still open or already covered"
      ],
      "secondary": [
        "the version you send when YOUR crew damaged somebody else's work",
        "the response when a back-charge lands for something that isn't yours"
      ]
    },
    "service-writeup": {
      "name": "Service Write-Up",
      "aka": [
        "service call",
        "service report",
        /* "write up" is in "Extra Work Write-Up"'s NAME on this shelf and was
           handing that document back instead of this one (2026-09-02). */
        "found did recommend",
        "trouble call",
        "callback",
        "customer letter",
        "site visit report",
        "PM report",
        "troubleshooting report"
      ],
      "why": "It's the only thing the customer reads, it's what gets the repair funded, and it's the record if the same thing burns up in November.",
      "sections": [
        {
          "h": "SITE / EQUIPMENT / DATE / WO",
          "r": "Site and the equipment by its own label first — that's how they search their mail in six months. Work order number if you have one, plus arrival and departure times. Never lead with the words 'Service Report'. If all you've got is the site and the date, lead with those. The shop's software owns the WO number and makes the write-up mandatory; these are the words you paste in."
        },
        {
          "h": "WHAT THEY CALLED US FOR",
          "r": "The complaint as the customer described it, in their words, one line. Don't correct it and don't diagnose inside it."
        },
        {
          "h": "WHAT WE FOUND",
          "r": "Condition, in facts he can picture — what was tripped, burnt, loose, wet, corroded, mis-wired, or simply not what the drawing says. Readings and nameplate data typed exactly as they read, with the point you took them at and the meter you used. This tool never supplies a normal, a range, a target or a 'should be' — you write what you measured and what the plate says, and nothing else."
        },
        {
          "h": "WHAT WE DID TODAY",
          "r": "What you actually performed, what parts went in, and what's energized and working when you left. If it's temporary, use the word temporary and say what still has to happen."
        },
        {
          "h": "WHAT NEEDS TO HAPPEN NEXT",
          "r": "The recommendation, then what you expect to happen if it's left — what you saw, what you think it takes down with it, and roughly when, in your own words. 'The B-phase lugs are discolored and the insulation is hardened; if that connection keeps heating I expect it to open under load and drop the whole panel, and it'll happen when the building loads up in summer.' That gets funded. 'Needs attention' sits in an inbox forever. No prices, no code-violation claims, no ratings, no threats."
        },
        {
          "h": "WHAT IT'LL TAKE TO GET IT DONE",
          "r": "Access, a shutdown window, parts with a lead time, a lift, another trade, after hours. Say it now so the quote comes out right the first time and nobody makes a second trip to find out."
        }
      ],
      "omit": "What you COULDN'T check, and why. Couldn't shut it down, tenant occupied, panel locked, no access, no prints, no lift, nobody could find the key. Literally nobody types this half, and it is the one that protects you when the same gear fails in November and it is the return trip you already sold. One line per item, with the reason and what it would take to get at it next time.",
      "needs": ["notdone"],
      "halt": "Only if the notes don't say what condition you left the site in — something energized, opened up, or a dead-front off. Say that first; the write-up can wait a minute, an open panel can't.",
      "facts": [
        "site name and address",
        "equipment label exactly as it reads",
        "work order number",
        "date, arrival and departure times",
        "the complaint in the customer's words",
        "what you found, with readings, the meter used and where you took them",
        "nameplate data typed as printed",
        "parts installed and work performed",
        "condition on departure — energized, isolated, temporary",
        "what you couldn't check and why",
        "your recommendation and what you expect if it's left",
        "what the next trip needs — access, shutdown, parts, lift",
        "who you spoke to on site"
      ],
      "secondary": [
        "the short version for the shop's write-up field",
        "the after-hours callback note",
        "the quote request to your own office off the same visit"
      ]
    }
  },
  "drop": [],
  "vocab": [
    "ex h h w -> XHHW",
    "empty cable -> MC cable",
    "em tee -> EMT",
    "ridged pipe -> rigid (RMC)",
    "liquid tite -> liquidtight",
    "elbe -> LB",
    "kayo -> KO (knockout)",
    "jay box -> J-box",
    "for square -> 4-square",
    "faze -> phase",
    "why connected -> wye",
    "three face -> 3-phase",
    "two seventy seven -> 277V",
    "four eighty -> 480V",
    "kay vee ay -> kVA",
    "k c mil -> kcmil",
    "amp a city -> ampacity",
    "g f i -> GFCI",
    "low toe -> LOTO",
    "mick see -> MCC",
    "vee eff dee -> VFD",
    "see tee cabinet -> CT cabinet",
    "buzz duct -> bus duct",
    "ock sensor -> occ sensor"
  ],
  "reminders": [
    "When anything is about to get covered — rock, ceiling grid, a pour, backfill, fireproofing, a poured wall -> remind him to shoot the photo now, with a room number or a tape in the frame, before it's buried. That photo is the whole argument in April.",
    "When a reading, a nameplate or a serial number shows up in the dump -> remind him to type it exactly as it reads and to name the instrument and the point he took it at. A number with no meter and no point of measurement is handwriting, not evidence.",
    "When he says somebody told him to do something -> remind him to name the man, his company and the time, and to send the confirming note the same hour. Verbal direction has a shelf life of about a day.",
    "When a shutdown, an outage or an energization comes up -> remind him to write down who's at the switch, who has authority to say go, and what does NOT come back on its own: fire alarm still on test, card access, walk-in coolers, sump pumps, elevator recall, time clocks, controllers that come back with dead batteries and lose their program. Name who resets each one, by name. The 11 p.m. call is never about the lights.",
    "When a circuit is described as dead -> remind him to record who tested for absence of voltage, with what, on which conductors, and when. If nobody wrote it down, write down that nobody wrote it down."
  ]
};
