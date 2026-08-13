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
  }
  // The loop appends new tools here as it builds them from wishing-well requests.
  // Next off the panel's ranked list (av/AV_SOCIETY.md §CREATIVE): Still Waiting
  // On (rowlog, the dated chase for what the client still owes — clipboard
  // round-trip is a ship gate), Before I Export (checklist, the deliverable
  // questions answered before the render), Shoot Day Confirm (checklist, access
  // and logistics — deliberately NOT a call sheet).
];
