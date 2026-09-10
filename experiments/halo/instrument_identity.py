#!/usr/bin/env python3
"""instrument_identity.py - a behavioural identity for the HALO resonance chamber.

WHY NOT sha256 OF THE PAGE: the chamber carries every sealed ring as one HTML
comment, so publishing prose changes the whole-file hash while changing no
simulation. Ring 17's labelled set (data/results/halo/memory_pilot/reproduction_probe.json)
re-ran one tag seven times changing one layer each and found four page revisions
in exactly TWO behavioural classes:
    class A = {HEAD-at-ring-17, 122d0a57, 05dfa4ab}   class B = {c6cd2cbe}
This script computes digests that reproduce that partition.

WHAT sim_digest COVERS (the GPU is where the physics is):
  * every GLSL literal in the page's main inline script - found by "contains a GLSL
    type or qualifier token AND a semicolon AND >60 chars", NOT by looking for
    'void main' (a marker rule silently misses PM_GLSL and FIELD_GLSL, which hold
    pmAt/pmCellOf and radialAt/legendreP/shTerm/cavityForce), with GLSL comments
    dropped and whitespace collapsed - comments and layout cannot change a float;
  * the named physics constants, because the GLSL interpolates ${EXTENT}, ${SG_GAIN},
    ${FORCE_SCALE}, ${CHLADNI_SCALE}, ${RESTITUTION}, ${PM_N}, ${PM_TX}, ${PM_TY},
    ${RAD_N} as text, so their VALUES must be hashed separately, plus TICK,
    PM_ITERS and PM_HALF_JS which the JS reads and the GLSL never sees;
  * the scenario presets actually driven, so a changed preset cannot masquerade
    as the same instrument.
WHAT IT EXCLUDES, ON PURPOSE: HTML comments (the rings), CSS, UI markup, prose,
the test build's probe bridge, and all other JavaScript.

WHAT IT THEREFORE MISSES - state this in any run record: a JS-only change to the
tick loop (for example const nSub = effectiveSubsteps() -> 2) does NOT move
sim_digest. tick_digest covers that code, but it is a change detector, not an
identity: it OVER-reports on this labelled set, because ring 16 added bench guard
calls to simTick that provably did not move the output. Record both, plus the
page's git rev and whole-file sha256.

Stdlib only. Author: Aldrin Payopay.
"""
import argparse, hashlib, json, pathlib, re, subprocess, sys

PAGE_REL = 'HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html'
GLSL_TOKEN = re.compile(r'\b(?:vec2|vec3|vec4|mat2|mat3|mat4|sampler2D|uniform|varying'
                        r'|attribute|precision|gl_\w+)\b')
NAMED_CONSTS = ('TICK', 'PM_ITERS', 'PM_N', 'PM_TX', 'PM_TY', 'PM_HALF_JS', 'EXTENT',
                'SG_GAIN', 'FORCE_SCALE', 'CHLADNI_SCALE', 'RESTITUTION', 'RAD_N')
TICK_FUNCS = ('simTick', 'simStep', 'pmSolve', 'pmDeposit', 'pmSolveExact', 'pmAlloc',
              'pmRebuild', 'effectiveSubsteps', 'autoSubsteps', 'snapshotPrev',
              'prevTexture', 'updateCosmos', 'labReadDensity', 'fieldAmp', 'reseed')
DRIVEN_PRESETS = ('spinchladni', 'goldstair', 'hardprint', 'stillspindle', 'jellyfish')
# 'default' is not a preset: memory_prereg_run.js:66 clicks nothing and takes the page's
# own DEFAULTS, which 30 of the 81 recorded runs used. A change to DEFAULTS would change
# what those runs compute, so the state block is hashed beside the presets.
PROBE_MARK = '/* ---- test-only probe bridge'
IIFE_CLOSE = '\n})();'
KEYWORDS = ('return', 'typeof', 'instanceof', 'in', 'of', 'new', 'delete', 'void',
            'case', 'do', 'else', 'yield', 'await')


