/* shared/lang.js — THE LANGUAGE LAYER (EN / ES), one engine for every page that
 * speaks two tongues.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * EXTRACTED AT THE SECOND INSTANCE (av/AV_SOCIETY.md §THE THREE SHAPES: the
 * first page hand-writes it, the second one extracts it). The first instance was
 * gc/tm-tag.html, built from the wish "Todo en Español para los Latinos"
 * (2026-08-17, panel 3/3); everything below is that page's behaviour, lifted
 * verbatim and made a config so the eleven sibling tags carry it as data.
 *
 * WHAT THE PANEL BOUND, and this engine honors on every page that mounts it:
 *  · The page follows the phone on the first visit (an ES-set phone opens en
 *    español; an EN phone never sees the toggle move), and after that the
 *    chip's own pick rules — one key, `toolkit.lang`, shared by every trade, so
 *    a man who picked ES on the plumbing tag lands on the roofing tag en español.
 *  · UI fully Spanish in ES mode; the DOCUMENT stays readable at the TOP of the
 *    chain — headings and labels print "ES / EN", picked options print
 *    "ES (EN)". A tag outlives its text thread (pay apps, CO backup, the AP clerk
 *    in March), and a receiver who can't read it breaks the reply-OK loop the
 *    tool exists for. EN mode's document is byte-identical to a page that never
 *    heard of this file: in EN, t() returns the EN string and vocab() returns the
 *    trade's own arrays untouched.
 *  · What the man TYPES prints as he typed it, either mode — his words are his.
 *  · Vocabulary rides in each trade's items.js as `tag_es`, every entry carrying
 *    its own en-twin ({ es, en, sub? }) — nothing paired by index, nothing that
 *    can drift apart.
 *
 * THE TOGGLE RELOADS, on purpose. Re-mounting the note engine in place leaves
 * the first mount's form/window listeners alive and both mounts persisting the
 * same key — a race that only wins by accident of registration order. So:
 * flush → store the choice → reload.
 *
 * TRANSLATE ON THE WAY IN, NEVER ON THE WAY OUT (§SCARS 2026-08-18). The note
 * engine flushes on pagehide/visibilitychange — both fire DURING
 * location.reload() — so anything remapped before the reload is overwritten by
 * the exit flush a millisecond later. remapDraft() therefore runs AT BOOT of the
 * next load, where nothing else is writing, and it is idempotent: picks already
 * in this tongue pass through untouched, a half-written draft from the other
 * tongue arrives translated, and free text, the stamp and sticky ride as-is.
 *
 *   <script src="../shared/lang.js"></script>      (after items.js, before the page)
 *   var t = Lang.t, L = Lang.lang;
 *   var V = Lang.vocab(T, ES, { roles: "opt", how: "opt", why: "tick", classes: "plain" });
 *   Lang.remapDraft(KEY, ES, { singles: [{ id: "role", key: "roles" }], lists: [...], rows: [...] });
 *   Lang.chrome({ title: ..., eyebrow: ..., h1: ..., lede: ..., warn: ... });
 *   var api = Note.mount({ ... });
 *   Lang.toggle(api);
 */
