/* CREATIVE FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request. The hub grid and the per-page nav dropdown both read this list, so a
 * new entry appears everywhere at once — no other file to touch. The deploy
 * asserts every href in here against the published artifact, so a renamed page
 * fails the build instead of 404ing in somebody's hand.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /creative/ (keep tool pages flat here)
 *   desc      one line — what document a real shooter/editor sends with it
 *   chip      accent color (any CSS color) — the left border on the hub card
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 */
window.TOOLKIT_TOOLS = [
  {
    name: "Notes Back",
    href: "notes-back.html",
    desc: "They sent a wall of notes — an email, a doc, a message, a call you typed up. Paste it exactly as it came, tap each line (doing it · already in · that’s an extra · need from you), and copy back one reply that answers every note in their own words.",
    chip: "#8B12B4",
    audience: "Editor → the client who sent notes",
    pinned: true
  },
  {
    name: "That’s Another Round",
    href: "thats-another-round.html",
    desc: "“Just one small thing” landed after the rounds you agreed. Write it the same day — who asked, what they actually asked for, why it’s outside, and where the delivery date lands. Warm, no price, ends in a choice instead of an ultimatum.",
    chip: "#A61457",
    audience: "Editor / producer → the client"
  },
  {
    name: "Still Waiting On",
    href: "still-waiting-on.html",
    desc: "The things you can’t finish without, in one list with the date you asked on each — and what each one is holding up. Tap a row as it moves: still waiting → they said it’s coming → in hand. Send the ones outstanding as one short message instead of a fourth “any update?”.",
    chip: "#5A3FC0",
    audience: "Editor / shooter → the client who owes you something"
  },
  {
    name: "Getting In",
    href: "getting-in.html",
    desc: "You need into a building somebody else locks. Send the ask that gets a yes on the first try — the day, the space, what you need open, who’s coming, and the heads-up that keeps a crew from getting walked before you’ve got the shot. It’s an ask, not a booking, and it says so. Then put whatever they send back against what you asked, and it names what they never answered — because “yeah that’s fine” is not an answer to eight things.",
    chip: "#C2660F",
    audience: "Shooter / producer → the venue or building manager"
  },
  {
    name: "Write-Up Setup",
    href: "write-up.html",
    desc: "The writing you put off — the day report, the cut note that goes out with every version, where the media is, what they actually approved and on which cut, the delivery note, handing a project to another editor, the recap after the kickoff call. Pick the one you’re stuck with and get the exact instructions to paste into your AI once. After that: dump the mess, get back something you can send.",
    chip: "#1D6F63",
    audience: "Editor / shooter / producer → whoever has to read it"
  }
  ,
  {
    name: "Before I Export",
    href: "before-i-export.html",
    desc: "The last message before you hit render. Say what the cut already is — shape, length, what's still standing in — then ask for the few things that put you back in the timeline if they're wrong: the spellings, the logo, the end card, the track, and anybody in it who's become a problem since you shot it. It counts your questions and tells you when you've asked too many to get an answer.",
    chip: "#A61457",
    audience: "Editor → the client, the night of the render"
  }
  ,
  {
    name: "What’s in the Drop",
    href: "whats-in-the-drop.html",
    desc: "The message that goes next to the link. Which file to open, what each thing in the folder is for, and the four or five things that aren’t in there — each one ending in an open door rather than a fence. No clock, no “considered approved”, nothing about what they’re allowed to do with it. Next drop for the same client is a restore and two taps.",
    chip: "#C2660F",
    audience: "Editor → the client, with the files"
  }
  // The loop appends new tools here as it builds them from wishing-well requests.
  // SHIPPED 2026-09-03, and the panel that graded it took two of the three parts
  // this comment used to name away. It scored 7 / 6 / 2 — one lens voted to KILL
  // it — and the page is smaller for the 2: "who signed" is a header field in the
  // sender's own first person, never a block and never a picker, because a typed
  // "Approved by [name]" is a signature that lands on the OTHER party the moment
  // it is forwarded; and the word "deliberately" is gone from the page entirely,
  // because nobody says it about something they are volunteering. What both
  // dissenting lenses agreed on is the ground it keeps: the transfer page already
  // lists the FILES, and nothing anywhere generates ABSENCE.
  // Still owed after that: the PARTICIPANT half of Shoot Day Confirm (the "how
  // the day goes" note to talent or a client coming to set) — "Shoot Day
  // Confirm" shipped above as GETTING IN instead — "confirm" is the exact defect
  // the page exists to prevent: a producer who believes he's confirmed a location
  // when he's only asked it. The 2026-08-13 safety lens's hard rails held through
  // the rename: no access-code field ever, no minors as a category, no map/
  // geolocation/address autocomplete, and no consequence-of-non-compliance line,
  // which is a contract term.
];