def scan(src):
    """Split JS into typed spans. Validated by feeding the comment-stripped result
    of all five labelled builds to `node --check` (all five parse)."""
    spans, i, n, buf = [], 0, len(src), []
    last_sig, last_word = '', ''
    def flush():
        if buf:
            spans.append(('code', ''.join(buf))); buf.clear()
    while i < n:
        c, two = src[i], src[i:i+2]
        if two == '//':
            flush(); j = src.find('\n', i); j = n if j < 0 else j
            spans.append(('line_comment', src[i:j])); i = j; continue
        if two == '/*':
            flush(); j = src.find('*/', i+2); j = n if j < 0 else j+2
            spans.append(('block_comment', src[i:j])); i = j; continue
        if c in '"\'':
            flush(); j = i+1
            while j < n:
                if src[j] == '\\': j += 2; continue
                if src[j] == c: j += 1; break
                j += 1
            spans.append(('string', src[i:j])); last_sig = 'x'; i = j; continue
        if c == '`':
            flush(); j, depth = i+1, 0
            while j < n:
                if src[j] == '\\': j += 2; continue
                if src[j] == '$' and src[j+1:j+2] == '{': depth += 1; j += 2; continue
                if src[j] == '}' and depth: depth -= 1; j += 1; continue
                if src[j] == '`' and depth == 0: j += 1; break
                j += 1
            spans.append(('template', src[i:j])); last_sig = 'x'; i = j; continue
        if c == '/' and (last_sig in '(,=:[!&|?{};+-*%~^<>\n' or last_sig == ''
                         or last_word in KEYWORDS):
            flush(); j, inclass = i+1, False
            while j < n:
                if src[j] == '\\': j += 2; continue
                if src[j] == '[': inclass = True
                elif src[j] == ']': inclass = False
                elif src[j] == '/' and not inclass: j += 1; break
                elif src[j] == '\n': break
                j += 1
            while j < n and src[j].isalpha(): j += 1
            spans.append(('regex', src[i:j])); last_sig = 'x'; i = j; continue
        buf.append(c)
        if not c.isspace():
            last_sig = c
            if c.isalnum() or c in '_$':
                k = len(buf)-1
                while k > 0 and (buf[k-1].isalnum() or buf[k-1] in '_$'): k -= 1
                last_word = ''.join(buf[k:])
            else:
                last_word = ''
        i += 1
    flush()
    return spans


def _flatten(src):
    out, mask = [], []
    for k, t in scan(src):
        out.append(t); mask.extend([k != 'code'] * len(t))
    return ''.join(out), mask


def _ws(s):
    return re.sub(r'\s+', ' ', s).strip()


def _norm_glsl(t):
    t = re.sub(r'/\*.*?\*/', ' ', t, flags=re.S)
    t = re.sub(r'//[^\n]*', ' ', t)
    return _ws(t)


def _match_block(text, start, mask=None):
    i = text.find('{', start); d, j = 0, i
    while j < len(text):
        if mask is None or not mask[j]:
            if text[j] == '{': d += 1
            elif text[j] == '}':
                d -= 1
                if d == 0: break
        j += 1
    return text[i:j+1]


def main_script(html):
    bodies = [m.group(2) for m in re.finditer(r'<script([^>]*)>(.*?)</script>', html, re.S)
              if 'src=' not in m.group(1) and 'ld+json' not in m.group(1)]
    body = max(bodies, key=len)
    i = body.find(PROBE_MARK)                       # drop the test build's probe bridge
    if i >= 0:
        j = body.find(IIFE_CLOSE, i)
        body = body[:i] + body[j:] if j > 0 else body[:i]
    return body


def glsl_literals(body):
    return [_norm_glsl(t) for k, t in scan(body)
            if k in ('string', 'template') and GLSL_TOKEN.search(t)
            and ';' in t and len(t) > 60]


def consts(body):
    text, mask = _flatten(body)
    out = {}
    for m in re.finditer(r'\b(?:const|let|var)\s+([A-Z][A-Z0-9_]{1,})\s*=\s*([^;\n]+)', text):
        if not mask[m.start()]:
            out[m.group(1)] = _ws(m.group(2))
    return out


def functions(body):
    """Top-level named functions, comments stripped and whitespace collapsed, so that
    commentary and layout cannot move tick_digest. Names defined more than once are
    dropped rather than guessed at."""
    text, mask = _flatten(body)
    seen = {}
    for m in re.finditer(r'\bfunction\s+([A-Za-z_$][\w$]*)\s*\(', text):
        if mask[m.start()]:
            continue
        i = text.find('{', m.end())
        if i < 0 or mask[i]:
            continue
        d, j = 0, i
        while j < len(text):
            if not mask[j]:
                if text[j] == '{': d += 1
                elif text[j] == '}':
                    d -= 1
                    if d == 0: break
            j += 1
        src = text[m.start():j+1]
        src = ''.join(t for k, t in scan(src) if k not in ('line_comment', 'block_comment'))
        seen.setdefault(m.group(1), []).append(_ws(src))
    return {k: v[0] for k, v in seen.items() if len(v) == 1}