(function () {
  "use strict";

  var LANG_KEY = "toolkit.lang";

  function storedLang() {
    try { var v = localStorage.getItem(LANG_KEY); if (v === "es" || v === "en") return v; } catch (e) {}
    return "";
  }
  var L = storedLang() || (((navigator.language || "").toLowerCase().indexOf("es") === 0) ? "es" : "en");

  function t(en, es) { return L === "es" ? es : en; }

  /* ── ES options, derived from the paired vocabulary. The "ES (EN)" the
   *    document prints is composed HERE, from each entry's own en-twin. ────── */
  function opt(p) {
    return (p.en !== p.es) ? { v: p.es, doc: p.es + " (" + p.en + ")" } : { v: p.es };
  }
  function tick(p) {
    var base = p.sub ? (p.es + " — " + p.sub) : p.es;
    var o = { name: p.es, doc: (p.en !== p.es) ? (base + " (" + p.en + ")") : base };
    if (p.sub) o.sub = p.sub;
    return o;
  }
  /* `plain` is for <select> columns inside rows, which print their value as-is:
   * the ES string carries its own twin ("MAYORDOMO (FOREMAN)") — the data's
   * job, not this engine's, so the first instance's vocabulary stays valid. */
  function plain(p) { return p.es; }
  var SHAPES = { opt: opt, tick: tick, plain: plain };

  /* vocab(T, ES, spec) — spec maps each vocabulary key to its shape. EN mode
   * hands back T's own arrays, untouched, so the EN document cannot change; ES
   * mode maps the twins; a key with no twins on this trade falls back to EN
   * rather than to an empty control. */
  function vocab(T, ES, spec) {
    var V = {};
    Object.keys(spec).forEach(function (k) {
      var f = SHAPES[spec[k]] || opt;
      var twins = ES && ES[k];
      V[k] = (L === "es" && twins && twins.length) ? twins.map(f) : T[k];
    });
    return V;
  }

  function pairMap(list, to) {
    var m = {};
    (list || []).forEach(function (p) {
      if (!p || p.en === p.es) return;
      if (to === "es") m[p.en] = p.es; else m[p.es] = p.en;
    });
    return m;
  }

  /* remapDraft(key, ES, plan) — the saved draft under `key`, translated into
   * the CURRENT tongue through each field's own twins. Per-key maps, never one
   * merged map: two vocabularies can share an EN word and mean different
   * things by it.
   *   plan.singles  [{ id, key }]        pick / seg fields — one saved string
   *   plan.lists    [{ id, key }]        ticks — an array of names
   *   plan.rows     [{ id, col, key }]   a <select> column inside a rows field */
  function remapDraft(key, ES, plan) {
    var s = null;
    try { s = JSON.parse(localStorage.getItem(key) || "null"); } catch (e) { s = null; }
    if (!s || typeof s !== "object") return;
    plan = plan || {};
    var touched = false;
    (plan.singles || []).forEach(function (f) {
      var m = pairMap(ES && ES[f.key], L);
      if (typeof s[f.id] === "string" && m[s[f.id]]) { s[f.id] = m[s[f.id]]; touched = true; }
    });
    (plan.lists || []).forEach(function (f) {
      var m = pairMap(ES && ES[f.key], L);
      if (s[f.id] && s[f.id].map) {
        s[f.id] = s[f.id].map(function (nm) { if (m[nm]) { touched = true; return m[nm]; } return nm; });
      }
    });
    (plan.rows || []).forEach(function (f) {
      var m = pairMap(ES && ES[f.key], L);
      if (s[f.id] && s[f.id].map) {
        s[f.id] = s[f.id].map(function (r) { if (r && m[r[f.col]]) { r[f.col] = m[r[f.col]]; touched = true; } return r; });
      }
    });
    if (!touched) return;
    try { localStorage.setItem(key, JSON.stringify(s)); } catch (e) {}
  }

  /* chrome(map) — the page's words OUTSIDE the engine's mount, swapped before
   * it renders. Keys are element ids; `title` is the document title; `warn`
   * is the one block allowed markup (a <b> lead-in) and is set as HTML. */
  function chrome(map) {
    document.documentElement.lang = L;
    Object.keys(map || {}).forEach(function (id) {
      var s = map[id];
      if (typeof s !== "string") return;
      if (id === "title") { document.title = s; return; }
      var n = document.getElementById(id);
      if (!n) return;
      if (id === "warn") n.innerHTML = s; else n.textContent = s;
    });
  }

  /* toggle(api) — the EN/ES chips. Uses the page's own #lang-en / #lang-es if
   * the markup is there (gc/tm-tag.html shipped it inline); otherwise builds
   * the same group beside the eyebrow, wrapping it in .platetop so the plate
   * lays out exactly as the first instance does. 44px min-height rides in
   * note.css (.langtog button). */
  function toggle(api) {
    var en = document.getElementById("lang-en");
    var es = document.getElementById("lang-es");
    if (!en || !es) {
      var eyebrow = document.querySelector(".plate .eyebrow");
      if (!eyebrow) return;
      var top = eyebrow.parentNode;
      if (!top.classList || !top.classList.contains("platetop")) {
        top = document.createElement("div");
        top.className = "platetop";
        eyebrow.parentNode.insertBefore(top, eyebrow);
        top.appendChild(eyebrow);
      }
      var g = document.createElement("div");
      g.className = "langtog";
      g.setAttribute("role", "group");
      g.setAttribute("aria-label", "Language / Idioma");
      en = document.createElement("button"); en.type = "button"; en.id = "lang-en"; en.textContent = "EN";
      es = document.createElement("button"); es.type = "button"; es.id = "lang-es"; es.textContent = "ES";
      g.appendChild(en); g.appendChild(es);
      top.appendChild(g);
    }
    en.classList.toggle("on", L === "en");
    es.classList.toggle("on", L === "es");
    en.setAttribute("aria-pressed", L === "en" ? "true" : "false");
    es.setAttribute("aria-pressed", L === "es" ? "true" : "false");
    function switchLang(to) {
      if (to === L) return;
      if (api && api.flush) api.flush();
      try { localStorage.setItem(LANG_KEY, to); } catch (e) {}
      location.reload();
    }
    en.addEventListener("click", function () { switchLang("en"); });
    es.addEventListener("click", function () { switchLang("es"); });
  }

  window.Lang = {
    KEY: LANG_KEY,
    lang: L,
    t: t,
    opt: opt,
    tick: tick,
    vocab: vocab,
    remapDraft: remapDraft,
    chrome: chrome,
    toggle: toggle
  };
})();
