/* FEEDBACK — the universal wishing well. ONE WELL, EVERY SURFACE.
 *
 * Operator directive 2026-08-04: "include a wish-it-better for the Collage Studio
 * too — there's a lot of bugs still and people should be able to send the feedback
 * so the loop cycles can address them. Make sure we have a solid scalable way of
 * addressing open item wishes/feedback for ANYTHING. Standardize the process so
 * anything that is made has this built in."
 *
 * WHAT THIS IS. The trade toolkits already had a wishing well, but it lived inside
 * shared/toolkit.js — welded to a trade's nav bar, its registry and its identity.
 * Collage Studio is a React app with none of those, so it had no way for a user to
 * report the bugs it still has. Rather than fork the well into every product, this
 * is the well with the trade assumptions removed: a dependency-free, framework-free
 * drop-in that any surface can carry.
 *
 * HOW YOU ADD IT — TWO LINES, and this is the standard for everything we ship:
 *
 *   <script>window.FEEDBACK = { surface: "collage", name: "Collage Studio",
 *                               accent: "#7C3AED", areas: [ ... ] };</script>
 *   <script src="../shared/feedback.js"></script>
 *
 * That is the whole integration. No build step, no bundler, no component, no
 * framework coupling — it renders its own floating button and its own modal, so it
 * works identically on a static HTML page and inside a React/Vue/Svelte SPA. A
 * surface that cannot spare two lines cannot claim it shipped.
 *
 * ONE QUEUE, NO MIGRATION. It writes to the SAME Supabase table the trade wells
 * write to (av_tool_requests). Migration 076 made `trade` a bounded lowercase slug
 * ON PURPOSE — "not an enum, so a new trade needs no migration" — which means it is
 * already a general SURFACE key. `surface: "collage"` inserts cleanly today. One
 * queue, one helper, one loop process, N surfaces; the loop reads everything with
 * `av_wishing_well.py --list` unscoped and narrows with `--trade <surface>`.
 *
 * THE THREE KINDS are unchanged and ordered the same way, because the ordering is
 * the point: a BUG on something already in someone's hands outranks an IMPROVEMENT,
 * which outranks a brand-new idea. `kind` is CHECK-constrained in the DB to
 * new_tool / improve / bug — a surface may relabel them, never rename the values.
 *
 * CREDENTIALS ARE WEIGHT, NEVER A LOGIN (operator 2026-08-04). Someone who says
 * "I'm a plumber, Local 38, we run this on commercial" is telling you the
 * provenance of a correction and the context to build it in. It is optional, it is
 * never required to send, and — like the entire queue — it is NEVER published.
 *
 * PRIVACY. The queue is private by RLS: anon may INSERT a status='new' row and read
 * nothing back. Never surface request contents, requesters, companies, emails or
 * the ranking on any public page.
 *
 * The URL + PUBLIC anon key are injected at DEPLOY time from repo secrets into the
 * built copy under dist/shared/ (see the "Inject wishing-well config" step in
 * .github/workflows/deploy_bridge.yml, which must glob dist/shared/*.js so every
 * shared module gets it). On a local or preview copy they stay as placeholders and
 * the well degrades gracefully instead of throwing.
 */
