/* FIELD TOOLKIT — the shared runtime (nav + wishing well). ONE RUNTIME, MANY TRADES.
 *
 * This file is trade-AGNOSTIC on purpose (av/AV_SOCIETY.md §TRADE EXPANSION:
 * "GENERALIZE the shared runtime to read a per-trade config rather than fork it").
 * It lives in shared/ so no single trade owns it. A new trade is a CONFIG + a
 * registry + tool pages — never a copy of this file.
 *
 * Include on every tool page, in this order:
 *   <script src="trade.js"></script>   <- window.TOOLKIT_TRADE (who am I)
 *   <script src="tools.js"></script>   <- window.TOOLKIT_TOOLS  (what's on the hub)
 *   <script src="../shared/toolkit.js"></script>
 * It injects a sticky toolkit bar (a dropdown of every tool in the registry) and
 * a "Wish for a tool" well that writes to Supabase. New tool pages get all of this
 * for free — the only edit to add a tool is a line in that trade's tools.js.
 *
 * The Supabase anon key below is PUBLIC by design (it ships in every client app);
 * the table's RLS lets anon INSERT a request and read nothing back, so the queue
 * is private. See supabase/migrations/075_av_tool_requests.sql and 076 (the
 * `trade` column that lets one queue serve every trade).
 */
