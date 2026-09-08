// Author: Aldrin Payopay · GPL-3.0-only
import { DEFAULT_RECIPE, validateRecipe, deriveRecipe, resolveTheme, generateBranches } from './engine.mjs';

const $ = id => document.getElementById(id);
const ROOT = document.documentElement;
const RECIPE_KEY = 'page-study.recipe.v1';
const WISH_KEY = 'page-study.wish.v1';
const WRITING_KEY = 'page-study.writing.v1';
const answerFields = ['palette', 'density', 'typeScale', 'motif'];
const systemTheme = matchMedia('(prefers-color-scheme: dark)');
let recipe = DEFAULT_RECIPE;
let previous = null;
let timer;
let initialNotice = 'Choices save automatically on this browser.';
const view = new URLSearchParams(location.search).get('view') === 'desk' ? 'desk' : 'explore';

function read(key) { return localStorage.getItem(key); }
function persist(key, value, status, success) {
  try { localStorage.setItem(key, value); status.textContent = success; return true; }
  catch { status.textContent = 'Storage is unavailable. You can still save a file.'; return false; }
}
try {
  const saved = read(RECIPE_KEY);
  if (saved !== null) { recipe = validateRecipe(JSON.parse(saved)); initialNotice = 'Your saved choices are back.'; }
} catch { initialNotice = 'Saved choices could not be read. Using the default page; you can open a recipe file.'; }

function updateTheme() {
  const now = new Date();
  const effective = resolveTheme(recipe.mode, now, systemTheme.matches);
  ROOT.dataset.theme = effective;
  $('time-badge').textContent = `${effective === 'dark' ? 'Night' : 'Day'} palette · ${recipe.mode === 'time' ? 'local time' : recipe.mode === 'system' ? 'device setting' : 'your choice'}`;
  $('theme-explanation').textContent = recipe.mode === 'time'
    ? 'Light from 7 am to 7 pm in your local time. No location access needed.'
    : recipe.mode === 'system' ? 'Uses the light or dark appearance your device reports.' : 'Your choice stays in place until you change it.';
  clearTimeout(timer);
  if (recipe.mode === 'time') {
    const boundary = new Date(now);
    if (now.getHours() < 7) boundary.setHours(7, 0, 0, 0);
    else if (now.getHours() < 19) boundary.setHours(19, 0, 0, 0);
    else { boundary.setDate(boundary.getDate() + 1); boundary.setHours(7, 0, 0, 0); }
    // Also resample once a minute so an awake device changing time zone recovers.
    timer = setTimeout(updateTheme, Math.min(60000, Math.max(1, boundary - now)));
  }
}

function draw() {
  const group = $('art-shapes');
  group.replaceChildren();
  const add = (tag, attrs) => {
    const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [key, value] of Object.entries(attrs)) element.setAttribute(key, String(value));
    group.append(element);
  };
  if (recipe.motif === 'branch') {
    for (const branch of generateBranches(recipe.seed)) add('path', { d:branch.d, 'stroke-width':branch.width, opacity:branch.opacity, fill:'none', stroke:'currentColor', 'stroke-linecap':'round' });
  } else if (recipe.motif === 'orbit') {
    let state = recipe.seed >>> 0;
    const next = () => { state = (Math.imul(state, 1664525) + 1013904223) >>> 0; return state / 4294967296; };
    for (let i = 0; i < 11; i++) {
      const rx = 9 + i * 3, ry = 8 + next() * 29;
      add('ellipse', { cx:50, cy:51, rx, ry, transform:`rotate(${(next()*170).toFixed(3)} 50 51)`, fill:'none', stroke:'currentColor', 'stroke-width':'.45', opacity:.5 + next()*.4 });
    }
    add('circle', { cx:50, cy:51, r:3.3, fill:'var(--secondary)' });
  }
  $('art').toggleAttribute('hidden', recipe.motif === 'quiet');
  $('art').setAttribute('aria-label', recipe.motif === 'orbit' ? 'An original orbit pattern generated from your page recipe' : 'An original branching pattern generated from your page recipe');
  $('pattern-caption').textContent = recipe.motif === 'quiet' ? 'A little more quiet.' : `Pattern ${recipe.seed.toLocaleString('en-US')} · ${recipe.motif === 'branch' ? 'branch study v1' : 'orbit study v1'}`;
}

function render() {
  ROOT.dataset.palette = recipe.palette;
  ROOT.dataset.density = recipe.density;
  ROOT.dataset.typeScale = recipe.typeScale;
  for (const field of [...answerFields, 'mode']) $(field).value = recipe[field];
  $('seed').value = String(recipe.seed);
  $('recipe-json').textContent = JSON.stringify(recipe, null, 2);
  $('undo').disabled = previous === null;
  updateTheme(); draw();
}

function apply(next, message = 'Saved on this browser.') {
  let checked;
  try { checked = validateRecipe(next); }
  catch { $('save-status').textContent = 'That recipe is not supported. Your current choices are unchanged.'; return false; }
  previous = recipe; recipe = checked; render();
  persist(RECIPE_KEY, JSON.stringify(recipe), $('save-status'), message);
  return true;
}