(function () {
  "use strict";

  var CFG = {
    url: "__SUPABASE_URL__",
    anon: "__SUPABASE_ANON_KEY__",
    table: "av_tool_requests"
  };
  var CFG_READY = CFG.url.indexOf("__SUPABASE") !== 0;

  var C = (window.FEEDBACK || {});

  /* requester_role is CHECK-constrained in the DB to exactly these four values
   * (migration 075). A surface may relabel them for its own audience — a plumbing
   * toolkit says "Foreman / PM", a video app says "Producer" — but the VALUES must
   * stay, or the insert is rejected. Anything a caller supplies is filtered against
   * this set rather than trusted, so a typo degrades to a missing role instead of a
   * silent 400 the user cannot understand. */
  var ROLE_VALUES = ["tech", "project_manager", "leadership", "other"];

  var S = {
    surface:   (C.surface || "").toLowerCase() || "unknown",
    name:      C.name || document.title || "this",
    accent:    C.accent || "#F0BE1E",
    accentInk: C.accentInk || "#231B00",
    // What a bug/improve can be ABOUT. For a trade toolkit these are tool pages;
    // for an app they are feature areas. [{ v: "export", label: "Export" }]
    areas:     Array.isArray(C.areas) ? C.areas : [],
    areaLabel: C.areaLabel || "Which part",
    roles:     (Array.isArray(C.roles) && C.roles.length ? C.roles : [
                 ["tech", "I use it"],
                 ["project_manager", "I run projects with it"],
                 ["leadership", "I own / lead the team"],
                 ["other", "Other"]
               ]).filter(function (r) { return ROLE_VALUES.indexOf(r[0]) !== -1; }),
    // Optional: the "we typically use this for ___" axis. Free-form per surface —
    // a trade uses residential/commercial, an app might use personal/client work.
    contexts:     Array.isArray(C.contexts) ? C.contexts : [],
    contextLabel: C.contextLabel || "You mostly use it for",
    newLabel:     C.newLabel || "Wish for a feature",
    trigger:      C.trigger !== false,   // set false to wire your own button
    triggerText:  C.triggerText || "✦ Feedback"
  };

  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]; }); };

  function h(tag, attrs, kids) {
    var el = document.createElement(tag);
    attrs = attrs || {};
    Object.keys(attrs).forEach(function (k) {
      if (k === "html") el.innerHTML = attrs[k];
      else if (k.indexOf("on") === 0 && typeof attrs[k] === "function") el.addEventListener(k.slice(2), attrs[k]);
      else if (attrs[k] != null) el.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (k) { if (k) el.appendChild(typeof k === "string" ? document.createTextNode(k) : k); });
    return el;
  }

  var KINDS = [
    { v: "bug",      label: "Something's broken", hint: "It's wrong, it crashed, or it did the wrong thing" },
    { v: "improve",  label: "Make it better",     hint: "It works, but it should work differently" },
    { v: "new_tool", label: S.newLabel,           hint: "Something that doesn't exist yet" }
  ];
  var COPY = {
    bug: {
      lead: "<b>Something's wrong — tell us.</b> A bug on something people are already using jumps the queue ahead of every new idea. Tell us what you did, what happened, and what you expected instead.",
      titleLabel: "What's wrong — in a few words",
      bodyLabel: "What you did, what happened, and what you expected instead"
    },
    improve: {
      lead: "<b>Wish it better.</b> You're the one actually using it — if it asks in the wrong order, misses something, or gets in your way, say so. Improvements get built the same way new things do.",
      titleLabel: "What should change",
      bodyLabel: "How it should work instead — and what you're doing when it gets in the way"
    },
    new_tool: {
      lead: "<b>A wishing well that actually works.</b> Ask for the thing you keep doing by hand. If it passes the bar, it gets built and it just shows up.",
      titleLabel: "The thing you want",
      bodyLabel: "What it should do — and what you'd use it for"
    }
  };

  /* ---- styles: fb- prefixed so they can never collide with the host app ----
   * MOBILE-WATERTIGHT by construction (operator 2026-08-04: "don't make anything
   * that's gonna clip or alter if zoomed out on phone"): no fixed widths, the
   * sheet is width:min(560px,100%) and scrolls internally, every control is >=44px,
   * long words break instead of pushing the layout sideways, and the trigger sits
   * above the iOS home indicator via env(safe-area-inset-*). */
  var CSS = ''
    + '.fb-btn{position:fixed;right:max(14px,env(safe-area-inset-right));bottom:max(14px,env(safe-area-inset-bottom));z-index:2147483000;'
    + 'min-height:44px;padding:11px 16px;border:0;border-radius:999px;cursor:pointer;'
    + 'font:700 13px/1 var(--fb-sans);letter-spacing:.06em;text-transform:uppercase;'
    + 'background:var(--fb-accent);color:var(--fb-ink);box-shadow:0 6px 20px rgba(0,0,0,.34);}'
    + '.fb-btn:hover{filter:brightness(1.08)}'
    + '.fb-wrap{position:fixed;inset:0;z-index:2147483100;display:none;align-items:flex-end;justify-content:center;'
    + 'background:rgba(8,10,13,.62);}'
    + '.fb-wrap.on{display:flex}'
    + '@media (min-width:620px){.fb-wrap{align-items:center}}'
    + '.fb-sheet{width:min(560px,100%);max-height:min(92vh,100%);overflow:auto;-webkit-overflow-scrolling:touch;'
    + 'background:var(--fb-paper);color:var(--fb-text);border-radius:14px 14px 0 0;'
    + 'padding-bottom:max(14px,env(safe-area-inset-bottom));font-family:var(--fb-sans);overflow-wrap:anywhere;}'
    + '@media (min-width:620px){.fb-sheet{border-radius:12px}}'
    + '.fb-head{position:sticky;top:0;background:var(--fb-steel);color:#EEF0EA;padding:15px 16px;'
    + 'display:flex;align-items:flex-start;gap:12px;border-bottom:2px solid var(--fb-accent);}'
    + '.fb-head h2{margin:0;font:700 17px/1.15 var(--fb-cond);text-transform:uppercase;letter-spacing:.04em}'
    + '.fb-head p{margin:3px 0 0;font-size:11px;color:#AEB6BE;font-family:var(--fb-mono);letter-spacing:.08em;text-transform:uppercase}'
    + '.fb-x{margin-left:auto;flex:none;min-width:44px;min-height:44px;background:transparent;border:1px solid #46505B;'
    + 'color:#C7CDD3;border-radius:6px;font-size:20px;line-height:1;cursor:pointer}'
    + '.fb-body{padding:14px 16px 18px}'
    + '.fb-lead{font-size:13px;line-height:1.5;margin:0 0 13px;color:var(--fb-text)}'
    + '.fb-f{margin-bottom:13px}'
    + '.fb-f>label{display:block;font:700 10.5px/1.3 var(--fb-mono);letter-spacing:.11em;text-transform:uppercase;'
    + 'color:var(--fb-muted);margin-bottom:5px}'
    + '.fb-f>label i{font-style:normal;font-weight:400;text-transform:none;letter-spacing:.02em}'
    + '.fb-f input,.fb-f select,.fb-f textarea{width:100%;max-width:100%;min-height:44px;padding:11px 12px;'
    + 'font:400 16px/1.35 var(--fb-sans);color:var(--fb-text);background:#fff;border:1px solid var(--fb-line);border-radius:7px;}'
    + '.fb-f textarea{min-height:96px;resize:vertical}'
    + '.fb-f input:focus,.fb-f select:focus,.fb-f textarea:focus{outline:2px solid var(--fb-accent);outline-offset:1px;border-color:var(--fb-accent)}'
    + '.fb-seg{display:flex;flex-wrap:wrap;gap:7px}'
    + '.fb-seg button{flex:1 1 auto;min-width:0;min-height:44px;padding:10px 12px;cursor:pointer;'
    + 'font:700 12px/1.2 var(--fb-sans);color:var(--fb-text);background:#fff;border:1px solid var(--fb-line);border-radius:7px}'
    + '.fb-seg button.on{background:var(--fb-accent);color:var(--fb-ink);border-color:var(--fb-accent)}'
    + '.fb-row{display:grid;grid-template-columns:1fr;gap:11px}'
    + '@media (min-width:520px){.fb-row{grid-template-columns:1fr 1fr}}'
    + '.fb-err{display:none;background:#FDECEC;border:1px solid #E6A6A6;color:#8A1F1F;'
    + 'border-radius:7px;padding:10px 12px;font-size:13px;margin-bottom:11px}'
    + '.fb-acts{display:flex;flex-wrap:wrap;gap:9px;align-items:center;margin-top:4px}'
    + '.fb-send{min-height:46px;padding:12px 20px;border:0;border-radius:7px;cursor:pointer;'
    + 'font:700 14px/1 var(--fb-cond);text-transform:uppercase;letter-spacing:.06em;'
    + 'background:var(--fb-accent);color:var(--fb-ink)}'
    + '.fb-send[disabled]{opacity:.6;cursor:default}'
    + '.fb-cancel{min-height:46px;padding:12px 16px;background:transparent;border:1px solid var(--fb-line);'
    + 'border-radius:7px;cursor:pointer;font:700 13px/1 var(--fb-sans);color:var(--fb-muted)}'
    + '.fb-note{font-size:11.5px;color:var(--fb-muted);margin:11px 0 0;line-height:1.45}'
    + '.fb-done{text-align:center;padding:22px 6px}'
    + '.fb-done .fb-check{width:52px;height:52px;line-height:52px;margin:0 auto 12px;border-radius:50%;'
    + 'background:var(--fb-accent);color:var(--fb-ink);font-size:26px;font-weight:700}'
    + '.fb-done h3{margin:0 0 7px;font:700 19px/1.2 var(--fb-cond);text-transform:uppercase;letter-spacing:.03em}'
    + '.fb-done p{margin:0 auto 16px;max-width:44ch;font-size:13px;line-height:1.5;color:var(--fb-muted)}';

  var modal, form, errBox, sendBtn, stepsF, kind = "bug", anon = false, setKind, areaRow, leadEl, titleLab, bodyLab;
  var refs = null;

  function injectStyles() {
    if (document.querySelector('style[data-fb="1"]')) return;
    var st = document.createElement("style");
    st.setAttribute("data-fb", "1");
    st.textContent =
      ':root{--fb-accent:' + S.accent + ';--fb-ink:' + S.accentInk + ';'
      + '--fb-steel:#242A31;--fb-paper:#F6F6F3;--fb-text:#12161A;--fb-line:#C3C7C0;--fb-muted:#5D656E;'
      + '--fb-sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;'
      + '--fb-cond:"Arial Narrow","Helvetica Neue Condensed","Liberation Sans Narrow","Roboto Condensed",var(--fb-sans);'
      + '--fb-mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;}'
      + CSS;
    document.head.appendChild(st);
  }

  function build() {
    errBox = h("div", { class: "fb-err", role: "alert" });
    leadEl = h("p", { class: "fb-lead" });

    // KIND — three buttons, not a select: on a phone the choice must be visible
    // without a tap, and the ORDER encodes the priority the loop serves them in.
    var kindBtns = KINDS.map(function (k) {
      var b = h("button", { type: "button", title: k.hint, class: k.v === kind ? "on" : "" }, [k.label]);
      b.addEventListener("click", function () { setKind(k.v); });
      return b;
    });
    var kindRow = h("div", { class: "fb-f" }, [
      h("label", {}, ["What kind of feedback is this?"]),
      h("div", { class: "fb-seg" }, kindBtns)
    ]);

    // WHICH PART — only for bug/improve. One tap, and it is the difference between
    // an actionable report and a note nobody can act on.
    var areaSel = h("select", { name: "about_tool", "aria-label": S.areaLabel });
    areaSel.appendChild(h("option", { value: "" }, [S.areaLabel + "?"]));
    S.areas.forEach(function (a) { areaSel.appendChild(h("option", { value: a.v }, [a.label])); });
    areaRow = h("div", { class: "fb-f", style: S.areas.length ? "" : "display:none" }, [
      h("label", {}, [S.areaLabel]), areaSel
    ]);

    titleLab = h("label", {}, [COPY[kind].titleLabel]);
    bodyLab = h("label", {}, [COPY[kind].bodyLabel]);

    var titleF = h("div", { class: "fb-f" }, [titleLab,
      h("input", { name: "tool_title", type: "text", maxlength: "200", autocomplete: "off" })]);
    var bodyF = h("div", { class: "fb-f" }, [bodyLab,
      h("textarea", { name: "tool_purpose", maxlength: "2000" })]);

    var stepsLab = h("label", {}, ["Anything that helps us reproduce it ", h("i", {}, ["(optional)"])]);
    stepsF = h("div", { class: "fb-f" }, [stepsLab,
      h("textarea", { name: "example", maxlength: "1600", placeholder: "The file, the setting, the browser — whatever you had going on." })]);

    /* CREDENTIALS — weight, not a login (operator 2026-08-04). Optional, never
     * required to send, NEVER published. It tells the loop the provenance of a
     * correction and the context to build it in. */
    var roleSel = h("select", { name: "requester_role", "aria-label": "You are" });
    roleSel.appendChild(h("option", { value: "" }, ["You are…"]));
    S.roles.forEach(function (r) { roleSel.appendChild(h("option", { value: r[0] }, [r[1]])); });

    var ctxSel = null;
    if (S.contexts.length) {
      ctxSel = h("select", { name: "fb_context", "aria-label": S.contextLabel });
      ctxSel.appendChild(h("option", { value: "" }, [S.contextLabel + "…"]));
      S.contexts.forEach(function (c) { ctxSel.appendChild(h("option", { value: c }, [c])); });
    }

    var nameRow = h("div", { class: "fb-row" }, [
      h("div", { class: "fb-f" }, [h("label", {}, ["Name ", h("i", {}, ["(optional)"])]),
        h("input", { name: "requester_name", type: "text", maxlength: "120", autocomplete: "off" })]),
      h("div", { class: "fb-f" }, [h("label", {}, ["Company / local ", h("i", {}, ["(optional)"])]),
        h("input", { name: "requester_company", type: "text", maxlength: "160", autocomplete: "off" })])
    ]);

    var idNamed = h("button", { type: "button", class: "on" }, ["With my name"]);
    var idAnon = h("button", { type: "button" }, ["Anonymous"]);
    function setAnon(on) {
      anon = on;
      nameRow.style.display = on ? "none" : "";
      idNamed.classList.toggle("on", !on);
      idAnon.classList.toggle("on", on);
    }
    idNamed.addEventListener("click", function () { setAnon(false); });
    idAnon.addEventListener("click", function () { setAnon(true); });

    var credF = h("div", { class: "fb-f" }, [
      h("label", {}, ["Who's asking ", h("i", {}, ["(optional — it never gets published, it just tells us how to weigh it)"])]),
      h("div", { class: "fb-seg" }, [idNamed, idAnon])
    ]);

    var contactF = h("div", { class: "fb-f" }, [
      h("label", {}, ["Email ", h("i", {}, ["(optional — only used to tell you when it's fixed)"])]),
      h("input", { name: "contact", type: "email", maxlength: "200", autocomplete: "email" })]);

    sendBtn = h("button", { type: "submit", class: "fb-send" }, ["Send it"]);
    var cancel = h("button", { type: "button", class: "fb-cancel" }, ["Cancel"]);
    cancel.addEventListener("click", close);

    var kids = [leadEl, errBox, kindRow, areaRow, titleF, bodyF, stepsF,
      h("div", { class: "fb-f" }, [h("label", {}, ["You are ", h("i", {}, ["(optional)"])]), roleSel])];
    if (ctxSel) kids.push(h("div", { class: "fb-f" }, [h("label", {}, [S.contextLabel + " ", h("i", {}, ["(optional)"])]), ctxSel]));
    kids.push(credF, nameRow, contactF,
      h("div", { class: "fb-acts" }, [sendBtn, cancel]),
      h("p", { class: "fb-note" }, ["Goes straight to the loop that builds this. It reads everything that comes in and fixes the broken things first. Nothing you send here is published."]));

    form = h("form", {}, kids);
    form.setAttribute("novalidate", "novalidate");
    form.addEventListener("submit", submit);

    var body = h("div", { class: "fb-body" }, [form]);
    var closeBtn = h("button", { type: "button", class: "fb-x", "aria-label": "Close" }, ["×"]);
    closeBtn.addEventListener("click", close);
    var head = h("div", { class: "fb-head" }, [
      h("div", {}, [h("h2", {}, ["Tell us"]), h("p", {}, [S.name])]),
      closeBtn
    ]);

    var sheet = h("div", { class: "fb-sheet", role: "dialog", "aria-modal": "true", "aria-label": "Send feedback" }, [head, body]);
    modal = h("div", { class: "fb-wrap" }, [sheet]);
    modal.addEventListener("click", function (e) { if (e.target === modal) close(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && modal && modal.classList.contains("on")) close(); });

    setKind = function (v) {
      kind = v;
      kindBtns.forEach(function (b, i) { b.classList.toggle("on", KINDS[i].v === v); });
      leadEl.innerHTML = COPY[v].lead;
      titleLab.textContent = COPY[v].titleLabel;
      bodyLab.textContent = COPY[v].bodyLabel;
      areaRow.style.display = (v !== "new_tool" && S.areas.length) ? "" : "none";
      stepsF.style.display = (v === "bug") ? "" : "none";
    };
    setKind(kind);

    document.body.appendChild(modal);
    return { areaSel: areaSel, ctxSel: ctxSel, body: body };
  }

  function showErr(m) {
    errBox.textContent = m;
    errBox.style.display = "block";
    try { errBox.scrollIntoView({ block: "nearest" }); } catch (e) {}
  }

  function submit(e) {
    e.preventDefault();
    errBox.style.display = "none";
    var fd = new FormData(form);
    var title = (fd.get("tool_title") || "").trim();
    var bodyTxt = (fd.get("tool_purpose") || "").trim();

    // Mirror the DB CHECK constraints client-side so a user gets a sentence they
    // can act on instead of a raw 400 from PostgREST.
    if (title.length < 3) { showErr("Give it a short title — a few words is plenty."); return; }
    if (bodyTxt.length < 10) { showErr("Add a line or two so we can actually act on it."); return; }
    var about = (fd.get("about_tool") || "").trim();
    if (kind !== "new_tool" && S.areas.length && !about) {
      showErr(kind === "bug" ? "Which part is broken?" : "Which part should be better?"); return;
    }
    if (!CFG_READY) { showErr("Feedback is live on the published site — this looks like a local or preview copy."); return; }

    /* The optional usage context rides in `example`, clearly labelled, rather than
     * adding a column: one queue with no migration is what makes this drop-in
     * usable on any surface the day it ships. */
    var extra = (fd.get("example") || "").trim();
    var ctx = refs && refs.ctxSel ? (fd.get("fb_context") || "").trim() : "";
    if (ctx) extra = (extra ? extra + "\n\n" : "") + S.contextLabel + ": " + ctx;

    var payload = {
      requester_role: fd.get("requester_role") || null,
      tool_title: title,
      tool_purpose: bodyTxt,
      example: extra || null,
      requester_name: anon ? null : ((fd.get("requester_name") || "").trim() || null),
      requester_company: anon ? null : ((fd.get("requester_company") || "").trim() || null),
      contact: (fd.get("contact") || "").trim() || null,
      // `trade` is the SURFACE key — a bounded lowercase slug by design (076), so
      // "collage" or any future product needs no migration to start collecting.
      trade: S.surface,
      kind: kind,
      about_tool: (kind === "new_tool") ? null : (about || null),
      source: S.surface + "_feedback",
      user_agent: (navigator.userAgent || "").slice(0, 500)
    };

    sendBtn.disabled = true; sendBtn.textContent = "Sending…";
    fetch(CFG.url + "/rest/v1/" + CFG.table, {
      method: "POST",
      headers: { "apikey": CFG.anon, "Authorization": "Bearer " + CFG.anon, "Content-Type": "application/json", "Prefer": "return=minimal" },
      body: JSON.stringify(payload)
    }).then(function (r) {
      if (r.ok) done();
      else {
        r.text().then(function (t) { showErr("Couldn't send (" + r.status + "). " + (t ? t.slice(0, 140) : "Please try again.")); });
        sendBtn.disabled = false; sendBtn.textContent = "Send it";
      }
    }).catch(function () {
      showErr("Network error — check your connection and try again.");
      sendBtn.disabled = false; sendBtn.textContent = "Send it";
    });
  }

  function done() {
    var again = h("button", { type: "button", class: "fb-send" }, ["Send another"]);
    again.addEventListener("click", function () {
      form.reset(); setKind("bug"); errBox.style.display = "none";
      sendBtn.disabled = false; sendBtn.textContent = "Send it";
      refs.body.innerHTML = ""; refs.body.appendChild(form);
    });
    var shut = h("button", { type: "button", class: "fb-cancel" }, ["Close"]);
    shut.addEventListener("click", close);
    var d = h("div", { class: "fb-done" }, [
      h("div", { class: "fb-check" }, ["✓"]),
      h("h3", {}, ["Got it"]),
      h("p", {}, ["This goes to the loop that builds " + S.name + ". Broken things get fixed first — ahead of every new idea. If you left an email you'll hear when it lands."]),
      h("div", { class: "fb-acts", style: "justify-content:center" }, [again, shut])
    ]);
    refs.body.innerHTML = ""; refs.body.appendChild(d);
  }

  function open(k) {
    if (!modal) { injectStyles(); refs = build(); }
    if (k && KINDS.some(function (x) { return x.v === k; })) setKind(k);
    modal.classList.add("on");
    try {
      if (window.matchMedia && window.matchMedia("(min-width:620px)").matches) {
        var first = form.querySelector("input,select,textarea");
        if (first) first.focus();
      }
    } catch (e) {}
  }
  function close() { if (modal) modal.classList.remove("on"); }

  function mount() {
    if (!S.trigger) return;
    if (document.querySelector(".fb-btn")) return;
    injectStyles();
    var b = h("button", { type: "button", class: "fb-btn", "aria-haspopup": "dialog" }, [S.triggerText]);
    b.addEventListener("click", function () { open(); });
    document.body.appendChild(b);
  }

  // The public handle. A surface that wants its own button sets trigger:false and
  // calls Feedback.open("bug") from wherever it likes — no framework coupling.
  window.Feedback = { open: open, close: close, surface: S.surface, config: S, ready: CFG_READY };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
  else mount();
})();
