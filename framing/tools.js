/* FRAMING & DRYWALL FIELD TOOLKIT — TOOL REGISTRY (the one edit point).
 *
 * The P0 loop (and you) add a tool HERE when its page ships from a wishing-well
 * request or the seed roster. The hub grid and the per-page nav dropdown both
 * read this list, so a new entry appears everywhere at once.
 *
 * Fields:
 *   name      short title
 *   href      the tool's page, relative to /framing/
 *   desc      one line — what document/request it helps a real hand produce
 *   chip      accent color (any CSS color)
 *   audience  who it's for / who they send the output to
 *   pinned    optional — keep at the very top of the hub regardless of favorites
 */
window.TOOLKIT_TOOLS = [
  {
    name: "What's In The Wall",
    href: "whats-in-the-wall.html",
    desc: "The backing ledger. Four taps and a height, room by room, as it goes in — then one paste that says exactly what's behind that rock, who asked for it, and that anything not on the list isn't in there.",
    chip: "#B7ADFF",
    audience: "Foreman → the trade that asked / super",
    pinned: true
  },
  {
    name: "Before I Close It",
    href: "rough-in-request.html",
    desc: "Everything that has to be in, marked, moved or sized before this wall or this lid closes — one list per trade instead of eleven texts, with the gate on every line. After we rock it, it's a cut-in.",
    chip: "#4A3BA8",
    audience: "Foreman → EC / mech / plumber / LV / GC"
  },
  {
    name: "What I'll Put In",
    href: "answer-back.html",
    desc: "Somebody sent you a list of backing and holds. Paste it, tap each line will do / already in / can't / need a number, put a date on the yesses, and send one answer back before the wall closes instead of after.",
    chip: "#8A1C4B",
    audience: "Foreman → the trade who sent the list"
  },
  {
    name: "Extra Work Tag",
    href: "tm-tag.html",
    desc: "Told to do something that isn't yours? Write the tag before you roll — who said it and how, what you found, why it's outside contract, men and material as counts, and the line everybody argues about: what is NOT in this tag.",
    chip: "#6B4FC4",
    audience: "Foreman → GC super / our PM"
  },
  {
    name: "The Write-Up I Owe",
    href: "write-up.html",
    desc: "The letters you keep putting off — the backing closeout, the damage-isn't-ours reply, the held-up notice, the scope narrative. Pick the one you're stuck with, get the exact instructions to paste into your AI once, then dictate it in the truck.",
    chip: "#4B3F8F",
    audience: "Foremen · leads · PMs"
  },
  {
    name: "The Load",
    href: "the-load.html",
    desc: "Boom truck\u2019s coming. Say what\u2019s on it and where every piece gets set down \u2014 a drop on every line, a by-drop list for the driver, and anything you left blank called out instead of guessed at.",
    chip: "#4A3BA8",
    audience: "Foreman \u2192 Yard / supplier"
  },
  {
    name: "Total Package",
    href: "total-package.html",
    desc: "The rate is not the package, and piece is not the rate. Put yours next to theirs line by line and use what you actually averaged — the comparison is only worth what that number is worth.",
    chip: "#7A5A05",
    audience: "Hands · foremen · anybody weighing a move"
  }
  // The loop appends new tools here as it builds them from wishes + the seed roster.
];