$('preferences-form').addEventListener('submit', event => event.preventDefault());
$('preferences-form').addEventListener('change', event => {
  if (event.target.id === 'mode') apply({ ...recipe, mode:$('mode').value });
  else {
    const answers = Object.fromEntries(answerFields.map(field => [field, $(field).value]));
    apply({ ...deriveRecipe(answers), mode:recipe.mode });
  }
});
$('another').addEventListener('click', () => apply({ ...recipe, seed:(recipe.seed + 1) >>> 0 }));
$('undo').addEventListener('click', () => {
  if (!previous) return;
  recipe = previous; previous = null; render();
  persist(RECIPE_KEY, JSON.stringify(recipe), $('save-status'), 'Previous choices restored.');
});
$('reset').addEventListener('click', () => apply(DEFAULT_RECIPE, 'Default page restored. Your writing and wish drafts are kept.'));
$('seed-form').addEventListener('submit', event => {
  event.preventDefault();
  const raw = $('seed').value;
  if (!/^\d{1,10}$/.test(raw) || Number(raw) > 4294967295) {
    $('save-status').textContent = 'Use a whole pattern number from 0 to 4,294,967,295.';
    return;
  }
  apply({ ...recipe, seed:Number(raw) });
});

function download(name, text, type) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const link = document.createElement('a'); link.href = url; link.download = name;
  document.body.append(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
$('export').addEventListener('click', () => download('my-page-recipe.json', JSON.stringify(recipe, null, 2), 'application/json'));
$('import-open').addEventListener('click', () => $('import-file').click());
$('import-file').addEventListener('change', async () => {
  const file = $('import-file').files[0];
  $('import-file').value = '';
  if (!file) return;
  if (file.size > 16384) { $('save-status').textContent = 'Choose a recipe file smaller than 16 KB.'; return; }
  // Do not let slow file reads overwrite a choice made after import began.
  const startedWith = recipe;
  try {
    const imported = validateRecipe(JSON.parse(await file.text()));
    if (recipe !== startedWith) { $('save-status').textContent = 'Your choices changed while the file opened. Open it again to apply it.'; return; }
    apply(imported, 'Recipe opened and saved on this browser.');
  } catch { $('save-status').textContent = 'That file is not a supported page recipe. Your current choices are unchanged.'; }
});

$('explore-view').hidden = view !== 'explore';
$('desk-view').hidden = view !== 'desk';
document.querySelector(`[data-view="${view}"]`).setAttribute('aria-current','page');
let wish = { text:'', view, recipe };
try {
  const saved = JSON.parse(read(WISH_KEY) || 'null');
  if (saved && typeof saved.text === 'string' && saved.text.length <= 2000 && ['explore','desk'].includes(saved.view)) {
    wish = { text:saved.text, view:saved.view, recipe:validateRecipe(saved.recipe) };
  }
} catch { $('wish-status').textContent = 'Your saved draft could not be read. You can save a new wish as a file.'; }
$('wish-text').value = wish.text;
$('wish-open').addEventListener('click', () => {
  if (!wish.text) wish = { text:'', view, recipe };
  $('wish-title').textContent = `Wish it better · ${wish.view === 'desk' ? 'Writing desk' : 'Explore'}`;
  $('wish-dialog').showModal(); $('wish-text').focus();
});
$('wish-close').addEventListener('click', () => $('wish-dialog').close());
$('wish-dialog').addEventListener('close', () => $('wish-open').focus());
$('wish-text').addEventListener('input', () => {
  wish.text = $('wish-text').value;
  persist(WISH_KEY, JSON.stringify(wish), $('wish-status'), 'Draft saved on this device. Not sent.');
});
$('wish-download').addEventListener('click', () => {
  if (!wish.text.trim()) { $('wish-status').textContent = 'Write a wish first.'; $('wish-text').focus(); return; }
  download('my-page-wish.json', JSON.stringify({ version:1, previewPage:wish.view, body:wish.text, recipe:wish.recipe, delivery:'local-file-only' }, null, 2), 'application/json');
  $('wish-status').textContent = 'Wish file prepared. It has not been sent.';
});

try { $('writing').value = (read(WRITING_KEY) || '').slice(0,20000); }
catch { $('desk-status').textContent = 'Local storage is unavailable; save a text file to keep your writing.'; }
function countWords() {
  const text = $('writing').value.trim();
  const count = text ? text.split(/\s+/u).length : 0;
  $('word-count').textContent = `${count} ${count === 1 ? 'word' : 'words'} · ${$('writing').value.length} characters`;
}
$('writing').addEventListener('input', () => {
  countWords();
  persist(WRITING_KEY, $('writing').value, $('desk-status'), 'Saved on this device.');
});
$('download-writing').addEventListener('click', () => download('my-writing.txt', $('writing').value, 'text/plain;charset=utf-8'));
systemTheme.addEventListener('change', updateTheme);
document.addEventListener('visibilitychange', () => { if (!document.hidden) updateTheme(); });
window.addEventListener('focus', updateTheme);
window.addEventListener('pageshow', updateTheme);
window.addEventListener('storage', event => {
  if (event.key !== RECIPE_KEY) return;
  try { recipe = event.newValue === null ? DEFAULT_RECIPE : validateRecipe(JSON.parse(event.newValue)); previous = null; render(); $('save-status').textContent = 'Choices updated from another tab.'; }
  catch { $('save-status').textContent = 'Another tab saved an unsupported recipe. Your choices are unchanged.'; }
});
render(); countWords(); $('save-status').textContent = initialNotice;