def presets(body, names):
    text, mask = _flatten(body)
    k = text.find('SCENARIOS')
    if k < 0:
        return {}
    tab = _match_block(text, k, mask)
    out = {}
    for nm in names:
        p = tab.find(nm + ':')
        if p >= 0:
            out[nm] = _ws(_match_block(tab, p))
    return out


def defaults_block(body):
    """The DEFAULTS state object, verbatim. The runs tagged preset 'default' are driven
    by it and by nothing else, so it is part of the instrument for 30 of the 81 records."""
    text, mask = _flatten(body)
    k = text.find('const DEFAULTS')
    return _ws(_match_block(text, k, mask)) if k >= 0 else 'ABSENT'


def digests(html, driven=DRIVEN_PRESETS):
    body = main_script(html)
    g = glsl_literals(body)
    c = consts(body)
    named = {k: c.get(k, 'ABSENT') for k in NAMED_CONSTS}
    fns = functions(body)
    core = {'glsl': g, 'consts': named}
    sim = dict(core, presets=presets(body, driven), defaults=defaults_block(body))
    tick = {f: fns.get(f, 'ABSENT') for f in TICK_FUNCS}
    h = lambda o: hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()
    return {'sim_digest': h(sim), 'core_digest': h(core), 'tick_digest': h(tick),
            'whole_file_sha256': hashlib.sha256(html.encode()).hexdigest(),
            'glsl_chunks': len(g), 'glsl_bytes': sum(map(len, g))}


def from_git(rev, repo):
    return subprocess.run(['git', '-C', repo, 'show', f'{rev}:{PAGE_REL}'],
                          capture_output=True, text=True, check=True).stdout


# ---------------------------------------------------------------- self-test
LABELLED = {'9e7e67c5': 'A', '05dfa4ab': 'A', '122d0a57': 'A', 'c6cd2cbe': 'B'}

def self_test(repo, extra_pages=None):
    """Reproduce ring 17's two-class partition from the committed pages alone."""
    seen, ok = {}, True
    for rev, cls in LABELLED.items():
        d = digests(from_git(rev, repo))
        seen[rev] = d['sim_digest']
        print(f'  {rev}  class {cls}  sim_digest {d["sim_digest"]}')
    groups = {}
    for rev, dg in seen.items():
        groups.setdefault(dg, []).append(rev)
    got = {frozenset(v) for v in groups.values()}
    want = {frozenset(['9e7e67c5', '05dfa4ab', '122d0a57']), frozenset(['c6cd2cbe'])}
    print(f'  classes produced: {len(groups)} (want 2)')
    if got != want:
        merged = any('c6cd2cbe' in v and len(v) > 1 for v in groups.values())
        print('  FAIL:', 'UNDER-REPORT - c6cd2cbe merged with class A' if merged
              else 'OVER-REPORT - class A split')
        ok = False
    else:
        print('  PASS: {HEAD, 122d0a57, 05dfa4ab} identical, {c6cd2cbe} distinct')
    # a prose-only change must NOT move the digest: 43e5081f -> 9e7e67c5 added only
    # the ring 17 HTML comment
    a = digests(from_git('43e5081f', repo)); b = digests(from_git('9e7e67c5', repo))
    same = a['sim_digest'] == b['sim_digest']
    print(f'  prose-only control (43e5081f -> 9e7e67c5, ring 17 comment appended): '
          f'sim_digest {"unchanged - PASS" if same else "CHANGED - FAIL"}; '
          f'whole-file sha256 {"unchanged" if a["whole_file_sha256"] == b["whole_file_sha256"] else "changed (this is why sha256 over-reports)"}')
    return ok and same


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('page', nargs='?', help='a built or shipped chamber HTML file')
    ap.add_argument('--from-git', metavar='REV', help='hash the page at a committed revision')
    ap.add_argument('--repo', default='/Volumes/dual/nested-resonance-memory-archive')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        print('self-test: ring 17 labelled set, from committed pages')
        sys.exit(0 if self_test(a.repo) else 1)
    html = from_git(a.from_git, a.repo) if a.from_git else pathlib.Path(a.page).read_text()
    print(json.dumps(digests(html), indent=1))
