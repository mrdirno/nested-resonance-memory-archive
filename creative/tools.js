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
  }
  // The loop appends new tools here as it builds them from wishing-well requests.
  // Next off the panel's ranked list (av/AV_SOCIETY.md §CREATIVE): Before I Export
  // (checklist, the deliverable questions answered before the render), Shoot Day
  // Confirm (checklist, access and logistics — deliberately NOT a call sheet, and
  // the 2026-08-13 safety lens set its hard rails: no access-code field ever, no
  // minors as a category, no map/geolocation/address autocomplete, and no
  // consequence-of-non-compliance line, which is a contract term).
];
