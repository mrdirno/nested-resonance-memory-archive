/* PLUMBING FIELD TOOLKIT — VOCABULARY DATA.
 *
 * THE BOUNDARY (av/AV_SOCIETY.md §THE THREE SHAPES): trade.js = IDENTITY + COPY ·
 * tools.js = REGISTRY · items.js = that trade's VOCABULARY DATA. Classifications,
 * reason lists, size ladders and configuration options live HERE — never in the
 * identity config and never inline in a tool page.
 *
 * TWO HARD INVARIANTS (§SAFETY): ZERO BRAND NAMES, and NOTHING IS COMPUTED OR
 * RATED. Every value below is something the tradesman PICKS — no sizing, no
 * ratings, no code references, no rates and no totals, not as a value, not as a
 * hint, not in a placeholder.
 *
 * This trade stood up before the boundary existed, so its FIRST tool still
 * carries its data inline. That is the migration debt, to be retired the next
 * time that page is touched.
 */

/* ── THE DIRECTED-WORK TICKET (shape #2 — shared/note.js) ─────────────────
 * The vocabulary for tm-tag.html. Same boundary as everything else in this file:
 * these are things the man PICKS, never things the page decides. No rates, no
 * totals, no arithmetic and no certified data anywhere in here — the office owns
 * the number and he owns what happened.
 *
 * EVERY WORD BELOW came from a working PLUMBING hand and was then cut by a second
 * one told to kill about a third of it. What survived:
   *  · WHAT IS **NOT** IN THIS TAG is the field this trade fights about and no other
   *    trade asked for. Ceiling left open, slab cored, sleeve in but firestop still
   *    to do, capped and holding but not trimmed — naming it the day it happened is
   *    what stops it being back-charged three months later.
   *  · SAY TAG, NEVER TICKET OR FORM. "Get a tag on it." "He signed the tag." "The
   *    yellow copy." T&M is never spelled out and extra work is "an extra".
   *  · THE ORDER OF THE OUTPUT IS THE ORDER OF THE YELLOW COPY. The triplicate book
   *    is contractual and is never going away, so this page only survives if he can
   *    read it straight off while he fills the paper one — otherwise it is a third
   *    form and it is dead on contact (§THE SYSTEM OF RECORD).
 */
window.TOOLKIT_ITEMS = window.TOOLKIT_ITEMS || {};
window.TOOLKIT_ITEMS.tag = {
  "roles": [
    "Super",
    "GC PM",
    "Owner / tenant",
    "Our PM",
    "Another sub's foreman",
    "Somebody else"
  ],
  "how": [
    {
      "v": "Face to face at the work"
    },
    {
      "v": "On the phone"
    },
    {
      "v": "Text / email"
    },
    {
      "v": "Field order / marked print"
    }
  ],
  "why": [
    {
      "name": "Not on my prints"
    },
    {
      "name": "Owner / tenant change after rough"
    },
    {
      "name": "Existing conditions",
      "sub": "not what the as-builts show"
    },
    {
      "name": "Rotted existing — had to replace it to tie in"
    },
    {
      "name": "Another trade in my way — moved it or stood by"
    },
    {
      "name": "Damage by others — we fixed it"
    },
    {
      "name": "Inspector wouldn't pass it as drawn"
    },
    {
      "name": "Emergency — leak / main stopped up"
    }
  ],
  "notin": [
    {
      "name": "Ceiling / wall left open",
      "sub": "put-back + paint not mine"
    },
    {
      "name": "Slab cored",
      "sub": "patch not mine"
    },
    {
      "name": "Sleeve in — firestop still to do"
    },
    {
      "name": "Not tested yet"
    },
    {
      "name": "Capped and holding — still needs trim"
    },
    {
      "name": "Needs a come-back to finish"
    }
  ],
  "classes": [
    "— class",
    "JOURNEYMAN",
    "APPRENTICE",
    "FOREMAN"
  ],
  "pics": [
    {
      "v": "In this message — shot before we closed it"
    },
    {
      "v": "None"
    }
  ]
};
