/* CREATIVE FIELD TOOLKIT — DOCUMENT LIBRARY (shape #4: shared/docspec.js).
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = picker VOCABULARY · docs.js = the WRITE-UPS
 * this trade actually has to produce. The engine owns the eleven blocks of the
 * emitted instruction set and every universal law in them; this file owns what
 * is different about creative work and nothing else.
 *
 * WHY THIS FILE IS THE LAST ONE WRITTEN, AND WHAT THAT COST. Creative shipped as
 * trade #9 with two of the five document engines — the note and the row log —
 * and ran without a library for the whole time it has been live. It is the only
 * trade of eleven that had no write-up page, which meant the one axis the
 * operator named by hand ("production-grade document engines, isomorphed from
 * the operator's own style") skipped the one trade whose week is almost entirely
 * writing. That is the backport, and this is it.
 *
 * THE SHARED LIBRARY IS ADDRESSED TO A JOBSITE, AND THIS TRADE IS NOT ON ONE.
 * Of the ELEVEN shared documents, eight route to "the GC and my PM", "safety and
 * my PM", "the office and estimating" — people a one-person shop does not have.
 * A freelancer who opens the library and reads "to: the GC super" has been told
 * this kit was not built for them, in the first three words, and no amount of
 * good copy underneath recovers it. So the arithmetic is: eleven shared, THREE
 * dropped, and every one of the eight that survives is overridden — more than
 * any sibling carries, and mostly changing only the addressing, the name and the
 * reason. The SPINE and the `omit` line of a delay notice are the same document
 * whether a super or a client is holding you up; that is the actual claim of one
 * runtime and many trades, and this is the first time it has been tested against
 * a trade that is not construction. Thirteen documents in the library in all.
 *
 * IT IS ALSO THE FIRST `drop`, AND AN OVERRIDE IS NOT A COSMETIC OPERATION.
 * Nine trades shipped before this one and none ever declared a drop, because all
 * nine wrote a service call and ran a toolbox talk. But the sharper lesson came
 * out of an adversarial pass on the FIRST draft of this file, and it is written
 * down here because the next non-construction trade will make the same mistake:
 * an override INHERITS every field it does not declare, and `library()` merges
 * field by field — so five overrides quietly shipped `secondary: ["a
 * one-paragraph version to paste into the GC's change form"]`, `from: "the lead
 * on the job"`, and an `omit` ending "worth nothing in a back-charge meeting"
 * straight into the block the user pastes. The header of this very file claimed
 * the addressing was fixed while the emitted block still said GC. Re-address a
 * shared document and you must walk EVERY field it owns, not the three that show
 * up on the library row.
 *
 * THREE HARD INVARIANTS (§SAFETY), same as every other data file here, plus the
 * three this trade adds (see items.js — the edge is not the construction one):
 *   · ZERO BRAND AND MANUFACTURER NAMES. No cameras, no editors, no review
 *     tools, no transfer services, no codecs by trade name. Generic terms and
 *     the acronyms a real hand actually says.
 *   · NOTHING IS RATED, SIZED, SPEC'D, THRESHOLDED OR JUDGED. No resolution, no
 *     bitrate, no loudness target, no safe area, no file-size cap, no license
 *     term, no usage window, no rate, no deposit split — and NO STANDARD NUMBER
 *     OF ROUNDS, which is the most tempting one in this trade and the most
 *     false. Every one of those changes without telling us, and the write-up
 *     that asserts one is the one that gets quoted back. The user states the
 *     spec their client gave them; nobody here supplies it and nobody grades it.
 *   · Every `omit` line is a SPECIFIC thing that costs money on THAT document.
 *     "Add more detail" is not an omit line and does not belong in this file.
 *   · TONE IS A SAFETY EDGE HERE. A legalistic or passive-aggressive line costs
 *     this user their client and they will blame the page. Every section below
 *     is written plain and warm, ends in an option rather than an ultimatum, and
 *     never carries a consequence-of-non-compliance clause, which is a contract
 *     term and not ours to write.
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
  "trade": "video",

  "docs": [
    {
      "id": "cut-note",
      "name": "What Changed In This Cut",
      "aka": [
        "version note",
        "new cut",
        "v2",
        "round 2",
        "what changed",
        "change log",
        "new version",
        "sending a cut",
        "revision note"
      ],
      "family": "recurring",
      "from": "the editor who cut it",
      "to": "the client, and whoever else is going to open the link",
      "why": "The message that goes out with every version. Sent well it ends the round; sent as “new cut attached” it starts a second thread about notes you already did.",
      "note": "This is the message, not the cut. It carries no price, and it never states how many rounds the deal has — that is the agreement talking, not this.",
      "omit": "THE NOTES YOU DIDN'T DO, and a one-line reason for each. Silence reads as agreement, so the note you quietly skipped comes back as a free round three weeks later — and the one you couldn't do because you are still waiting on something of theirs comes back as your fault.",
      "needs": ["notdone"],
      "halt": "Only if no version or round is named at all — a cut note with no version on it is the exact confusion this document exists to end.",
      "facts": ["which version this is", "which round of notes it answers", "what changed", "what you did not do, and why", "what you are still waiting on"],
      "sections": [
        {
          "h": "WHAT THIS VERSION IS",
          "r": "Name it the way you will name it every time — the version and the date — and say which set of notes it answers. If their notes came off an older cut than the one you last sent, say so plainly right here. That one line stops the whole second thread."
        },
        {
          "h": "WHAT CHANGED",
          "r": "Only what moved since the last version. Group it the way they will watch it, top to bottom through the piece, not in the order the notes arrived. Never re-describe work that was already in the last cut — re-listing finished work is how a client starts re-reviewing it."
        },
        {
          "h": "NOTES I DIDN'T DO, AND WHY",
          "r": "One line each, and a reason that is a fact rather than a defense: it is outside what we agreed / it needs something I do not have yet / doing it undoes note 4 / it needs your call between two options. Never fold this into the section above and never leave a note out of it entirely. This is the section that protects you."
        },
        {
          "h": "WHAT I NEED FROM YOU",
          "r": "One ask, and the date you need it by for the next version to land when they expect. If you need a decision between two options, put both in one line each and ask which — never send somebody away to think about it with no shape to think in."
        },
        {
          "h": "STILL OUTSTANDING",
          "r": "What is still open on your side and on theirs, carried forward from the last version with the date each has been sitting since, so nothing quietly drops off the list between rounds."
        }
      ],
      "secondary": ["a two-line message to send with the link", "a running list of every note across all the rounds so far and where each one landed"]
    },

    {
      "id": "media-report",
      "name": "Where the Media Is",
      "aka": [
        "card report",
        "media report",
        "offload",
        "backup",
        "wheres the footage",
        "media handoff",
        "drive handoff",
        "camera report",
        "dit report"
      ],
      "family": "verification",
      "from": "whoever offloaded the cards",
      "to": "the producer, the editor picking it up, and whoever is paying for the drives",
      "why": "The only record of what came off the cards and where every copy went. It gets read on the day something is missing, and by then the cards are back in the camera.",
      "note": "It records what YOU did with the media. It never states what anything SHOULD be — how many copies, how long anything is kept, what a card can be trusted to hold — because that is the shop's own rule and the deal, not ours.",
      "omit": "EVERY COPY, NOT JUST THE ONE IN YOUR HAND — which drive, whose hands it is in, and where each one physically is. A media report that names one location is a record of a single point of failure, and it is the line everybody leaves out because on the day it feels obvious.",
      "needs": ["who", "where"],
      "halt": "Only if no shoot day or job is named at all.",
      "facts": ["the date and the job", "every card or source, by its own label", "where each copy went", "what was verified, and how", "what has to be true before the cards get reused"],
      "sections": [
        {
          "h": "WHAT CAME IN",
          "r": "One line per card or source, using the label physically on it — camera letter and roll, the audio recorder, drone, second unit, stills, a phone somebody shot on. Say the clip count or the size if you have it, and say plainly if a source arrived with no label on it, because that is the one that goes missing."
        },
        {
          "h": "WHERE EVERY COPY IS",
          "r": "One line per copy: which drive or volume, where it physically is right now, and who has it. Every copy gets its own line, and never write “backed up” as the whole sentence — that names none of them. If a copy is somewhere you do not control, say whose it is. Record the copies that exist; never state how many there ought to be."
        },
        {
          "h": "WHAT I ACTUALLY VERIFIED",
          "r": "What you checked and how you checked it — opened and played, checksum, file count matched, spot-checked a few. Then say what you did NOT verify. Copied and verified are two different claims and only one of them survives a missing clip. Record what you did; never state whether it was enough."
        },
        {
          "h": "WHAT'S WRONG OR MISSING",
          "r": "Corrupt clips, a card that came back short, timecode that does not line up, audio with no matching picture, a file that will not open, a roll nobody can find. What you did about each one — and if you have not done anything yet, say that instead of leaving it out."
        },
        {
          "h": "BEFORE THESE CARDS GET WIPED",
          "r": "Not a date you invented. Name what has to be true first and who is the one who says it is true. If nobody has said it yet, write that nobody has said it yet. This is the section that stops a card getting formatted on a Tuesday because somebody needed it for another job."
        }
      ],
      "secondary": ["a one-line message to the producer confirming the media is down", "a label list for the drives"]
    },

    {
      "id": "sign-off-record",
      "name": "What They Approved, and On Which Version",
      "aka": [
        "sign off",
        "signoff",
        "approval",
        "approved",
        "locked",
        "picture lock",
        "final approval",
        "they said yes"
      ],
      "family": "verification",
      "from": "the person who got the yes",
      "to": "the client who said it, copied to anyone else who will have an opinion later",
      "why": "The message you send within the hour of getting a yes. It is the only thing standing between “approved” and another round nobody is paying for.",
      "note": "It records the approval that was actually given. It never states how many rounds the deal has, what happens next time, or what anything costs — that is the agreement, and this document does not amend it.",
      "omit": "THE VERSION AND THE DATE THE YES WAS GIVEN AGAINST, and what was still open at that moment. An approval with no version on it approves whatever the next argument says it approved.",
      "needs": ["ref", "when", "notdone"],
      "halt": "Only if no approval or decision is described at all.",
      "facts": ["the version approved", "who approved it, and when", "how it came — call, message, email, in the room", "what was still open at that moment", "what happens next, and by when"],
      "sections": [
        {
          "h": "WHAT WAS APPROVED",
          "r": "The version by its own name, and the date. Then one plain sentence about what that version actually is — the length, the cut, the pieces it contains — so nobody has to open a dead link in a year to know what was signed off."
        },
        {
          "h": "WHO SAID IT, WHEN, AND HOW",
          "r": "The name, the date and the channel: on the call, in a message, in an email, in the room. If it came verbally, say it came verbally and that this message is the record of it. Never write an approval as if it were in writing when it was not."
        },
        {
          "h": "WHAT WAS STILL OPEN WHEN THEY SAID YES",
          "r": "The part everybody leaves out. The pass you had not done, the element that was still a placeholder in the version they watched, the thing you were waiting on from them. Named here it is a known exception; unnamed it becomes a defect you fix for free."
        },
        {
          "h": "WHAT'S IN THE VERSION THEY APPROVED — AND WHAT ISN'T",
          "r": "In their words and with no legal register: this covers the version and the pieces named above, and anything not on that list has not been approved because it has not been sent. State only what was and was not in the thing they watched. Never state a term of the deal here."
        },
        {
          "h": "WHAT HAPPENS NEXT",
          "r": "The next step and its date, and what you need from them for it to happen. If nothing is needed from them, say that too, so the message ends on a fact rather than leaving a question hanging in a thread."
        }
      ],
      "secondary": ["a two-line version to drop into the thread where the yes came in", "a short summary of every approval on this job so far"]
    },

    {
      "id": "project-handover",
      "name": "Handing the Project To Somebody Else",
      "aka": [
        "project handoff",
        "hand off",
        "handing it over",
        "another editor",
        "picking it up",
        "taking over",
        "project file",
        "handover to the next editor"
      ],
      "family": "verification",
      "from": "the editor letting go of it",
      "to": "the editor picking it up, and the producer who has to make it work",
      "why": "Somebody has to open your project cold and finish it. Everything you know that is not written down is about to become their problem, and then yours again on a phone call at nine at night.",
      "note": "It says where things are and what is missing. It never states what a license permits or whether anything can be reused somewhere else — that is on whoever bought it, and the question goes to them.",
      "omit": "WHAT IS NOT IN THE FOLDER. Fonts, plugins, the music, the stock, the graphics project the titles were built in, the file that lives in somebody's account rather than on the drive. A handover that lists what IS there reads complete, and it is the one that fails on a Friday afternoon.",
      "needs": ["where", "notdone"],
      "halt": "Only if no project or job is identified at all.",
      "facts": ["the job and the current version", "where the media and the project files are", "what is missing from the folder", "what is still open", "who owns what"],
      "sections": [
        {
          "h": "WHAT THIS IS, AND WHERE IT STANDS",
          "r": "The job, the current version, what is finished and what is not. One plain paragraph, so the next person knows what they are opening before they open it."
        },
        {
          "h": "WHERE EVERYTHING LIVES",
          "r": "The drive or volume, the folder, and the structure inside it: media, project files, exports, graphics, audio, documents. Name the current project file exactly as it is named, and say plainly which of the older ones are dead so nobody spends a morning in the wrong one."
        },
        {
          "h": "WHAT IS NOT IN THE FOLDER",
          "r": "Fonts, plugins, effects, music, stock, an element built somewhere else, anything sitting in an account rather than on the drive. One line each, saying where it actually is and who can get it. This section is the entire reason this document exists, so it is never merged upward."
        },
        {
          "h": "WHAT'S HELD TOGETHER WITH TAPE",
          "r": "Every place you did something the next person would never guess: a nested sequence, a speed change that breaks if it is re-rendered, a manual sync, a mix that only works with one thing muted, a rename that has to stay. Say what it is and what happens if they touch it."
        },
        {
          "h": "WHAT IS STILL OPEN, AND WHO IT'S WITH",
          "r": "The outstanding notes, the missing element, the thing the client owes, the pass nobody has done. Each one with an owner and the date it has been sitting since — an open item with no date attached gets read as “not urgent” by somebody who was not there."
        },
        {
          "h": "WHO TO CALL, AND FOR WHAT",
          "r": "Names, and what each person actually owns: the decision-maker on the client side, whoever owns the media, whoever owns the accounts things live in. Not a contact dump — who to call when one specific thing is wrong."
        }
      ],
      "secondary": ["a short message to send with the drive", "a list for the person picking it up to run through before they start"]
    },

    {
      "id": "brief-recap",
      "name": "What I Understood the Job To Be",
      "aka": [
        "recap",
        "after the call",
        "kickoff",
        "scope",
        "what we agreed",
        "confirming",
        "the brief",
        "understanding"
      ],
      "family": "minutes",
      /* MINUTES-SHAPED, BUT IT DOES NOT RECUR — the engine's §ONE DOCUMENT MAY
         OPT OUT case, and the gate's DELTA ROSTER caught this file in it on the
         first run. A recap records a conversation and what got decided, which is
         minutes exactly; but minutes report DELTAS because a coordination
         meeting recurs, and a kickoff does not. A second recap on the same job
         memorializes a DIFFERENT call, so writing it as an update to the first
         would drop the first one's facts — on the single document in this
         library whose whole purpose is to be read months later to settle what
         was in scope. Re-familying it would fix the behavior by lying about
         what the document is, so the family and the spine stay and the
         continuity rule is what opts out. */
      "standalone": true,
      "from": "the person who was on the call",
      "to": "the client, and anyone on their side who was not on the call",
      "why": "The message you send the same day as the kickoff call. It is the cheapest document in this library and it is the one that decides, months later, what counts as an extra.",
      "note": "It records what was said, in your words, and asks them to correct it. It is not the agreement: it sets no price, no rate and no number of rounds. If those were said on the call they belong in the deal, not in a recap you wrote afterwards.",
      "omit": "WHAT IS NOT INCLUDED, in the same message as what is. A recap that only lists what you are doing is a wish list; the line that stops the arguments is the short one naming the things a reasonable person will assume are in and are not.",
      "needs": ["notdone"],
      "halt": "Only if no conversation or job is described at all.",
      "facts": ["the date of the call and who was on it", "what you are making", "what got decided", "what is not included", "the dates, and what has to arrive for them to hold"],
      "sections": [
        {
          "h": "WHAT WE'RE MAKING",
          "r": "In plain words and in their language, not yours: what the pieces are, how many, roughly how long, where they land. If a number was not actually said on the call, do not put one here — write <MISSING> and ask for it in the section below."
        },
        {
          "h": "WHAT GOT DECIDED",
          "r": "The decisions, each with who made it. Discussion that decided nothing does not appear. If something was left open it goes in the needs-an-answer section, never here dressed up as a decision."
        },
        {
          "h": "WHAT'S NOT IN THIS",
          "r": "The short list of things a reasonable person would assume are included and are not: another cut for somewhere else it lands, captions, a different length, the stills, another language, more rounds than we talked about, the thing their other team keeps mentioning. Neutral and unapologetic, no price attached and no consequence attached."
        },
        {
          "h": "WHAT I NEED FROM YOU, AND WHEN",
          "r": "One list, each item with the date it has to arrive for the dates below to hold: the brief, the copy, the logo files, the music call, somebody's availability, the location confirmed. This is what turns a schedule into something real."
        },
        {
          "h": "THE DATES",
          "r": "What lands when, each stated with what it depends on. If a date only holds because something arrives by Tuesday, say that in the same line. Never state a date as fixed when it is not — a date that quietly depends on them is the one you get blamed for."
        },
        {
          "h": "TELL ME IF I'VE GOT THIS WRONG",
          "r": "One closing line asking them to correct anything above, so the recap gets fixed before it becomes the thing everyone remembers. Warm, one sentence, and nothing attached to it — no date, no ultimatum, and never a line saying what happens if they do not reply. This is an invitation to correct you, not a clock."
        }
      ],
      "secondary": ["a two-line email body to send it with", "just the list of what you need from them, as its own message"]
    }
  ],

  /* ── DROPS — the first in the program, and the third one is the finding ───
   * A service call goes to dispatch and a toolbox talk goes to a safety
   * department; a one-person shop has neither, and a library padded with
   * documents its user will never pick is one they stop scrolling.
   *
   * `change-request` is dropped for the opposite reason, and it is the more
   * interesting one: this trade already SHIPS that document as a page.
   * `thats-another-round.html` is the same trigger ("one small thing" after the
   * rounds you agreed), the same audience, the same day, and the same rails —
   * no price, ends in a choice. On the ten construction kits the pair coexists
   * because `tm-tag.html` is a signed TICKET with hours and materials on it,
   * structurally a different artefact from a change NARRATIVE. Here they are one
   * artefact with two front doors, and §THE GATE is explicit: ONE job per tool.
   * So the tool wins — it is interactive, it is pinned, and the library must not
   * compete for its own search terms. First time in the program a shipped TOOL
   * has displaced a shared DOCUMENT, which is a real result about how far the
   * shared library carries into a trade that is not construction.
   */
  "drop": ["service-writeup", "toolbox-talk", "change-request"],

  /* ── OVERRIDES — eight, and almost all of them are ADDRESSING ─────────────
   * The shared library is written to a jobsite. The SPINE of a delay notice and
   * its omitted line are identical whether a super or a client is holding you
   * up — so the spines are untouched here, and what changes is who the document
   * is going to, what this trade calls it, and the one reason line that has to
   * sound like it was written by somebody who has done the job.
   */
  "overrides": {
    "daily-report": {
      "name": "The Day Report (Shoot Day or Edit Day)",
      "aka": ["day report", "production report", "wrap report", "end of day", "eod", "how the day went", "daily"],
      "from": "the person who ran the day",
      "to": "the producer, or the client who is paying for the day",
      "why": "The one your producer forwards, and the only record of what a day actually cost in time. Written on the day it is a fact; written on Friday it is a memory.",
      "omit": "THE AUDIBLE — the thing you changed on the day to keep the day moving. A location swapped, a lens you did not have, talent an hour late, a setup dropped to make the light. Nobody writes it down, and three weeks later there is no paper for why the cut does not match what was pitched.",
      "needs": ["change"],
      "facts": ["the date and the job", "who was on it, and for how long", "what you got", "what you did not get, and why", "what is holding tomorrow"],
      "halt": "Only if this is the first one in the thread and there is no job or date at all.",
      "secondary": ["a wrap summary rolled up from every day on this shoot", "a shorter one you can send the client, with the internal detail taken out"]
    },

    "incident-report": {
      "name": "Something Happened (Incident / Near-Miss)",
      "aka": ["incident", "near miss", "accident", "somebody got hurt", "gear damage", "on set", "safety"],
      "to": "the producer, the client's contact, and whoever owns the space",
      "why": "Written once and read by people who were not there. On a small crew nobody else is writing this, so if you do not, it does not exist.",
      "secondary": ["a short message to the client and to whoever owns the space, with the internal detail taken out", "a follow-up once whatever caused it has been dealt with"]
    },

    "damage-found": {
      "name": "How It Was When We Got There",
      "aka": ["condition", "pre-existing", "already damaged", "location condition", "came in like this", "not us"],
      "to": "the producer, the venue or building contact, and the rental house if it is gear",
      "why": "You walked into something already broken — a wall, a floor, a lens, a light, a room somebody left wrecked. This is the note that means it is not yours when somebody goes looking for who pays.",
      "omit": "THE DATE, THE TIME, AND WHERE THE PHOTOS ARE. A description with no photo reference and no date on it is your word about a room, and it settles nothing on the day somebody asks who pays for it.",
      "needs": ["when", "where"],
      "secondary": ["a short message to whoever owns the space or the gear, with the photos attached"]
    },

    /* TWO EDITS AND BOTH ARE RAILS, NOT POLISH. The shared `why` opens "The
       clock only starts when somebody is told in writing" — literally true of a
       subcontract notice provision and a bare statement of legal effect once it
       is ported to a freelancer who has no notice clause at all. And `aka`
       carried "waiting on", which is the shipped `still-waiting-on.html` by its
       own name: that page owns the running LIST of everything they owe, this
       document is the single thing that has actually stopped the work. The words
       have to carry that split or the kit has two doors onto one job. */
    "delay-notice": {
      "name": "We're Held Up",
      "aka": ["held up", "stopped", "blocked", "cant start", "date is moving", "impact", "delay"],
      "from": "the person the work stops with",
      "to": "the client, or whoever owes you the thing",
      "why": "One thing has actually stopped the work and the date is going to move because of it. Sent warm and early it moves the thing; sent late it only explains why you are late. (The running list of everything they still owe you is a different message — that one is Still Waiting On.)"
    },

    "site-walk": {
      "name": "Location Scout Write-Up",
      "aka": ["scout", "location scout", "tech scout", "recce", "site visit", "went and looked", "walk"],
      "from": "the person who went and looked",
      "to": "the producer, the crew who have to shoot it, and whoever is booking it",
      "why": "Everything you noticed standing in the room, written so somebody who was not there can plan a day out of it.",
      "omit": "POWER, SOUND, ACCESS AND HOURS — where the outlets actually are, what you can hear from inside the room, how the gear gets in, and the hours you are genuinely allowed to be in there. It never makes the notes and it is the thing that kills the day.",
      "needs": ["when", "where"],
      "halt": "Only if no location is identified.",
      "facts": ["the date and the place", "who showed you around, and who can let you in", "what is there and what you would have to bring", "what you can hear, and how it is lit", "the hours, and how the gear gets in"],
      "secondary": ["a list of questions to send back to whoever books it", "a short summary for whoever is planning the day"]
    },

    "handover": {
      "name": "Delivery Note — What I'm Sending",
      "aka": ["delivery", "final", "final files", "sending it over", "here it is", "delivered", "closeout"],
      "from": "the person sending it",
      "to": "the client, and whoever on their side has to put it somewhere",
      "why": "The last thing they read and the first thing they come back to. Written well it ends the job; sent as “files attached” it brings you back for free.",
      "omit": "WHAT IS NOT IN THIS DELIVERY, and what would have to happen to get it. A delivery that reads as if everything is finished turns every leftover into work you do for nothing.",
      "needs": ["notdone"],
      "halt": "Only if what is being delivered is not identified at all.",
      "facts": ["what you are sending, item by item", "which version each one is", "where it is, and how long the link lives", "what is not included", "what is still open"],
      "secondary": ["a two-line message to send with the link", "a list of just what is still outstanding"]
    },

    "look-ahead": {
      "name": "Where Everything Stands",
      "aka": ["status", "where are we", "update", "this week", "next week", "whats coming"],
      "from": "the person holding the schedule",
      "to": "the producer, or the client who keeps asking",
      "why": "What is landing and when, sent before they ask. It is a request wearing a status update — the dates below only hold if the things underneath them arrive.",
      "omit": "WHAT HAS TO BE TRUE BEFORE EACH ITEM CAN START — the approval, the file, the person's time, the thing they still owe you. A status with no preconditions on it is a wish list, and the date slips with nobody having agreed to it.",
      "needs": ["notdone"],
      "facts": ["the period", "what is landing, and when", "what each one is waiting on", "what is stopped", "what you need, and by when"],
      "secondary": ["just the list of what you need from them, as its own message", "a two-line version for the thread it gets asked in"]
    },

    /* THE NINTH, AND IT WAS THE ONE THIS FILE ALMOST MISSED. `meeting-minutes`
       was the single shared document reaching this trade untouched, so a
       freelancer scrolling the library hit "Coordination Meeting Notes" with
       "oac" among its search terms — the exact failure the other eight exist to
       prevent, sitting in the middle of the list that fixes it. Found by an
       adversarial pass, not by the author. */
    "meeting-minutes": {
      "name": "Notes From the Call",
      "aka": ["call notes", "notes from the call", "we agreed on the call", "review call", "meeting", "minutes", "what we said"],
      "from": "whoever typed it up after",
      "to": "the client, and anyone on their side who was not on the call",
      "why": "Nobody remembers the discussion and everybody argues the decisions. The version that goes out first becomes the truth, so send it the same day and it is yours. This is any call once the job is moving; the one you send after the FIRST call is the recap of what the job actually is.",
      "secondary": ["just the action items, as their own short message", "a two-line email body to send it with"]
    }
  },

  /* ── VOCAB — what this trade dictates that a phone gets wrong ──────────────
   * Spoken-to-written only, and every pair must actually CORRECT something — 19
   * identity mappings ("rough cut -> rough cut") shipped in the first draft, and
   * the engine emits this list under "these are the ones my phone gets wrong",
   * so a pair that changes nothing reads as a broken instruction both to the
   * model and to the man reading his own block. No brand names (items.js §NO
   * BRAND NAMES AS DATA),
   * and nothing here is a claim about what anything should be — a ratio and a
   * frame rate are geometry and arithmetic this trade says out loud, never a
   * requirement. US dialect throughout, held with the rest of the kit.
   */
  "vocab": [
    "bee roll -> B-roll",
    "b roll -> B-roll",
    "a roll -> A-roll",
    "a cam -> A-cam",
    "b cam -> B-cam",
    "el you tee -> LUT",
    "look up table -> LUT",
    "el oh gee -> log",
    "eff pee ess -> fps",
    "frames per second -> fps",
    "twenty three ninety eight -> 23.98",
    "twenty nine ninety seven -> 29.97",
    "sixteen by nine -> 16:9",
    "nine by sixteen -> 9:16",
    "four by five -> 4:5",
    "one by one -> 1:1",
    "time code -> timecode",
    "tee see -> TC",
    "em oh ess -> MOS",
    "vee oh -> VO",
    "jay cut -> J-cut",
    "el cut -> L-cut",
    "cut down -> cutdown",
    "cut downs -> cutdowns",
    "string out -> stringout",
    "off line -> offline",
    "on line -> online",
    "ay ay eff -> AAF",
    "ee dee el -> EDL",
    "ex em el -> XML",
    "colour -> color",
    "wave form -> waveform",
    "vector scope -> vectorscope",
    "en dee filter -> ND filter",
    "lower 3rd -> lower third",
    "colour grade -> color grade",
    "mo graph -> motion graphics",
    "mix down -> mixdown",
    "el you eff ess -> LUFS",
    "off load -> offload",
    "check sum -> checksum",
    "round trip -> round-trip",
    "hand off -> handoff",
    "sign off -> sign-off",
    "vee one -> v1",
    "vee two -> v2",
    "vee three -> v3",
    "story board -> storyboard",
    "one liner -> one-liner",
    "run and gun -> run-and-gun",
    "pick ups -> pickups",
    "re shoot -> reshoot",
    "turn around -> turnaround",
    "first ay see -> 1st AC",
    "d eye tee -> DIT"
  ],

  /* ── REMINDERS — trigger-only, never nagging ──────────────────────────────
   * The last one is this trade's alone and it is the most important line in the
   * file: the block is what talks to the AI, and an AI asked to write a delivery
   * note is exactly where an invented resolution, bitrate or license term walks
   * in. items.js keeps them off the page; this keeps them out of the document.
   */
  "reminders": [
    "When a version, a cut, a round or “v2” comes up -> remind them to put the version and the date on it, and to say which set of notes it answers. A cut sent with no version on it is how two people end up watching different films while arguing about the same note.",
    "When cards, media, an offload, a drive or a backup comes up -> remind them to give EVERY copy its own line — which drive, whose hands, where it physically is — and never to write “backed up” as the whole sentence, because that names none of them. Remind them too that copied and verified are two different claims and only one survives a missing clip.",
    "When an approval, a yes, “locked” or a sign-off comes up -> remind them to record the version it was given against, the date, and what was still open at that moment. An approval with no version on it approves whatever the next argument says it approved.",
    "When something out of scope, an extra, another round or “one small thing” comes up -> remind them to name who asked, when, and in which call or message, and to keep every number out of it. The record made on the day is what makes it a change rather than a favor.",
    "When a location, a venue, a building, talent or somebody else's space comes up -> remind them to write who let them in, the hours they were actually allowed, and how the place was when they arrived. Never let the document state what a release or a license permits; that question goes to whoever holds it.",
    "When a delivery, a final file, a link or a handoff comes up -> remind them to say what is NOT in it and how long the link stays up. A delivery that reads finished turns every leftover into free work.",
    "When a platform, a spec, a resolution, a codec, a loudness figure or a file-size limit comes up -> remind them to state it as the number the CLIENT gave them and to mark it <MISSING> if the client never did. Never let the document supply one: what a place requires changes without telling anybody, and the write-up that asserts it is the one that gets quoted back."
  ]
};
