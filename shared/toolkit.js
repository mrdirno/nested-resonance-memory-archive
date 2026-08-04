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
  .av-brand{display:flex;align-items:center;gap:8px;text-decoration:none;color:#EEF0EA;font-family:var(--av-cond);
    text-transform:uppercase;letter-spacing:.08em;font-weight:700;font-size:15px;white-space:nowrap;}
  .av-brand b{color:var(--av-flag)}
  .av-menu{position:relative}
  .av-menu>button{font-family:var(--av-mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;
    background:transparent;color:#C7CDD3;border:1px solid #3A424B;border-radius:2px;padding:6px 10px;cursor:pointer;}
  .av-menu>button:hover{border-color:var(--av-flag);color:#fff}
  .av-menu[open]>button{border-color:var(--av-flag);color:#fff}
  .av-drop{position:absolute;top:calc(100% + 6px);left:0;min-width:250px;background:var(--av-paper);color:var(--av-ink);
    border:1px solid var(--av-steel);border-radius:3px;box-shadow:0 10px 30px rgba(0,0,0,.28);padding:5px;display:none;}
  .av-menu[open] .av-drop{display:block}
  .av-drop a{display:block;text-decoration:none;color:var(--av-ink);padding:8px 9px;border-radius:2px;}
  .av-drop a:hover{background:var(--av-flag)}
  .av-drop a b{display:block;font-family:var(--av-cond);text-transform:uppercase;letter-spacing:.03em;font-size:14px;}
  .av-drop a span{display:block;font-family:var(--av-mono);font-size:9.5px;letter-spacing:.08em;color:var(--av-muted);text-transform:uppercase;}
  .av-drop hr{border:0;border-top:1px solid var(--av-line);margin:5px 3px}
  .av-drop .av-req b{color:#7a5a00}
  .av-spacer{flex:1}
  .av-req-btn{font-family:var(--av-cond);text-transform:uppercase;letter-spacing:.06em;font-size:14px;font-weight:700;
    background:var(--av-flag);color:var(--flag-ink);border:1px solid var(--av-flag);border-radius:2px;padding:7px 12px;cursor:pointer;white-space:nowrap;}
  .av-req-btn:hover{background:#FFD34A}
  .av-fav-btn{background:transparent;border:1px solid #3A424B;color:#8892a0;border-radius:2px;width:34px;height:31px;cursor:pointer;font-size:15px;line-height:1;flex:none}
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
  .av-field input,.av-field select,.av-field textarea{width:100%;font-family:var(--av-sans);font-size:14px;color:var(--av-ink);
    background:#fff;border:1px solid var(--av-line);border-radius:2px;padding:9px 10px;}
  .av-field textarea{min-height:74px;resize:vertical;line-height:1.4}
  .av-field input:focus-visible,.av-field select:focus-visible,.av-field textarea:focus-visible{outline:2px solid var(--av-flag);outline-offset:1px}
  .av-row{display:flex;gap:9px;flex-wrap:wrap}
  .av-row .av-field{flex:1 1 150px}
  .av-idtoggle{display:flex;gap:6px}
  .av-idbtn{flex:1;font-family:var(--av-mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;background:#fff;color:var(--av-muted);border:1px solid var(--av-line);border-radius:2px;padding:8px 6px;cursor:pointer}
  .av-idbtn:hover{border-color:var(--av-steel);color:var(--av-ink)}
  .av-idbtn.on{background:var(--av-steel);color:#fff;border-color:var(--av-steel)}
  .av-hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
  .av-err{color:#B0201A;font-size:12.5px;margin:0 0 10px;display:none}
  .av-actions{display:flex;align-items:center;gap:10px;margin-top:4px}
  .av-send{font-family:var(--av-cond);text-transform:uppercase;letter-spacing:.06em;font-size:15px;font-weight:700;
    background:var(--av-steel);color:#fff;border:1px solid var(--av-steel);border-radius:2px;padding:10px 16px;cursor:pointer}
  .av-send:hover{background:#333B44}
  .av-send[disabled]{opacity:.5;cursor:progress}
  .av-cancel{background:none;border:0;color:var(--av-muted);font-size:13px;cursor:pointer;text-decoration:underline}
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

  /* ---------------------------------------------------------------- toolkit bar */
  function buildBar() {
    var drop = h("div", { class: "av-drop", role: "menu" });
    drop.appendChild(h("a", { href: "index.html", html: "<b>All tools</b><span>The " + esc(TRADE.name) + " home</span>" }));
    drop.appendChild(h("a", { href: "credits.html", html: "<b>&#9733; Wall of Wishes</b><span>Who wished each tool into existence</span>" }));
    if (TOOLS.length) drop.appendChild(h("hr"));
    TOOLS.forEach(function (t) {
      drop.appendChild(h("a", { href: t.href, html: "<b>" + esc(t.name) + "</b><span>" + esc(t.audience || "") + "</span>" }));
    });
    drop.appendChild(h("hr"));
    var reqLink = h("a", { href: "#", class: "av-req", html: "<b>✦ Wish for a tool</b><span>Aldrin's AI builds it &mdash; for real</span>" });
    reqLink.addEventListener("click", function (e) { e.preventDefault(); closeMenu(); openWell(); });
    drop.appendChild(reqLink);

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
  var modal, form, errBox, sendBtn, wellAnon = false;
  function buildWell() {
    var guide = h("div", { class: "av-guide", html:
      "<b>A wishing well that actually works.</b> Every tool here started as a wish — someone asked, Aldrin's AI built it. Wish for the one you keep making by hand; if it passes the bar it becomes a real page you (and everyone in the trade) can use. What gets granted:" +
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

    form = h("form", { class: "av-form", novalidate: "novalidate" }, [
      guide,
      idToggle,
      h("p", { class: "av-err", role: "alert" }),
      h("div", { class: "av-field" }, [h("label", {}, ["You are a… ", h("i", {}, ["(optional)"])]), roleSel]),
      h("div", { class: "av-field" }, [h("label", {}, ["The tool"]), h("input", { name: "tool_title", type: "text", maxlength: "200", required: "required", placeholder: TRADE.wishTitleHint, autocomplete: "off" })]),
      h("div", { class: "av-field" }, [h("label", {}, ["What it should do — the doc/request you make by hand, and who you send it to"]), h("textarea", { name: "tool_purpose", maxlength: "2000", required: "required", placeholder: TRADE.wishPurposeHint })]),
      h("div", { class: "av-field" }, [h("label", {}, ["An example ", h("i", {}, ["(optional)"])]), h("textarea", { name: "example", maxlength: "2000", placeholder: "A real example of what you'd type in and what you'd want out." })]),
      nameRow,
      h("div", { class: "av-field" }, [h("label", {}, ["Email to hear when it ships ", h("i", {}, ["(optional, never shown — even if anonymous)"])]), h("input", { name: "contact", type: "email", maxlength: "200", placeholder: "you@company.com", autocomplete: "off" })]),
      // honeypot — real people never see or fill this
      h("div", { class: "av-hp", "aria-hidden": "true" }, [h("label", {}, ["Website"]), h("input", { name: "website", type: "text", tabindex: "-1", autocomplete: "off" })]),
      h("div", { class: "av-actions" }, [
        h("button", { type: "submit", class: "av-send" }, ["Make the wish"]),
        h("button", { type: "button", class: "av-cancel", onclick: closeWell }, ["Cancel"])
      ])
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
      h("button", { type: "button", class: "av-send", onclick: function () { form.reset(); errBox.style.display = "none"; sendBtn.disabled = false; sendBtn.textContent = "Make the wish"; body.innerHTML = ""; body.appendChild(form); } }, ["Make another wish"]),
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
      + ";--flag-ink:" + TRADE.accentInk + ";}\n";
    document.head.appendChild(style);
    document.body.insertBefore(buildBar(), document.body.firstChild);
    // Toolkit is the canonical global; AV stays as an alias so every page the AV
    // toolkit already shipped (which calls AV.today() / AV.toggleFav()) keeps working.
    window.Toolkit = { openWell: openWell, tools: TOOLS, trade: TRADE,
                       today: function(){ return TODAY; }, todayStr: function(){ return fmtDate(TODAY); },
                       favorites: favLoad, isFav: favIs, toggleFav: favToggle };
    window.AV = window.Toolkit;
    resolveToday();
    document.dispatchEvent(new CustomEvent("av:ready"));
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