(function () {
  "use strict";

  // The URL + PUBLIC anon key are injected at DEPLOY time from GitHub repo
  // secrets (the anon key is public-by-design but must not live in this public
  // repo — a JWT-shaped string trips the secret-scan guard). See the "Inject
  // wishing-well config" step in .github/workflows/deploy_bridge.yml. On a local
  // or preview copy these stay as placeholders and the well degrades gracefully.
  var CFG = {
    url: "__SUPABASE_URL__",
    anon: "__SUPABASE_ANON_KEY__",
    table: "av_tool_requests"
  };
  var CFG_READY = CFG.url.indexOf("__SUPABASE") !== 0;

  /* ---- WHO ELSE IS OUT THERE: the one list of trades ----------------------
   * Trade #1 and trade #2 each hard-wired a footer link to the other. That does
   * not scale past two: standing up trade #3 meant editing every hub already
   * shipped, and the hub that got forgotten is the one nobody can reach the new
   * trade from — which is exactly how /plumbing/ spent its whole life reachable
   * only from a hand-wired link inside av/index.html.
   * ONE list, here, in the runtime every trade already loads. A hub renders
   * whoever is not itself. Adding trade #4 is one line in this array.
   *
   * EACH ENTRY CARRIES THE OTHER TRADE'S FACE, and that is a deliberate copy.
   * `icon` and `accent` are the property of `<slug>/trade.js` — but a trade.js
   * is loaded ONLY on its own pages, so /av/ cannot ask /plumbing/ what colour
   * it is. Every cross-trade surface therefore has to hold a copy (the
   * persona500 manifest already does, on the same terms). A copy that can drift
   * is a copy that WILL drift, so the drift is a GATE rather than a promise:
   * kit-switcher.spec asserts, on every hub, that this row's icon and accent
   * are `Object.is`-equal to what that trade's own trade.js declares.
   *
   * `short` is what fits on a 44px chip in a 104px column on a 320px phone —
   * "Low-Volt", not "Low-Voltage Field Toolkit". The long name still rides as
   * the title/aria-label, so the chip is terse to the eye and complete to a
   * screen reader. */
  var TRADES = [
    { slug: "av",          name: "AV Field Toolkit",             short: "AV",         icon: "🧰", accent: "#F0BE1E" },
    { slug: "plumbing",    name: "Plumbing Field Toolkit",       short: "Plumbing",   icon: "🔧", accent: "#C87137" },
    { slug: "electrical",  name: "Electrical Field Toolkit",     short: "Electrical", icon: "⚡", accent: "#3FB6F5" },
    { slug: "hvac",        name: "HVAC/R Field Toolkit",         short: "HVAC/R",     icon: "❄️", accent: "#4FE0C0" },
    { slug: "low-voltage", name: "Low-Voltage Field Toolkit",    short: "Low-Volt",   icon: "📹", accent: "#FF9E80" },
    { slug: "gc",          name: "GC & Site Super Toolkit",      short: "GC & Super", icon: "🦺", accent: "#8CE86B" },
    { slug: "framing",     name: "Framing & Drywall Field Toolkit", short: "Framing", icon: "🪚", accent: "#B7ADFF" },
    // NOT A TRADE — the commons, and the only entry here that is not a toolkit.
    // It rides this list on purpose: the six hubs each render "whoever is not me"
    // from it, so one line surfaces the human layer in every hub footer with zero
    // per-hub edits — the same reasoning that put the trades here in the first
    // place. Nothing else consumes this array (grepped: six index.html footers),
    // and the disk-derived trade COUNT comes from `<dir>/trade.js`, which the
    // commons deliberately does not have. So this cannot inflate breadth debt.
    // `kit:false` is what keeps it out of the NAV switcher only: the dropdown
    // already carries "What's in the bag" as its own row three entries above, and
    // the same destination twice in one menu is clutter. The FOOTER block still
    // renders it, exactly as the footer link row it replaces did.
    { slug: "commons",     name: "The Commons · What's in the Bag", short: "Commons", icon: "🎒", accent: "#BABEB6", kit: false }
  ];

  /* ---- WHO AM I: the per-trade config, with the AV defaults ---------------
   * Every string a visitor can see that names the trade comes from here. A new
   * trade ships a trade.js defining window.TOOLKIT_TRADE and gets the whole
   * runtime — nav, well, favorites, credit toggle — with its own identity.    */
  var _T = (window.TOOLKIT_TRADE || {});
  var TRADE = {
    slug:       _T.slug       || "av",
    name:       _T.name       || "AV Field Toolkit",
    icon:       _T.icon       || "🧰",
    brandLead:  _T.brandLead  || "AV",
    brandTail:  _T.brandTail  || "Field Toolkit",
    accent:     _T.accent     || "#F0BE1E",
    // Readable text ON the accent. Was hardcoded #231B00 (dark-on-yellow) in four
    // button rules — unreadable the moment a trade picks a dark accent.
    accentInk:  _T.accentInk  || "#231B00",
    // THE DEEP PAIR — added at shape #2's engine extraction (shared/note.js), which
    // ships ONE stylesheet across six trades. `accent` is deliberately LIGHT and
    // high-chroma because it is painted on the dark nav; that makes it unusable as
    // a border or as text on paper. So a trade also declares the DARK end of its
    // own hue (`accentDeep`, for rules, headings and the impact block's outline)
    // and the palest end (`accentTint`, the impact block's fill). Both are hand
    // picked and contrast-checked per trade rather than computed, because
    // color-mix() is not safe on the old Android browsers these pages land on.
    accentDeep: _T.accentDeep || "#22303A",
    accentTint: _T.accentTint || "#EEF1EC",
    // "…and everyone in the trade" copy + who the handoff goes to
    chain:      _T.chain      || "techs / PMs / leadership",
    roles:      _T.roles      || [["tech", "AV Tech"], ["project_manager", "Project Manager"], ["leadership", "Leadership / Owner"], ["other", "Other"]],
    wishTitleHint:   _T.wishTitleHint   || "e.g. Cable-types picker — HDMI / patch / fiber",
    wishPurposeHint: _T.wishPurposeHint || "e.g. Pick the exact cables for a job and copy a clean spec to send my PM — HDMI (2.0/2.1, lengths), Cat patch (5e/6/6a), fiber (OM3/OM4/OS2, connector types)…"
  };

  // Registry: TOOLKIT_TOOLS is canonical; AV_TOOLS is the back-compat alias the
  // original AV pages shipped with. Either works, so no page had to be rewritten.
  var TOOLS = (window.TOOLKIT_TOOLS || window.AV_TOOLS || []);
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]; }); };

  /* ---- favorites: per-device, no login (fewer steps = the whole point) ----
   * Keyed PER TRADE — a plumber's favorites must not surface on the AV hub.
   * The original AV build stored under the un-namespaced "av.favorites.v1"; if a
   * returning AV visitor has that and no namespaced key yet, adopt it once so
   * nobody silently loses the tools they starred. */
  var FAV_KEY = "toolkit.favorites." + TRADE.slug + ".v1";
  (function migrateLegacyFavorites(){
    if (TRADE.slug !== "av") return;
    try {
      if (localStorage.getItem(FAV_KEY) !== null) return;      // already namespaced
      var legacy = localStorage.getItem("av.favorites.v1");
      if (legacy) localStorage.setItem(FAV_KEY, legacy);
    } catch (e) {}
  })();
  function favLoad(){ try { var a = JSON.parse(localStorage.getItem(FAV_KEY) || "[]"); return Array.isArray(a) ? a : []; } catch (e) { return []; } }
  function favSave(a){ try { localStorage.setItem(FAV_KEY, JSON.stringify(a)); } catch (e) {} document.dispatchEvent(new CustomEvent("av:favorites", { detail: { favorites: a.slice() } })); }
  function favIs(href){ return favLoad().indexOf(href) !== -1; }
  function favToggle(href){ var a = favLoad(), i = a.indexOf(href); if (i === -1) a.push(href); else a.splice(i, 1); favSave(a); return i === -1; }
  function currentTool(){ var name = (location.pathname.split("/").pop() || ""); for (var i = 0; i < TOOLS.length; i++) if (TOOLS[i].href === name) return TOOLS[i]; return null; }

  /* ---- scoped styles (av- prefix so they never collide with a tool page) ---- */
  var CSS = `
  :root{--av-steel:#242A31;--av-ink:#12161A;--av-paper:#FBFBF8;--av-line:#BABEB6;--av-muted:#5D656E;--av-flag:#F0BE1E;
    --av-sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    --av-cond:"Arial Narrow","Helvetica Neue Condensed","Liberation Sans Narrow","Roboto Condensed",var(--av-sans);
    --av-mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;}
  .av-bar{position:sticky;top:0;z-index:40;display:flex;align-items:center;gap:10px;
    background:var(--av-steel);color:#EEF0EA;padding:8px 14px;border-bottom:2px solid var(--av-flag);
    font-family:var(--av-sans);}
  /* min-height 44: the brand IS the home link on every page of every trade, and it
     measured 21px tall — half a tap target, on the one control that gets someone
     back to the hub. The bar already carries 44px buttons so its height is
     unchanged. Found standing up trade #4 and swept to all of them at once
     (§THE EXPANSION ORDER — a fix that lands on one trade is half a fix). */
  .av-brand{display:flex;align-items:center;gap:8px;text-decoration:none;color:#EEF0EA;font-family:var(--av-cond);
    text-transform:uppercase;letter-spacing:.08em;font-weight:700;font-size:15px;white-space:nowrap;
    min-width:0;overflow:hidden;flex:0 1 auto;min-height:44px;}
  .av-brand b{color:var(--av-flag)}
  /* A CUT WORD IS A DIFFERENT WORD. The rules below give the brand up in two
     deliberate steps — the tail at 560px, the word at 380px — but between those
     two the word was hard-cut by this element's own overflow:hidden, with no
     ellipsis, because the SPAN could not shrink and so never became the overflow
     box. MEASURED LIVE at 390px across all seven kits: /plumbing/ lost 13px,
     /electrical/ 28px, /low-voltage/ 42px, and trade #7 rendered its brand as
     the two letters "FR". A fragment with no ellipsis does not read as a
     truncation, it reads as a name — which is worse than showing less. Letting
     the span own the overflow costs nothing on the kits that already fit and
     turns the rest into honest truncation. Swept to all seven the cycle it was
     found (§THE EXPANSION ORDER). */
  .av-brand span{min-width:0;overflow:hidden;text-overflow:ellipsis}
  /* MOBILE-WATERTIGHT (operator 2026-08-04: "don't make anything that's gonna clip
   * or alter if zoomed out on phone"). MEASURED BEFORE THE FIX, in a real browser
   * at a 390px viewport: this sticky bar's content was 433px on /av/, 487px on
   * /av/consumables.html and 489px on /plumbing/ — so EVERY page of EVERY trade
   * scrolled sideways on every phone. Cause: a flex row of two nowrap items that
   * cannot shrink (the brand, and the 158px "Wish for a tool" CTA).
   * Fix, in priority order for someone holding a phone on a job: the CTA is the
   * demand funnel and never shrinks; the brand gives up its tail ("FIELD TOOLKIT")
   * below 560px, keeping the icon + the trade word ("AV", "PLUMBING") as the home
   * link. NEVER put overflow:hidden on .av-bar itself — .av-drop is absolutely
   * positioned inside it and would be clipped shut. */
  @media (max-width:560px){ .av-brand b{display:none} .av-brand span{margin-right:0} }
  /* At 320px (iPhone SE) a tool page also carries the favourite ★, and the bar
   * measured 332px against a 320px viewport — 12px out. Below 380 the brand gives
   * up its word too and keeps only the icon, which is still the home link. The CTA
   * and the tool menu never shrink: on the narrowest phone we own, what survives is
   * exactly what someone came to tap. */
  @media (max-width:380px){ .av-brand span{display:none} .av-bar{gap:8px;padding:8px 10px} }
  .av-menu{position:relative}
  /* TAP TARGETS >= 44px (operator 2026-08-04, the MOBILE-WATERTIGHT law). Measured
   * before the fix at a 390px viewport: Tools 39px, Wish 32px, fav 31px. These sit
   * in the sticky bar on EVERY page of EVERY trade, and "Wish for a tool" is the
   * demand funnel the whole program runs on — a 32px primary CTA is the single
   * worst tap target we ship. The bar is position:sticky so it takes flow space;
   * no page offsets content by a hardcoded nav height, so growing it is safe. */
  .av-menu>button{font-family:var(--av-mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;
    background:transparent;color:#C7CDD3;border:1px solid #3A424B;border-radius:2px;padding:6px 10px;cursor:pointer;
    min-height:44px;white-space:nowrap;}
  .av-menu>button:hover{border-color:var(--av-flag);color:#fff}
  .av-menu[open]>button{border-color:var(--av-flag);color:#fff}
  /* max-height: the menu now carries the kit switcher, and it had NO bound at all
     before — a six-tool trade already ran past a 568px screen with nothing to
     scroll. The bar is sticky, so subtracting its height keeps the last row of
     the menu on the glass instead of under the fold. */
  .av-drop{position:absolute;top:calc(100% + 6px);left:0;min-width:250px;background:var(--av-paper);color:var(--av-ink);
    border:1px solid var(--av-steel);border-radius:3px;box-shadow:0 10px 30px rgba(0,0,0,.28);padding:5px;display:none;
    max-height:calc(100vh - 72px);overflow-y:auto;-webkit-overflow-scrolling:touch;}
  .av-menu[open] .av-drop{display:block}
  .av-drop a{display:block;text-decoration:none;color:var(--av-ink);padding:8px 9px;border-radius:2px;}
  /* Hover paints the row in the TRADE's accent, so the text on it has to be the
   * trade's accent-ink — not a hardcoded near-black that happened to read well on
   * AV yellow. The children set their own colours, so they have to be pulled back
   * to inherit or the sub-line stays grey-on-accent. */
  .av-drop a:hover{background:var(--av-flag);color:var(--flag-ink)}
  .av-drop a:hover b,.av-drop a:hover span{color:inherit}
  .av-drop a b{display:block;font-family:var(--av-cond);text-transform:uppercase;letter-spacing:.03em;font-size:14px;}
  .av-drop a span{display:block;font-family:var(--av-mono);font-size:9.5px;letter-spacing:.08em;color:var(--av-muted);text-transform:uppercase;}
  .av-drop hr{border:0;border-top:1px solid var(--av-line);margin:5px 3px}
  .av-drop .av-req b{color:#7a5a00}

  /* ---- THE KIT SWITCHER ---------------------------------------------------
   * The one control whose entire job is moving a tradesperson between kits, and
   * it was the smallest thing we shipped. MEASURED on all six LIVE hubs at
   * 320/360/390/430 before this: 16.7px tall, 7-8 of them per page, 100% under
   * the 44px law — and it existed on the SIX HUBS ONLY. From any of the 26 TOOL
   * pages there was no route to another kit at all, because the nav dropdown
   * every page carries never knew the other trades existed.
   * ONE component, TWO mounts: the hub footer block, and a section at the foot
   * of that dropdown. A seventh trade is still one line in TRADES and lights up
   * both, on every page of every trade, with no per-hub edit. */
  .av-kits{margin:0}
  .av-kits-foot{margin:26px 0 0;padding-top:16px;border-top:1px solid var(--av-line)}
  .av-kits-h{font-family:var(--av-mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;
    color:var(--av-muted);margin:0 0 9px;padding:0 2px}
  /* 112px is not a round number, it is the longest label plus its furniture.
     "ELECTRICAL" is the widest single word in the roster and it cannot break at a
     space: at 12px condensed it measures ~63px, and the chip spends 16 on padding,
     4 on borders, 15 on the icon and 7 on the gap = 105. A 104px column split it
     as ELECTRICA / L (MEASURED, 390px). Below the column count drops instead:
     3 up at 430, 3 at 390, 2 at 320, 2 in the 238px-wide menu. */
  .av-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(112px,1fr));gap:6px}
  /* The chip wears the OTHER trade's colour as an index tab, never as a fill:
     every accent in TRADES is tuned to be light and high-chroma on the dark nav
     (§SCARS — "the trade accent is painted"), which makes it a poor background
     for ink on paper. As a 3px edge it identifies without carrying any text. */
  .av-kit{display:flex;align-items:center;gap:7px;min-height:44px;padding:5px 8px;
    border:1px solid var(--av-line);border-left:3px solid var(--k,var(--av-line));border-radius:2px;
    background:#FFF;text-decoration:none;color:var(--av-ink)}
  .av-kit:hover{border-color:var(--av-steel);border-left-color:var(--k,var(--av-steel));background:#F4F5F1}
  .av-kit i{font-style:normal;font-size:15px;line-height:1;flex:none}
  /* overflow-wrap:anywhere stays as the SAFETY NET, not as the plan. A grid item's
     min-width is auto, so an unbreakable word wider than its column would push the
     whole page sideways — which is the one thing the mobile law forbids outright.
     The column above is sized so it never has to fire; the gate asserts both (zero
     horizontal overflow, and no one-word label rendering on two lines). */
  .av-kit b{font-family:var(--av-cond);text-transform:uppercase;letter-spacing:.03em;font-weight:700;
    font-size:12px;line-height:1.15;min-width:0;overflow-wrap:anywhere}
  /* Inside the menu the generic .av-drop a rules (0,1,1) outrank the chip's own
     (0,1,0), so every one of them has to be answered at (0,2,x) or the chips
     render as the menu's block rows. The hover is answered too: painting another
     trade's chip in the CURRENT trade's accent says the wrong thing. */
  .av-drop .av-kit{display:flex;padding:5px 9px}
  .av-drop .av-kit b{font-size:12px;letter-spacing:.03em}
  .av-drop .av-kit:hover{background:#F4F5F1;color:var(--av-ink)}
  .av-drop .av-kits-h{margin:0 0 6px}

  /* THE FOOTER'S OTHER LINKS ARE THE SAME CLASS, and they are declared per page:
     20 files carry a .foot, 12 of them with their own .foot a rule, and every
     one measured 16.7px. This sheet is appended to <head> at boot — AFTER each
     page's own <style> — so at equal specificity one rule here beats twelve
     copies, and any page added later inherits the fix instead of re-earning it.
     The accent underline goes because a 1px border sitting at the bottom of a
     44px box is no longer under the words; the outline says "tap me" better. */
  .foot a{display:inline-flex;align-items:center;min-height:44px;padding:0 10px;
    border:1px solid var(--av-line);border-radius:2px}
  .foot a:hover{border-color:var(--av-steel)}
  .av-spacer{flex:1}
  .av-req-btn{font-family:var(--av-cond);text-transform:uppercase;letter-spacing:.06em;font-size:14px;font-weight:700;
    background:var(--av-flag);color:var(--flag-ink);border:1px solid var(--av-flag);border-radius:2px;padding:7px 12px;cursor:pointer;white-space:nowrap;
    min-height:44px;}
  /* Was #FFD34A — a hardcoded lighter AV YELLOW. Every trade's primary CTA, the
   * one the whole demand loop runs on, flashed AV yellow on hover: copper on
   * /plumbing/, blue on /electrical/. A brightness filter lifts whatever the
   * trade's accent actually is. */
  .av-req-btn:hover{filter:brightness(1.1)}
  .av-fav-btn{background:transparent;border:1px solid #3A424B;color:#8892a0;border-radius:2px;width:44px;min-height:44px;cursor:pointer;font-size:15px;line-height:1;flex:none}
  .av-fav-btn:hover{border-color:var(--av-flag);color:#C7CDD3}
  .av-fav-btn.on{color:var(--av-flag);border-color:var(--av-flag)}
  .av-bar :focus-visible{outline:2px solid var(--av-flag);outline-offset:2px}

  .av-modal{position:fixed;inset:0;z-index:60;display:none;align-items:flex-start;justify-content:center;
    background:rgba(18,22,26,.62);padding:20px 14px;overflow-y:auto;}
  .av-modal.av-open{display:flex}
  .av-sheet{background:var(--av-paper);color:var(--av-ink);width:100%;max-width:560px;border-radius:4px;
    border-top:4px solid var(--av-flag);box-shadow:0 24px 60px rgba(0,0,0,.4);font-family:var(--av-sans);margin:auto;}
  .av-sheet-hd{display:flex;align-items:flex-start;gap:10px;padding:16px 18px 12px;border-bottom:1px solid var(--av-line)}
  .av-sheet-hd h2{font-family:var(--av-cond);text-transform:uppercase;letter-spacing:.04em;font-size:20px;margin:0;flex:1;line-height:1}
  .av-sheet-hd .av-eye{display:block;font-family:var(--av-mono);font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--av-flag);margin-bottom:5px}
  .av-x{border:1px solid var(--av-line);background:none;color:var(--av-muted);width:30px;height:30px;border-radius:2px;cursor:pointer;font-size:17px;line-height:1;flex:none}
  .av-x:hover{border-color:var(--av-ink);color:var(--av-ink)}
  .av-body{padding:14px 18px 18px}
  .av-guide{background:#FDF7E1;border:1px solid #E9DFB6;border-radius:3px;padding:11px 12px;margin-bottom:14px;font-size:12.5px;line-height:1.45;color:#3f3a28}
  .av-guide b{color:var(--av-ink)}
  .av-guide ul{margin:7px 0 0;padding-left:16px}
  .av-guide li{margin:3px 0}
  .av-guide .av-test{margin-top:8px;font-style:italic;color:#5a5030}
  .av-field{margin-bottom:11px}
  .av-field label{display:block;font-family:var(--av-mono);font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:var(--av-muted);margin-bottom:5px}
  .av-field label i{color:#b3671a;font-style:normal}
  /* 44px MINIMUM on every control in the well. This is the ship gate, not a
     preference — the well is filled in one-handed, on a phone, often in gloves,
     and it was shipping 37px inputs, 39px selects, 31px identity buttons and an
     18px "Cancel" on all six trades. shared/feedback.js already held this line;
     the trade well did not. 16px font-size is load-bearing too: below 16, iOS
     Safari zooms the page on focus and the layout the operator told us must
     never "alter if zoomed out" does exactly that. */
  .av-field input,.av-field select,.av-field textarea{width:100%;font-family:var(--av-sans);font-size:16px;color:var(--av-ink);
    background:#fff;border:1px solid var(--av-line);border-radius:2px;padding:10px 10px;min-height:44px;}
  .av-field textarea{min-height:74px;resize:vertical;line-height:1.4}
  .av-field input:focus-visible,.av-field select:focus-visible,.av-field textarea:focus-visible{outline:2px solid var(--av-flag);outline-offset:1px}
  .av-row{display:flex;gap:9px;flex-wrap:wrap}
  .av-row .av-field{flex:1 1 150px}
  .av-idtoggle{display:flex;gap:6px}
  .av-idbtn{flex:1;min-height:44px;font-family:var(--av-mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;background:#fff;color:var(--av-muted);border:1px solid var(--av-line);border-radius:2px;padding:8px 6px;cursor:pointer}
  .av-idbtn:hover{border-color:var(--av-steel);color:var(--av-ink)}
  .av-idbtn.on{background:var(--av-steel);color:#fff;border-color:var(--av-steel)}
  .av-hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
  .av-err{color:#B0201A;font-size:12.5px;margin:0 0 10px;display:none}
  .av-actions{display:flex;align-items:center;gap:10px;margin-top:4px}
  /* THE DISCLOSURE — everything optional behind one 44px tap, so the distance
     from "open the well" to "Make the wish" is four controls, not eleven.
     (Reported into the well itself: "too long it's cumbersome".) */
  .av-more-t{display:flex;align-items:center;gap:8px;width:100%;min-height:44px;margin:12px 0 11px;
    padding:10px 12px;cursor:pointer;text-align:left;background:none;border:1px dashed var(--av-line,#C3C7C0);
    border-radius:2px;font-family:var(--av-cond);text-transform:uppercase;letter-spacing:.07em;
    font-size:11.5px;font-weight:700;color:var(--av-muted)}
  .av-more-t:hover{border-color:var(--av-steel);color:var(--av-steel)}
  .av-more-t i{font-style:normal;font-weight:400;text-transform:none;letter-spacing:.01em;
    font-family:inherit;font-size:12px}
  .av-more-t b{flex:none;width:14px;font-size:14px}
  .av-send{min-height:46px;font-family:var(--av-cond);text-transform:uppercase;letter-spacing:.06em;font-size:15px;font-weight:700;
    background:var(--av-steel);color:#fff;border:1px solid var(--av-steel);border-radius:2px;padding:10px 16px;cursor:pointer}
  .av-send:hover{background:#333B44}
  .av-send[disabled]{opacity:.5;cursor:progress}
  .av-cancel{min-height:46px;padding:0 12px;background:none;border:0;color:var(--av-muted);font-size:13px;cursor:pointer;text-decoration:underline}
  .av-done{text-align:center;padding:8px 4px 4px}
  .av-done .av-check{width:46px;height:46px;border-radius:50%;background:var(--av-flag);color:var(--flag-ink);display:flex;align-items:center;justify-content:center;font-size:26px;margin:0 auto 12px;font-weight:700}
  .av-done h3{font-family:var(--av-cond);text-transform:uppercase;letter-spacing:.03em;font-size:19px;margin:0 0 8px}
  .av-done p{font-size:13.5px;color:var(--av-muted);line-height:1.5;max-width:42ch;margin:0 auto 14px}
  @media (prefers-reduced-motion:reduce){*{transition:none !important}}
  `;


  function h(tag, attrs, kids) {
    var el = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === "class") el.className = attrs[k];
      else if (k === "html") el.innerHTML = attrs[k];
      else if (k.slice(0, 2) === "on") el.addEventListener(k.slice(2), attrs[k]);
      else el.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (c) { if (c) el.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return el;
  }

  /* ------------------------------------------------------------ kit switcher */
  /* Renders "everyone who is not me" as real chips. `inNav` is the only thing
   * that differs between the two mounts, and it decides exactly two questions:
   * whether the commons rides along (see `kit:false` in TRADES), and which
   * heading the block wears. Everything else — the chip, the colour, the href,
   * the accessible name — is one code path, so the footer and the menu can never
   * disagree about which kits exist. */
  function kitChips(inNav) {
    var me = TRADE.slug;
    var grid = h("div", { class: "av-grid" });
    TRADES.filter(function (t) { return t.slug !== me && !(inNav && t.kit === false); })
      .forEach(function (t) {
        grid.appendChild(h("a", {
          // Every page of every trade sits exactly one directory below the root,
          // so ../<slug>/ resolves from a hub and from a tool page alike — and it
          // stays relative, which is what keeps the deployed repo-path prefix
          // (/nested-resonance-memory-archive/) from being silently dropped.
          class: "av-kit", href: "../" + t.slug + "/", style: "--k:" + t.accent,
          title: t.name, "aria-label": t.name
        }, [h("i", { "aria-hidden": "true" }, [t.icon]), h("b", null, [t.short])]));
      });
    return h("nav", {
      class: "av-kits" + (inNav ? "" : " av-kits-foot"), "aria-label": "Other field toolkits"
    }, [
      h("p", { class: "av-kits-h" }, [inNav ? "Switch kit" : "The other kits — same deal, free"]),
      grid
    ]);
  }

  /* A hub declares WHERE the other kits belong with <span id="siblings"></span>.
   * That span used to be filled by a copy of the same eight-line renderer pasted
   * into each of the six hubs; the runtime owns it now, which is the whole point
   * of the list living here (a hub that got forgotten is a kit nobody can reach —
   * measured once already, on /plumbing/). The span sits INSIDE .foot, a wrapping
   * flex row of words, and a grid of 44px chips is not a footer word — so the
   * block is placed before the footer and the marker retires. */
  function mountKitBlock() {
    var slot = document.getElementById("siblings");
    if (!slot || document.querySelector(".av-kits-foot")) return;
    var foot = (slot.closest ? slot.closest(".foot") : null) || slot.parentNode;
    var anchor = (foot && foot.parentNode) ? foot : slot;
    anchor.parentNode.insertBefore(kitChips(false), anchor);
    slot.parentNode.removeChild(slot);
  }

  /* ---------------------------------------------------------------- toolkit bar */
  function buildBar() {
    var drop = h("div", { class: "av-drop", role: "menu" });
    drop.appendChild(h("a", { href: "index.html", html: "<b>All tools</b><span>The " + esc(TRADE.name) + " home</span>" }));
    drop.appendChild(h("a", { href: "credits.html", html: "<b>&#9733; Wall of Wishes</b><span>Who wished each tool into existence</span>" }));
    // THE COMMONS — the human layer, and the one surface that is NOT a trade. Every
    // one of the 26 tools shipped before it generates a document you SEND; nothing
    // on the site was a place to go when you have nothing to generate. It lives at
    // the repo root beside the trades (never inside one — no trade owns it), and it
    // deliberately carries no trade.js: every tool that counts served trades derives
    // them from `<dir>/trade.js` on disk, so a config here would report a seventh
    // trade that does not exist and corrupt the breadth-debt signal.
    // Added HERE, in the shared runtime, so all six trades get it in one edit — and
    // asserted in deploy_bridge.yml for the same reason credits.html is: a nav entry
    // with no per-trade guard means a missing page 404s from every page of every
    // trade at once (measured, 2026-08-04, /plumbing/credits.html).
    drop.appendChild(h("a", { href: "../commons/", html: "<b>&#129520; What's in the bag</b><span>The gear the field actually carries &mdash; every trade</span>" }));
    if (TOOLS.length) drop.appendChild(h("hr"));
    TOOLS.forEach(function (t) {
      drop.appendChild(h("a", { href: t.href, html: "<b>" + esc(t.name) + "</b><span>" + esc(t.audience || "") + "</span>" }));
    });
    drop.appendChild(h("hr"));
    var reqLink = h("a", { href: "#", class: "av-req", html: "<b>✦ Wish for a tool</b><span>Aldrin's AI builds it &mdash; for real</span>" });
    reqLink.addEventListener("click", function (e) { e.preventDefault(); closeMenu(); openWell(); });
    drop.appendChild(reqLink);

    // LAST, and deliberately after the wish CTA. The menu reads as: where you are
    // (all tools / wall / the bag), what you can do here (the tools), ask for more
    // (the wish — the demand funnel the whole program runs on, and it keeps the
    // position it has always had), then leave for another kit. Before this, the
    // 26 tool pages had no route to another trade at all.
    drop.appendChild(h("hr"));
    drop.appendChild(kitChips(true));

    var menu = h("div", { class: "av-menu" }, [
      h("button", { type: "button", "aria-haspopup": "true", "aria-expanded": "false", onclick: toggleMenu }, ["Tools ▾"]),
      drop
    ]);
    window.__avMenu = menu;

    var reqBtn = h("button", { type: "button", class: "av-req-btn", onclick: openWell }, ["✦ Wish for a tool"]);

    // On a tool page, a ★ to favorite THIS tool (pins it to the top of the hub).
    var cur = currentTool();
    var favBtn = null;
    if (cur) {
      favBtn = h("button", { type: "button", class: "av-fav-btn" + (favIs(cur.href) ? " on" : ""), title: "Favorite this tool — pins it to the top of the toolkit", "aria-pressed": favIs(cur.href) ? "true" : "false" }, ["★"]);
      favBtn.addEventListener("click", function () { var on = favToggle(cur.href); favBtn.classList.toggle("on", on); favBtn.setAttribute("aria-pressed", on ? "true" : "false"); });
    }

    return h("nav", { class: "av-bar", "aria-label": TRADE.name }, [
      h("a", { class: "av-brand", href: "index.html", html: esc(TRADE.icon) + ' <span>' + esc(TRADE.brandLead) + '&nbsp;</span><b>' + esc(TRADE.brandTail).replace(/ /g, "&nbsp;") + '</b>' }),
      menu,
      favBtn,
      h("div", { class: "av-spacer" }),
      reqBtn
    ]);
  }
  function toggleMenu() { var m = window.__avMenu; if (!m) return; var open = m.hasAttribute("open"); if (open) closeMenu(); else { m.setAttribute("open", ""); m.querySelector("button").setAttribute("aria-expanded", "true"); } }
  function closeMenu() { var m = window.__avMenu; if (m) { m.removeAttribute("open"); var b = m.querySelector("button"); if (b) b.setAttribute("aria-expanded", "false"); } }
  document.addEventListener("click", function (e) { var m = window.__avMenu; if (m && !m.contains(e.target)) closeMenu(); });

  /* ------------------------------------------------------------------ the well */
  var modal, form, errBox, sendBtn, wellAnon = false, wellKind = "new_tool", resetWellKind = null;

  /* THREE KINDS OF WISH (migration 077). A well that only takes "build me a new
   * thing" cannot make the tools it already shipped any better — and the people
   * best placed to say what is wrong with a tool are the ones using it on a job.
   * So "improve it" and "it's broken" are first-class, not a contact form. */
  var KINDS = [
    { v: "new_tool", label: "Wish for a tool",  hint: "Something that doesn't exist yet" },
    { v: "improve",  label: "Wish it better",   hint: "A tool here should do more, or do it differently" },
    { v: "bug",      label: "Something's wrong", hint: "A tool here is broken or gives the wrong thing" }
  ];
  var COPY = {
    new_tool: {
      lead: "<b>A wishing well that actually works.</b> Every tool here started as a wish — someone asked, Aldrin's AI built it. Wish for the one you keep making by hand; if it passes the bar it becomes a real page you (and everyone in the trade) can use. What gets granted:",
      titleLabel: "The tool",
      purposeLabel: "What it should do — the doc/request you make by hand, and who you send it to"
    },
    improve: {
      lead: "<b>Wish an existing tool better.</b> You're the one using it on a job — if it's missing a line, asks for something in the wrong order, or doesn't speak the way your crew does, say so. Improvements are built the same way wishes are, and you get the same credit.",
      titleLabel: "What should change",
      purposeLabel: "How it should work instead — and what you're doing when it gets in the way"
    },
    bug: {
      lead: "<b>Something's wrong — tell us.</b> A tool that ships a wrong value costs real money on a real job, so a bug on a live tool jumps the queue ahead of any new-tool wish. Tell us what you did, what you got, and what you expected.",
      titleLabel: "What's wrong",
      purposeLabel: "What you did, what happened, and what you expected instead"
    }
  };

  function buildWell() {
    var guide = h("div", { class: "av-guide", html:
      COPY.new_tool.lead +
      "<ul>" +
      "<li><b>Practical, not theoretical</b> — something you'd actually use on a job.</li>" +
      "<li><b>Targeted &amp; common</b> — one clear job, the stuff everyone deals with.</li>" +
      "<li><b>Speaks your language</b> — the real terms, shortcuts and formats your " + esc(TRADE.chain) + " already use.</li>" +
      "<li><b>Fewer steps</b> — it makes a real task faster; it never adds work.</li>" +
      "</ul><div class='av-test'>The test: would you actually use it to send something to your boss, PM, or techs? If yes, wish for it.</div>"
    });

    var roleSel = h("select", { name: "requester_role", "aria-label": "You are a" });
    // NOTE: requester_role is CHECK-constrained in the DB to tech / project_manager
    // / leadership / other. A trade may relabel them ("Service Plumber") but must
    // keep those four VALUES, or the insert is rejected. See migration 075.
    [["", "You are a…"]].concat(TRADE.roles)
      .forEach(function (o) { roleSel.appendChild(h("option", { value: o[0] }, [o[1]])); });

    // Credit / identity choice. If a wish is built the wisher is credited on the
    // tool AND the Wall of Wishes — a public, git-permanent ledger. Named = public
    // credit; Anonymous = credited as "an anonymous AV <role>". Name hides when anon.
    wellAnon = false;
    var nameRow = h("div", { class: "av-row" }, [
      h("div", { class: "av-field" }, [h("label", {}, ["Name ", h("i", {}, ["(your public credit if it's built)"])]), h("input", { name: "requester_name", type: "text", maxlength: "120", autocomplete: "off" })]),
      h("div", { class: "av-field" }, [h("label", {}, ["Company ", h("i", {}, ["(optional)"])]), h("input", { name: "requester_company", type: "text", maxlength: "160", autocomplete: "off" })])
    ]);
    var idName = h("button", { type: "button", class: "av-idbtn on", "aria-pressed": "true" }, ["With my name"]);
    var idAnon = h("button", { type: "button", class: "av-idbtn", "aria-pressed": "false" }, ["Anonymous"]);
    function setWellAnon(on){ wellAnon = on; nameRow.style.display = on ? "none" : ""; idName.classList.toggle("on", !on); idName.setAttribute("aria-pressed", !on ? "true" : "false"); idAnon.classList.toggle("on", on); idAnon.setAttribute("aria-pressed", on ? "true" : "false"); }
    idName.addEventListener("click", function(){ setWellAnon(false); });
    idAnon.addEventListener("click", function(){ setWellAnon(true); });
    var idToggle = h("div", { class: "av-field" }, [ h("label", {}, ["Credit — if it's built, your name goes on the tool + the Wall of Wishes, forever"]), h("div", { class: "av-idtoggle" }, [idName, idAnon]) ]);

    // KIND picker. Three buttons, not a dropdown — on a phone at a job site the
    // choice has to be visible without a tap.
    var kindBtns = KINDS.map(function (k) {
      return h("button", {
        type: "button",
        class: "av-idbtn" + (k.v === "new_tool" ? " on" : ""),
        "aria-pressed": k.v === "new_tool" ? "true" : "false",
        title: k.hint
      }, [k.label]);
    });
    var kindToggle = h("div", { class: "av-field" }, [
      h("label", {}, ["What kind of wish is this?"]),
      h("div", { class: "av-idtoggle" }, kindBtns)
    ]);

    // Which tool it's about — only shown for improve/bug, and populated from THIS
    // trade's registry so nobody has to remember a page name.
    var aboutSel = h("select", { name: "about_tool", "aria-label": "Which tool" });
    aboutSel.appendChild(h("option", { value: "" }, ["Which tool?"]));
    TOOLS.forEach(function (t) { aboutSel.appendChild(h("option", { value: t.href }, [t.name])); });
    var aboutRow = h("div", { class: "av-field", style: "display:none" }, [
      h("label", {}, ["Which tool"]), aboutSel
    ]);

    var titleLabel   = h("label", {}, [COPY.new_tool.titleLabel]);
    var purposeLabel = h("label", {}, [COPY.new_tool.purposeLabel]);

    function setKind(v) {
      wellKind = v;
      kindBtns.forEach(function (b, i) {
        var on = KINDS[i].v === v;
        b.classList.toggle("on", on);
        b.setAttribute("aria-pressed", on ? "true" : "false");
      });
      var c = COPY[v];
      guide.innerHTML = c.lead + (v === "new_tool"
        ? "<ul><li><b>Practical, not theoretical</b> — something you'd actually use on a job.</li>"
          + "<li><b>Targeted &amp; common</b> — one clear job, the stuff everyone deals with.</li>"
          + "<li><b>Speaks your language</b> — the real terms, shortcuts and formats your " + esc(TRADE.chain) + " already use.</li>"
          + "<li><b>Fewer steps</b> — it makes a real task faster; it never adds work.</li></ul>"
          + "<div class='av-test'>The test: would you actually use it to send something to your boss, PM, or techs? If yes, wish for it.</div>"
        : "");
      titleLabel.textContent = c.titleLabel;
      purposeLabel.textContent = c.purposeLabel;
      // A tool must exist before it can be improved or reported broken.
      aboutRow.style.display = (v === "new_tool" || !TOOLS.length) ? "none" : "";
      if (v === "new_tool") aboutSel.value = "";
    }
    kindBtns.forEach(function (b, i) { b.addEventListener("click", function () { setKind(KINDS[i].v); }); });
    resetWellKind = function () { setKind("new_tool"); };

    /* ---- PROGRESSIVE DISCLOSURE (swept from shared/feedback.js, same cycle) ---
     * Reported into this very well: "your something's broken or feedback stuff
     * is too long it's cumbersome."
     *
     * Eleven field-groups stood between opening the well and sending it, seven
     * of them optional. Someone on a ladder reporting a broken tool had to
     * scroll past a credit toggle, a role picker, an example box, a name, a
     * company and an email to reach the button. The well is where this whole
     * program's demand signal comes from, so friction here is the most
     * expensive friction there is.
     *
     * Core is now kind, which tool, what, why — then SEND. The rest folds. The
     * fold names CREDIT explicitly, because a wisher who wants their name on
     * the tool must not lose it just by not tapping.
     */
    var moreWrap = h("div", { class: "av-more", style: "display:none" }, [
      idToggle,
      nameRow,
      h("div", { class: "av-field" }, [h("label", {}, ["You are a… ", h("i", {}, ["(optional)"])]), roleSel]),
      h("div", { class: "av-field" }, [h("label", {}, ["An example ", h("i", {}, ["(optional)"])]), h("textarea", { name: "example", maxlength: "2000", placeholder: "A real example of what you'd type in and what you'd want out." })]),
      h("div", { class: "av-field" }, [h("label", {}, ["Email to hear when it ships ", h("i", {}, ["(optional, never shown — even if anonymous)"])]), h("input", { name: "contact", type: "email", maxlength: "200", placeholder: "you@company.com", autocomplete: "off" })])
    ]);
    var moreBtn = h("button", { type: "button", class: "av-more-t", "aria-expanded": "false" }, [
      h("b", {}, ["+"]),
      h("i", {}, ["Add your name for credit, an example, or your email — all optional"])
    ]);
    moreBtn.addEventListener("click", function () {
      var open = moreWrap.style.display === "none";
      moreWrap.style.display = open ? "" : "none";
      moreBtn.setAttribute("aria-expanded", open ? "true" : "false");
      moreBtn.firstChild.textContent = open ? "−" : "+";
    });

    form = h("form", { class: "av-form", novalidate: "novalidate" }, [
      guide,
      kindToggle,
      aboutRow,
      h("p", { class: "av-err", role: "alert" }),
      h("div", { class: "av-field" }, [titleLabel, h("input", { name: "tool_title", type: "text", maxlength: "200", required: "required", placeholder: TRADE.wishTitleHint, autocomplete: "off" })]),
      h("div", { class: "av-field" }, [purposeLabel, h("textarea", { name: "tool_purpose", maxlength: "2000", required: "required", placeholder: TRADE.wishPurposeHint })]),
      h("div", { class: "av-actions" }, [
        h("button", { type: "submit", class: "av-send" }, ["Make the wish"]),
        h("button", { type: "button", class: "av-cancel", onclick: closeWell }, ["Cancel"])
      ]),
      moreBtn,
      moreWrap,
      // honeypot — real people never see or fill this
      h("div", { class: "av-hp", "aria-hidden": "true" }, [h("label", {}, ["Website"]), h("input", { name: "website", type: "text", tabindex: "-1", autocomplete: "off" })])
    ]);
    errBox = form.querySelector(".av-err");
    sendBtn = form.querySelector(".av-send");
    form.addEventListener("submit", onSubmit);

    var sheet = h("div", { class: "av-sheet", role: "dialog", "aria-modal": "true", "aria-label": "Wish for a tool" }, [
      h("div", { class: "av-sheet-hd" }, [
        h("div", {}, [h("span", { class: "av-eye" }, ["Wishing well"]), h("h2", {}, ["Wish for a tool"])]),
        h("button", { type: "button", class: "av-x", "aria-label": "Close", onclick: closeWell }, ["×"])
      ]),
      h("div", { class: "av-body" }, [form])
    ]);
    modal = h("div", { class: "av-modal", onclick: function (e) { if (e.target === modal) closeWell(); } }, [sheet]);
    document.body.appendChild(modal);
  }

  function openWell() {
    if (!modal) buildWell();
    modal.classList.add("av-open");
    document.documentElement.style.overflow = "hidden";
    var first = form.querySelector('[name="tool_title"]'); if (first) setTimeout(function () { first.focus(); }, 30);
  }
  function closeWell() { if (modal) { modal.classList.remove("av-open"); document.documentElement.style.overflow = ""; } }
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") { closeWell(); closeMenu(); } });

  /**
   * KEEP TAB INSIDE THE SHEET.
   *
   * `aria-modal="true"` is a PROMISE TO ASSISTIVE TECH, not a behaviour: it
   * tells a screen reader the rest of the page is inert and changes nothing at
   * all about where Tab goes. Measured on LIVE production — av, plumbing and
   * hvac hubs plus av/consumables — 12 of 16 tab stops landed OUTSIDE the open
   * dialog, on the nav, on the trigger button, and on a tool page on the user's
   * own INPUT: typing into the document behind a sheet that is covering it.
   *
   * The well is injected into every page of every trade, so this one handler is
   * the whole toolkit's fix. `.av-hp` is the honeypot and already carries
   * tabindex="-1"; the filter keeps it out for the same reason it is hidden.
   */
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Tab" || !modal || !modal.classList.contains("av-open")) return;
    var sheet = modal.querySelector('[role="dialog"]');
    if (!sheet) return;
    var all = sheet.querySelectorAll('a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
    var focusable = [];
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (el.disabled || el.getAttribute("tabindex") === "-1") continue;
      // offsetParent is null for anything display:none — the "more" fields are
      // collapsed by default and must not be a stop the user cannot see.
      if (!el.offsetParent && el.type !== "hidden") continue;
      focusable.push(el);
    }
    if (!focusable.length) return;
    var first = focusable[0], last = focusable[focusable.length - 1];
    var active = document.activeElement;
    if (e.shiftKey && (active === first || !sheet.contains(active))) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && (active === last || !sheet.contains(active))) { e.preventDefault(); first.focus(); }
  });

  function showErr(msg) { errBox.textContent = msg; errBox.style.display = "block"; }

  function onSubmit(e) {
    e.preventDefault();
    errBox.style.display = "none";
    var fd = new FormData(form);
    if ((fd.get("website") || "").trim()) { doneUI(); return; } // honeypot tripped — pretend success
    var title = (fd.get("tool_title") || "").trim();
    var purpose = (fd.get("tool_purpose") || "").trim();
    if (title.length < 3) { showErr("Give the tool a short name (a few characters)."); return; }
    if (purpose.length < 10) { showErr("Add a line on what it should do — what you'd use it for."); return; }
    // One tap, and it is the difference between an actionable report and a note
    // nobody can act on: a bug or an improvement has to name the tool it is about.
    var aboutTool = (fd.get("about_tool") || "").trim();
    if (wellKind !== "new_tool" && TOOLS.length && !aboutTool) {
      showErr(wellKind === "bug" ? "Which tool is giving you the wrong thing?" : "Which tool should be better?");
      return;
    }
    if (!CFG_READY) { showErr("The wishing well is live on the published site — this looks like a local or preview copy."); return; }

    var payload = {
      requester_role: fd.get("requester_role") || null,
      tool_title: title,
      tool_purpose: purpose,
      example: (fd.get("example") || "").trim() || null,
      requester_name: wellAnon ? null : ((fd.get("requester_name") || "").trim() || null),
      requester_company: wellAnon ? null : ((fd.get("requester_company") || "").trim() || null),
      contact: (fd.get("contact") || "").trim() || null,
      // WHICH TRADE wished this (migration 076). One queue serves every toolkit;
      // the loop reads a trade's wishes with `av_wishing_well.py --trade <slug>`.
      // A wish from a trade we do not serve yet is DEMAND SIGNAL for the next
      // isomorph, not an error — hence a slug column, not an enum.
      trade: TRADE.slug,
      // WHAT KIND of wish (migration 077): build something new · make a shipped
      // tool better · a shipped tool is wrong. A bug outranks a new-tool wish —
      // something already in someone's hands is broken.
      kind: wellKind,
      about_tool: (wellKind === "new_tool") ? null : (aboutTool || null),
      source: TRADE.slug + "_wishing_well",
      user_agent: (navigator.userAgent || "").slice(0, 500)
    };

    sendBtn.disabled = true; sendBtn.textContent = "Sending…";
    fetch(CFG.url + "/rest/v1/" + CFG.table, {
      method: "POST",
      headers: { "apikey": CFG.anon, "Authorization": "Bearer " + CFG.anon, "Content-Type": "application/json", "Prefer": "return=minimal" },
      body: JSON.stringify(payload)
    }).then(function (r) {
      if (r.ok) { doneUI(); }
      else { r.text().then(function (t) { showErr("Couldn't send (" + r.status + "). " + (t ? t.slice(0, 140) : "Please try again.")); }); sendBtn.disabled = false; sendBtn.textContent = "Make the wish"; }
    }).catch(function () {
      showErr("Network error — check your connection and try again.");
      sendBtn.disabled = false; sendBtn.textContent = "Make the wish";
    });
  }

  function doneUI() {
    var body = modal.querySelector(".av-body");
    var done = h("div", { class: "av-done" }, [
      h("div", { class: "av-check" }, ["✓"]),
      h("h3", {}, ["Your wish is in the well"]),
      h("p", {}, ["Aldrin's AI reads the well every cycle and grants the ones that pass the bar — practical, common, and something a real tech or PM would actually use. When yours is built it just shows up on the toolkit. Leave an email and you'll hear the moment it's live."]),
      h("button", { type: "button", class: "av-send", onclick: function () { form.reset(); if (resetWellKind) resetWellKind(); errBox.style.display = "none"; sendBtn.disabled = false; sendBtn.textContent = "Make the wish"; body.innerHTML = ""; body.appendChild(form); } }, ["Make another wish"]),
      h("button", { type: "button", class: "av-cancel", onclick: closeWell, style: "margin-left:10px" }, ["Close"])
    ]);
    body.innerHTML = ""; body.appendChild(done);
  }

  /* --------------------------------------------------- self-aware "today" */
  // The clock on a job-site tablet can be wrong. Resolve the real date from
  // public sources — a world time API, then THIS server's Date response header —
  // each rendered in the device's own timezone; fall back to the device clock.
  // Any tool reads AV.today() / AV.todayStr() and may listen for "av:date".
  var TODAY = new Date();
  function fmtDate(d){ try{ return d.toLocaleDateString(undefined,{ year:"numeric", month:"short", day:"numeric" }); }catch(e){ return String(d); } }
  function tryDate(fn){ return new Promise(function(res){ var done=false, t=setTimeout(function(){ if(!done){ done=true; res(null); } }, 2500); try{ fn().then(function(d){ if(done)return; done=true; clearTimeout(t); res(d && !isNaN(d.getTime()) ? d : null); }).catch(function(){ if(done)return; done=true; clearTimeout(t); res(null); }); }catch(e){ if(!done){ done=true; clearTimeout(t); res(null); } } }); }
  function resolveToday(){
    var sources = [
      function(){ return fetch("https://worldtimeapi.org/api/ip", { cache:"no-store" }).then(function(r){ return r.json(); }).then(function(j){ return new Date(j.datetime || j.utc_datetime); }); },
      function(){ return fetch(location.href, { method:"HEAD", cache:"no-store" }).then(function(r){ var h=r.headers.get("date"); return h ? new Date(h) : null; }); }
    ];
    (function step(i){ if(i>=sources.length) return; tryDate(sources[i]).then(function(d){ if(d){ TODAY=d; document.dispatchEvent(new CustomEvent("av:date", { detail:{ date:d } })); } else step(i+1); }); })(0);
  }

  /* ------------------------------------------------------------------- boot */
  function boot() {
    // Base sheet, then the trade's accent overrides the AV yellow. One runtime,
    // many trades — a trade is recognisable at a glance without forking the CSS.
    var style = document.createElement("style");
    style.textContent = CSS
      + "\n:root{--av-flag:" + TRADE.accent + ";--flag:" + TRADE.accent
      + ";--flag-ink:" + TRADE.accentInk
      + ";--deep:" + TRADE.accentDeep + ";--tint:" + TRADE.accentTint + ";}\n";
    document.head.appendChild(style);
    document.body.insertBefore(buildBar(), document.body.firstChild);
    mountKitBlock();
    // Toolkit is the canonical global; AV stays as an alias so every page the AV
    // toolkit already shipped (which calls AV.today() / AV.toggleFav()) keeps working.
    window.Toolkit = { openWell: openWell, tools: TOOLS, trade: TRADE, trades: TRADES,
                       today: function(){ return TODAY; }, todayStr: function(){ return fmtDate(TODAY); },
                       favorites: favLoad, isFav: favIs, toggleFav: favToggle };
    window.AV = window.Toolkit;
    resolveToday();
    document.dispatchEvent(new CustomEvent("av:ready"));
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
